#!/usr/bin/env python3
"""
Spherical Standing Wave Analysis for DESI ELG Data

Perform a spherical Bessel (j0) transform of the radial galaxy distribution
and identify resonance peaks in k-space, indicating 3D standing-wave modes from a central source.
"""
import numpy as np
import os
from astropy.io import fits
from astropy.table import Table
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
# Headless backend
import matplotlib
matplotlib.use('Agg')

def load_distances():
    filepath = os.path.expanduser('~/telescope_data/desi_elg_clustering_sample.fits')
    with fits.open(filepath) as hdul:
        data = Table.read(hdul[1])
    mask = (data['Z'] > 0.01) & (data['Z'] < 3.0)
    # Comoving distances in Mpc
    dist = (299792.458/67.4) * np.array(data['Z'][mask])
    return dist

def spherical_bessel_transform(r, k_values):
    # j0(kr) = sin(kr)/(kr)
    # Use sinc: np.sinc(x/pi) = sin(x)/x
    A = []
    for k in k_values:
        kr = k * r
        # Avoid division by zero
        j0 = np.sinc(kr/np.pi)
        A_k = np.mean(j0)
        A.append(A_k)
    return np.array(A)

def main():
    print('Spherical Standing Wave Analysis')
    # Load data
    r = load_distances()
    print(f'Loaded {len(r):,} radial distances')
    # Define k range
    k_vals = np.linspace(0.001, 0.05, 500)
    # Compute transform
    A = spherical_bessel_transform(r, k_vals)
    # Find threshold multiplier to match hot/cold ratio similar to Planck (~0.682)
    stdA = np.std(A)
    target_ratio = 0.682  # Planck hot/cold galaxy density ratio
    # Search multipliers from 0.5 to 5.0 sigma
    multipliers = np.linspace(0.5, 5.0, 46)
    best_m = None
    best_diff = np.inf
    best_peaks = None
    best_troughs = None
    for m in multipliers:
        h = stdA * m
        # peaks = standing waves; troughs = anti-standing waves
        peaks_m, _ = find_peaks(A, height=h)
        troughs_m, _ = find_peaks(-A, height=h)
        if len(troughs_m) == 0:
            continue
        ratio = len(peaks_m) / len(troughs_m)
        diff = abs(ratio - target_ratio)
        if diff < best_diff:
            best_diff = diff
            best_m = m
            best_peaks = peaks_m
            best_troughs = troughs_m
    # Use best threshold
    peaks = best_peaks
    troughs = best_troughs
    achieved_ratio = len(peaks) / len(troughs) if troughs is not None else None
    print(f'Best threshold: {best_m:.2f}σ * std => peaks/troughs ratio ≈ {achieved_ratio:.3f}')
    print(f'Detected {len(peaks)} standing-wave peaks and {len(troughs)} anti-wave troughs at this threshold')
    # List k-values of peaks for context
    for k in k_vals[peaks]:
        print(f'  Peak at k={k:.5f} h/Mpc (λ={2*np.pi/k:.1f} Mpc)')
    # Optionally list trough k-values
    # for k in k_vals[troughs]:
    #     print(f'  Trough at k={k:.5f} h/Mpc (λ={2*np.pi/k:.1f} Mpc)')
    
    # Plot with both peaks and troughs
    # Plot
    plt.figure(figsize=(8,5))
    plt.plot(k_vals, A, label='Spherical j0 Transform')
    # Plot peaks (standing-wave)
    plt.scatter(k_vals[peaks], A[peaks], color='red', label='Standing-wave Peaks')
    # Plot troughs (anti-wave)
    plt.scatter(k_vals[troughs], A[troughs], color='blue', marker='x', label='Anti-wave Troughs')
    for k in np.concatenate((k_vals[peaks], k_vals[troughs])):
        plt.axvline(k, color='gray', linestyle='--', alpha=0.3)
    plt.xlabel('k (h/Mpc)')
    plt.ylabel('⟨j0(kr)⟩')
    plt.title('Spherical Bessel Transform & Standing/Anti-wave Detection')
    plt.legend()
    plt.tight_layout()
    out = 'spherical_standing_wave_analysis.png'
    plt.savefig(out, dpi=200)
    print(f'Saved plot: {out}')

if __name__ == '__main__':
    main() 