#!/usr/bin/env python3

import numpy as np
from astropy.io import fits
from astropy.table import Table
from scipy import signal
import os
import matplotlib.pyplot as plt

def load_complete_desi_data():
    """Load the complete DESI DR1 redshift catalog with all galaxy types"""
    file_path = os.path.expanduser("~/telescope_data/desi_dr1_zpix_main.fits")
    
    with fits.open(file_path) as hdul:
        data = Table.read(hdul[1])
    
    # Filter for galaxies with good redshifts
    galaxy_mask = (data['SPECTYPE'] == 'GALAXY') & (data['ZWARN'] == 0) & (data['Z'] > 0) & (data['Z'] < 3)
    
    ra = np.array(data['RA'][galaxy_mask])
    dec = np.array(data['DEC'][galaxy_mask])
    redshift = np.array(data['Z'][galaxy_mask])
    
    # Convert to comoving coordinates (h=0.674, Ωm=0.315)
    c, H0 = 299792.458, 67.4
    distances = (c/H0) * redshift  # Simple Hubble law approximation
    
    ra_rad, dec_rad = np.radians(ra), np.radians(dec)
    x = distances * np.cos(dec_rad) * np.cos(ra_rad)
    y = distances * np.cos(dec_rad) * np.sin(ra_rad)
    z = distances * np.sin(dec_rad)
    
    print(f"Loaded {len(x):,} galaxies from complete DESI DR1 catalog")
    print(f"Redshift range: {redshift.min():.3f} to {redshift.max():.3f}")
    print(f"Distance range: {distances.min():.0f} to {distances.max():.0f} Mpc")
    
    return {'x': x, 'y': y, 'z': z, 'redshift': redshift, 'distances': distances}

def test_342_framework_comprehensive(coords):
    """Test 3-4:2 modal framework across multiple scales"""
    x, y, z = coords['x'], coords['y'], coords['z']
    
    print("\nTESTING 3-4:2 MODAL FRAMEWORK - COMPLETE DESI DR1")
    print("="*55)
    print(f"Dataset: {len(x):,} galaxies")
    
    # Test multiple scale ranges
    scale_tests = [
        {"name": "Large Scale Structure", "k_range": (0.001, 0.1), "n_k": 20},
        {"name": "Supercluster Scale", "k_range": (0.01, 0.2), "n_k": 15}, 
        {"name": "Observable Universe Scale", "k_range": (0.0001, 0.001), "n_k": 10}
    ]
    
    results = {}
    
    for test in scale_tests:
        print(f"\n{test['name']} Test:")
        print("-" * len(test['name']) + " Test:")
        
        k_values = np.logspace(np.log10(test['k_range'][0]), 
                              np.log10(test['k_range'][1]), 
                              test['n_k'])
        
        harmonic_detections = []
        best_ratio_deviations = []
        
        for k1 in k_values:
            # Test 1:2:3 harmonic series
            k2, k3 = 2*k1, 3*k1
            
            # Compute Fourier modes
            mode1 = np.exp(1j * (k1*x + k1*y + k1*z))
            mode2 = np.exp(1j * (k2*x + k2*y + k2*z))
            mode3 = np.exp(1j * (k3*x + k3*y + k3*z))
            
            power1 = np.abs(np.mean(mode1))**2
            power2 = np.abs(np.mean(mode2))**2
            power3 = np.abs(np.mean(mode3))**2
            
            # Check for 3:4:2 ratio in powers
            total_power = power1 + power2 + power3
            if total_power > 0:
                p1_frac = power1 / total_power
                p2_frac = power2 / total_power
                p3_frac = power3 / total_power
                
                # Expected 3:4:2 ratios normalized
                expected = np.array([3, 4, 2]) / 9
                observed = np.array([p1_frac, p2_frac, p3_frac])
                
                deviation = np.sqrt(np.mean((observed - expected)**2))
                
                # Consider it a detection if deviation < 0.1
                if deviation < 0.1:
                    harmonic_detections.append({
                        'k1': k1,
                        'wavelength_Mpc': 2*np.pi/k1,
                        'deviation': deviation,
                        'powers': (power1, power2, power3)
                    })
                
                best_ratio_deviations.append(deviation)
        
        results[test['name']] = {
            'detections': len(harmonic_detections),
            'total_tested': len(k_values),
            'best_detections': harmonic_detections[:5] if harmonic_detections else [],
            'min_deviation': min(best_ratio_deviations) if best_ratio_deviations else np.inf
        }
        
        print(f"  Scale range: {2*np.pi/test['k_range'][1]:.0f} - {2*np.pi/test['k_range'][0]:.0f} Mpc")
        print(f"  Harmonic detections: {len(harmonic_detections)}/{len(k_values)}")
        print(f"  Best deviation: {min(best_ratio_deviations):.4f}" if best_ratio_deviations else "  No valid measurements")
        
        if harmonic_detections:
            best = min(harmonic_detections, key=lambda x: x['deviation'])
            print(f"  Best match: λ = {best['wavelength_Mpc']:.0f} Mpc, deviation = {best['deviation']:.4f}")
    
    return results

def control_test_random(n_galaxies):
    """Test the same analysis on random data as a control"""
    print(f"\nCONTROL TEST: Random data with {n_galaxies:,} points")
    print("=" * 50)
    
    # Generate random coordinates matching DESI survey volume
    redshifts = np.random.uniform(0.1, 2.0, n_galaxies)
    ra = np.random.uniform(0, 360, n_galaxies)
    dec = np.random.uniform(-30, 70, n_galaxies)
    
    c, H0 = 299792.458, 67.4
    distances = (c/H0) * redshifts
    ra_rad, dec_rad = np.radians(ra), np.radians(dec)
    x = distances * np.cos(dec_rad) * np.cos(ra_rad)
    y = distances * np.cos(dec_rad) * np.sin(ra_rad)
    z = distances * np.sin(dec_rad)
    
    coords = {'x': x, 'y': y, 'z': z, 'redshift': redshifts, 'distances': distances}
    
    return test_342_framework_comprehensive(coords)

def cosmic_scale_specific_test(coords):
    """Specific test at cosmic scales (1-20 Gpc)"""
    x, y, z = coords['x'], coords['y'], coords['z']
    
    print(f"\nCOSMIC SCALE SPECIFIC TEST")
    print("=" * 30)
    
    # Test specific cosmic scales
    cosmic_scales = [1, 2, 5, 10, 14, 20]  # Gpc
    
    for scale_gpc in cosmic_scales:
        scale_mpc = scale_gpc * 1000
        k = 2 * np.pi / scale_mpc
        
        k1, k2, k3 = k, 2*k, 3*k
        
        # Compute 3D Fourier modes
        mode1 = np.exp(1j * (k1*x + k1*y + k1*z))
        mode2 = np.exp(1j * (k2*x + k2*y + k2*z))
        mode3 = np.exp(1j * (k3*x + k3*y + k3*z))
        
        power1 = np.abs(np.mean(mode1))**2
        power2 = np.abs(np.mean(mode2))**2
        power3 = np.abs(np.mean(mode3))**2
        
        total_power = power1 + power2 + power3
        
        print(f"Scale {scale_gpc} Gpc: Total power = {total_power:.2e}")

if __name__ == "__main__":
    # Load complete DESI data
    print("Loading complete DESI DR1 dataset...")
    coords = load_complete_desi_data()
    
    # Test 3-4:2 framework
    desi_results = test_342_framework_comprehensive(coords)
    
    # Control test with same number of galaxies
    n_desi = len(coords['x'])
    print(f"\nRunning control test with {n_desi:,} random galaxies...")
    random_results = control_test_random(n_desi)
    
    # Cosmic scale test
    cosmic_scale_specific_test(coords)
    
    # Summary comparison
    print(f"\nSUMMARY COMPARISON")
    print("=" * 20)
    
    for test_name in desi_results.keys():
        desi_det = desi_results[test_name]['detections']
        rand_det = random_results[test_name]['detections']
        desi_min_dev = desi_results[test_name]['min_deviation']
        rand_min_dev = random_results[test_name]['min_deviation']
        
        print(f"\n{test_name}:")
        print(f"  DESI detections: {desi_det}")
        print(f"  Random detections: {rand_det}")
        print(f"  DESI best deviation: {desi_min_dev:.4f}")
        print(f"  Random best deviation: {rand_min_dev:.4f}")
        
        if desi_det > rand_det * 1.5:
            print(f"  *** SIGNIFICANT: DESI shows {desi_det/max(rand_det,1):.1f}x more detections")
        elif desi_det < rand_det * 0.5:
            print(f"  *** DEFICIT: DESI shows {desi_det/max(rand_det,1):.1f}x fewer detections")
        else:
            print(f"  No significant difference from random") 