#!/usr/bin/env python3
"""
Sawtooth Wave Analysis for DESI DR1 - Testing 3-4:2 Modal Framework

Sawtooth waves have unique harmonic properties:
- Contains all integer harmonics
- Amplitude ∝ 1/n where n is harmonic number
- For 3-4:2 framework: expect specific relationships in sawtooth decomposition
"""

import numpy as np
import os
import sys
from astropy.io import fits
from astropy.table import Table
import matplotlib.pyplot as plt
from scipy import signal
from scipy.fft import fft, fftfreq
import requests
from io import BytesIO

class SawtoothCosmicAnalyzer:
    """
    Analyzes cosmic structure for sawtooth wave patterns
    """
    
    def __init__(self, coords):
        self.coords = coords
        self.x, self.y, self.z = coords['x'], coords['y'], coords['z']
        self.n_galaxies = len(self.x)
        
        print(f"Initialized sawtooth analyzer with {self.n_galaxies:,} galaxies")
    
    def generate_sawtooth_basis(self, fundamental_k, n_harmonics=10):
        """
        Generate sawtooth wave basis functions for given fundamental frequency
        
        Sawtooth wave: sum of harmonics with amplitudes 1/n
        """
        sawtooth_components = []
        harmonic_ks = []
        
        for n in range(1, n_harmonics + 1):
            k_n = n * fundamental_k
            amplitude = 1.0 / n  # Sawtooth harmonic amplitude
            
            # 3D sawtooth component
            component = amplitude * np.sin(k_n * self.x + k_n * self.y + k_n * self.z)
            sawtooth_components.append(component)
            harmonic_ks.append(k_n)
        
        # Full sawtooth signal
        full_sawtooth = np.sum(sawtooth_components, axis=0)
        
        return {
            'full_sawtooth': full_sawtooth,
            'components': sawtooth_components,
            'harmonic_ks': harmonic_ks,
            'fundamental_k': fundamental_k
        }
    
    def test_sawtooth_signatures(self):
        """
        Test for sawtooth wave signatures in cosmic structure
        """
        print("\n" + "="*60)
        print("SAWTOOTH WAVE ANALYSIS")
        print("="*60)
        
        # Create 3D density field from galaxy positions
        density_field = self._create_density_field()
        
        # Test different fundamental frequencies
        k_fundamentals = np.logspace(-4, -1, 20)  # 63 Mpc to 63 Gpc scales
        
        sawtooth_detections = []
        
        for i, k_fund in enumerate(k_fundamentals):
            wavelength = 2 * np.pi / k_fund
            print(f"Testing sawtooth at λ = {wavelength:.0f} Mpc [{i+1}/{len(k_fundamentals)}]")
            
            # Generate sawtooth basis
            sawtooth_basis = self.generate_sawtooth_basis(k_fund, n_harmonics=10)
            
            # Cross-correlate density field with sawtooth
            correlation = self._calculate_sawtooth_correlation(
                density_field, sawtooth_basis
            )
            
            # Test for 3-4:2 ratios in harmonic components
            ratio_test = self._test_342_sawtooth_ratios(sawtooth_basis, density_field)
            
            detection = {
                'fundamental_k': k_fund,
                'wavelength_Mpc': wavelength,
                'correlation_strength': correlation['total_correlation'],
                'harmonic_correlations': correlation['harmonic_correlations'],
                'ratio_342_score': ratio_test['score'],
                'ratio_deviation': ratio_test['deviation'],
                'harmonic_3_strength': ratio_test['harmonic_3'],
                'harmonic_4_strength': ratio_test['harmonic_4'], 
                'harmonic_2_strength': ratio_test['harmonic_2']
            }
            
            sawtooth_detections.append(detection)
        
        return self._analyze_sawtooth_results(sawtooth_detections)
    
    def _create_density_field(self):
        """
        Create 3D density field from galaxy positions using grid binning
        """
        print("Creating 3D density field...")
        
        # Determine grid size (compromise between resolution and computation)
        grid_size = min(64, int(self.n_galaxies**(1/3) / 10))  # Adaptive grid
        grid_size = max(16, grid_size)  # Minimum grid size
        
        print(f"Using {grid_size}³ grid")
        
        # Find data bounds
        x_min, x_max = self.x.min(), self.x.max()
        y_min, y_max = self.y.min(), self.y.max()
        z_min, z_max = self.z.min(), self.z.max()
        
        # Create 3D histogram (density field)
        density_field, edges = np.histogramdd(
            np.column_stack([self.x, self.y, self.z]),
            bins=grid_size,
            range=[(x_min, x_max), (y_min, y_max), (z_min, z_max)]
        )
        
        # Normalize to mean density
        mean_density = density_field.mean()
        if mean_density > 0:
            density_field = density_field / mean_density - 1.0  # Delta field
        
        print(f"Density field: {density_field.shape}, RMS = {density_field.std():.6f}")
        
        return {
            'field': density_field,
            'grid_size': grid_size,
            'edges': edges,
            'bounds': [(x_min, x_max), (y_min, y_max), (z_min, z_max)]
        }
    
    def _calculate_sawtooth_correlation(self, density_field, sawtooth_basis):
        """
        Calculate correlation between density field and sawtooth pattern
        """
        field = density_field['field']
        grid_size = density_field['grid_size']
        
        # Create coordinate grids for sawtooth evaluation
        bounds = density_field['bounds']
        x_grid = np.linspace(bounds[0][0], bounds[0][1], grid_size)
        y_grid = np.linspace(bounds[1][0], bounds[1][1], grid_size)
        z_grid = np.linspace(bounds[2][0], bounds[2][1], grid_size)
        
        X, Y, Z = np.meshgrid(x_grid, y_grid, z_grid, indexing='ij')
        
        # Evaluate sawtooth components on grid
        harmonic_correlations = []
        
        for i, k_harm in enumerate(sawtooth_basis['harmonic_ks']):
            amplitude = 1.0 / (i + 1)  # Sawtooth amplitude
            
            # Sawtooth harmonic on grid
            harmonic_field = amplitude * np.sin(k_harm * X + k_harm * Y + k_harm * Z)
            
            # Cross-correlation
            correlation = np.corrcoef(field.flatten(), harmonic_field.flatten())[0, 1]
            if np.isnan(correlation):
                correlation = 0.0
                
            harmonic_correlations.append(abs(correlation))
        
        # Total sawtooth correlation
        full_sawtooth_grid = np.sum([
            (1.0 / (i + 1)) * np.sin(k * X + k * Y + k * Z) 
            for i, k in enumerate(sawtooth_basis['harmonic_ks'])
        ], axis=0)
        
        total_correlation = np.corrcoef(field.flatten(), full_sawtooth_grid.flatten())[0, 1]
        if np.isnan(total_correlation):
            total_correlation = 0.0
        
        return {
            'total_correlation': abs(total_correlation),
            'harmonic_correlations': harmonic_correlations
        }
    
    def _test_342_sawtooth_ratios(self, sawtooth_basis, density_field):
        """
        Test for 3-4:2 ratios in sawtooth harmonic components
        """
        correlations = []
        k_values = sawtooth_basis['harmonic_ks']
        
        # Get correlations for first 10 harmonics
        field = density_field['field']
        grid_size = density_field['grid_size']
        bounds = density_field['bounds']
        
        x_grid = np.linspace(bounds[0][0], bounds[0][1], grid_size)
        y_grid = np.linspace(bounds[1][0], bounds[1][1], grid_size)
        z_grid = np.linspace(bounds[2][0], bounds[2][1], grid_size)
        X, Y, Z = np.meshgrid(x_grid, y_grid, z_grid, indexing='ij')
        
        for i, k_harm in enumerate(k_values[:10]):
            amplitude = 1.0 / (i + 1)
            harmonic_field = amplitude * np.sin(k_harm * X + k_harm * Y + k_harm * Z)
            
            correlation = np.corrcoef(field.flatten(), harmonic_field.flatten())[0, 1]
            if np.isnan(correlation):
                correlation = 0.0
            correlations.append(abs(correlation))
        
        # Look for 3-4:2 pattern in harmonic strengths
        if len(correlations) >= 4:
            # Compare harmonic 2, 3, 4 (indices 1, 2, 3)
            h2_strength = correlations[1] if len(correlations) > 1 else 0
            h3_strength = correlations[2] if len(correlations) > 2 else 0  
            h4_strength = correlations[3] if len(correlations) > 3 else 0
            
            total_strength = h2_strength + h3_strength + h4_strength
            
            if total_strength > 0:
                # Normalize observed ratios
                h2_ratio = h2_strength / total_strength
                h3_ratio = h3_strength / total_strength
                h4_ratio = h4_strength / total_strength
                
                # Expected sawtooth harmonic ratios from amplitudes 1/n
                raw = np.array([1/2, 1/3, 1/4])
                expected = raw / raw.sum()
                observed = np.array([h2_ratio, h3_ratio, h4_ratio])
                
                deviation = np.sqrt(np.mean((observed - expected)**2))
                score = 1.0 / (1.0 + deviation)  # Higher score = better match
                
                return {
                    'score': score,
                    'deviation': deviation,
                    'harmonic_2': h2_strength,
                    'harmonic_3': h3_strength,
                    'harmonic_4': h4_strength,
                    'ratio_342': observed,
                    'expected_ratios': expected
                }
        
        return {
            'score': 0.0,
            'deviation': np.inf,
            'harmonic_2': 0.0,
            'harmonic_3': 0.0,
            'harmonic_4': 0.0,
            'ratio_342': np.array([0, 0, 0]),
            # Fallback expected ratios using normalized amplitudes 1/n
            'expected_ratios': np.array([1/2, 1/3, 1/4]) / np.sum([1/2, 1/3, 1/4])
        }
    
    def _analyze_sawtooth_results(self, detections):
        """
        Analyze and summarize sawtooth test results
        """
        print(f"\n{'='*60}")
        print("SAWTOOTH ANALYSIS RESULTS")
        print("="*60)
        
        # Sort by 3-4:2 ratio score
        best_detections = sorted(detections, key=lambda x: x['ratio_342_score'], reverse=True)
        
        # Find detections with significant 3-4:2 ratios
        significant_detections = [d for d in detections if d['ratio_342_score'] > 0.5]
        
        print(f"Total scales tested: {len(detections)}")
        print(f"Significant 3-4:2 sawtooth detections: {len(significant_detections)}")
        print(f"Detection rate: {len(significant_detections)/len(detections):.1%}")
        
        if best_detections:
            best = best_detections[0]
            print(f"\nBest 3-4:2 sawtooth signature:")
            print(f"  Scale: {best['wavelength_Mpc']:.0f} Mpc")
            print(f"  3-4:2 score: {best['ratio_342_score']:.6f}")
            print(f"  Ratio deviation: {best['ratio_deviation']:.6f}")
            print(f"  Harmonic strengths (2:3:4): {best['harmonic_2_strength']:.4f}:{best['harmonic_3_strength']:.4f}:{best['harmonic_4_strength']:.4f}")
            print(f"  Total correlation: {best['correlation_strength']:.6f}")
        
        # Plot results
        self._plot_sawtooth_results(detections)
        
        return {
            'total_tested': len(detections),
            'significant_detections': len(significant_detections),
            'best_detection': best_detections[0] if best_detections else None,
            'all_detections': detections
        }
    
    def _plot_sawtooth_results(self, detections):
        """
        Plot sawtooth analysis results
        """
        wavelengths = [d['wavelength_Mpc'] for d in detections]
        scores = [d['ratio_342_score'] for d in detections]
        correlations = [d['correlation_strength'] for d in detections]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # 3-4:2 ratio scores
        ax1.loglog(wavelengths, scores, 'b-o', markersize=4)
        ax1.axhline(y=0.5, color='r', linestyle='--', alpha=0.7, label='Significance threshold')
        ax1.set_xlabel('Wavelength (Mpc)')
        ax1.set_ylabel('3-4:2 Sawtooth Score')
        ax1.set_title('3-4:2 Sawtooth Pattern Detection vs Scale')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Total correlations
        ax2.loglog(wavelengths, correlations, 'g-s', markersize=4)
        ax2.set_xlabel('Wavelength (Mpc)')
        ax2.set_ylabel('Total Sawtooth Correlation')
        ax2.set_title('Overall Sawtooth Correlation vs Scale')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('sawtooth_cosmic_analysis.png', dpi=300, bbox_inches='tight')
        print(f"\nSaved results plot: sawtooth_cosmic_analysis.png")
        
        return fig

    def control_test_random_sawtooth(self, n_trials=3):
        """
        Control test: run sawtooth analysis on random data
        """
        print(f"\n{'='*60}")
        print(f"SAWTOOTH CONTROL TEST: Random data ({n_trials} trials)")
        print("="*60)
        
        control_results = []
        
        for trial in range(n_trials):
            print(f"\nSawtooth Control Trial {trial + 1}/{n_trials}")
            
            # Generate random coordinates
            redshifts = np.random.uniform(
                self.coords['redshift'].min(),
                self.coords['redshift'].max(),
                self.n_galaxies
            )
            
            ra = np.random.uniform(self.coords['ra'].min(), self.coords['ra'].max(), self.n_galaxies)
            dec = np.random.uniform(self.coords['dec'].min(), self.coords['dec'].max(), self.n_galaxies)
            
            # Convert to comoving coordinates
            c, H0 = 299792.458, 67.4
            distances = (c/H0) * redshifts
            ra_rad, dec_rad = np.radians(ra), np.radians(dec)
            x = distances * np.cos(dec_rad) * np.cos(ra_rad)
            y = distances * np.cos(dec_rad) * np.sin(ra_rad)
            z = distances * np.sin(dec_rad)
            
            # Create temporary analyzer for random data
            random_coords = {'x': x, 'y': y, 'z': z, 'redshift': redshifts, 'ra': ra, 'dec': dec}
            random_analyzer = SawtoothCosmicAnalyzer(random_coords)
            
            # Run abbreviated sawtooth test
            result = random_analyzer._abbreviated_sawtooth_test()
            control_results.append(result)
            
            print(f"  Trial {trial+1}: {result['significant_detections']} significant detections")
            print(f"  Best score: {result['best_score']:.6f}")
        
        return control_results
    
    def _abbreviated_sawtooth_test(self):
        """
        Run abbreviated sawtooth test for control purposes
        """
        density_field = self._create_density_field()
        
        # Test fewer scales for speed
        k_fundamentals = np.logspace(-3, -2, 10)
        
        detections = []
        for k_fund in k_fundamentals:
            sawtooth_basis = self.generate_sawtooth_basis(k_fund, n_harmonics=5)
            correlation = self._calculate_sawtooth_correlation(density_field, sawtooth_basis)
            ratio_test = self._test_342_sawtooth_ratios(sawtooth_basis, density_field)
            
            detections.append({
                'fundamental_k': k_fund,
                'wavelength_Mpc': 2 * np.pi / k_fund,
                'ratio_342_score': ratio_test['score']
            })
        
        significant = [d for d in detections if d['ratio_342_score'] > 0.5]
        best_score = max([d['ratio_342_score'] for d in detections]) if detections else 0.0
        
        return {
            'significant_detections': len(significant),
            'total_tested': len(detections),
            'best_score': best_score
        }


def load_desi_data():
    """Load DESI data from available files"""
    sample_files = [
        os.path.expanduser("~/telescope_data/desi_elg_clustering_sample.fits"),
        os.path.expanduser("~/telescope_data/desi_elg_ngc_real.fits")
    ]
    
    for filepath in sample_files:
        if os.path.exists(filepath):
            print(f"Loading DESI data from {filepath}")
            try:
                with fits.open(filepath) as hdul:
                    data = Table.read(hdul[1])
                
                # Filter for good galaxies
                mask = ((data['Z'] > 0.01) & (data['Z'] < 3.0))
                filtered_data = data[mask]
                
                # Convert to coordinates
                ra = np.array(filtered_data['RA'])
                dec = np.array(filtered_data['DEC'])
                redshift = np.array(filtered_data['Z'])
                
                # Convert to comoving coordinates
                c, H0 = 299792.458, 67.4
                distances = (c/H0) * redshift
                ra_rad, dec_rad = np.radians(ra), np.radians(dec)
                x = distances * np.cos(dec_rad) * np.cos(ra_rad)
                y = distances * np.cos(dec_rad) * np.sin(ra_rad)
                z = distances * np.sin(dec_rad)
                
                coords = {
                    'x': x, 'y': y, 'z': z,
                    'redshift': redshift,
                    'distances': distances,
                    'ra': ra, 'dec': dec
                }
                
                print(f"Loaded {len(x):,} galaxies")
                print(f"Redshift range: {redshift.min():.3f} to {redshift.max():.3f}")
                
                return coords
                
            except Exception as e:
                print(f"Failed to load {filepath}: {e}")
                continue
    
    raise RuntimeError("No DESI data files found")


def main():
    """Main sawtooth analysis"""
    print("SAWTOOTH WAVE ANALYSIS FOR 3-4:2 MODAL FRAMEWORK")
    print("="*60)
    
    # Load DESI data
    print("Loading DESI DR1 data...")
    try:
        coords = load_desi_data()
    except RuntimeError as e:
        print(f"Error: {e}")
        return
    
    # Initialize sawtooth analyzer
    print("\nInitializing sawtooth analyzer...")
    analyzer = SawtoothCosmicAnalyzer(coords)
    
    # Run sawtooth analysis
    print("\nRunning sawtooth wave analysis...")
    desi_results = analyzer.test_sawtooth_signatures()
    
    # Control test
    print("\nRunning control test with random data...")
    control_results = analyzer.control_test_random_sawtooth(n_trials=2)
    
    # Compare results
    print(f"\n{'='*60}")
    print("SAWTOOTH ANALYSIS SUMMARY")
    print("="*60)
    
    avg_control_detections = np.mean([r['significant_detections'] for r in control_results])
    avg_control_score = np.mean([r['best_score'] for r in control_results])
    
    print(f"\nDESI sawtooth detections: {desi_results['significant_detections']}")
    print(f"Random sawtooth detections (avg): {avg_control_detections:.1f}")
    print(f"DESI best 3-4:2 score: {desi_results['best_detection']['ratio_342_score']:.6f}")
    print(f"Random best score (avg): {avg_control_score:.6f}")
    
    if desi_results['significant_detections'] > avg_control_detections * 1.5:
        print(f"\n*** SIGNIFICANT SAWTOOTH SIGNATURES DETECTED ***")
        print(f"DESI shows {desi_results['significant_detections']/avg_control_detections:.1f}x more sawtooth detections than random")
    elif desi_results['significant_detections'] < avg_control_detections * 0.5:
        print(f"\n*** SAWTOOTH DEFICIT DETECTED ***")
        print(f"DESI shows {desi_results['significant_detections']/avg_control_detections:.1f}x fewer sawtooth detections than random")
    else:
        print(f"\nNo significant sawtooth signatures - consistent with random noise")
    
    print(f"\nSawtooth analysis complete.")


if __name__ == "__main__":
    main() 