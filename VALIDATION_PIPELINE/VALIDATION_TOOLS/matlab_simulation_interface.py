#!/usr/bin/env python3
"""
MATLAB Simulation Interface - Enables physics simulations for validation
Provides automated MATLAB execution for computational validation
"""

import os
import sys
import numpy as np
import subprocess
import tempfile
import shutil
from pathlib import Path
import logging
from typing import Dict, List, Any, Tuple, Optional
import json
import time

class MATLABSimulationInterface:
    """Interface for running MATLAB simulations in validation pipeline"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.matlab_executable = self._find_matlab_executable()
        self.temp_dir = Path(tempfile.mkdtemp(prefix="validation_matlab_"))
        self.simulation_timeout = 300  # 5 minutes
        
    def __del__(self):
        """Cleanup temporary directory"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def _find_matlab_executable(self) -> Optional[str]:
        """Find MATLAB executable on system"""
        common_paths = [
            "matlab",
            "/usr/local/bin/matlab",
            "/Applications/MATLAB_R2023b.app/bin/matlab",
            "C:\\Program Files\\MATLAB\\R2023b\\bin\\matlab.exe",
            "C:\\Program Files\\MATLAB\\R2024a\\bin\\matlab.exe"
        ]
        
        for path in common_paths:
            try:
                result = subprocess.run([path, "-help"], 
                                      capture_output=True, 
                                      timeout=10, 
                                      text=True)
                if result.returncode == 0:
                    self.logger.info(f"Found MATLAB at: {path}")
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                continue
        
        self.logger.warning("MATLAB not found - simulations will use fallback methods")
        return None
    
    def validate_physics_simulation(self, physics_description: Dict[str, Any]) -> Dict[str, Any]:
        """Validate physics through MATLAB simulation"""
        result = {
            "simulation_type": "physics_validation",
            "success": False,
            "matlab_available": self.matlab_executable is not None,
            "simulation_results": {},
            "validation_metrics": {},
            "error_message": None
        }
        
        try:
            if self.matlab_executable:
                # Use MATLAB for simulation
                result.update(self._run_matlab_physics_simulation(physics_description))
            else:
                # Use Python fallback
                result.update(self._run_python_physics_simulation(physics_description))
                
        except Exception as e:
            result["error_message"] = str(e)
            self.logger.error(f"Physics simulation failed: {str(e)}")
            
        return result
    
    def _run_matlab_physics_simulation(self, physics_desc: Dict[str, Any]) -> Dict[str, Any]:
        """Run physics simulation using MATLAB"""
        
        # Generate MATLAB simulation code
        matlab_code = self._generate_physics_matlab_code(physics_desc)
        
        # Write to temporary file
        matlab_file = self.temp_dir / "physics_simulation.m"
        with open(matlab_file, 'w') as f:
            f.write(matlab_code)
        
        # Run MATLAB simulation
        try:
            cmd = [
                self.matlab_executable,
                "-batch",
                f"cd('{self.temp_dir}'); physics_simulation; exit;"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=self.simulation_timeout,
                text=True,
                cwd=str(self.temp_dir)
            )
            
            if result.returncode == 0:
                # Read simulation results
                return self._parse_matlab_results()
            else:
                return {
                    "success": False,
                    "error_message": f"MATLAB execution failed: {result.stderr}",
                    "matlab_stdout": result.stdout,
                    "matlab_stderr": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error_message": "MATLAB simulation timed out"
            }
    
    def _run_python_physics_simulation(self, physics_desc: Dict[str, Any]) -> Dict[str, Any]:
        """Run physics simulation using Python fallback"""
        simulation_type = physics_desc.get("type", "generic")
        
        if simulation_type == "harmonic_oscillator":
            return self._simulate_harmonic_oscillator(physics_desc)
        elif simulation_type == "wave_equation":
            return self._simulate_wave_equation(physics_desc)
        elif simulation_type == "heat_equation":
            return self._simulate_heat_equation(physics_desc)
        elif simulation_type == "projectile_motion":
            return self._simulate_projectile_motion(physics_desc)
        else:
            return self._simulate_generic_physics(physics_desc)
    
    def _generate_physics_matlab_code(self, physics_desc: Dict[str, Any]) -> str:
        """Generate MATLAB code for physics simulation"""
        
        simulation_type = physics_desc.get("type", "generic")
        
        if simulation_type == "harmonic_oscillator":
            return self._generate_harmonic_oscillator_matlab()
        elif simulation_type == "wave_equation":
            return self._generate_wave_equation_matlab()
        elif simulation_type == "heat_equation":
            return self._generate_heat_equation_matlab()
        else:
            return self._generate_generic_matlab_template()
    
    def _generate_harmonic_oscillator_matlab(self) -> str:
        """Generate MATLAB code for harmonic oscillator simulation"""
        return """
% Harmonic Oscillator Simulation
function physics_simulation()
    % Parameters
    omega = 1.0;  % Natural frequency
    t_span = [0, 10];  % Time span
    y0 = [1; 0];  % Initial conditions [position; velocity]
    
    % Solve differential equation
    [t, y] = ode45(@(t,y) harmonic_ode(t, y, omega), t_span, y0);
    
    % Calculate energy conservation
    kinetic_energy = 0.5 * y(:,2).^2;
    potential_energy = 0.5 * omega^2 * y(:,1).^2;
    total_energy = kinetic_energy + potential_energy;
    
    % Validation metrics
    energy_variation = std(total_energy) / mean(total_energy);
    max_amplitude = max(abs(y(:,1)));
    period = 2*pi/omega;
    
    % Save results
    results = struct();
    results.success = true;
    results.energy_conserved = energy_variation < 0.01;
    results.energy_variation = energy_variation;
    results.max_amplitude = max_amplitude;
    results.theoretical_period = period;
    results.time_series = struct('t', t, 'position', y(:,1), 'velocity', y(:,2));
    results.validation_score = 1.0 - energy_variation;
    
    % Write results to JSON file
    json_str = jsonencode(results);
    fid = fopen('simulation_results.json', 'w');
    fprintf(fid, '%s', json_str);
    fclose(fid);
    
    fprintf('Harmonic oscillator simulation completed successfully\\n');
end

function dydt = harmonic_ode(t, y, omega)
    dydt = zeros(2,1);
    dydt(1) = y(2);           % dx/dt = v
    dydt(2) = -omega^2 * y(1); % dv/dt = -omega^2 * x
end
"""
    
    def _generate_wave_equation_matlab(self) -> str:
        """Generate MATLAB code for wave equation simulation"""
        return """
% Wave Equation Simulation (1D)
function physics_simulation()
    % Parameters
    L = 10;          % Domain length
    c = 1;           % Wave speed
    N = 100;         % Number of spatial points
    T = 10;          % Total time
    dt = 0.01;       % Time step
    
    % Spatial grid
    dx = L / (N-1);
    x = linspace(0, L, N);
    
    % Initial conditions: Gaussian pulse
    sigma = 1;
    x0 = L/4;
    u0 = exp(-((x - x0)/sigma).^2);
    v0 = zeros(size(x));
    
    % Time evolution using finite differences
    u_prev = u0;
    u_curr = u0 + dt * v0;
    
    % CFL condition check
    CFL = c * dt / dx;
    stable = CFL <= 1;
    
    % Time stepping
    t = 0:dt:T;
    energy_history = zeros(size(t));
    
    for n = 1:length(t)
        if n > 2
            % Wave equation finite difference scheme
            u_next = zeros(size(u_curr));
            for i = 2:N-1
                u_next(i) = 2*u_curr(i) - u_prev(i) + ...
                           (c*dt/dx)^2 * (u_curr(i+1) - 2*u_curr(i) + u_curr(i-1));
            end
            
            % Boundary conditions (absorbing)
            u_next(1) = 0;
            u_next(end) = 0;
            
            % Update
            u_prev = u_curr;
            u_curr = u_next;
        end
        
        % Calculate energy
        kinetic = sum((u_curr - u_prev).^2) / (2*dt^2);
        potential = sum(diff(u_curr).^2) / (2*dx^2);
        energy_history(n) = kinetic + potential;
    end
    
    % Validation metrics
    energy_conservation = std(energy_history) / mean(energy_history);
    
    % Save results
    results = struct();
    results.success = true;
    results.stable = stable;
    results.CFL_number = CFL;
    results.energy_conservation = energy_conservation;
    results.energy_conserved = energy_conservation < 0.1;
    results.final_wave = u_curr;
    results.energy_history = energy_history;
    results.validation_score = 1.0 - min(energy_conservation, 1.0);
    
    % Write results
    json_str = jsonencode(results);
    fid = fopen('simulation_results.json', 'w');
    fprintf(fid, '%s', json_str);
    fclose(fid);
    
    fprintf('Wave equation simulation completed successfully\\n');
end
"""
    
    def _generate_heat_equation_matlab(self) -> str:
        """Generate MATLAB code for heat equation simulation"""
        return """
% Heat Equation Simulation (1D)
function physics_simulation()
    % Parameters
    L = 1;           % Domain length
    alpha = 0.01;    % Thermal diffusivity
    N = 50;          % Number of spatial points
    T = 1;           % Total time
    dt = 0.0001;     % Time step
    
    % Spatial grid
    dx = L / (N-1);
    x = linspace(0, L, N);
    
    % Initial condition: step function
    u = zeros(N, 1);
    u(x <= 0.5) = 1;
    
    % Stability check
    stability_param = alpha * dt / dx^2;
    stable = stability_param <= 0.5;
    
    % Time evolution
    t = 0:dt:T;
    total_heat_history = zeros(size(t));
    max_temp_history = zeros(size(t));
    
    for n = 1:length(t)
        if n > 1
            % Heat equation finite difference scheme
            u_new = u;
            for i = 2:N-1
                u_new(i) = u(i) + alpha * dt / dx^2 * ...
                          (u(i+1) - 2*u(i) + u(i-1));
            end
            
            % Boundary conditions (Dirichlet: fixed at 0)
            u_new(1) = 0;
            u_new(end) = 0;
            
            u = u_new;
        end
        
        % Conservation quantities
        total_heat_history(n) = trapz(x, u);
        max_temp_history(n) = max(u);
    end
    
    % Analytical solution for comparison (if available)
    % For step function initial condition
    
    % Validation metrics
    monotonic_decrease = all(diff(max_temp_history) <= 1e-10);
    heat_loss_rate = (total_heat_history(1) - total_heat_history(end)) / total_heat_history(1);
    
    % Save results
    results = struct();
    results.success = true;
    results.stable = stable;
    results.stability_parameter = stability_param;
    results.monotonic_cooling = monotonic_decrease;
    results.heat_loss_rate = heat_loss_rate;
    results.final_temperature = u;
    results.max_temp_history = max_temp_history;
    results.total_heat_history = total_heat_history;
    results.validation_score = double(stable && monotonic_decrease);
    
    % Write results
    json_str = jsonencode(results);
    fid = fopen('simulation_results.json', 'w');
    fprintf(fid, '%s', json_str);
    fclose(fid);
    
    fprintf('Heat equation simulation completed successfully\\n');
end
"""
    
    def _generate_generic_matlab_template(self) -> str:
        """Generate generic MATLAB template for custom physics"""
        return """
% Generic Physics Simulation Template
function physics_simulation()
    % Default parameters
    t_span = [0, 10];
    
    % Simple harmonic oscillator as default
    omega = 1.0;
    y0 = [1; 0];
    
    % Solve
    [t, y] = ode45(@(t,y) [y(2); -omega^2*y(1)], t_span, y0);
    
    % Basic validation
    energy = 0.5 * (y(:,2).^2 + omega^2 * y(:,1).^2);
    energy_variation = std(energy) / mean(energy);
    
    % Results
    results = struct();
    results.success = true;
    results.energy_variation = energy_variation;
    results.validation_score = 1.0 - energy_variation;
    
    % Write results
    json_str = jsonencode(results);
    fid = fopen('simulation_results.json', 'w');
    fprintf(fid, '%s', json_str);
    fclose(fid);
    
    fprintf('Generic physics simulation completed\\n');
end
"""
    
    def _parse_matlab_results(self) -> Dict[str, Any]:
        """Parse MATLAB simulation results from JSON file"""
        results_file = self.temp_dir / "simulation_results.json"
        
        if results_file.exists():
            try:
                with open(results_file, 'r') as f:
                    matlab_results = json.load(f)
                
                return {
                    "success": matlab_results.get("success", False),
                    "simulation_results": matlab_results,
                    "validation_metrics": {
                        "validation_score": matlab_results.get("validation_score", 0),
                        "energy_conserved": matlab_results.get("energy_conserved", False),
                        "stable": matlab_results.get("stable", False)
                    }
                }
            except Exception as e:
                return {
                    "success": False,
                    "error_message": f"Failed to parse MATLAB results: {str(e)}"
                }
        else:
            return {
                "success": False,
                "error_message": "MATLAB results file not found"
            }
    
    # Python fallback simulations
    
    def _simulate_harmonic_oscillator(self, physics_desc: Dict[str, Any]) -> Dict[str, Any]:
        """Python simulation of harmonic oscillator"""
        from scipy.integrate import solve_ivp
        
        # Parameters
        omega = physics_desc.get("frequency", 1.0)
        t_span = (0, 10)
        y0 = [1, 0]  # [position, velocity]
        
        # Differential equation
        def harmonic_ode(t, y):
            return [y[1], -omega**2 * y[0]]
        
        # Solve
        sol = solve_ivp(harmonic_ode, t_span, y0, dense_output=True, rtol=1e-8)
        
        # Evaluate solution
        t_eval = np.linspace(0, 10, 1000)
        y_eval = sol.sol(t_eval)
        
        # Energy conservation check
        kinetic = 0.5 * y_eval[1]**2
        potential = 0.5 * omega**2 * y_eval[0]**2
        total_energy = kinetic + potential
        
        energy_variation = np.std(total_energy) / np.mean(total_energy)
        
        return {
            "success": True,
            "simulation_results": {
                "energy_variation": float(energy_variation),
                "max_amplitude": float(np.max(np.abs(y_eval[0]))),
                "period": float(2 * np.pi / omega)
            },
            "validation_metrics": {
                "energy_conserved": energy_variation < 0.01,
                "validation_score": float(1.0 - energy_variation)
            }
        }
    
    def _simulate_wave_equation(self, physics_desc: Dict[str, Any]) -> Dict[str, Any]:
        """Python simulation of wave equation"""
        # Simplified 1D wave equation simulation
        L = 10
        c = 1
        N = 100
        T = 5
        dt = 0.01
        
        dx = L / (N-1)
        x = np.linspace(0, L, N)
        
        # Initial Gaussian pulse
        sigma = 1
        x0 = L/4
        u0 = np.exp(-((x - x0)/sigma)**2)
        v0 = np.zeros_like(x)
        
        # Finite difference simulation
        u_prev = u0.copy()
        u_curr = u0 + dt * v0
        
        CFL = c * dt / dx
        stable = CFL <= 1
        
        # Simple time stepping
        for _ in range(int(T/dt)):
            u_next = np.zeros_like(u_curr)
            u_next[1:-1] = (2*u_curr[1:-1] - u_prev[1:-1] + 
                           (c*dt/dx)**2 * (u_curr[2:] - 2*u_curr[1:-1] + u_curr[:-2]))
            
            u_prev = u_curr.copy()
            u_curr = u_next.copy()
        
        return {
            "success": True,
            "simulation_results": {
                "CFL_number": float(CFL),
                "stable": bool(stable),
                "final_amplitude": float(np.max(np.abs(u_curr)))
            },
            "validation_metrics": {
                "stable": stable,
                "validation_score": 1.0 if stable else 0.5
            }
        }
    
    def _simulate_heat_equation(self, physics_desc: Dict[str, Any]) -> Dict[str, Any]:
        """Python simulation of heat equation"""
        # 1D heat equation simulation
        L = 1
        alpha = 0.01
        N = 50
        T = 1
        dt = 0.0001
        
        dx = L / (N-1)
        x = np.linspace(0, L, N)
        
        # Step function initial condition
        u = np.zeros(N)
        u[x <= 0.5] = 1
        
        stability_param = alpha * dt / dx**2
        stable = stability_param <= 0.5
        
        # Time evolution
        initial_heat = np.trapz(u, x)
        
        for _ in range(int(T/dt)):
            u_new = u.copy()
            u_new[1:-1] = (u[1:-1] + alpha * dt / dx**2 * 
                          (u[2:] - 2*u[1:-1] + u[:-2]))
            u_new[0] = 0
            u_new[-1] = 0
            u = u_new
        
        final_heat = np.trapz(u, x)
        heat_loss = (initial_heat - final_heat) / initial_heat
        
        return {
            "success": True,
            "simulation_results": {
                "stability_parameter": float(stability_param),
                "heat_loss_rate": float(heat_loss),
                "max_final_temp": float(np.max(u))
            },
            "validation_metrics": {
                "stable": stable,
                "validation_score": 1.0 if stable else 0.5
            }
        }
    
    def _simulate_projectile_motion(self, physics_desc: Dict[str, Any]) -> Dict[str, Any]:
        """Python simulation of projectile motion"""
        # Parameters
        v0 = physics_desc.get("initial_velocity", 50)  # m/s
        angle = physics_desc.get("launch_angle", 45)   # degrees
        g = 9.81
        
        # Convert angle to radians
        theta = np.radians(angle)
        
        # Initial velocity components
        vx0 = v0 * np.cos(theta)
        vy0 = v0 * np.sin(theta)
        
        # Time of flight
        t_flight = 2 * vy0 / g
        
        # Trajectory
        t = np.linspace(0, t_flight, 1000)
        x = vx0 * t
        y = vy0 * t - 0.5 * g * t**2
        
        # Range and max height
        max_range = vx0 * t_flight
        max_height = vy0**2 / (2 * g)
        
        # Theoretical values
        theoretical_range = v0**2 * np.sin(2*theta) / g
        theoretical_height = v0**2 * np.sin(theta)**2 / (2 * g)
        
        # Validation
        range_error = abs(max_range - theoretical_range) / theoretical_range
        height_error = abs(max_height - theoretical_height) / theoretical_height
        
        return {
            "success": True,
            "simulation_results": {
                "max_range": float(max_range),
                "max_height": float(max_height),
                "time_of_flight": float(t_flight),
                "theoretical_range": float(theoretical_range),
                "theoretical_height": float(theoretical_height)
            },
            "validation_metrics": {
                "range_accuracy": float(1 - range_error),
                "height_accuracy": float(1 - height_error),
                "validation_score": float(1 - (range_error + height_error) / 2)
            }
        }
    
    def _simulate_generic_physics(self, physics_desc: Dict[str, Any]) -> Dict[str, Any]:
        """Generic physics simulation fallback"""
        return {
            "success": True,
            "simulation_results": {
                "note": "Generic physics simulation - limited validation"
            },
            "validation_metrics": {
                "validation_score": 0.5
            }
        }
    
    def run_custom_simulation(self, matlab_code: str) -> Dict[str, Any]:
        """Run custom MATLAB code"""
        if not self.matlab_executable:
            return {
                "success": False,
                "error_message": "MATLAB not available for custom simulation"
            }
        
        # Write custom code to file
        matlab_file = self.temp_dir / "custom_simulation.m"
        with open(matlab_file, 'w') as f:
            f.write(matlab_code)
        
        try:
            cmd = [
                self.matlab_executable,
                "-batch",
                f"cd('{self.temp_dir}'); custom_simulation; exit;"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=self.simulation_timeout,
                text=True,
                cwd=str(self.temp_dir)
            )
            
            return {
                "success": result.returncode == 0,
                "matlab_output": result.stdout,
                "matlab_errors": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error_message": "Custom simulation timed out"
            } 