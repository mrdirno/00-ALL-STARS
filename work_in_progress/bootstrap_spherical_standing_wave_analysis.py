#!/usr/bin/env python3
"""
Bootstrap Spherical Standing Wave Analysis
Estimate confidence intervals on standing-wave peak counts and positions via resampling.
"""

import numpy as np
from astropy.io import fits
from astropy.table import Table
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import os

# Headless plotting
import matplotlib
matplotlib.use('Agg')

# --- Functions from spherical_standing_wave_analysis.py ---

def load_distances():
    filepath = os.path.expanduser('~/telescope_data/desi_elg_clustering_sample.fits')
    with fits.open(filepath) as hdul:
        data = Table.read(hdul[1])
    mask = (data['Z'] > 0.01) & (data['Z'] < 3.0)
    r = (299792.458/67.4) * np.array(data['Z'][mask])
    return r

def spherical_bessel_transform(r, k_values):
    A = []
    for k in k_values:
        kr = k * r
        j0 = np.sinc(kr/np.pi)
        A.append(np.mean(j0))
    return np.array(A)

# --- Bootstrap analysis ---

def bootstrap_peaks(r, k_vals, threshold_sigma, n_boot=200):
    stdA = None
    peak_counts = []
    all_peaks = []
    N = len(r)
    for i in range(n_boot):
        # Resample distances
        r_sample = np.random.choice(r, size=N, replace=True)
        A_sample = spherical_bessel_transform(r_sample, k_vals)
        stdA = stdA or np.std(A_sample)
        h = threshold_sigma * stdA
        peaks, _ = find_peaks(A_sample, height=h)
        peak_counts.append(len(peaks))
        all_peaks.append(k_vals[peaks])
    peak_counts = np.array(peak_counts)
    return peak_counts, all_peaks

# --- Main ---

def main():
    print('=== Bootstrap Standing-Wave Analysis ===')
    r = load_distances()
    print(f'Loaded {len(r):,} radial distances')
    k_vals = np.linspace(0.001, 0.05, 500)
    # Compute transform once to get std and best threshold
    A = spherical_bessel_transform(r, k_vals)
    stdA = np.std(A)
    target_ratio = 0.682
    # find best sigma multiplier as in spherical_standing_wave_analysis
    best_m = None
    best_diff = np.inf
    for m in np.linspace(0.5, 5.0, 46):
        h = stdA * m
        p, _ = find_peaks(A, height=h)
        t, _ = find_peaks(-A, height=h)
        if len(t)==0: continue
        ratio = len(p)/len(t)
        diff = abs(ratio-target_ratio)
        if diff < best_diff:
            best_diff, best_m = diff, m
    print(f'Using threshold: {best_m:.2f}σ')
    
    # Bootstrap peak counts
    peak_counts, all_peaks = bootstrap_peaks(r, k_vals, best_m, n_boot=200)
    lower, upper = np.percentile(peak_counts, [2.5, 97.5])
    mean_count = np.mean(peak_counts)
    print(f'Peak count distribution: mean={mean_count:.1f}, 95% CI=({lower:.1f}, {upper:.1f})')

    # Plot histogram of counts
    plt.figure(figsize=(6,4))
    plt.hist(peak_counts, bins=20, color='purple', alpha=0.7)
    plt.axvline(mean_count, color='black', linestyle='--', label='Mean')
    plt.axvline(lower, color='red', linestyle=':', label='2.5% CI')
    plt.axvline(upper, color='red', linestyle=':', label='97.5% CI')
    plt.xlabel('Number of Peaks')
    plt.ylabel('Frequency')
    plt.title('Bootstrap Distribution of Standing-Wave Peaks')
    plt.legend()
    plt.tight_layout()
    plt.savefig('bootstrap_peak_counts.png', dpi=150)
    print('Saved plot: bootstrap_peak_counts.png')

if __name__ == '__main__':
    main() 