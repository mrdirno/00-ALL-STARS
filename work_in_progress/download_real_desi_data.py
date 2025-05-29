#!/usr/bin/env python3
"""
Download Real DESI DR1 Spectroscopic Data
=========================================

Downloads actual DESI spectroscopic galaxy catalogs for testing
the 3-4:2 Modal Framework on real data (not mock data).
"""

import urllib.request
import os
import sys

def download_desi_sample():
    """Download a sample of real DESI DR1 data"""
    
    print("🌌 DOWNLOADING REAL DESI DR1 SPECTROSCOPIC DATA")
    print("=" * 50)
    
    # Create data directory
    data_dir = os.path.expanduser("~/telescope_data")
    os.makedirs(data_dir, exist_ok=True)
    
    # DESI DR1 catalog URLs (real data)
    urls = [
        {
            'name': 'ELG_NGC_clustering',
            'url': 'https://data.desi.lbl.gov/public/dr1/survey/catalogs/dr1/LSS/iron/LSScats/v1.5/ELG_LOPnotqso_NGC_clustering.dat.fits',
            'filename': 'desi_elg_ngc_real.fits',
            'description': 'DESI ELG galaxies (North Galactic Cap) - ~200MB',
            'size_mb': 196
        },
        {
            'name': 'BGS_clustering_sample', 
            'url': 'https://data.desi.lbl.gov/public/dr1/survey/catalogs/dr1/LSS/iron/LSScats/v1.5/BGS_BRIGHT_NGC_clustering.dat.fits',
            'filename': 'desi_bgs_ngc_real.fits',
            'description': 'DESI Bright Galaxy Survey (North) - ~325MB',
            'size_mb': 325
        }
    ]
    
    print("Available real DESI catalogs:")
    for i, catalog in enumerate(urls):
        print(f"  {i+1}. {catalog['description']}")
    
    # Download the smaller ELG catalog first
    catalog = urls[0]  # ELG catalog
    
    output_path = os.path.join(data_dir, catalog['filename'])
    
    if os.path.exists(output_path):
        print(f"✅ File already exists: {output_path}")
        return output_path
    
    print(f"\n📥 Downloading {catalog['name']}...")
    print(f"   URL: {catalog['url']}")
    print(f"   Output: {output_path}")
    print(f"   Size: ~{catalog['size_mb']} MB")
    
    try:
        def progress_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, downloaded * 100 / total_size)
                mb_downloaded = downloaded / 1024 / 1024
                mb_total = total_size / 1024 / 1024
                print(f"\r   Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='')
            
        urllib.request.urlretrieve(catalog['url'], output_path, progress_hook)
        print(f"\n✅ Download completed: {output_path}")
        
        # Verify file
        size_mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"   File size: {size_mb:.1f} MB")
        
        return output_path
        
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return None

def main():
    """Download real DESI data"""
    
    print("This will download actual DESI DR1 spectroscopic galaxy data.")
    print("This is REAL observational data, not mock data with injected signals.")
    print()
    
    choice = input("Download DESI ELG catalog (~196 MB)? [y/N]: ").strip().lower()
    
    if choice in ['y', 'yes']:
        file_path = download_desi_sample()
        if file_path:
            print(f"\n🎯 Ready to test 3-4:2 Modal Framework on real data:")
            print(f"   python3 real_desi_data_analyzer.py")
    else:
        print("Download cancelled.")

if __name__ == "__main__":
    main() 