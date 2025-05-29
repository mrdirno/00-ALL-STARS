#!/usr/bin/env python3
"""
MATLAB Simulation Interface for Scientific Validation

Provides physics simulation capabilities with automatic fallback to Python
when MATLAB is not available.
"""

import os
import sys
import subprocess
import numpy as np
from scipy import integrate, optimize
import matplotlib.pyplot as plt
from pathlib import Path
import logging

class MATLABSimulationInterface:
    """
    Interface for running physics simulations with MATLAB or Python fallbacks
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.matlab_executable = self.find_matlab()
        self.matlab_available = self.matlab_executable is not None
        
        if self.matlab_available:
            self.logger.info("MATLAB detected - using enhanced simulations")
        else:
            self.logger.info("MATLAB not found - using Python fallbacks")
            
    def find_matlab(self):
        """Find MATLAB executable on system"""
        possible_paths = [
            "/Applications/MATLAB_R2023b.app/bin/matlab",
            "/usr/local/bin/matlab",
            "matlab"  # In PATH
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "-batch", "exit"], 
                                      capture_output=True, timeout=10)
                if result.returncode == 0:
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
                
        return None
        
    def run_harmonic_oscillator_simulation(self, params=None):
        """
        Run harmonic oscillator simulation
        """
        if params is None:
            params = {"m": 1.0, "k": 1.0, "x0": 1.0, "v0": 0.0, "t_max": 10.0}
            
        if self.matlab_available:
            return self.matlab_harmonic_oscillator(params)
        else:
            return self.python_harmonic_oscillator(params)
            
    def matlab_harmonic_oscillator(self, params):
        """Run harmonic oscillator in MATLAB"""
        try:
            # Create MATLAB script
            matlab_script = f"""
            % Harmonic Oscillator Simulation
            m = {params['m']};
            k = {params['k']};
            x0 = {params['x0']};
            v0 = {params['v0']};
            t_max = {params['t_max']};
            
            omega = sqrt(k/m);
            t = linspace(0, t_max, 1000);
            
            % Analytical solution
            x = x0 * cos(omega * t) + (v0/omega) * sin(omega * t);
            v = -x0 * omega * sin(omega * t) + v0 * cos(omega * t);
            
            % Energy calculation
            KE = 0.5 * m * v.^2;
            PE = 0.5 * k * x.^2;
            E_total = KE + PE;
            
            % Energy conservation check
            E_mean = mean(E_total);
            E_std = std(E_total);
            energy_variation = E_std / E_mean;
            
            % Save results
            save('harmonic_results.mat', 't', 'x', 'v', 'E_total', 'energy_variation');
            
            fprintf('Energy variation: %.6f\\n', energy_variation);
            fprintf('Period: %.6f\\n', 2*pi/omega);
            """
            
            # Write and execute MATLAB script
            with open('harmonic_sim.m', 'w') as f:
                f.write(matlab_script)
                
            result = subprocess.run([self.matlab_executable, "-batch", "harmonic_sim"],
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Parse MATLAB output
                output_lines = result.stdout.split('\n')
                energy_variation = None
                period = None
                
                for line in output_lines:
                    if "Energy variation:" in line:
                        energy_variation = float(line.split(':')[1].strip())
                    elif "Period:" in line:
                        period = float(line.split(':')[1].strip())
                        
                return {
                    "success": True,
                    "energy_variation": energy_variation,
                    "period": period,
                    "energy_conserved": energy_variation < 0.01 if energy_variation else False,
                    "method": "MATLAB"
                }
            else:
                self.logger.warning(f"MATLAB simulation failed: {result.stderr}")
                return self.python_harmonic_oscillator(params)
                
        except Exception as e:
            self.logger.warning(f"MATLAB simulation error: {str(e)}")
            return self.python_harmonic_oscillator(params)
        finally:
            # Cleanup
            for file in ['harmonic_sim.m', 'harmonic_results.mat']:
                if os.path.exists(file):
                    os.remove(file)
                    
    def python_harmonic_oscillator(self, params):
        """Run harmonic oscillator in Python"""
        try:
            m = params['m']
            k = params['k'] 
            x0 = params['x0']
            v0 = params['v0']
            t_max = params['t_max']
            
            omega = np.sqrt(k/m)
            t = np.linspace(0, t_max, 1000)
            
            # Analytical solution
            x = x0 * np.cos(omega * t) + (v0/omega) * np.sin(omega * t)
            v = -x0 * omega * np.sin(omega * t) + v0 * np.cos(omega * t)
            
            # Energy calculation
            KE = 0.5 * m * v**2
            PE = 0.5 * k * x**2
            E_total = KE + PE
            
            # Energy conservation check
            E_mean = np.mean(E_total)
            E_std = np.std(E_total)
            energy_variation = E_std / E_mean if E_mean > 0 else float('inf')
            
            period = 2 * np.pi / omega
            
            return {
                "success": True,
                "energy_variation": energy_variation,
                "period": period,
                "energy_conserved": energy_variation < 0.01,
                "method": "Python",
                "time": t.tolist(),
                "position": x.tolist(),
                "velocity": v.tolist(),
                "energy": E_total.tolist()
            }
            
        except Exception as e:
            self.logger.error(f"Python simulation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "method": "Python"
            }
            
    def run_wave_equation_simulation(self, params=None):
        """
        Run wave equation simulation
        """
        if params is None:
            params = {"c": 1.0, "L": 1.0, "n_modes": 5, "t_max": 5.0}
            
        if self.matlab_available:
            return self.matlab_wave_equation(params)
        else:
            return self.python_wave_equation(params)
            
    def python_wave_equation(self, params):
        """Solve wave equation in Python"""
        try:
            c = params['c']  # wave speed
            L = params['L']  # domain length
            n_modes = params['n_modes']
            t_max = params['t_max']
            
            # Spatial and temporal grids
            x = np.linspace(0, L, 100)
            t = np.linspace(0, t_max, 200)
            
            # Wave solution (standing wave modes)
            u = np.zeros((len(t), len(x)))
            
            for n in range(1, n_modes + 1):
                k_n = n * np.pi / L
                omega_n = c * k_n
                
                # Mode amplitude (example)
                A_n = 1.0 / n**2
                
                for i, t_val in enumerate(t):
                    u[i, :] += A_n * np.sin(k_n * x) * np.cos(omega_n * t_val)
                    
            # Energy calculation
            energy = np.zeros(len(t))
            for i in range(len(t)):
                # Kinetic + potential energy density integrated
                if i > 0:
                    dudt = (u[i, :] - u[i-1, :]) / (t[1] - t[0])
                    dudx = np.gradient(u[i, :], x)
                    energy[i] = 0.5 * np.trapz(dudt**2 + c**2 * dudx**2, x)
                    
            # Energy conservation check
            if len(energy) > 1:
                energy_variation = np.std(energy[1:]) / np.mean(energy[1:])
            else:
                energy_variation = 0.0
                
            return {
                "success": True,
                "energy_variation": energy_variation,
                "energy_conserved": energy_variation < 0.1,
                "method": "Python",
                "wave_data": u.tolist(),
                "energy": energy.tolist()
            }
            
        except Exception as e:
            self.logger.error(f"Wave equation simulation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "method": "Python"
            }
            
    def matlab_wave_equation(self, params):
        """Run wave equation in MATLAB"""
        try:
            matlab_script = f"""
            % Wave Equation Simulation
            c = {params['c']};
            L = {params['L']};
            n_modes = {params['n_modes']};
            t_max = {params['t_max']};
            
            x = linspace(0, L, 100);
            t = linspace(0, t_max, 200);
            
            u = zeros(length(t), length(x));
            
            for n = 1:n_modes
                k_n = n * pi / L;
                omega_n = c * k_n;
                A_n = 1.0 / n^2;
                
                for i = 1:length(t)
                    u(i, :) = u(i, :) + A_n * sin(k_n * x) * cos(omega_n * t(i));
                end
            end
            
            % Energy calculation
            energy = zeros(size(t));
            for i = 2:length(t)
                dudt = (u(i, :) - u(i-1, :)) / (t(2) - t(1));
                dudx = gradient(u(i, :), x);
                energy(i) = 0.5 * trapz(x, dudt.^2 + c^2 * dudx.^2);
            end
            
            energy_variation = std(energy(2:end)) / mean(energy(2:end));
            
            fprintf('Wave energy variation: %.6f\\n', energy_variation);
            """
            
            with open('wave_sim.m', 'w') as f:
                f.write(matlab_script)
                
            result = subprocess.run([self.matlab_executable, "-batch", "wave_sim"],
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Parse output
                energy_variation = None
                for line in result.stdout.split('\n'):
                    if "Wave energy variation:" in line:
                        energy_variation = float(line.split(':')[1].strip())
                        
                return {
                    "success": True,
                    "energy_variation": energy_variation,
                    "energy_conserved": energy_variation < 0.1 if energy_variation else False,
                    "method": "MATLAB"
                }
            else:
                return self.python_wave_equation(params)
                
        except Exception as e:
            self.logger.warning(f"MATLAB wave simulation error: {str(e)}")
            return self.python_wave_equation(params)
        finally:
            if os.path.exists('wave_sim.m'):
                os.remove('wave_sim.m')
                
    def run_heat_equation_simulation(self, params=None):
        """
        Run heat equation simulation
        """
        if params is None:
            params = {"alpha": 1.0, "L": 1.0, "T0": 100.0, "t_max": 1.0}
            
        return self.python_heat_equation(params)
        
    def python_heat_equation(self, params):
        """Solve heat equation in Python"""
        try:
            alpha = params['alpha']  # thermal diffusivity
            L = params['L']  # domain length
            T0 = params['T0']  # initial temperature
            t_max = params['t_max']
            
            # Spatial grid
            nx = 50
            x = np.linspace(0, L, nx)
            dx = x[1] - x[0]
            
            # Time grid
            dt = 0.001
            nt = int(t_max / dt)
            
            # Initial condition
            T = np.zeros((nt, nx))
            T[0, :] = T0 * np.sin(np.pi * x / L)  # Initial temperature profile
            
            # Finite difference solution
            r = alpha * dt / dx**2
            
            for n in range(nt - 1):
                for i in range(1, nx - 1):
                    T[n+1, i] = T[n, i] + r * (T[n, i+1] - 2*T[n, i] + T[n, i-1])
                    
                # Boundary conditions (T = 0 at ends)
                T[n+1, 0] = 0
                T[n+1, -1] = 0
                
            # Check for stability and physical behavior
            max_temp = np.max(T)
            min_temp = np.min(T)
            
            # Temperature should decrease over time (second law)
            initial_energy = np.trapz(T[0, :], x)
            final_energy = np.trapz(T[-1, :], x)
            
            energy_decrease = (initial_energy - final_energy) / initial_energy
            
            return {
                "success": True,
                "max_temperature": max_temp,
                "min_temperature": min_temp,
                "energy_decrease": energy_decrease,
                "physically_consistent": energy_decrease > 0 and min_temp >= 0,
                "method": "Python",
                "temperature_data": T.tolist()
            }
            
        except Exception as e:
            self.logger.error(f"Heat equation simulation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "method": "Python"
            }
            
    def validate_physics_simulation(self, simulation_type, params=None):
        """
        Validate physics simulation results
        """
        simulation_methods = {
            "harmonic_oscillator": self.run_harmonic_oscillator_simulation,
            "wave_equation": self.run_wave_equation_simulation,
            "heat_equation": self.run_heat_equation_simulation
        }
        
        if simulation_type not in simulation_methods:
            return {
                "success": False,
                "error": f"Unknown simulation type: {simulation_type}"
            }
            
        try:
            result = simulation_methods[simulation_type](params)
            
            # Add validation metadata
            result["simulation_type"] = simulation_type
            result["validation_timestamp"] = str(np.datetime64('now'))
            result["matlab_available"] = self.matlab_available
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "simulation_type": simulation_type
            }
            
    def cleanup_temp_files(self):
        """Clean up temporary simulation files"""
        temp_files = [
            'harmonic_sim.m', 'harmonic_results.mat',
            'wave_sim.m', 'heat_sim.m'
        ]
        
        for file in temp_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except Exception as e:
                    self.logger.warning(f"Failed to remove {file}: {str(e)}") 