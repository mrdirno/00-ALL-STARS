#!/usr/bin/env python3

import numpy as np
from scipy import signal

def test_random_data():
    # Generate random positions with same statistics as DESI
    n_gal = 1821322
    z_min, z_max = 0.8, 1.6
    redshifts = np.random.uniform(z_min, z_max, n_gal)
    ra = np.random.uniform(0, 360, n_gal)
    dec = np.random.uniform(-30, 60, n_gal)

    # Convert to distances and Cartesian
    c, H0 = 299792.458, 67.4
    distances = (c/H0) * redshifts
    ra_rad, dec_rad = np.radians(ra), np.radians(dec)
    x = distances * np.cos(dec_rad) * np.cos(ra_rad)
    y = distances * np.cos(dec_rad) * np.sin(ra_rad)
    z = distances * np.sin(dec_rad)

    # Compute power spectrum
    k_range = np.logspace(-3, -1, 200)
    power = []
    for k in k_range:
        modes_x = np.cos(k * x) + 1j * np.sin(k * x)
        modes_y = np.cos(k * y) + 1j * np.sin(k * y)
        modes_z = np.cos(k * z) + 1j * np.sin(k * z)
        mode_3d = modes_x * modes_y * modes_z
        power.append(np.abs(np.mean(mode_3d))**2)

    power = np.array(power)

    # Find peaks
    peaks, _ = signal.find_peaks(power)
    peak_freqs = k_range[peaks]
    peak_powers = power[peaks]
    sort_idx = np.argsort(peak_powers)[::-1]
    peak_freqs = peak_freqs[sort_idx]

    # Check for 1:2:3 relationships
    matches = 0
    tolerance = 0.05
    for i in range(len(peak_freqs)):
        for j in range(i+1, len(peak_freqs)):
            for k in range(j+1, len(peak_freqs)):
                f1, f2, f3 = np.sort([peak_freqs[i], peak_freqs[j], peak_freqs[k]])
                r21, r31, r32 = f2/f1, f3/f1, f3/f2
                dev = (abs(r21-2)/2 + abs(r31-3)/3 + abs(r32-1.5)/1.5) / 3
                if dev < tolerance:
                    matches += 1

    return len(peak_freqs), matches

# Run multiple trials
trials = 3
total_peaks = 0
total_matches = 0

print("NULL HYPOTHESIS TEST")
print("===================")
print("Testing random data with same statistics as DESI")

for i in range(trials):
    peaks, matches = test_random_data()
    total_peaks += peaks
    total_matches += matches
    print(f"Trial {i+1}: {peaks} peaks, {matches} harmonic matches")

avg_peaks = total_peaks / trials
avg_matches = total_matches / trials

print(f"\nAverage per trial:")
print(f"Peaks: {avg_peaks:.0f}")
print(f"Harmonic matches: {avg_matches:.0f}")

print(f"\nDESI data had 68 harmonic matches")
print(f"Random data average: {avg_matches:.0f}")

if avg_matches > 50:
    print("HIGH FALSE POSITIVE RATE - Results likely meaningless")
elif avg_matches > 20:
    print("MODERATE FALSE POSITIVE RATE - Results need careful interpretation")
else:
    print("LOW FALSE POSITIVE RATE - DESI results may be significant") 