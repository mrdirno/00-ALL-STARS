#!/usr/bin/env python3
"""
Modal Ratio Explorer - Test different modal ratio patterns in DESI data
"""
import numpy as np
import os
time_start = None

from astropy.io import fits
from astropy.table import Table

def load_coords():
    # Load DESI ELG clustering sample
    filepath = os.path.expanduser("~/telescope_data/desi_elg_clustering_sample.fits")
    with fits.open(filepath) as hdul:
        data = Table.read(hdul[1])
    mask = (data['Z'] > 0.01) & (data['Z'] < 3.0)
    filtered = data[mask]
    ra = np.array(filtered['RA'])
    dec = np.array(filtered['DEC'])
    z = np.array(filtered['Z'])
    # Convert to comoving
    c, H0 = 299792.458, 67.4
    dist = (c / H0) * z
    ra_rad, dec_rad = np.radians(ra), np.radians(dec)
    x = dist * np.cos(dec_rad) * np.cos(ra_rad)
    y = dist * np.cos(dec_rad) * np.sin(ra_rad)
    z3d = dist * np.sin(dec_rad)
    return {'x': x, 'y': y, 'z': z3d}

def test_modal_ratio(coords, ratio, k_values=None, threshold=0.05):
    x, y, z = coords['x'], coords['y'], coords['z']
    expected = np.array(ratio, dtype=float)
    expected = expected / expected.sum()
    if k_values is None:
        k_values = np.logspace(np.log10(0.001), np.log10(0.1), 30)
    detections = []
    for k1 in k_values:
        k2, k3 = 2 * k1, 3 * k1
        m1 = np.exp(1j * (k1 * x + k1 * y + k1 * z))
        m2 = np.exp(1j * (k2 * x + k2 * y + k2 * z))
        m3 = np.exp(1j * (k3 * x + k3 * y + k3 * z))
        p1, p2, p3 = np.abs(np.mean(m1))**2, np.abs(np.mean(m2))**2, np.abs(np.mean(m3))**2
        tot = p1 + p2 + p3
        if tot <= 0:
            continue
        obs = np.array([p1, p2, p3]) / tot
        deviation = np.sqrt(np.mean((obs - expected)**2))
        if deviation < threshold:
            detections.append((k1, deviation, obs))
    rate = len(detections) / len(k_values)
    print(f"Pattern {ratio}: {len(detections)}/{len(k_values)} detections (rate={rate:.1%})")
    if detections:
        best = sorted(detections, key=lambda x: x[1])[0]
        k_best, dev_best, obs_best = best
        print(f" Best detection at k={k_best:.5f}, dev={dev_best:.4f}, obs_ratios={obs_best}")
    print("")

def main():
    print("Modal Ratio Explorer\n================================")
    coords = load_coords()
    n = len(coords['x'])
    print(f"Loaded {n:,} galaxies")
    print("")
    # Test 4:3:6 pattern
    test_modal_ratio(coords, [4, 3, 6])
    # Test 3:4:2 pattern for comparison
    test_modal_ratio(coords, [3, 4, 2])

if __name__ == '__main__':
    main() 