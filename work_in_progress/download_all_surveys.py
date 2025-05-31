#!/usr/bin/env python3
"""
Comprehensive Survey Data Downloader for 3-4:2 Modal Framework Testing
Downloads ALL major cosmic survey datasets for framework validation

Date: 2025-01-29
Purpose: Systematic acquisition of telescope data for observational testing
Status: Ready for comprehensive data acquisition
"""

import os
import sys
import requests
import asyncio
import aiohttp
import pandas as pd
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SurveyDownloader:
    """Comprehensive survey data downloader"""
    
    def __init__(self, data_dir: str = "external_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Survey registry with download specifications
        self.surveys = {
            # TIER 1: IMMEDIATE ACCESS
            "2dfgrs_100k": {
                "name": "2dFGRS 100k Sample",
                "url": "http://www.2dfgrs.net/Release/2dfgrs.dat",
                "size": "25MB",
                "galaxies": 100000,
                "priority": "HIGHEST",
                "access": "immediate",
                "format": "ascii"
            },
            "2dfgrs_complete": {
                "name": "2dFGRS Complete",
                "url": "http://www.2dfgrs.net/Release/2dfgrs-complete.dat",
                "size": "120MB", 
                "galaxies": 245591,
                "priority": "HIGH",
                "access": "immediate",
                "format": "ascii"
            },
            "6dfgs_complete": {
                "name": "6dF Galaxy Survey",
                "url": "http://www-wfau.roe.ac.uk/6dFGS/cvs/6dFGS_FinalRelease.txt",
                "size": "180MB",
                "galaxies": 136304,
                "priority": "MEDIUM",
                "access": "immediate",
                "format": "ascii"
            },
            
            # SDSS Samples (SQL query based)
            "sdss_sample": {
                "name": "SDSS DR17 Galaxy Sample",
                "url": "http://skyserver.sdss.org/dr17/SkyServerWS/SearchTools/SqlSearch",
                "size": "45MB",
                "galaxies": 200000,
                "priority": "HIGHEST",
                "access": "immediate",
                "format": "csv",
                "query": """
                SELECT TOP 200000
                    objid, ra, dec, z, 
                    petroMag_r, petroR50_r,
                    petroMag_g, petroMag_i
                FROM SpecObj s
                JOIN PhotoObj p ON s.bestobjid = p.objid
                WHERE s.class = 'GALAXY' 
                AND s.z > 0.01 AND s.z < 0.8
                AND s.zwarning = 0
                AND p.petroMag_r < 20
                ORDER BY s.z
                """
            },
            
            # Galaxy clusters 
            "spt_clusters": {
                "name": "SPT Cluster Catalog",
                "url": "https://pole.uchicago.edu/public/data/sptsz-clusters/2500d_cluster_sample_Bocquet19.fits",
                "size": "5MB",
                "clusters": 677,
                "priority": "HIGH",
                "access": "immediate",
                "format": "fits"
            },
            
            "planck_clusters": {
                "name": "Planck Cluster Catalog",
                "url": "https://pla.esac.esa.int/pla/aio/product-action?COSMOLOGY.FILE_ID=COM_PCCS_030_R2.00.fits",
                "size": "25MB",
                "clusters": 1653,
                "priority": "HIGH", 
                "access": "immediate",
                "format": "fits"
            }
        }
        
        # Phase definitions
        self.phases = {
            "1": ["2dfgrs_100k", "sdss_sample", "spt_clusters"],
            "2": ["2dfgrs_complete", "6dfgs_complete", "planck_clusters"],
            "3": ["sdss_boss", "des_y1", "gama_dr4"],  # Requires registration
            "4": ["desi_edr", "des_y3", "hsc_pdr2"]   # Special access
        }
    
    async def download_file(self, session: aiohttp.ClientSession, url: str, 
                          filename: str) -> bool:
        """Download a single file with progress tracking"""
        try:
            logger.info(f"Downloading {filename} from {url}")
            
            async with session.get(url) as response:
                if response.status == 200:
                    filepath = self.data_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    
                    file_size = filepath.stat().st_size / (1024*1024)  # MB
                    logger.info(f"✅ Downloaded {filename} ({file_size:.1f} MB)")
                    return True
                else:
                    logger.error(f"❌ Failed to download {filename}: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error downloading {filename}: {str(e)}")
            return False
    
    def download_sdss_query(self, survey_key: str) -> bool:
        """Download SDSS data using SQL query"""
        survey = self.surveys[survey_key]
        
        logger.info(f"Executing SDSS query for {survey['name']}")
        
        # SDSS SQL query parameters
        params = {
            'cmd': survey['query'],
            'format': 'csv'
        }
        
        try:
            response = requests.post(survey['url'], data=params, timeout=300)
            
            if response.status_code == 200:
                filename = f"{survey_key}.csv"
                filepath = self.data_dir / filename
                
                with open(filepath, 'w') as f:
                    f.write(response.text)
                
                # Count rows
                df = pd.read_csv(filepath)
                logger.info(f"✅ Downloaded {survey['name']}: {len(df)} galaxies")
                return True
            else:
                logger.error(f"❌ SDSS query failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error with SDSS query: {str(e)}")
            return False
    
    async def download_phase(self, phase: str) -> Dict[str, bool]:
        """Download all surveys in a specific phase"""
        if phase not in self.phases:
            logger.error(f"Invalid phase: {phase}")
            return {}
        
        survey_keys = self.phases[phase]
        results = {}
        
        logger.info(f"🚀 Starting Phase {phase} downloads")
        logger.info(f"Surveys: {', '.join(survey_keys)}")
        
        # Special handling for different data types
        async with aiohttp.ClientSession() as session:
            for survey_key in survey_keys:
                if survey_key not in self.surveys:
                    logger.warning(f"Survey {survey_key} not found in registry")
                    results[survey_key] = False
                    continue
                
                survey = self.surveys[survey_key]
                
                if survey_key == "sdss_sample":
                    # Handle SDSS SQL query
                    results[survey_key] = self.download_sdss_query(survey_key)
                else:
                    # Handle direct downloads
                    filename = f"{survey_key}.{survey.get('format', 'dat')}"
                    results[survey_key] = await self.download_file(
                        session, survey['url'], filename
                    )
        
        return results
    
    def generate_data_registry(self) -> None:
        """Generate registry of downloaded datasets"""
        registry = {
            "timestamp": datetime.now().isoformat(),
            "data_directory": str(self.data_dir),
            "datasets": {}
        }
        
        # Check what files exist
        for survey_key, survey in self.surveys.items():
            filepath = self.data_dir / f"{survey_key}.{survey.get('format', 'dat')}"
            
            if filepath.exists():
                file_size = filepath.stat().st_size / (1024*1024)  # MB
                registry["datasets"][survey_key] = {
                    "name": survey["name"],
                    "file": str(filepath),
                    "size_mb": round(file_size, 1),
                    "status": "downloaded",
                    "galaxies": survey.get("galaxies", "unknown"),
                    "priority": survey["priority"]
                }
        
        # Save registry
        import yaml
        registry_path = self.data_dir / "data_registry.yaml"
        with open(registry_path, 'w') as f:
            yaml.dump(registry, f, default_flow_style=False)
        
        logger.info(f"✅ Registry saved: {registry_path}")
        logger.info(f"Downloaded datasets: {len(registry['datasets'])}")
    
    def estimate_resources(self, phase: str) -> Dict:
        """Estimate storage and processing requirements"""
        if phase not in self.phases:
            return {}
        
        survey_keys = self.phases[phase]
        total_size_mb = 0
        total_galaxies = 0
        
        for survey_key in survey_keys:
            if survey_key in self.surveys:
                survey = self.surveys[survey_key]
                # Extract size in MB
                size_str = survey.get("size", "0MB")
                size_mb = float(size_str.replace("MB", "").replace("GB", "").replace("KB", ""))
                if "GB" in size_str:
                    size_mb *= 1024
                elif "KB" in size_str:
                    size_mb /= 1024
                
                total_size_mb += size_mb
                total_galaxies += survey.get("galaxies", 0)
        
        return {
            "phase": phase,
            "datasets": len(survey_keys),
            "total_size_mb": round(total_size_mb, 1),
            "total_size_gb": round(total_size_mb / 1024, 2),
            "total_galaxies": total_galaxies,
            "estimated_processing_time": f"{max(1, total_size_mb // 100)} hours"
        }


async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Download cosmic survey data for 3-4:2 framework testing"
    )
    parser.add_argument("--phase", choices=["1", "2", "3", "4", "all"], 
                       default="1", help="Download phase")
    parser.add_argument("--estimate", action="store_true", 
                       help="Estimate resources without downloading")
    parser.add_argument("--data-dir", default="external_data", 
                       help="Data directory")
    
    args = parser.parse_args()
    
    downloader = SurveyDownloader(args.data_dir)
    
    if args.estimate:
        print("\n📊 RESOURCE ESTIMATES:")
        for phase in ["1", "2", "3", "4"]:
            estimate = downloader.estimate_resources(phase)
            print(f"\nPhase {phase}:")
            print(f"  Datasets: {estimate['datasets']}")
            print(f"  Storage: {estimate['total_size_gb']} GB")
            print(f"  Galaxies: {estimate['total_galaxies']:,}")
            print(f"  Processing: {estimate['estimated_processing_time']}")
        return
    
    phases_to_run = ["1", "2", "3", "4"] if args.phase == "all" else [args.phase]
    
    print(f"\n🔬 COMPREHENSIVE SURVEY DATA ACQUISITION")
    print(f"Target: 3-4:2 Modal Framework Validation")
    print(f"Phases: {', '.join(phases_to_run)}")
    print(f"Data directory: {args.data_dir}")
    
    all_results = {}
    
    for phase in phases_to_run:
        print(f"\n{'='*50}")
        print(f"PHASE {phase}")
        print(f"{'='*50}")
        
        estimate = downloader.estimate_resources(phase)
        print(f"📈 Expected: {estimate['total_size_gb']} GB, {estimate['total_galaxies']:,} galaxies")
        
        results = await downloader.download_phase(phase)
        all_results[f"phase_{phase}"] = results
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        print(f"\n📊 Phase {phase} Results: {success_count}/{total_count} successful")
        
        for survey, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {survey}")
    
    # Generate final registry
    downloader.generate_data_registry()
    
    print(f"\n🎯 ACQUISITION COMPLETE")
    print(f"✅ Data ready for 3-4:2 framework testing")
    print(f"📁 Location: {args.data_dir}")
    print(f"📋 Registry: {args.data_dir}/data_registry.yaml")
    
    return all_results


if __name__ == "__main__":
    try:
        results = asyncio.run(main())
        print("\n🚀 Ready for automated agent testing!")
    except KeyboardInterrupt:
        print("\n⚠️ Download interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1) 