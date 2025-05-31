#!/usr/bin/env python3
"""
Power Spectrum Analysis for DESI ELG Data

Compute the 1D radial density power spectrum from galaxy comoving distances,
identify peaks, and test for harmonic relationships (e.g., k, 2k, 3k) to validate modal patterns.
"""
import numpy as np
import os
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from scipy.signal import find_peaks

# Headless backend
import matplotlib
matplotlib.use('Agg')

# Load comoving distances
def load_distances():
    filepath = os.path.expanduser('~/telescope_data/desi_elg_clustering_sample.fits')
    with fits.open(filepath) as hdul:
        data = Table.read(hdul[1])
    mask = (data['Z'] > 0.01) & (data['Z'] < 3.0)
    dist = (299792.458/67.4) * np.array(data['Z'][mask])
    return dist

def compute_power_spectrum(distances, n_bins=2048):
    # Histogram radial distances
    r_min, r_max = distances.min(), distances.max()
    bins = np.linspace(r_min, r_max, n_bins+1)
    counts, edges = np.histogram(distances, bins=bins)
    dr = edges[1] - edges[0]
    delta = counts / np.mean(counts) - 1.0
    # FFT
    fft_vals = np.fft.rfft(delta)
    power = np.abs(fft_vals)**2
    k = 2 * np.pi * np.fft.rfftfreq(n_bins, d=dr)
    return k[1:], power[1:]  # skip zero mode

def detect_harmonic_peaks(k, power, fundamental=None, tol=0.05):
    # Find peaks
    peaks, _ = find_peaks(power, height=np.mean(power)+np.std(power))
    # Handle case with no peaks: fallback to global maximum
    if len(peaks) == 0:
        idx_global = np.argmax(power)
        fundamental = k[idx_global]
        k_peaks = np.array([fundamental])
    else:
        k_peaks = k[peaks]
        if fundamental is None:
            # Use the highest power among peaks as fundamental
            idx_max = np.argmax(power[peaks])
            fundamental = k_peaks[idx_max]
    # Check for 2k and 3k
    detected = {'fundamental': fundamental}
    for n in [2,3]:
        target = n * fundamental
        # Find nearest peak
        diff = np.abs(k_peaks - target)
        idx = np.argmin(diff)
        rel_err = diff[idx] / target
        detected[f'{n}k'] = (k_peaks[idx], rel_err)
    return k_peaks, detected

def main():
    print('Power Spectrum Analysis for modal harmonics')
    dist = load_distances()
    print(f'Loaded {len(dist):,} distances')
    k, power = compute_power_spectrum(dist, n_bins=2048)
    k_peaks, det = detect_harmonic_peaks(k, power)
    print(f"Fundamental k: {det['fundamental']:.5f} h/Mpc")
    for n in [2,3]:
        kp, err = det[f'{n}k']
        print(f" {n}k peak: {kp:.5f} (rel error {err:.2%})")
    # Plot
    plt.figure(figsize=(8,5))
    plt.loglog(k, power, label='P(k)')
    plt.scatter(k_peaks, power[np.searchsorted(k, k_peaks)], color='red', s=20, label='Peaks')
    for n in [1,2,3]:
        plt.axvline(det['fundamental']*n, color='gray', linestyle='--', alpha=0.7, label=f'{n}k')
    plt.xlabel('k (h/Mpc)')
    plt.ylabel('Power')
    plt.title('1D Radial Power Spectrum & Harmonics')
    plt.legend()
    out = 'power_spectrum_analysis.png'
    plt.savefig(out, dpi=200, bbox_inches='tight')
    print(f'Saved plot: {out}')

if __name__=='__main__':
    main() 