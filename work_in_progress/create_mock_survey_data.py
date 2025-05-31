#!/usr/bin/env python3
"""
Mock Survey Data Generator for 3-4:2 Framework Testing
Creates realistic galaxy survey datasets for immediate testing

Date: 2025-01-29
Purpose: Generate mock data while fixing real survey data access
Status: Ready for immediate testing
"""

import numpy as np
import pandas as pd
from pathlib import Path
import yaml
from datetime import datetime
import argparse

class MockSurveyGenerator:
    """Generate realistic mock survey data"""
    
    def __init__(self, data_dir: str = "external_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Cosmological parameters for realistic mock data
        self.h = 0.7  # Hubble parameter
        self.omega_m = 0.3  # Matter density
        self.omega_l = 0.7  # Dark energy density
        
    def generate_galaxy_sample(self, n_galaxies: int, survey_name: str, 
                             z_min: float = 0.01, z_max: float = 0.5,
                             inject_modal_signal: bool = True) -> pd.DataFrame:
        """Generate realistic galaxy sample with optional 3-4:2 signal injection"""
        
        np.random.seed(42)  # Reproducible results
        
        # Generate redshift distribution (realistic)
        redshifts = self.generate_realistic_redshift_distribution(n_galaxies, z_min, z_max)
        
        # Generate sky positions
        ra = np.random.uniform(0, 360, n_galaxies)  # Right ascension (degrees)
        dec = np.arcsin(2 * np.random.random(n_galaxies) - 1) * 180 / np.pi  # Realistic declination
        
        # Convert to comoving coordinates
        x_mpc, y_mpc, z_mpc = self.redshift_to_comoving(ra, dec, redshifts)
        
        # Generate realistic magnitudes
        mag_r = self.generate_realistic_magnitudes(redshifts, n_galaxies)
        
        # Generate additional properties
        data = {
            'objid': np.arange(1000000, 1000000 + n_galaxies),
            'ra': ra,
            'dec': dec,
            'z': redshifts,
            'x_mpc': x_mpc,
            'y_mpc': y_mpc,
            'z_mpc': z_mpc,
            'petroMag_r': mag_r,
            'petroMag_g': mag_r - 0.5 + np.random.normal(0, 0.1, n_galaxies),
            'petroMag_i': mag_r + 0.3 + np.random.normal(0, 0.1, n_galaxies),
            'petroR50_r': np.random.lognormal(0.5, 0.3, n_galaxies),
            'survey': [survey_name] * n_galaxies
        }
        
        df = pd.DataFrame(data)
        
        # Inject 3-4:2 modal signal if requested
        if inject_modal_signal:
            df = self.inject_342_modal_signal(df)
        
        return df
    
    def generate_realistic_redshift_distribution(self, n_galaxies: int, 
                                               z_min: float, z_max: float) -> np.ndarray:
        """Generate realistic redshift distribution matching survey observations"""
        
        # Model selection function (realistic survey sensitivity)
        z_vals = np.linspace(z_min, z_max, 1000)
        
        # Realistic galaxy luminosity function evolution
        selection_function = np.exp(-((z_vals - 0.1)**2) / (2 * 0.15**2))  # Peak at z~0.1
        selection_function *= (1 + z_vals)**2  # Comoving volume element
        selection_function /= (1 + z_vals)**3  # Survey depth limits
        
        # Normalize
        selection_function /= np.sum(selection_function)
        
        # Sample from this distribution
        redshifts = np.random.choice(z_vals, size=n_galaxies, p=selection_function)
        
        # Add scatter
        redshifts += np.random.normal(0, 0.001, n_galaxies)  # Redshift measurement errors
        redshifts = np.clip(redshifts, z_min, z_max)
        
        return redshifts
    
    def redshift_to_comoving(self, ra: np.ndarray, dec: np.ndarray, 
                           z: np.ndarray) -> tuple:
        """Convert RA, Dec, redshift to comoving coordinates"""
        
        # Simple comoving distance calculation (flat universe approximation)
        c = 299792.458  # km/s
        H0 = 70  # km/s/Mpc
        
        # Comoving distance
        d_c = c * z / H0  # Mpc (simplified for small z)
        
        # Convert spherical to Cartesian
        ra_rad = np.deg2rad(ra)
        dec_rad = np.deg2rad(dec)
        
        x = d_c * np.cos(dec_rad) * np.cos(ra_rad)
        y = d_c * np.cos(dec_rad) * np.sin(ra_rad)
        z = d_c * np.sin(dec_rad)
        
        return x, y, z
    
    def generate_realistic_magnitudes(self, redshifts: np.ndarray, 
                                    n_galaxies: int) -> np.ndarray:
        """Generate realistic r-band magnitudes"""
        
        # Magnitude-redshift relation (K-correction + evolution)
        M_star = -20.5  # Typical L* galaxy absolute magnitude
        
        # Distance modulus
        d_L = 3000 * redshifts  # Approximate luminosity distance in Mpc
        mu = 5 * np.log10(d_L) + 25  # Distance modulus
        
        # Absolute magnitude distribution (Schechter function)
        M_abs = np.random.normal(M_star, 1.5, n_galaxies)
        
        # Apparent magnitude
        m_app = M_abs + mu
        
        # K-correction (simplified)
        k_corr = 2.5 * redshifts  # Rough K-correction for r-band
        m_app += k_corr
        
        # Add observational scatter
        m_app += np.random.normal(0, 0.1, n_galaxies)
        
        return m_app
    
    def inject_342_modal_signal(self, df: pd.DataFrame, 
                              amplitude: float = 0.03) -> pd.DataFrame:
        """Inject 3-4:2 modal framework signal into galaxy positions"""
        
        print(f"🔬 Injecting 3-4:2 modal signal (amplitude: {amplitude})")
        
        # Framework parameters
        r_s = 150  # Sound horizon scale (Mpc)
        k_fundamental = 2 * np.pi / r_s
        
        # Calculate radial distance for each galaxy
        r = np.sqrt(df['x_mpc']**2 + df['y_mpc']**2 + df['z_mpc']**2)
        
        # Generate 3-4:2 modal modulation
        k1 = k_fundamental
        k2 = 2 * k1  # Second harmonic
        k3 = 3 * k1  # Third harmonic
        
        # Harmonic modulation (key prediction of framework)
        modulation = (amplitude * np.sin(k1 * r) + 
                     0.5 * amplitude * np.sin(k2 * r) + 
                     0.33 * amplitude * np.sin(k3 * r))
        
        # Apply modulation to galaxy density (shifts positions slightly)
        modulation_factor = 1 + modulation
        
        df['x_mpc'] *= modulation_factor
        df['y_mpc'] *= modulation_factor
        df['z_mpc'] *= modulation_factor
        
        # Mark as signal-injected
        df['modal_signal_injected'] = True
        df['modal_amplitude'] = amplitude
        
        return df
    
    def generate_cluster_catalog(self, n_clusters: int = 500) -> pd.DataFrame:
        """Generate realistic galaxy cluster catalog"""
        
        np.random.seed(42)
        
        # Cluster redshift distribution
        z_clusters = np.random.exponential(0.3, n_clusters)
        z_clusters = np.clip(z_clusters, 0.05, 2.0)
        
        # Sky positions
        ra = np.random.uniform(0, 360, n_clusters)
        dec = np.arcsin(2 * np.random.random(n_clusters) - 1) * 180 / np.pi
        
        # Cluster masses (log-normal distribution)
        log_mass = np.random.normal(14.5, 0.5, n_clusters)  # log10(M_500 / M_sun)
        mass_500 = 10**log_mass
        
        # Convert to comoving coordinates
        x_mpc, y_mpc, z_mpc = self.redshift_to_comoving(ra, dec, z_clusters)
        
        data = {
            'cluster_id': np.arange(1, n_clusters + 1),
            'ra': ra,
            'dec': dec,
            'z': z_clusters,
            'x_mpc': x_mpc,
            'y_mpc': y_mpc,
            'z_mpc': z_mpc,
            'mass_500': mass_500,
            'log_mass': log_mass
        }
        
        return pd.DataFrame(data)
    
    def save_datasets(self, inject_signal: bool = True) -> dict:
        """Generate and save all mock datasets"""
        
        print("🔬 GENERATING MOCK SURVEY DATA FOR 3-4:2 TESTING")
        print(f"Data directory: {self.data_dir}")
        print(f"Modal signal injection: {'✅ ENABLED' if inject_signal else '❌ DISABLED'}")
        
        datasets = {}
        
        # Generate galaxy surveys
        surveys = [
            {"name": "mock_sdss_sample", "n_galaxies": 200000, "z_min": 0.01, "z_max": 0.8},
            {"name": "mock_2dfgrs_sample", "n_galaxies": 100000, "z_min": 0.01, "z_max": 0.3},
            {"name": "mock_6dfgs_sample", "n_galaxies": 50000, "z_min": 0.01, "z_max": 0.15},
            {"name": "mock_des_sample", "n_galaxies": 150000, "z_min": 0.2, "z_max": 1.2}
        ]
        
        for survey in surveys:
            print(f"\n📊 Generating {survey['name']}: {survey['n_galaxies']:,} galaxies")
            
            df = self.generate_galaxy_sample(
                survey['n_galaxies'], 
                survey['name'],
                survey['z_min'],
                survey['z_max'],
                inject_modal_signal=inject_signal
            )
            
            # Save as CSV
            filename = f"{survey['name']}.csv"
            filepath = self.data_dir / filename
            df.to_csv(filepath, index=False)
            
            file_size = filepath.stat().st_size / (1024*1024)  # MB
            print(f"✅ Saved {filename} ({file_size:.1f} MB)")
            
            datasets[survey['name']] = {
                "file": str(filepath),
                "size_mb": round(file_size, 1),
                "galaxies": len(df),
                "redshift_range": [survey['z_min'], survey['z_max']],
                "modal_signal": inject_signal
            }
        
        # Generate cluster catalog
        print(f"\n🔗 Generating mock cluster catalog")
        clusters_df = self.generate_cluster_catalog(500)
        cluster_file = self.data_dir / "mock_clusters.csv"
        clusters_df.to_csv(cluster_file, index=False)
        
        cluster_size = cluster_file.stat().st_size / (1024*1024)
        print(f"✅ Saved mock_clusters.csv ({cluster_size:.1f} MB)")
        
        datasets["mock_clusters"] = {
            "file": str(cluster_file),
            "size_mb": round(cluster_size, 1),
            "clusters": len(clusters_df),
            "type": "cluster_catalog"
        }
        
        # Generate data registry
        registry = {
            "timestamp": datetime.now().isoformat(),
            "data_type": "mock_survey_data",
            "modal_signal_injected": inject_signal,
            "framework_version": "3-4:2 Modal Framework v2.0",
            "purpose": "Testing modal framework predictions",
            "datasets": datasets
        }
        
        registry_path = self.data_dir / "data_registry.yaml"
        with open(registry_path, 'w') as f:
            yaml.dump(registry, f, default_flow_style=False)
        
        print(f"\n✅ Registry saved: {registry_path}")
        print(f"📊 Total datasets: {len(datasets)}")
        
        total_galaxies = sum(d.get('galaxies', 0) for d in datasets.values())
        total_size = sum(d.get('size_mb', 0) for d in datasets.values())
        
        print(f"🌌 Total galaxies: {total_galaxies:,}")
        print(f"💾 Total size: {total_size:.1f} MB")
        
        return datasets


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Generate mock survey data for 3-4:2 framework testing"
    )
    parser.add_argument("--no-signal", action="store_true",
                       help="Generate control data without modal signal")
    parser.add_argument("--data-dir", default="external_data",
                       help="Data directory")
    
    args = parser.parse_args()
    
    generator = MockSurveyGenerator(args.data_dir)
    
    # Generate datasets
    inject_signal = not args.no_signal
    datasets = generator.save_datasets(inject_signal=inject_signal)
    
    print(f"\n🎯 MOCK DATA GENERATION COMPLETE")
    print(f"✅ Ready for 3-4:2 framework testing")
    print(f"📁 Location: {args.data_dir}")
    
    if inject_signal:
        print(f"🔬 Modal signal injected - framework should detect harmonic ratios")
        print(f"🎯 Expected detection: 1:2:3 wavenumber ratios")
    else:
        print(f"🚫 Control data - no modal signal (should not detect ratios)")
    
    return datasets


if __name__ == "__main__":
    datasets = main() 