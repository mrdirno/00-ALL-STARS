#!/usr/bin/env python3
"""
Real-space Peak Spacing Analysis for Standing Waves

Compute distances between successive peaks in the radial galaxy density histogram
and compare the average spacing to the expected standing-wave wavelength (λ=2π/k).
"""
import numpy as np
import os
from astropy.io import fits
from astropy.table import Table
import matplotlib.pyplot as plt
import scipy.signal as sig

# Headless plotting
import matplotlib
matplotlib.use('Agg')

# Load comoving distances
def load_distances():
    filepath = os.path.expanduser("~/telescope_data/desi_elg_clustering_sample.fits")
    with fits.open(filepath) as hdul:
        data = Table.read(hdul[1])
    mask = (data['Z'] > 0.01) & (data['Z'] < 3.0)
    dist = (299792.458/67.4) * np.array(data['Z'][mask])
    return dist

# Analyze peak spacing
def analyze_spacing(distances, bin_width=10.0):
    # Histogram counts
    r_min, r_max = distances.min(), distances.max()
    bins = np.arange(r_min, r_max + bin_width, bin_width)
    counts, edges = np.histogram(distances, bins=bins)
    centers = edges[:-1] + bin_width/2
    # Find peaks in counts
    peaks, _ = sig.find_peaks(counts, distance=2)
    peak_pos = centers[peaks]
    # Compute spacings between successive peaks
    spacings = np.diff(peak_pos)
    mean_spacing = np.mean(spacings) if len(spacings)>0 else np.nan
    std_spacing = np.std(spacings) if len(spacings)>0 else np.nan
    # Plot
    plt.figure(figsize=(8,4))
    plt.plot(centers, counts, label='Radial Counts')
    plt.scatter(peak_pos, counts[peaks], color='red', label='Peaks')
    for p in peak_pos:
        plt.axvline(p, color='gray', linestyle='--', alpha=0.5)
    plt.xlabel('Comoving Distance (Mpc)')
    plt.ylabel('Galaxy Count')
    plt.title('Radial Histogram Peak Spacing')
    plt.legend()
    plt.tight_layout()
    out_plot = 'real_space_peak_spacing.png'
    plt.savefig(out_plot, dpi=200)
    plt.close()
    print(f"Saved plot: {out_plot}")
    return peak_pos, spacings, mean_spacing, std_spacing

# Main routine
def main():
    print('Real-Space Peak Spacing Analysis')
    dist = load_distances()
    print(f'Loaded {len(dist):,} distances')
    peaks, spacings, mean_sp, std_sp = analyze_spacing(dist)
    print(f'Detected {len(peaks)} peaks')
    print(f'Mean spacing: {mean_sp:.1f} ± {std_sp:.1f} Mpc')
    # Example: compare to standing-wave λ for k1=0.00788 h/Mpc
    lambda_mpc = 2 * np.pi / 0.00788
    print(f'Expected λ for k1=0.00788: {lambda_mpc:.0f} Mpc')

if __name__ == '__main__':
    main() 