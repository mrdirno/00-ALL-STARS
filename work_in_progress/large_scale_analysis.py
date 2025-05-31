#!/usr/bin/env python3

import numpy as np
from astropy.io import fits
from astropy.table import Table
from scipy import signal
import os

def load_desi_data():
    file_path = os.path.expanduser("~/telescope_data/desi_elg_clustering_sample.fits")
    
    with fits.open(file_path) as hdul:
        data = Table.read(hdul[1])
    
    ra = np.array(data['RA'])
    dec = np.array(data['DEC'])
    redshift = np.array(data['Z'])
    
    valid = (redshift > 0) & (redshift < 5) & np.isfinite(redshift)
    ra, dec, redshift = ra[valid], dec[valid], redshift[valid]
    
    c, H0 = 299792.458, 67.4
    distances = (c/H0) * redshift
    
    ra_rad, dec_rad = np.radians(ra), np.radians(dec)
    x = distances * np.cos(dec_rad) * np.cos(ra_rad)
    y = distances * np.cos(dec_rad) * np.sin(ra_rad)
    z = distances * np.sin(dec_rad)
    
    return {'x': x, 'y': y, 'z': z, 'redshift': redshift}

def test_14gpc_scale():
    print("TESTING 3-4:2 FRAMEWORK AT 14 GPC SCALE")
    print("="*45)
    
    coords = load_desi_data()
    x, y, z = coords['x'], coords['y'], coords['z']
    
    print(f"Data: {len(x):,} galaxies")
    print(f"Volume: {x.min():.0f} to {x.max():.0f} Mpc")
    
    # 14 Gpc scale corresponds to k ≈ 2π/14000 ≈ 0.00045 h/Mpc
    k_14gpc = 2 * np.pi / 14000  # h/Mpc
    
    # Test fundamental and harmonics at 14 Gpc scale
    k1 = k_14gpc
    k2 = 2 * k1  # 7 Gpc scale
    k3 = 3 * k1  # 4.7 Gpc scale
    
    print(f"\nTesting wavelengths:")
    print(f"λ₁ = {2*np.pi/k1:.0f} Mpc = {2*np.pi/k1/1000:.1f} Gpc")
    print(f"λ₂ = {2*np.pi/k2:.0f} Mpc = {2*np.pi/k2/1000:.1f} Gpc") 
    print(f"λ₃ = {2*np.pi/k3:.0f} Mpc = {2*np.pi/k3/1000:.1f} Gpc")
    
    # Compute Fourier modes
    mode1_x = np.cos(k1 * x) + 1j * np.sin(k1 * x)
    mode1_y = np.cos(k1 * y) + 1j * np.sin(k1 * y)
    mode1_z = np.cos(k1 * z) + 1j * np.sin(k1 * z)
    mode1_3d = mode1_x * mode1_y * mode1_z
    power1 = np.abs(np.mean(mode1_3d))**2
    
    mode2_x = np.cos(k2 * x) + 1j * np.sin(k2 * x)
    mode2_y = np.cos(k2 * y) + 1j * np.sin(k2 * y)
    mode2_z = np.cos(k2 * z) + 1j * np.sin(k2 * z)
    mode2_3d = mode2_x * mode2_y * mode2_z
    power2 = np.abs(np.mean(mode2_3d))**2
    
    mode3_x = np.cos(k3 * x) + 1j * np.sin(k3 * x)
    mode3_y = np.cos(k3 * y) + 1j * np.sin(k3 * y)
    mode3_z = np.cos(k3 * z) + 1j * np.sin(k3 * z)
    mode3_3d = mode3_x * mode3_y * mode3_z
    power3 = np.abs(np.mean(mode3_3d))**2
    
    print(f"\nPower measurements:")
    print(f"P(k₁) = {power1:.2e}")
    print(f"P(k₂) = {power2:.2e}")
    print(f"P(k₃) = {power3:.2e}")
    
    # Test for 1:2:3 relationship
    total_power = power1 + power2 + power3
    
    print(f"\nCombined signal: {total_power:.2e}")
    
    return power1, power2, power3

def test_random_14gpc():
    print("\nCONTROL: RANDOM DATA AT 14 GPC SCALE")
    print("="*40)
    
    # Generate random data with same statistics
    n_gal = 1821322
    redshifts = np.random.uniform(0.8, 1.6, n_gal)
    ra = np.random.uniform(0, 360, n_gal)
    dec = np.random.uniform(-30, 60, n_gal)
    
    c, H0 = 299792.458, 67.4
    distances = (c/H0) * redshifts
    ra_rad, dec_rad = np.radians(ra), np.radians(dec)
    x = distances * np.cos(dec_rad) * np.cos(ra_rad)
    y = distances * np.cos(dec_rad) * np.sin(ra_rad)
    z = distances * np.sin(dec_rad)
    
    k_14gpc = 2 * np.pi / 14000
    k1, k2, k3 = k_14gpc, 2*k_14gpc, 3*k_14gpc
    
    mode1_3d = (np.cos(k1*x) + 1j*np.sin(k1*x)) * (np.cos(k1*y) + 1j*np.sin(k1*y)) * (np.cos(k1*z) + 1j*np.sin(k1*z))
    mode2_3d = (np.cos(k2*x) + 1j*np.sin(k2*x)) * (np.cos(k2*y) + 1j*np.sin(k2*y)) * (np.cos(k2*z) + 1j*np.sin(k2*z))
    mode3_3d = (np.cos(k3*x) + 1j*np.sin(k3*x)) * (np.cos(k3*y) + 1j*np.sin(k3*y)) * (np.cos(k3*z) + 1j*np.sin(k3*z))
    
    power1_rand = np.abs(np.mean(mode1_3d))**2
    power2_rand = np.abs(np.mean(mode2_3d))**2
    power3_rand = np.abs(np.mean(mode3_3d))**2
    
    print(f"Random P(k₁) = {power1_rand:.2e}")
    print(f"Random P(k₂) = {power2_rand:.2e}")
    print(f"Random P(k₃) = {power3_rand:.2e}")
    print(f"Random combined: {power1_rand + power2_rand + power3_rand:.2e}")
    
    return power1_rand, power2_rand, power3_rand

if __name__ == "__main__":
    # Test DESI data
    desi_p1, desi_p2, desi_p3 = test_14gpc_scale()
    
    # Test random control
    rand_p1, rand_p2, rand_p3 = test_random_14gpc()
    
    desi_total = desi_p1 + desi_p2 + desi_p3
    rand_total = rand_p1 + rand_p2 + rand_p3
    
    print(f"\nCOMPARISON:")
    print(f"DESI total power:   {desi_total:.2e}")
    print(f"Random total power: {rand_total:.2e}")
    print(f"Ratio (DESI/Random): {desi_total/rand_total:.2f}")
    
    if desi_total > 2 * rand_total:
        print("SIGNIFICANT SIGNAL - Possible 3-4:2 structure at 14 Gpc scale")
    elif desi_total < 0.5 * rand_total:
        print("SIGNIFICANT DEFICIT - Galaxies avoid 14 Gpc harmonic structure")
    else:
        print("NO SIGNIFICANT DIFFERENCE - No 14 Gpc harmonic structure detected") 