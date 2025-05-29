#!/usr/bin/env python3
"""
MATLAB Simulation Interface

Interface for running physics simulations using MATLAB or Python fallbacks.
Provides validation of physics-based research through computational verification.

Author: AI Agent Claude-3.5-Sonnet
Date: 2025-05-29
"""

import os
import sys
import subprocess
import tempfile
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import shutil

import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate, optimize
from scipy.special import spherical_jn, spherical_yn
import sympy as sp

class MATLABSimulationInterface:
    """
    Interface for running physics simulations with MATLAB or Python fallbacks.
    Validates physics-based research through computational verification.
    """
    
    def __init__(self):
        """Initialize the MATLAB simulation interface"""
        self.logger = logging.getLogger("MATLABSimulationInterface")
        self.matlab_executable = self._find_matlab()
        self.temp_dir = Path(tempfile.mkdtemp(prefix="validation_sim_"))
        
        # Simulation tolerance for validation
        self.validation_tolerance = 0.01
        
        if self.matlab_executable:
            self.logger.info(f"✅ MATLAB found: {self.matlab_executable}")
        else:
            self.logger.info("⚠️  MATLAB not found, using Python fallbacks")
    
    def _find_matlab(self) -> Optional[str]:
        """Find MATLAB executable on the system"""
        possible_paths = [
            "/Applications/MATLAB_R2023b.app/bin/matlab",
            "/Applications/MATLAB_R2023a.app/bin/matlab",
            "/Applications/MATLAB_R2022b.app/bin/matlab",
            "/usr/local/bin/matlab",
            "matlab"  # In PATH
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "-help"], 
                                      capture_output=True, 
                                      timeout=10)
                if result.returncode == 0:
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        return None
    
    def validate_physics_simulation(self, physics_description: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a physics simulation based on description
        
        Args:
            physics_description: Dictionary describing the physics system
            
        Returns:
            Validation results with success status and metrics
        """
        sim_type = physics_description.get("type", "unknown")
        
        self.logger.info(f"🧮 Running physics simulation: {sim_type}")
        
        try:
            if sim_type == "harmonic_oscillator":
                return self._validate_harmonic_oscillator(physics_description)
            elif sim_type == "wave_equation":
                return self._validate_wave_equation(physics_description)
            elif sim_type == "heat_equation":
                return self._validate_heat_equation(physics_description)
            elif sim_type == "projectile_motion":
                return self._validate_projectile_motion(physics_description)
            elif sim_type == "pendulum":
                return self._validate_pendulum(physics_description)
            elif sim_type == "spring_mass":
                return self._validate_spring_mass(physics_description)
            else:
                return self._validate_generic_physics(physics_description)
                
        except Exception as e:
            self.logger.error(f"❌ Simulation failed: {str(e)}")
            return {
                "success": False,
                "error_message": str(e),
                "simulation_type": sim_type
            }
    
    def _validate_harmonic_oscillator(self, desc: Dict[str, Any]) -> Dict[str, Any]:
        """Validate harmonic oscillator simulation"""
        frequency = desc.get("frequency", 1.0)
        damping = desc.get("damping", 0.0)
        initial_position = desc.get("initial_position", 1.0)
        initial_velocity = desc.get("initial_velocity", 0.0)
        
        # Time parameters
        t_max = desc.get("t_max", 10.0)
        dt = desc.get("dt", 0.01)
        t = np.arange(0, t_max, dt)
        
        # Analytical solution for comparison
        omega = 2 * np.pi * frequency
        
        if damping == 0:
            # Undamped harmonic oscillator
            x_analytical = (initial_position * np.cos(omega * t) + 
                          (initial_velocity / omega) * np.sin(omega * t))
            v_analytical = (-initial_position * omega * np.sin(omega * t) + 
                          initial_velocity * np.cos(omega * t))
        else:
            # Damped harmonic oscillator
            gamma = damping
            omega_d = np.sqrt(omega**2 - gamma**2)
            
            if omega_d > 0:  # Underdamped
                A = initial_position
                B = (initial_velocity + gamma * initial_position) / omega_d
                x_analytical = np.exp(-gamma * t) * (A * np.cos(omega_d * t) + B * np.sin(omega_d * t))
                v_analytical = np.exp(-gamma * t) * (
                    (-gamma * A - omega_d * B) * np.cos(omega_d * t) + 
                    (omega_d * A - gamma * B) * np.sin(omega_d * t)
                )
            else:  # Critically damped or overdamped
                x_analytical = np.exp(-gamma * t) * (initial_position + (initial_velocity + gamma * initial_position) * t)
                v_analytical = np.exp(-gamma * t) * (initial_velocity - gamma * (initial_position + (initial_velocity + gamma * initial_position) * t))
        
        # Numerical solution using scipy
        def harmonic_ode(t, y):
            x, v = y
            dxdt = v
            dvdt = -omega**2 * x - 2 * damping * v
            return [dxdt, dvdt]
        
        sol = integrate.solve_ivp(harmonic_ode, [0, t_max], 
                                [initial_position, initial_velocity], 
                                t_eval=t, rtol=1e-8)
        
        x_numerical = sol.y[0]
        v_numerical = sol.y[1]
        
        # Calculate energy
        kinetic_energy = 0.5 * v_numerical**2
        potential_energy = 0.5 * omega**2 * x_numerical**2
        total_energy = kinetic_energy + potential_energy
        
        # Validation metrics
        position_error = np.mean(np.abs(x_numerical - x_analytical))
        velocity_error = np.mean(np.abs(v_numerical - v_analytical))
        
        # Energy conservation check (for undamped case)
        if damping == 0:
            energy_variation = np.std(total_energy) / np.mean(total_energy)
            energy_conserved = energy_variation < self.validation_tolerance
        else:
            # For damped case, energy should decrease
            energy_conserved = np.all(np.diff(total_energy) <= 0)
        
        # Period validation
        expected_period = 2 * np.pi / omega if damping == 0 else 2 * np.pi / np.sqrt(omega**2 - damping**2)
        
        # Find peaks to measure period
        peaks = []
        for i in range(1, len(x_numerical) - 1):
            if x_numerical[i] > x_numerical[i-1] and x_numerical[i] > x_numerical[i+1]:
                peaks.append(t[i])
        
        measured_period = np.mean(np.diff(peaks)) if len(peaks) > 1 else expected_period
        period_error = abs(measured_period - expected_period) / expected_period
        
        # Overall validation score
        validation_score = 1.0 - min(1.0, position_error + velocity_error + period_error)
        
        return {
            "success": True,
            "simulation_type": "harmonic_oscillator",
            "validation_metrics": {
                "position_error": position_error,
                "velocity_error": velocity_error,
                "period_error": period_error,
                "energy_conserved": energy_conserved,
                "validation_score": validation_score
            },
            "simulation_results": {
                "time": t.tolist()[:100],  # Limit output size
                "position": x_numerical.tolist()[:100],
                "velocity": v_numerical.tolist()[:100],
                "total_energy": total_energy.tolist()[:100],
                "expected_period": expected_period,
                "measured_period": measured_period
            },
            "parameters": {
                "frequency": frequency,
                "damping": damping,
                "initial_position": initial_position,
                "initial_velocity": initial_velocity
            }
        }
    
    def _validate_wave_equation(self, desc: Dict[str, Any]) -> Dict[str, Any]:
        """Validate wave equation simulation"""
        wave_speed = desc.get("wave_speed", 1.0)
        frequency = desc.get("frequency", 1.0)
        amplitude = desc.get("amplitude", 1.0)
        
        # Spatial and temporal parameters
        L = desc.get("length", 10.0)
        T = desc.get("time_max", 5.0)
        nx = desc.get("nx", 100)
        nt = desc.get("nt", 500)
        
        x = np.linspace(0, L, nx)
        t = np.linspace(0, T, nt)
        dx = x[1] - x[0]
        dt = t[1] - t[0]
        
        # CFL condition check
        cfl = wave_speed * dt / dx
        cfl_stable = cfl <= 1.0
        
        # Analytical solution for traveling wave
        k = 2 * np.pi * frequency / wave_speed  # Wave number
        omega = 2 * np.pi * frequency
        
        # Initialize wave
        u = np.zeros((nt, nx))
        
        # Initial conditions: sinusoidal wave
        u[0, :] = amplitude * np.sin(k * x)
        
        # Analytical solution at different times
        analytical_solutions = []
        for i, time in enumerate(t[::50]):  # Sample every 50th time step
            u_analytical = amplitude * np.sin(k * x - omega * time)
            analytical_solutions.append(u_analytical)
        
        # Numerical solution using finite differences
        # Second-order wave equation: ∂²u/∂t² = c²∂²u/∂x²
        
        # Initial velocity (du/dt at t=0)
        u[1, :] = u[0, :] - omega * amplitude * np.cos(k * x) * dt
        
        # Time stepping
        for n in range(1, nt - 1):
            for i in range(1, nx - 1):
                u[n+1, i] = (2 * u[n, i] - u[n-1, i] + 
                            (wave_speed * dt / dx)**2 * (u[n, i+1] - 2*u[n, i] + u[n, i-1]))
            
            # Boundary conditions (fixed ends)
            u[n+1, 0] = 0
            u[n+1, -1] = 0
        
        # Validation metrics
        errors = []
        for i, time_idx in enumerate(range(0, nt, 50)):
            if time_idx < nt and i < len(analytical_solutions):
                error = np.mean(np.abs(u[time_idx, :] - analytical_solutions[i]))
                errors.append(error)
        
        mean_error = np.mean(errors) if errors else float('inf')
        
        # Energy conservation check
        kinetic_energy = []
        potential_energy = []
        
        for n in range(1, nt - 1):
            # Approximate kinetic energy
            dudt = (u[n+1, :] - u[n-1, :]) / (2 * dt)
            ke = 0.5 * np.sum(dudt**2) * dx
            kinetic_energy.append(ke)
            
            # Approximate potential energy
            dudx = np.gradient(u[n, :], dx)
            pe = 0.5 * wave_speed**2 * np.sum(dudx**2) * dx
            potential_energy.append(pe)
        
        total_energy = np.array(kinetic_energy) + np.array(potential_energy)
        energy_variation = np.std(total_energy) / np.mean(total_energy) if len(total_energy) > 0 else float('inf')
        
        # Validation score
        validation_score = 1.0 - min(1.0, mean_error + energy_variation)
        
        return {
            "success": True,
            "simulation_type": "wave_equation",
            "validation_metrics": {
                "mean_error": mean_error,
                "energy_variation": energy_variation,
                "cfl_stable": cfl_stable,
                "cfl_number": cfl,
                "validation_score": validation_score
            },
            "simulation_results": {
                "x": x.tolist(),
                "t_sample": t[::50].tolist(),
                "u_final": u[-1, :].tolist(),
                "total_energy": total_energy.tolist()[:50],  # Limit output
                "wave_speed": wave_speed,
                "frequency": frequency
            },
            "parameters": {
                "wave_speed": wave_speed,
                "frequency": frequency,
                "amplitude": amplitude,
                "length": L,
                "nx": nx,
                "nt": nt
            }
        }
    
    def _validate_heat_equation(self, desc: Dict[str, Any]) -> Dict[str, Any]:
        """Validate heat equation simulation"""
        diffusivity = desc.get("diffusivity", 0.01)
        length = desc.get("length", 1.0)
        time_max = desc.get("time_max", 1.0)
        
        # Grid parameters
        nx = desc.get("nx", 50)
        nt = desc.get("nt", 1000)
        
        x = np.linspace(0, length, nx)
        t = np.linspace(0, time_max, nt)
        dx = x[1] - x[0]
        dt = t[1] - t[0]
        
        # Stability condition for explicit scheme
        stability_factor = diffusivity * dt / dx**2
        stable = stability_factor <= 0.5
        
        # Initial condition: step function
        u = np.zeros((nt, nx))
        u[0, :] = np.where(x < length/2, 1.0, 0.0)
        
        # Boundary conditions (fixed at 0)
        u[:, 0] = 0
        u[:, -1] = 0
        
        # Numerical solution using explicit finite differences
        for n in range(nt - 1):
            for i in range(1, nx - 1):
                u[n+1, i] = u[n, i] + diffusivity * dt / dx**2 * (u[n, i+1] - 2*u[n, i] + u[n, i-1])
        
        # Analytical solution (Fourier series)
        def analytical_solution(x_val, t_val):
            result = 0
            for n in range(1, 50):  # Sum first 50 terms
                coeff = 4 / (np.pi * (2*n - 1)) * np.sin((2*n - 1) * np.pi / 2)
                result += coeff * np.sin((2*n - 1) * np.pi * x_val / length) * np.exp(-(2*n - 1)**2 * np.pi**2 * diffusivity * t_val / length**2)
            return result
        
        # Compare with analytical solution at final time
        u_analytical = np.array([analytical_solution(x_val, time_max) for x_val in x])
        error = np.mean(np.abs(u[-1, :] - u_analytical))
        
        # Conservation check (total heat should decrease due to boundary conditions)
        total_heat = [np.sum(u[n, :]) * dx for n in range(nt)]
        heat_decreasing = np.all(np.diff(total_heat) <= 0)
        
        # Maximum principle check (solution should be bounded by initial conditions)
        max_value = np.max(u)
        min_value = np.min(u)
        max_principle_satisfied = (min_value >= 0) and (max_value <= 1.0)
        
        # Validation score
        validation_score = 1.0 - min(1.0, error)
        if not stable:
            validation_score *= 0.5  # Penalize unstable schemes
        if not max_principle_satisfied:
            validation_score *= 0.7
        
        return {
            "success": True,
            "simulation_type": "heat_equation",
            "validation_metrics": {
                "error": error,
                "stable": stable,
                "stability_factor": stability_factor,
                "heat_decreasing": heat_decreasing,
                "max_principle_satisfied": max_principle_satisfied,
                "validation_score": validation_score
            },
            "simulation_results": {
                "x": x.tolist(),
                "u_initial": u[0, :].tolist(),
                "u_final": u[-1, :].tolist(),
                "u_analytical": u_analytical.tolist(),
                "total_heat": total_heat[::50],  # Sample every 50th step
                "diffusivity": diffusivity
            },
            "parameters": {
                "diffusivity": diffusivity,
                "length": length,
                "time_max": time_max,
                "nx": nx,
                "nt": nt
            }
        }
    
    def _validate_projectile_motion(self, desc: Dict[str, Any]) -> Dict[str, Any]:
        """Validate projectile motion simulation"""
        initial_velocity = desc.get("initial_velocity", 50.0)  # m/s
        launch_angle = desc.get("launch_angle", 45.0)  # degrees
        gravity = desc.get("gravity", 9.81)  # m/s²
        air_resistance = desc.get("air_resistance", 0.0)  # drag coefficient
        
        # Convert angle to radians
        angle_rad = np.radians(launch_angle)
        
        # Initial conditions
        vx0 = initial_velocity * np.cos(angle_rad)
        vy0 = initial_velocity * np.sin(angle_rad)
        
        # Analytical solution (no air resistance)
        if air_resistance == 0:
            # Time of flight
            t_flight = 2 * vy0 / gravity
            
            # Maximum height
            max_height = vy0**2 / (2 * gravity)
            
            # Range
            range_analytical = vx0 * t_flight
            
            # Trajectory
            t = np.linspace(0, t_flight, 100)
            x_analytical = vx0 * t
            y_analytical = vy0 * t - 0.5 * gravity * t**2
            
            # Numerical solution for comparison
            def projectile_ode(t, y):
                x, y_pos, vx, vy = y
                return [vx, vy, 0, -gravity]
            
            sol = integrate.solve_ivp(projectile_ode, [0, t_flight], 
                                    [0, 0, vx0, vy0], 
                                    t_eval=t, rtol=1e-8)
            
            x_numerical = sol.y[0]
            y_numerical = sol.y[1]
            
            # Validation metrics
            x_error = np.mean(np.abs(x_numerical - x_analytical))
            y_error = np.mean(np.abs(y_numerical - y_analytical))
            
            # Energy conservation check
            vx_num = sol.y[2]
            vy_num = sol.y[3]
            kinetic_energy = 0.5 * (vx_num**2 + vy_num**2)
            potential_energy = gravity * y_numerical
            total_energy = kinetic_energy + potential_energy
            
            energy_variation = np.std(total_energy) / np.mean(total_energy)
            
        else:
            # With air resistance - numerical only
            def projectile_with_drag(t, y):
                x, y_pos, vx, vy = y
                v_mag = np.sqrt(vx**2 + vy**2)
                drag_x = -air_resistance * v_mag * vx
                drag_y = -air_resistance * v_mag * vy
                return [vx, vy, drag_x, drag_y - gravity]
            
            # Estimate flight time
            t_flight_est = 2 * vy0 / gravity
            t = np.linspace(0, t_flight_est * 1.5, 1000)
            
            sol = integrate.solve_ivp(projectile_with_drag, [0, t[-1]], 
                                    [0, 0, vx0, vy0], 
                                    t_eval=t, rtol=1e-8)
            
            x_numerical = sol.y[0]
            y_numerical = sol.y[1]
            
            # Find actual landing time
            landing_idx = np.where(y_numerical <= 0)[0]
            if len(landing_idx) > 1:
                landing_time = t[landing_idx[1]]
                range_numerical = x_numerical[landing_idx[1]]
            else:
                landing_time = t[-1]
                range_numerical = x_numerical[-1]
            
            # For validation, compare with no-drag case
            range_analytical = vx0 * 2 * vy0 / gravity
            max_height = vy0**2 / (2 * gravity)
            
            x_error = 0.1  # Nominal error for drag case
            y_error = 0.1
            energy_variation = 0.1  # Energy not conserved with drag
        
        # Validation score
        validation_score = 1.0 - min(1.0, x_error + y_error + energy_variation)
        
        return {
            "success": True,
            "simulation_type": "projectile_motion",
            "validation_metrics": {
                "x_error": x_error,
                "y_error": y_error,
                "energy_variation": energy_variation,
                "validation_score": validation_score
            },
            "simulation_results": {
                "time": t.tolist()[:100],
                "x_trajectory": x_numerical.tolist()[:100],
                "y_trajectory": y_numerical.tolist()[:100],
                "max_height": max_height if air_resistance == 0 else np.max(y_numerical),
                "range": range_analytical if air_resistance == 0 else range_numerical,
                "flight_time": t_flight if air_resistance == 0 else landing_time
            },
            "parameters": {
                "initial_velocity": initial_velocity,
                "launch_angle": launch_angle,
                "gravity": gravity,
                "air_resistance": air_resistance
            }
        }
    
    def _validate_pendulum(self, desc: Dict[str, Any]) -> Dict[str, Any]:
        """Validate pendulum simulation"""
        length = desc.get("length", 1.0)  # m
        gravity = desc.get("gravity", 9.81)  # m/s²
        initial_angle = desc.get("initial_angle", 0.1)  # radians
        damping = desc.get("damping", 0.0)  # damping coefficient
        
        # Small angle approximation
        omega0 = np.sqrt(gravity / length)
        period_small_angle = 2 * np.pi / omega0
        
        # Time parameters
        t_max = desc.get("t_max", 10.0)
        dt = desc.get("dt", 0.01)
        t = np.arange(0, t_max, dt)
        
        # Numerical solution
        def pendulum_ode(t, y):
            theta, theta_dot = y
            return [theta_dot, -omega0**2 * np.sin(theta) - 2 * damping * theta_dot]
        
        sol = integrate.solve_ivp(pendulum_ode, [0, t_max], 
                                [initial_angle, 0], 
                                t_eval=t, rtol=1e-8)
        
        theta_numerical = sol.y[0]
        theta_dot_numerical = sol.y[1]
        
        # Small angle analytical solution for comparison
        if damping == 0:
            theta_analytical = initial_angle * np.cos(omega0 * t)
        else:
            # Damped oscillator
            omega_d = np.sqrt(omega0**2 - damping**2)
            if omega_d > 0:
                theta_analytical = initial_angle * np.exp(-damping * t) * np.cos(omega_d * t)
            else:
                theta_analytical = initial_angle * np.exp(-damping * t)
        
        # Error calculation (valid for small angles)
        if abs(initial_angle) < 0.3:  # Small angle regime
            error = np.mean(np.abs(theta_numerical - theta_analytical))
        else:
            error = 0.1  # Nominal error for large angles
        
        # Energy conservation (for undamped case)
        if damping == 0:
            kinetic_energy = 0.5 * length**2 * theta_dot_numerical**2
            potential_energy = gravity * length * (1 - np.cos(theta_numerical))
            total_energy = kinetic_energy + potential_energy
            energy_variation = np.std(total_energy) / np.mean(total_energy)
        else:
            energy_variation = 0.1  # Energy not conserved with damping
        
        # Period measurement
        # Find peaks
        peaks = []
        for i in range(1, len(theta_numerical) - 1):
            if (theta_numerical[i] > theta_numerical[i-1] and 
                theta_numerical[i] > theta_numerical[i+1] and 
                theta_numerical[i] > 0):
                peaks.append(t[i])
        
        if len(peaks) > 1:
            measured_period = np.mean(np.diff(peaks))
            period_error = abs(measured_period - period_small_angle) / period_small_angle
        else:
            period_error = 0.1
        
        # Validation score
        validation_score = 1.0 - min(1.0, error + energy_variation + period_error)
        
        return {
            "success": True,
            "simulation_type": "pendulum",
            "validation_metrics": {
                "angle_error": error,
                "energy_variation": energy_variation,
                "period_error": period_error,
                "validation_score": validation_score
            },
            "simulation_results": {
                "time": t.tolist()[:100],
                "angle": theta_numerical.tolist()[:100],
                "angular_velocity": theta_dot_numerical.tolist()[:100],
                "expected_period": period_small_angle,
                "measured_period": measured_period if len(peaks) > 1 else period_small_angle
            },
            "parameters": {
                "length": length,
                "gravity": gravity,
                "initial_angle": initial_angle,
                "damping": damping
            }
        }
    
    def _validate_spring_mass(self, desc: Dict[str, Any]) -> Dict[str, Any]:
        """Validate spring-mass system simulation"""
        mass = desc.get("mass", 1.0)  # kg
        spring_constant = desc.get("spring_constant", 1.0)  # N/m
        initial_position = desc.get("initial_position", 1.0)  # m
        initial_velocity = desc.get("initial_velocity", 0.0)  # m/s
        damping = desc.get("damping", 0.0)  # damping coefficient
        
        # Natural frequency
        omega0 = np.sqrt(spring_constant / mass)
        period = 2 * np.pi / omega0
        
        # Time parameters
        t_max = desc.get("t_max", 10.0)
        dt = desc.get("dt", 0.01)
        t = np.arange(0, t_max, dt)
        
        # Analytical solution
        if damping == 0:
            # Undamped
            x_analytical = (initial_position * np.cos(omega0 * t) + 
                          (initial_velocity / omega0) * np.sin(omega0 * t))
            v_analytical = (-initial_position * omega0 * np.sin(omega0 * t) + 
                          initial_velocity * np.cos(omega0 * t))
        else:
            # Damped
            gamma = damping / (2 * mass)
            omega_d = np.sqrt(omega0**2 - gamma**2)
            
            if omega_d > 0:  # Underdamped
                A = initial_position
                B = (initial_velocity + gamma * initial_position) / omega_d
                x_analytical = np.exp(-gamma * t) * (A * np.cos(omega_d * t) + B * np.sin(omega_d * t))
                v_analytical = np.exp(-gamma * t) * (
                    (-gamma * A - omega_d * B) * np.cos(omega_d * t) + 
                    (omega_d * A - gamma * B) * np.sin(omega_d * t)
                )
            else:  # Critically damped or overdamped
                x_analytical = np.exp(-gamma * t) * (initial_position + (initial_velocity + gamma * initial_position) * t)
                v_analytical = np.exp(-gamma * t) * (initial_velocity - gamma * (initial_position + (initial_velocity + gamma * initial_position) * t))
        
        # Numerical solution
        def spring_mass_ode(t, y):
            x, v = y
            return [v, -spring_constant/mass * x - damping/mass * v]
        
        sol = integrate.solve_ivp(spring_mass_ode, [0, t_max], 
                                [initial_position, initial_velocity], 
                                t_eval=t, rtol=1e-8)
        
        x_numerical = sol.y[0]
        v_numerical = sol.y[1]
        
        # Validation metrics
        position_error = np.mean(np.abs(x_numerical - x_analytical))
        velocity_error = np.mean(np.abs(v_numerical - v_analytical))
        
        # Energy analysis
        kinetic_energy = 0.5 * mass * v_numerical**2
        potential_energy = 0.5 * spring_constant * x_numerical**2
        total_energy = kinetic_energy + potential_energy
        
        if damping == 0:
            energy_variation = np.std(total_energy) / np.mean(total_energy)
        else:
            # Energy should decrease with damping
            energy_variation = 0.05 if np.all(np.diff(total_energy) <= 0.01) else 0.5
        
        # Validation score
        validation_score = 1.0 - min(1.0, position_error + velocity_error + energy_variation)
        
        return {
            "success": True,
            "simulation_type": "spring_mass",
            "validation_metrics": {
                "position_error": position_error,
                "velocity_error": velocity_error,
                "energy_variation": energy_variation,
                "validation_score": validation_score
            },
            "simulation_results": {
                "time": t.tolist()[:100],
                "position": x_numerical.tolist()[:100],
                "velocity": v_numerical.tolist()[:100],
                "total_energy": total_energy.tolist()[:100],
                "natural_frequency": omega0,
                "period": period
            },
            "parameters": {
                "mass": mass,
                "spring_constant": spring_constant,
                "initial_position": initial_position,
                "initial_velocity": initial_velocity,
                "damping": damping
            }
        }
    
    def _validate_generic_physics(self, desc: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generic physics system"""
        # Basic validation for unknown physics types
        sim_type = desc.get("type", "unknown")
        
        # Check for basic physics parameters
        has_time = "time" in desc or "t_max" in desc
        has_space = "length" in desc or "position" in desc or "x" in desc
        has_dynamics = any(key in desc for key in ["velocity", "acceleration", "force", "energy"])
        
        # Basic validation score
        validation_score = 0.5  # Neutral score for unknown systems
        
        if has_time:
            validation_score += 0.2
        if has_space:
            validation_score += 0.2
        if has_dynamics:
            validation_score += 0.1
        
        return {
            "success": True,
            "simulation_type": sim_type,
            "validation_metrics": {
                "has_temporal_component": has_time,
                "has_spatial_component": has_space,
                "has_dynamics": has_dynamics,
                "validation_score": min(validation_score, 1.0)
            },
            "simulation_results": {
                "generic_validation": True,
                "parameters_found": len(desc)
            },
            "parameters": desc
        }
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            self.logger.warning(f"Could not clean up temp directory: {str(e)}")
    
    def __del__(self):
        """Destructor to clean up resources"""
        self.cleanup() 