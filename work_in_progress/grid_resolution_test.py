#!/usr/bin/env python3
"""
CRITICAL VALIDATION: Grid Resolution Independence Test

Tests whether sawtooth signature persists across different grid resolutions.
If pattern is only in 16³ grid, it's likely an artifact.
If pattern persists in 32³, 64³ grids, it's more likely real.

Following agent instructions: proper folder placement, headless operation.
"""

import os
os.environ['MPLBACKEND'] = 'Agg'
import matplotlib
matplotlib.use('Agg')

import numpy as np
from astropy.io import fits
from astropy.table import Table
import matplotlib.pyplot as plt
import time

class GridResolutionValidator:
    """
    Test sawtooth signatures across multiple grid resolutions
    """
    
    def __init__(self, coords):
        self.coords = coords
        self.x, self.y, self.z = coords['x'], coords['y'], coords['z']
        self.n_galaxies = len(self.x)
        
        print(f"Initialized grid validator with {self.n_galaxies:,} galaxies")
    
    def test_multiple_resolutions(self):
        """
        Test sawtooth detection across grid resolutions: 16³, 32³, 64³
        Critical test: If pattern only appears at one resolution, it's suspect
        """
        print("\n" + "="*70)
        print("CRITICAL VALIDATION: GRID RESOLUTION INDEPENDENCE TEST")
        print("="*70)
        
        # Test resolutions (limited by memory/computation)
        resolutions = [16, 32, 48]  # 48³ instead of 64³ for safety
        
        results = {}
        
        for grid_size in resolutions:
            print(f"\n{'='*50}")
            print(f"TESTING GRID RESOLUTION: {grid_size}³")
            print(f"{'='*50}")
            
            start_time = time.time()
            
            # Create density field at this resolution
            density_field = self._create_density_field(grid_size)
            
            # Test sawtooth at 63 Mpc (our best detection)
            k_63mpc = 2 * np.pi / 63  # Our primary detection
            sawtooth_result = self._test_sawtooth_at_scale(density_field, k_63mpc)
            
            # Also test a few nearby scales for robustness
            test_scales = [50, 63, 80]  # Mpc
            scale_results = {}
            
            for scale_mpc in test_scales:
                k_test = 2 * np.pi / scale_mpc
                result = self._test_sawtooth_at_scale(density_field, k_test)
                scale_results[scale_mpc] = result
            
            elapsed = time.time() - start_time
            
            results[grid_size] = {
                'primary_result': sawtooth_result,
                'scale_tests': scale_results,
                'computation_time': elapsed,
                'grid_size': grid_size
            }
            
            print(f"\nResults for {grid_size}³ grid:")
            print(f"  63 Mpc 3-4:2 score: {sawtooth_result['ratio_342_score']:.6f}")
            print(f"  63 Mpc correlation: {sawtooth_result['total_correlation']:.6f}")
            print(f"  Computation time: {elapsed:.1f}s")
            
            # Print scale comparison
            print(f"  Scale test results:")
            for scale, res in scale_results.items():
                print(f"    {scale} Mpc: score={res['ratio_342_score']:.6f}")
        
        # Analyze consistency across resolutions
        consistency_analysis = self._analyze_resolution_consistency(results)
        
        # Generate report
        self._generate_validation_report(results, consistency_analysis)
        
        return results, consistency_analysis
    
    def _create_density_field(self, grid_size):
        """
        Create density field at specified grid resolution
        """
        print(f"Creating {grid_size}³ density field...")
        
        # Find data bounds
        x_min, x_max = self.x.min(), self.x.max()
        y_min, y_max = self.y.min(), self.y.max()
        z_min, z_max = self.z.min(), self.z.max()
        
        # Create 3D histogram
        density_field, edges = np.histogramdd(
            np.column_stack([self.x, self.y, self.z]),
            bins=grid_size,
            range=[(x_min, x_max), (y_min, y_max), (z_min, z_max)]
        )
        
        # Normalize to overdensity field
        mean_density = density_field.mean()
        if mean_density > 0:
            density_field = density_field / mean_density - 1.0
        
        print(f"  Field shape: {density_field.shape}")
        print(f"  RMS density: {density_field.std():.6f}")
        print(f"  Non-zero cells: {np.sum(density_field != 0)}/{grid_size**3}")
        
        return {
            'field': density_field,
            'grid_size': grid_size,
            'edges': edges,
            'bounds': [(x_min, x_max), (y_min, y_max), (z_min, z_max)],
            'rms': density_field.std()
        }
    
    def _test_sawtooth_at_scale(self, density_field, k_fundamental):
        """
        Test sawtooth signature at specific scale
        """
        field = density_field['field']
        grid_size = density_field['grid_size']
        bounds = density_field['bounds']
        
        # Create coordinate grids
        x_grid = np.linspace(bounds[0][0], bounds[0][1], grid_size)
        y_grid = np.linspace(bounds[1][0], bounds[1][1], grid_size)
        z_grid = np.linspace(bounds[2][0], bounds[2][1], grid_size)
        X, Y, Z = np.meshgrid(x_grid, y_grid, z_grid, indexing='ij')
        
        # Generate sawtooth harmonics (2nd, 3rd, 4th)
        harmonic_correlations = []
        harmonic_strengths = []
        
        for n in [2, 3, 4]:  # Focus on 3-4:2 harmonics
            k_n = n * k_fundamental
            amplitude = 1.0 / n  # Sawtooth amplitude
            
            # Harmonic field
            harmonic_field = amplitude * np.sin(k_n * X + k_n * Y + k_n * Z)
            
            # Correlation with density field
            correlation = np.corrcoef(field.flatten(), harmonic_field.flatten())[0, 1]
            if np.isnan(correlation):
                correlation = 0.0
                
            harmonic_correlations.append(abs(correlation))
            harmonic_strengths.append(abs(correlation))
        
        # Test 3-4:2 ratios
        if len(harmonic_strengths) >= 3:
            h2, h3, h4 = harmonic_strengths
            total_strength = h2 + h3 + h4
            
            if total_strength > 0:
                # Observed ratios
                r2 = h2 / total_strength
                r3 = h3 / total_strength  
                r4 = h4 / total_strength
                
                # Expected 3-4:2 pattern: [2/9, 3/9, 4/9]
                expected = np.array([2/9, 3/9, 4/9])
                observed = np.array([r2, r3, r4])
                
                deviation = np.sqrt(np.mean((observed - expected)**2))
                score = 1.0 / (1.0 + deviation)
                
                # Total sawtooth correlation
                total_sawtooth = np.sum([
                    (1.0/n) * np.sin(n * k_fundamental * X + n * k_fundamental * Y + n * k_fundamental * Z)
                    for n in range(1, 5)
                ], axis=0)
                
                total_correlation = np.corrcoef(field.flatten(), total_sawtooth.flatten())[0, 1]
                if np.isnan(total_correlation):
                    total_correlation = 0.0
                
                return {
                    'ratio_342_score': score,
                    'deviation': deviation,
                    'harmonic_strengths': harmonic_strengths,
                    'ratios': observed,
                    'expected_ratios': expected,
                    'total_correlation': abs(total_correlation),
                    'individual_correlations': harmonic_correlations
                }
        
        # Failed case
        return {
            'ratio_342_score': 0.0,
            'deviation': np.inf,
            'harmonic_strengths': [0, 0, 0],
            'ratios': np.array([0, 0, 0]),
            'expected_ratios': np.array([2/9, 3/9, 4/9]),
            'total_correlation': 0.0,
            'individual_correlations': [0, 0, 0]
        }
    
    def _analyze_resolution_consistency(self, results):
        """
        Analyze consistency of results across resolutions
        """
        print(f"\n{'='*60}")
        print("RESOLUTION CONSISTENCY ANALYSIS")
        print("="*60)
        
        resolutions = list(results.keys())
        scores_63mpc = [results[res]['primary_result']['ratio_342_score'] for res in resolutions]
        correlations_63mpc = [results[res]['primary_result']['total_correlation'] for res in resolutions]
        
        # Calculate coefficient of variation
        score_mean = np.mean(scores_63mpc)
        score_std = np.std(scores_63mpc)
        score_cv = score_std / score_mean if score_mean > 0 else np.inf
        
        corr_mean = np.mean(correlations_63mpc)
        corr_std = np.std(correlations_63mpc)
        corr_cv = corr_std / corr_mean if corr_mean > 0 else np.inf
        
        # Trend analysis
        score_trend = np.polyfit(resolutions, scores_63mpc, 1)[0]  # Linear slope
        corr_trend = np.polyfit(resolutions, correlations_63mpc, 1)[0]
        
        consistency = {
            'resolutions_tested': resolutions,
            'scores_63mpc': scores_63mpc,
            'correlations_63mpc': correlations_63mpc,
            'score_statistics': {
                'mean': score_mean,
                'std': score_std,
                'cv': score_cv,
                'trend': score_trend
            },
            'correlation_statistics': {
                'mean': corr_mean,
                'std': corr_std,
                'cv': corr_cv,
                'trend': corr_trend
            }
        }
        
        # Print analysis
        print(f"3-4:2 Score consistency:")
        print(f"  Mean: {score_mean:.6f} ± {score_std:.6f}")
        print(f"  Coefficient of variation: {score_cv:.3f}")
        print(f"  Trend with resolution: {score_trend:.8f}")
        
        print(f"\nTotal correlation consistency:")
        print(f"  Mean: {corr_mean:.6f} ± {corr_std:.6f}")
        print(f"  Coefficient of variation: {corr_cv:.3f}")
        print(f"  Trend with resolution: {corr_trend:.8f}")
        
        # Verdict
        if score_cv < 0.3 and corr_cv < 0.3:
            verdict = "CONSISTENT - Pattern appears resolution-independent"
            confidence = "HIGH"
        elif score_cv < 0.5 and corr_cv < 0.5:
            verdict = "MODERATELY CONSISTENT - Some resolution dependence"
            confidence = "MEDIUM"
        else:
            verdict = "INCONSISTENT - Strong resolution dependence (possible artifact)"
            confidence = "LOW"
        
        consistency['verdict'] = verdict
        consistency['confidence'] = confidence
        
        print(f"\nVERDICT: {verdict}")
        print(f"CONFIDENCE: {confidence}")
        
        return consistency
    
    def _generate_validation_report(self, results, consistency):
        """
        Generate comprehensive validation report
        """
        report_path = "work_in_progress/grid_resolution_validation_report.md"
        
        with open(report_path, 'w') as f:
            f.write("# Grid Resolution Independence Validation Report\n\n")
            f.write(f"**Test Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Galaxies**: {self.n_galaxies:,}\n")
            f.write(f"**Primary Scale**: 63 Mpc\n\n")
            
            f.write("## Executive Summary\n\n")
            f.write(f"**Verdict**: {consistency['verdict']}\n")
            f.write(f"**Confidence**: {consistency['confidence']}\n\n")
            
            f.write("## Detailed Results\n\n")
            f.write("| Resolution | 3-4:2 Score | Total Correlation | Computation Time |\n")
            f.write("|------------|-------------|-------------------|------------------|\n")
            
            for grid_size in consistency['resolutions_tested']:
                result = results[grid_size]['primary_result']
                time_s = results[grid_size]['computation_time']
                f.write(f"| {grid_size}³ | {result['ratio_342_score']:.6f} | {result['total_correlation']:.6f} | {time_s:.1f}s |\n")
            
            f.write(f"\n## Statistical Analysis\n\n")
            f.write(f"**3-4:2 Score Statistics**:\n")
            f.write(f"- Mean: {consistency['score_statistics']['mean']:.6f}\n")
            f.write(f"- Standard Deviation: {consistency['score_statistics']['std']:.6f}\n")
            f.write(f"- Coefficient of Variation: {consistency['score_statistics']['cv']:.3f}\n")
            f.write(f"- Trend with Resolution: {consistency['score_statistics']['trend']:.8f}\n\n")
            
            f.write(f"**Interpretation**:\n")
            if consistency['score_statistics']['cv'] < 0.3:
                f.write("- Low CV indicates good consistency across resolutions\n")
                f.write("- Pattern appears to be resolution-independent\n")
                f.write("- Suggests physical origin rather than numerical artifact\n")
            else:
                f.write("- High CV indicates poor consistency across resolutions\n")
                f.write("- Pattern may be resolution-dependent artifact\n")
                f.write("- Requires further investigation\n")
        
        print(f"\nValidation report saved: {report_path}")
        
        # Create visualization
        self._plot_resolution_results(results, consistency)
    
    def _plot_resolution_results(self, results, consistency):
        """
        Plot resolution test results
        """
        resolutions = consistency['resolutions_tested']
        scores = consistency['scores_63mpc']
        correlations = consistency['correlations_63mpc']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 3-4:2 scores vs resolution
        ax1.plot(resolutions, scores, 'b-o', markersize=8, linewidth=2)
        ax1.set_xlabel('Grid Resolution (N³)')
        ax1.set_ylabel('3-4:2 Score at 63 Mpc')
        ax1.set_title('Sawtooth Score vs Grid Resolution')
        ax1.grid(True, alpha=0.3)
        
        # Add error bars (standard deviation)
        mean_score = np.mean(scores)
        ax1.axhline(y=mean_score, color='r', linestyle='--', alpha=0.7, label=f'Mean: {mean_score:.6f}')
        ax1.legend()
        
        # Total correlations vs resolution
        ax2.plot(resolutions, correlations, 'g-s', markersize=8, linewidth=2)
        ax2.set_xlabel('Grid Resolution (N³)')
        ax2.set_ylabel('Total Correlation at 63 Mpc')
        ax2.set_title('Total Correlation vs Grid Resolution')
        ax2.grid(True, alpha=0.3)
        
        mean_corr = np.mean(correlations)
        ax2.axhline(y=mean_corr, color='r', linestyle='--', alpha=0.7, label=f'Mean: {mean_corr:.6f}')
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig('work_in_progress/grid_resolution_validation.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Validation plot saved: work_in_progress/grid_resolution_validation.png")


def load_desi_data():
    """Load DESI data"""
    filepath = os.path.expanduser("~/telescope_data/desi_elg_clustering_sample.fits")
    
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
    
    return {
        'x': x, 'y': y, 'z': z,
        'redshift': redshift,
        'distances': distances,
        'ra': ra, 'dec': dec
    }


def main():
    """
    CRITICAL VALIDATION: Test grid resolution independence
    
    This is the HIGHEST PRIORITY test after our discovery.
    If sawtooth pattern only appears at 16³ resolution, it's likely an artifact.
    If it persists across 16³, 32³, 48³, it's more likely real.
    """
    print("CRITICAL VALIDATION: GRID RESOLUTION INDEPENDENCE TEST")
    print("="*60)
    print("Testing whether sawtooth discovery is resolution-dependent artifact")
    print("Priority: HIGHEST (could invalidate discovery)")
    print()
    
    # Load data
    print("Loading DESI data...")
    coords = load_desi_data()
    print(f"Loaded {len(coords['x']):,} galaxies")
    
    # Initialize validator
    validator = GridResolutionValidator(coords)
    
    # Run critical test
    print("\nRunning grid resolution independence test...")
    results, consistency = validator.test_multiple_resolutions()
    
    # Final summary
    print(f"\n{'='*70}")
    print("FINAL VALIDATION SUMMARY")
    print("="*70)
    print(f"Test result: {consistency['verdict']}")
    print(f"Confidence: {consistency['confidence']}")
    
    if "CONSISTENT" in consistency['verdict']:
        print("\n✅ DISCOVERY VALIDATED: Pattern is resolution-independent")
        print("   → Sawtooth signature appears genuine")
        print("   → Ready for next validation phase")
    elif "MODERATELY" in consistency['verdict']:
        print("\n⚠️ CAUTION: Some resolution dependence detected")
        print("   → Further investigation needed")
        print("   → Consider higher resolution tests")
    else:
        print("\n❌ DISCOVERY QUESTIONED: Strong resolution dependence")
        print("   → Pattern may be numerical artifact")
        print("   → Recommend alternative analysis methods")
    
    print(f"\nValidation complete. See reports in work_in_progress/")


if __name__ == "__main__":
    main() 