#!/usr/bin/env python3
"""
CMB-Galaxy Mass Cross-Correlation

Load a Planck CMB temperature map and DESI galaxy catalog,
bin galaxies by HEALPix pixel to estimate mass proxy,
then compare mean galaxy density in hot vs cold CMB regions.
"""
import os
import numpy as np
import healpy as hp
from astropy.io import fits as fits_io
from astropy.table import Table

# Parameters
NSIDE = 128  # HEALPix resolution for cross-correlation
# Use the downloaded Planck Commander CMB map
MAP_FILE = os.path.expanduser('~/telescope_data/planck_data/planck_pr4_cmb_commander.fits')
CAT_FILE = os.path.expanduser('~/telescope_data/desi_elg_clustering_sample.fits')
HOT_THRESHOLD = 100e-6  # 100 μK
COLD_THRESHOLD = -100e-6  # -100 μK

# Load CMB map
print('Loading CMB map...')
if not os.path.exists(MAP_FILE):
    raise FileNotFoundError(f'CMB map not found: {MAP_FILE}')
# Read Commander map via astropy and degrade to desired NSIDE
with fits_io.open(MAP_FILE, memmap=False) as hdul:
    full_map = hdul[1].data['I_STOKES']  # temperature in K
# Degrade to NSIDE resolution
cmb_map = hp.ud_grade(full_map, nside_out=NSIDE)

# Load galaxy data and compute pixel counts
print('Loading galaxy catalog...')
with fits_io.open(CAT_FILE) as hdul:
    data = Table.read(hdul[1])
mask = (data['Z'] > 0.01) & (data['Z'] < 3.0)
data = data[mask]

# Convert RA,Dec to HEALPix pixel indices
ra = np.array(data['RA'])
dec = np.array(data['DEC'])
theta = np.radians(90 - dec)
phi = np.radians(ra)
pix = hp.ang2pix(NSIDE, theta, phi)

# Count galaxies per pixel as mass proxy
mass_counts = np.bincount(pix, minlength=hp.nside2npix(NSIDE))

# Separate hot and cold pixels
hot_pixels = np.where(cmb_map > HOT_THRESHOLD)[0]
cold_pixels = np.where(cmb_map < COLD_THRESHOLD)[0]

# Compute mean galaxy density in each region
area_pixel = 4 * np.pi / hp.nside2npix(NSIDE)
mean_hot = np.mean(mass_counts[hot_pixels] / area_pixel)
mean_cold = np.mean(mass_counts[cold_pixels] / area_pixel)

print(f'Mean galaxy density in hot CMB regions: {mean_hot:.3f} galaxies per steradian')
print(f'Mean galaxy density in cold CMB regions: {mean_cold:.3f} galaxies per steradian')
print(f'Hot/Cold density ratio: {mean_hot/mean_cold:.3f}')

# Plot results
import matplotlib.pyplot as plt
plt.figure(figsize=(6,4))
plt.bar(['Cold','Hot'], [mean_cold, mean_hot], color=['blue','red'])
plt.ylabel('Galaxy density (counts / sr)')
plt.title('Galaxy Density vs CMB Temperature Region')
plt.tight_layout()
out_plot = 'cmb_galaxy_density_comparison.png'
plt.savefig(out_plot, dpi=200)
print(f'Saved plot: {out_plot}') 