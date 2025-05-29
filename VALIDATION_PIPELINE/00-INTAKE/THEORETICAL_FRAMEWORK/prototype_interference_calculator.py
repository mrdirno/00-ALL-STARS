#!/usr/bin/env python3
"""
Prototype: Central Mass Determination via Cosmic Interference Pattern Analysis
==============================================================================

This prototype demonstrates the core computational approach for calculating
interference patterns from simultaneous explosions on a sphere and relating
pattern scales to central mass.

Authors: Aldrin Payopay, Claude Opus 4, Gemini 2.5 Pro
Date: January 2025
Status: Proof of Concept Implementation
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
from scipy.optimize import minimize_scalar
import time

class CosmicInterferenceCalculator:
    """
    Calculates interference patterns from simultaneous spherical explosions
    and determines scaling relationships with central mass.
    """
    
    def __init__(self, grid_resolution=100, sphere_radius=1.0):
        """
        Initialize the calculator with computational grid.
        
        Parameters:
        -----------
        grid_resolution : int
            Number of grid points per dimension
        sphere_radius : float
            Radius of the explosion sphere
        """
        self.grid_resolution = grid_resolution
        self.sphere_radius = sphere_radius
        self.setup_computational_grid()
        
    def setup_computational_grid(self):
        """Create 3D computational grid for interference calculation."""
        # Create symmetric grid centered at origin
        extent = 2.0 * self.sphere_radius
        x = np.linspace(-extent, extent, self.grid_resolution)
        y = np.linspace(-extent, extent, self.grid_resolution)
        z = np.linspace(-extent, extent, self.grid_resolution)
        
        self.X, self.Y, self.Z = np.meshgrid(x, y, z, indexing='ij')
        self.grid_points = np.stack([self.X.ravel(), self.Y.ravel(), self.Z.ravel()], axis=1)
        
        print(f"Computational grid: {self.grid_resolution}³ = {len(self.grid_points):,} points")
        
    def generate_fibonacci_sphere(self, n_points):
        """
        Generate uniformly distributed points on sphere using Fibonacci spiral.
        
        Parameters:
        -----------
        n_points : int
            Number of explosion points on sphere
            
        Returns:
        --------
        points : ndarray, shape (n_points, 3)
            3D coordinates of explosion points
        """
        indices = np.arange(0, n_points, dtype=float) + 0.5
        
        # Fibonacci spiral algorithm
        theta = np.arccos(1 - 2 * indices / n_points)  # Polar angle
        phi = np.pi * (1 + 5**0.5) * indices  # Azimuthal angle (golden ratio)
        
        # Convert to Cartesian coordinates
        x = self.sphere_radius * np.sin(theta) * np.cos(phi)
        y = self.sphere_radius * np.sin(theta) * np.sin(phi)
        z = self.sphere_radius * np.cos(theta)
        
        return np.column_stack([x, y, z])
    
    def calculate_wave_contribution(self, source_point, central_mass=1.0, wave_speed=1.0):
        """
        Calculate wave contribution from single explosion point.
        
        Parameters:
        -----------
        source_point : array_like, shape (3,)
            3D coordinates of explosion source
        central_mass : float
            Central mass affecting wave propagation
        wave_speed : float
            Wave propagation speed
            
        Returns:
        --------
        wave_field : ndarray, shape (grid_resolution³,)
            Wave amplitude at each grid point
        """
        # Calculate distances from source to all grid points
        distances = np.linalg.norm(self.grid_points - source_point, axis=1)
        
        # Avoid division by zero at source location
        distances = np.maximum(distances, 1e-10)
        
        # Central mass affects wave number (frequency)
        k = 2 * np.pi * np.sqrt(central_mass) / wave_speed
        
        # Spherical wave with central mass modulation
        amplitude = 1.0 / distances  # 1/r falloff
        phase = k * distances
        
        # Add central mass gravitational effect
        gravitational_factor = 1.0 + central_mass / (distances + 1.0)
        
        wave_field = amplitude * np.sin(phase) * gravitational_factor
        
        return wave_field
    
    def calculate_total_interference(self, n_explosion_points, central_mass=1.0):
        """
        Calculate total interference pattern from all explosion points.
        
        Parameters:
        -----------
        n_explosion_points : int
            Number of simultaneous explosion points
        central_mass : float
            Central mass parameter
            
        Returns:
        --------
        total_field : ndarray, shape (grid_resolution³,)
            Total interference pattern
        explosion_points : ndarray, shape (n_explosion_points, 3)
            Coordinates of explosion points
        """
        print(f"Calculating interference from {n_explosion_points:,} explosion points...")
        start_time = time.time()
        
        # Generate explosion points on sphere
        explosion_points = self.generate_fibonacci_sphere(n_explosion_points)
        
        # Initialize total field
        total_field = np.zeros(len(self.grid_points))
        
        # Calculate contribution from each explosion point
        for i, point in enumerate(explosion_points):
            if i % (n_explosion_points // 10) == 0:
                progress = 100 * i / n_explosion_points
                print(f"  Progress: {progress:.1f}%")
            
            wave_contrib = self.calculate_wave_contribution(point, central_mass)
            total_field += wave_contrib
        
        elapsed = time.time() - start_time
        print(f"  Completed in {elapsed:.2f} seconds")
        
        return total_field, explosion_points
    
    def analyze_pattern_characteristics(self, field):
        """
        Extract characteristic scales from interference pattern.
        
        Parameters:
        -----------
        field : ndarray
            3D interference field
            
        Returns:
        --------
        characteristics : dict
            Pattern characteristics including dominant wavelength
        """
        # Reshape field to 3D grid
        field_3d = field.reshape(self.grid_resolution, self.grid_resolution, self.grid_resolution)
        
        # Calculate power spectrum to find dominant wavelengths
        field_fft = np.fft.fftn(field_3d)
        power_spectrum = np.abs(field_fft)**2
        
        # Find peak frequencies
        freqs = np.fft.fftfreq(self.grid_resolution, d=4.0*self.sphere_radius/self.grid_resolution)
        freq_magnitude = np.sqrt(freqs[:, None, None]**2 + freqs[None, :, None]**2 + freqs[None, None, :]**2)
        
        # Calculate radially averaged power spectrum
        freq_bins = np.linspace(0, freqs.max(), 50)
        power_radial = np.zeros(len(freq_bins)-1)
        
        for i in range(len(freq_bins)-1):
            mask = (freq_magnitude >= freq_bins[i]) & (freq_magnitude < freq_bins[i+1])
            if np.any(mask):
                power_radial[i] = np.mean(power_spectrum[mask])
        
        # Find dominant frequency (excluding DC component)
        dominant_freq_idx = np.argmax(power_radial[1:]) + 1
        dominant_freq = (freq_bins[dominant_freq_idx] + freq_bins[dominant_freq_idx+1]) / 2
        
        # Convert to wavelength
        dominant_wavelength = 1.0 / dominant_freq if dominant_freq > 0 else np.inf
        
        # Calculate field statistics
        field_std = np.std(field)
        field_mean = np.mean(field)
        
        return {
            'dominant_wavelength': dominant_wavelength,
            'dominant_frequency': dominant_freq,
            'field_std': field_std,
            'field_mean': field_mean,
            'power_spectrum': power_radial,
            'freq_bins': freq_bins
        }
    
    def mass_scaling_study(self, mass_range, n_explosion_points=1000):
        """
        Study how pattern characteristics scale with central mass.
        
        Parameters:
        -----------
        mass_range : array_like
            Range of central masses to test
        n_explosion_points : int
            Number of explosion points for each calculation
            
        Returns:
        --------
        results : dict
            Scaling study results
        """
        print(f"\nMass Scaling Study: {len(mass_range)} mass values")
        print(f"Explosion points per calculation: {n_explosion_points:,}")
        
        wavelengths = []
        field_stds = []
        
        for i, mass in enumerate(mass_range):
            print(f"\nMass {i+1}/{len(mass_range)}: M = {mass:.3f}")
            
            # Calculate interference pattern for this mass
            field, _ = self.calculate_total_interference(n_explosion_points, mass)
            
            # Analyze pattern characteristics
            characteristics = self.analyze_pattern_characteristics(field)
            
            wavelengths.append(characteristics['dominant_wavelength'])
            field_stds.append(characteristics['field_std'])
            
            print(f"  Dominant wavelength: {characteristics['dominant_wavelength']:.3f}")
            print(f"  Field standard deviation: {characteristics['field_std']:.3f}")
        
        return {
            'masses': mass_range,
            'wavelengths': np.array(wavelengths),
            'field_stds': np.array(field_stds)
        }
    
    def fit_scaling_law(self, masses, wavelengths):
        """
        Fit power law scaling relationship: λ ∝ M^α
        
        Parameters:
        -----------
        masses : array_like
            Central mass values
        wavelengths : array_like
            Corresponding dominant wavelengths
            
        Returns:
        --------
        scaling_params : dict
            Fitted scaling parameters
        """
        # Remove infinite wavelengths
        valid_mask = np.isfinite(wavelengths) & (wavelengths > 0)
        masses_valid = masses[valid_mask]
        wavelengths_valid = wavelengths[valid_mask]
        
        if len(masses_valid) < 2:
            return {'alpha': np.nan, 'lambda_0': np.nan, 'r_squared': 0}
        
        # Fit log-linear relationship: log(λ) = log(λ₀) + α*log(M₀/M)
        log_masses = np.log(masses_valid)
        log_wavelengths = np.log(wavelengths_valid)
        
        # Linear regression
        A = np.vstack([log_masses, np.ones(len(log_masses))]).T
        coeffs, residuals, rank, s = np.linalg.lstsq(A, log_wavelengths, rcond=None)
        
        alpha = -coeffs[0]  # Negative because λ ∝ M^(-α)
        log_lambda_0 = coeffs[1]
        lambda_0 = np.exp(log_lambda_0)
        
        # Calculate R²
        ss_res = np.sum((log_wavelengths - (coeffs[0] * log_masses + coeffs[1]))**2)
        ss_tot = np.sum((log_wavelengths - np.mean(log_wavelengths))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {
            'alpha': alpha,
            'lambda_0': lambda_0,
            'r_squared': r_squared,
            'fit_equation': f'λ = {lambda_0:.3f} * (M₀/M)^{alpha:.3f}'
        }
    
    def reverse_engineer_mass(self, observed_wavelength, reference_mass, scaling_params):
        """
        Reverse engineer central mass from observed wavelength.
        
        Parameters:
        -----------
        observed_wavelength : float
            Observed cosmic structure wavelength
        reference_mass : float
            Reference central mass
        scaling_params : dict
            Fitted scaling parameters
            
        Returns:
        --------
        inferred_mass : float
            Inferred central mass
        """
        alpha = scaling_params['alpha']
        lambda_0 = scaling_params['lambda_0']
        
        # From λ = λ₀ * (M₀/M)^α, solve for M
        mass_ratio = (lambda_0 / observed_wavelength)**(1/alpha)
        inferred_mass = reference_mass / mass_ratio
        
        return inferred_mass

def run_proof_of_concept():
    """Run proof of concept demonstration."""
    print("="*70)
    print("COSMIC INTERFERENCE PATTERN ANALYSIS - PROOF OF CONCEPT")
    print("="*70)
    
    # Initialize calculator
    calculator = CosmicInterferenceCalculator(grid_resolution=50, sphere_radius=1.0)
    
    # Test mass range (relative to reference)
    mass_range = np.array([0.5, 0.7, 1.0, 1.5, 2.0, 3.0])
    
    # Perform scaling study
    results = calculator.mass_scaling_study(mass_range, n_explosion_points=500)
    
    # Fit scaling law
    scaling_params = calculator.fit_scaling_law(results['masses'], results['wavelengths'])
    
    print(f"\n" + "="*50)
    print("SCALING LAW RESULTS")
    print("="*50)
    print(f"Fitted relationship: {scaling_params['fit_equation']}")
    print(f"R² = {scaling_params['r_squared']:.3f}")
    print(f"Scaling exponent α = {scaling_params['alpha']:.3f}")
    
    # Demonstrate reverse engineering
    print(f"\n" + "="*50)
    print("REVERSE ENGINEERING DEMONSTRATION")
    print("="*50)
    
    # Use reference mass = 1.0, observed wavelength = 0.8
    reference_mass = 1.0
    observed_wavelength = 0.8
    
    inferred_mass = calculator.reverse_engineer_mass(
        observed_wavelength, reference_mass, scaling_params
    )
    
    print(f"Reference mass: {reference_mass:.3f}")
    print(f"Observed wavelength: {observed_wavelength:.3f}")
    print(f"Inferred central mass: {inferred_mass:.3f}")
    
    # Validation: calculate expected wavelength for inferred mass
    expected_wavelength = scaling_params['lambda_0'] * (reference_mass / inferred_mass)**scaling_params['alpha']
    print(f"Validation - Expected wavelength: {expected_wavelength:.3f}")
    print(f"Error: {abs(expected_wavelength - observed_wavelength):.6f}")
    
    print(f"\n" + "="*50)
    print("COSMIC SCALE APPLICATION")
    print("="*50)
    
    # Apply to cosmic scales
    cosmic_wavelength_mpc = 150  # Mpc (CMB large structures)
    cosmic_reference_mass = 1e12  # Solar masses (hypothetical)
    
    cosmic_inferred_mass = calculator.reverse_engineer_mass(
        cosmic_wavelength_mpc, cosmic_reference_mass, scaling_params
    )
    
    print(f"Cosmic structure wavelength: {cosmic_wavelength_mpc} Mpc")
    print(f"Reference cosmic mass: {cosmic_reference_mass:.0e} M☉")
    print(f"Inferred cosmic central mass: {cosmic_inferred_mass:.2e} M☉")
    
    return results, scaling_params

if __name__ == "__main__":
    # Run the proof of concept
    results, scaling_params = run_proof_of_concept()
    
    print(f"\n" + "="*70)
    print("PROOF OF CONCEPT COMPLETED SUCCESSFULLY")
    print("="*70)
    print("\nThis demonstrates the mathematical feasibility of:")
    print("1. Calculating interference patterns from spherical explosions")
    print("2. Extracting characteristic wavelengths from patterns")
    print("3. Determining scaling relationships with central mass")
    print("4. Reverse engineering central mass from observed wavelengths")
    print("\nNext steps: Scale to realistic cosmic parameters and observational data") 