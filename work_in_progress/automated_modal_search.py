#!/usr/bin/env python3
"""
Automated Modal Ratio Search

Tests many 3-element modal ratio patterns (a:b:c) for best 3-4:2-like fit
to the DESI ELG clustering sample, then evaluates repeatability via bootstraps.
"""
import numpy as np
import os
from astropy.io import fits
from astropy.table import Table
import itertools

# Load coordinates once
def load_coords():
    filepath = os.path.expanduser("~/telescope_data/desi_elg_clustering_sample.fits")
    with fits.open(filepath) as hdul:
        data = Table.read(hdul[1])
    mask = (data['Z'] > 0.01) & (data['Z'] < 3.0)
    d = data[mask]
    ra, dec, z = np.array(d['RA']), np.array(d['DEC']), np.array(d['Z'])
    c, H0 = 299792.458, 67.4
    dist = (c/H0) * z
    ra_rad, dec_rad = np.radians(ra), np.radians(dec)
    x = dist * np.cos(dec_rad) * np.cos(ra_rad)
    y = dist * np.cos(dec_rad) * np.sin(ra_rad)
    z3d = dist * np.sin(dec_rad)
    return x, y, z3d

# Evaluate one pattern
def best_deviation_for_pattern(x, y, z, ratio, k_values):
    # expected normalized
    exp = np.array(ratio, float)
    exp = exp / exp.sum()
    best_dev = np.inf
    best_k = None
    for k1 in k_values:
        k2, k3 = 2*k1, 3*k1
        m1 = np.exp(1j*(k1*x + k1*y + k1*z))
        m2 = np.exp(1j*(k2*x + k2*y + k2*z))
        m3 = np.exp(1j*(k3*x + k3*y + k3*z))
        p1, p2, p3 = np.abs(np.mean(m1))**2, np.abs(np.mean(m2))**2, np.abs(np.mean(m3))**2
        tot = p1 + p2 + p3
        if tot <= 0: continue
        obs = np.array([p1, p2, p3]) / tot
        dev = np.sqrt(np.mean((obs - exp)**2))
        if dev < best_dev:
            best_dev = dev
            best_k = k1
    return best_dev, best_k

# Bootstrap repeatability
def bootstrap_deviation(x, y, z, ratio, k_values, n_trials=5, sample_frac=0.5):
    rng = np.random.default_rng(42)
    devs = []
    n = len(x)
    for t in range(n_trials):
        idx = rng.choice(n, size=int(n*sample_frac), replace=False)
        xb, yb, zb = x[idx], y[idx], z[idx]
        dev, _ = best_deviation_for_pattern(xb, yb, zb, ratio, k_values)
        devs.append(dev)
    return np.mean(devs), np.std(devs)

# Main search
def main():
    print("Automated Modal Ratio Search\n=================================")
    x, y, z = load_coords()
    n = len(x)
    print(f"Loaded {n:,} galaxies")
    # k range
    k_vals = np.logspace(np.log10(0.001), np.log10(0.1), 30)
    # generate combinations of ratios 1..6, enforce a<b<c to reduce duplicates
    patterns = [r for r in itertools.combinations(range(1,7), 3)]
    results = []
    for ratio in patterns:
        dev, kbest = best_deviation_for_pattern(x, y, z, ratio, k_vals)
        results.append((ratio, dev, kbest))
    # sort by deviation
    results.sort(key=lambda r: r[1])
    print("\nTop 5 patterns by best deviation:")
    for ratio, dev, kbest in results[:5]:
        print(f" Pattern {ratio}: dev={dev:.4f}, k1={kbest:.5f}")
    # repeatability on top pattern
    top = results[0]
    ratio0 = top[0]
    mean_dev, std_dev = bootstrap_deviation(x, y, z, ratio0, k_vals, n_trials=5)
    print(f"\nBootstrapped mean deviation for {ratio0}: {mean_dev:.4f} ± {std_dev:.4f}")

if __name__ == '__main__':
    main() 