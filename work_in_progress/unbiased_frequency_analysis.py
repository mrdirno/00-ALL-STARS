#!/usr/bin/env python3
"""
Unbiased Frequency Analysis - Real DESI Data
============================================

Independent frequency detection without assuming 1:2:3 ratios.
This tests if natural peaks occur at those specific relationships.
"""

import numpy as np
from astropy.io import fits
from astropy.table import Table
import matplotlib.pyplot as plt
from scipy import signal
import os

def load_desi_data():
    """Load real DESI data"""
    
    file_path = os.path.expanduser("~/telescope_data/desi_elg_clustering_sample.fits")
    
    if not os.path.exists(file_path):
        print(f"No DESI data found at {file_path}")
        return None
    
    with fits.open(file_path) as hdul:
        data = Table.read(hdul[1])
    
    # Extract coordinates and redshifts
    ra = np.array(data['RA'])
    dec = np.array(data['DEC'])
    redshift = np.array(data['Z'])
    
    # Filter valid data
    valid = (redshift > 0) & (redshift < 5) & np.isfinite(redshift)
    ra = ra[valid]
    dec = dec[valid]
    redshift = redshift[valid]
    
    # Convert to comoving distances
    c = 299792.458  
    H0 = 67.4       
    distances = (c/H0) * redshift
    
    # Convert to Cartesian
    ra_rad = np.radians(ra)
    dec_rad = np.radians(dec)
    
    x = distances * np.cos(dec_rad) * np.cos(ra_rad)
    y = distances * np.cos(dec_rad) * np.sin(ra_rad)
    z = distances * np.sin(dec_rad)
    
    print(f"Loaded {len(x):,} real DESI galaxies")
    print(f"Redshift range: {redshift.min():.3f} - {redshift.max():.3f}")
    
    return {'x': x, 'y': y, 'z': z, 'redshift': redshift}

def compute_power_spectrum(coords, k_range):
    """Compute 3D power spectrum without assuming specific ratios"""
    
    x, y, z = coords['x'], coords['y'], coords['z']
    n_galaxies = len(x)
    
    power_spectrum = []
    
    for k in k_range:
        # Fourier modes at this wavenumber
        modes_x = np.cos(k * x) + 1j * np.sin(k * x)
        modes_y = np.cos(k * y) + 1j * np.sin(k * y)
        modes_z = np.cos(k * z) + 1j * np.sin(k * z)
        
        # Combined 3D mode
        mode_3d = modes_x * modes_y * modes_z
        
        # Power (amplitude squared)
        power = np.abs(np.mean(mode_3d))**2
        power_spectrum.append(power)
    
    return np.array(power_spectrum)

def find_independent_peaks(k_range, power_spectrum, min_prominence=None):
    """Find peaks in power spectrum independently"""
    
    # Find peaks
    peaks, properties = signal.find_peaks(power_spectrum, prominence=min_prominence)
    
    peak_frequencies = k_range[peaks]
    peak_powers = power_spectrum[peaks]
    
    # Sort by power (strongest first)
    sort_indices = np.argsort(peak_powers)[::-1]
    peak_frequencies = peak_frequencies[sort_indices]
    peak_powers = peak_powers[sort_indices]
    
    return peak_frequencies, peak_powers

def test_harmonic_relationships(frequencies, tolerance=0.05):
    """Test if detected frequencies show harmonic relationships"""
    
    if len(frequencies) < 3:
        return None
    
    results = []
    
    # Test all combinations for 1:2:3 relationships
    for i in range(len(frequencies)):
        for j in range(i+1, len(frequencies)):
            for k in range(j+1, len(frequencies)):
                f1, f2, f3 = frequencies[i], frequencies[j], frequencies[k]
                
                # Sort them
                freqs = np.sort([f1, f2, f3])
                f_low, f_mid, f_high = freqs
                
                # Check for 1:2:3 ratios
                ratio_2_1 = f_mid / f_low
                ratio_3_1 = f_high / f_low
                ratio_3_2 = f_high / f_mid
                
                # Check deviations from 1:2:3
                dev_2_1 = abs(ratio_2_1 - 2.0) / 2.0
                dev_3_1 = abs(ratio_3_1 - 3.0) / 3.0
                dev_3_2 = abs(ratio_3_2 - 1.5) / 1.5
                
                avg_deviation = (dev_2_1 + dev_3_1 + dev_3_2) / 3
                
                if avg_deviation < tolerance:
                    results.append({
                        'frequencies': [f_low, f_mid, f_high],
                        'ratios': [ratio_2_1, ratio_3_1, ratio_3_2],
                        'deviation': avg_deviation
                    })
    
    return results

def analyze_real_desi():
    """Main analysis of real DESI data"""
    
    print("UNBIASED FREQUENCY ANALYSIS OF REAL DESI DATA")
    print("=" * 50)
    
    # Load data
    coords = load_desi_data()
    if coords is None:
        return
    
    # Define frequency range
    k_range = np.logspace(-3, -1, 200)  # h/Mpc
    
    print(f"Computing power spectrum over {len(k_range)} frequencies...")
    
    # Compute power spectrum
    power = compute_power_spectrum(coords, k_range)
    
    # Find peaks independently
    peak_freqs, peak_powers = find_independent_peaks(k_range, power)
    
    print(f"Found {len(peak_freqs)} independent peaks")
    
    if len(peak_freqs) > 0:
        print("Top 10 peaks:")
        for i in range(min(10, len(peak_freqs))):
            print(f"  {i+1}. k = {peak_freqs[i]:.6f} h/Mpc, power = {peak_powers[i]:.2e}")
    
    # Test for harmonic relationships
    harmonic_matches = test_harmonic_relationships(peak_freqs)
    
    print(f"\nHarmonic relationship analysis:")
    
    if harmonic_matches is None or len(harmonic_matches) == 0:
        print("NO 1:2:3 harmonic relationships found")
        print("3-4:2 Modal Framework NOT supported by independent analysis")
        return "NO_DETECTION"
    
    else:
        print(f"Found {len(harmonic_matches)} potential 1:2:3 relationships:")
        
        for i, match in enumerate(harmonic_matches):
            freqs = match['frequencies']
            ratios = match['ratios']
            dev = match['deviation']
            
            print(f"\nCandidate {i+1}:")
            print(f"  k₁ = {freqs[0]:.6f} h/Mpc")
            print(f"  k₂ = {freqs[1]:.6f} h/Mpc") 
            print(f"  k₃ = {freqs[2]:.6f} h/Mpc")
            print(f"  k₂/k₁ = {ratios[0]:.3f} (target: 2.0)")
            print(f"  k₃/k₁ = {ratios[1]:.3f} (target: 3.0)")
            print(f"  k₃/k₂ = {ratios[2]:.3f} (target: 1.5)")
            print(f"  Deviation: {dev*100:.1f}%")
        
        best_match = min(harmonic_matches, key=lambda x: x['deviation'])
        print(f"\nBest match deviation: {best_match['deviation']*100:.1f}%")
        
        if best_match['deviation'] < 0.05:  # 5% tolerance
            return "DETECTED"
        else:
            return "WEAK_EVIDENCE"
    
    # Plot results
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.loglog(k_range, power)
    plt.scatter(peak_freqs[:10], peak_powers[:10], color='red', s=50, zorder=5)
    plt.xlabel('Wavenumber k (h/Mpc)')
    plt.ylabel('Power')
    plt.title('Power Spectrum - Real DESI Data')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    if len(harmonic_matches) > 0:
        best = best_match
        freqs = best['frequencies']
        plt.axvline(freqs[0], color='blue', alpha=0.7, label=f'k₁ = {freqs[0]:.4f}')
        plt.axvline(freqs[1], color='red', alpha=0.7, label=f'k₂ = {freqs[1]:.4f}')
        plt.axvline(freqs[2], color='green', alpha=0.7, label=f'k₃ = {freqs[2]:.4f}')
        plt.loglog(k_range, power, alpha=0.5)
        plt.xlabel('Wavenumber k (h/Mpc)')
        plt.ylabel('Power')
        plt.title('Harmonic Relationship Candidates')
        plt.legend()
        plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('desi_frequency_analysis.png', dpi=150, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    result = analyze_real_desi()
    
    print(f"\nFINAL RESULT: {result}")
    
    if result == "DETECTED":
        print("Strong evidence for 3-4:2 Modal Framework")
    elif result == "WEAK_EVIDENCE":
        print("Weak evidence - requires further investigation")
    else:
        print("No evidence for 3-4:2 Modal Framework") 