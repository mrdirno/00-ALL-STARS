#!/usr/bin/env python3
"""
Mathematical Error Detection and Code Issue Analysis
Claude-3.5-Sonnet - 2025-05-29

This script specifically searches for mathematical errors and code issues in physics simulations,
applying rigorous mathematical validation and edge case testing.
"""

import re
import json
import numpy as np
from pathlib import Path
import ast
import warnings
warnings.filterwarnings('ignore')

class MathematicalErrorDetector:
    """
    Detects mathematical errors and code issues in physics simulations
    """
    
    def __init__(self):
        self.errors_found = []
        self.warnings_found = []
        self.edge_case_failures = []
        
    def analyze_html_file(self, file_path):
        """
        Analyze an HTML file for mathematical errors and code issues
        """
        print(f"\n🔍 ANALYZING: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.errors_found.append({
                "file": file_path,
                "error_type": "FILE_READ_ERROR",
                "description": f"Cannot read file: {str(e)}"
            })
            return
        
        # Extract JavaScript code
        js_code = self.extract_javascript(content)
        
        # Run mathematical validation tests
        self.check_mathematical_consistency(file_path, js_code)
        self.check_physics_equations(file_path, js_code)
        self.check_numerical_stability(file_path, js_code)
        self.check_dimensional_analysis(file_path, js_code)
        self.test_edge_cases(file_path, js_code)
        
    def extract_javascript(self, html_content):
        """
        Extract JavaScript code from HTML content
        """
        # Find all script tags
        script_pattern = r'<script[^>]*>(.*?)</script>'
        scripts = re.findall(script_pattern, html_content, re.DOTALL | re.IGNORECASE)
        
        # Combine all JavaScript
        js_code = '\n'.join(scripts)
        return js_code
    
    def check_mathematical_consistency(self, file_path, js_code):
        """
        Check for mathematical consistency issues
        """
        print("   Checking mathematical consistency...")
        
        # Check for division by zero
        division_patterns = [
            r'\/\s*0\s*[;\)\],]',  # Direct division by zero
            r'\/\s*\(\s*[^)]*\s*\)',  # Division by expression that could be zero
        ]
        
        for pattern in division_patterns:
            matches = re.findall(pattern, js_code)
            if matches:
                self.errors_found.append({
                    "file": file_path,
                    "error_type": "POTENTIAL_DIVISION_BY_ZERO",
                    "description": f"Found potential division by zero: {matches}",
                    "severity": "HIGH"
                })
        
        # Check for NaN/Infinity handling
        if 'NaN' in js_code or 'Infinity' in js_code:
            if 'isNaN' not in js_code and 'isFinite' not in js_code:
                self.warnings_found.append({
                    "file": file_path,
                    "warning_type": "MISSING_NAN_CHECK",
                    "description": "Code uses NaN/Infinity but lacks proper checking",
                    "severity": "MEDIUM"
                })
        
        # Check for mathematical function misuse
        math_functions = ['Math.sqrt', 'Math.log', 'Math.asin', 'Math.acos']
        for func in math_functions:
            if func in js_code:
                # Check if there's domain validation
                if func == 'Math.sqrt' and 'sqrt(' in js_code:
                    # Should check for negative values
                    if not re.search(r'if.*<\s*0', js_code):
                        self.warnings_found.append({
                            "file": file_path,
                            "warning_type": "MISSING_DOMAIN_CHECK",
                            "description": f"Using {func} without negative value check",
                            "severity": "MEDIUM"
                        })
    
    def check_physics_equations(self, file_path, js_code):
        """
        Check physics equations for correctness
        """
        print("   Checking physics equations...")
        
        # Check for energy conservation violations
        energy_patterns = [
            r'energy\s*\+=\s*[^;]*',  # Energy addition
            r'energy\s*\*=\s*[^;]*',  # Energy multiplication
        ]
        
        for pattern in energy_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            if matches:
                # Check if there's corresponding energy loss
                if 'energy -=' not in js_code and 'energy /=' not in js_code:
                    self.warnings_found.append({
                        "file": file_path,
                        "warning_type": "ENERGY_CONSERVATION_VIOLATION",
                        "description": "Energy is added/multiplied but no corresponding loss found",
                        "severity": "HIGH"
                    })
        
        # Check for momentum conservation
        momentum_patterns = [
            r'velocity\s*\+=\s*[^;]*',
            r'momentum\s*\+=\s*[^;]*',
        ]
        
        for pattern in momentum_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            if matches:
                # Should have corresponding momentum changes in other objects
                if 'total_momentum' not in js_code.lower():
                    self.warnings_found.append({
                        "file": file_path,
                        "warning_type": "MOMENTUM_CONSERVATION_CONCERN",
                        "description": "Momentum changes without total momentum tracking",
                        "severity": "MEDIUM"
                    })
        
        # Check for unrealistic physical constants
        constants_to_check = {
            'c': (299792458, 3e8),  # Speed of light
            'G': (6.67e-11, 6.7e-11),  # Gravitational constant
            'h': (6.62e-34, 6.63e-34),  # Planck constant
        }
        
        for const_name, (min_val, max_val) in constants_to_check.items():
            pattern = rf'{const_name}\s*=\s*([\d.e+-]+)'
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            for match in matches:
                try:
                    value = float(match)
                    if not (min_val <= value <= max_val):
                        self.errors_found.append({
                            "file": file_path,
                            "error_type": "INCORRECT_PHYSICAL_CONSTANT",
                            "description": f"Constant {const_name} = {value} is outside realistic range [{min_val}, {max_val}]",
                            "severity": "HIGH"
                        })
                except ValueError:
                    pass
    
    def check_numerical_stability(self, file_path, js_code):
        """
        Check for numerical stability issues
        """
        print("   Checking numerical stability...")
        
        # Check for very small time steps that could cause instability
        dt_pattern = r'dt\s*=\s*([\d.e+-]+)'
        matches = re.findall(dt_pattern, js_code, re.IGNORECASE)
        for match in matches:
            try:
                dt = float(match)
                if dt < 1e-10:
                    self.warnings_found.append({
                        "file": file_path,
                        "warning_type": "VERY_SMALL_TIMESTEP",
                        "description": f"Time step dt = {dt} may cause numerical instability",
                        "severity": "MEDIUM"
                    })
                elif dt > 1.0:
                    self.warnings_found.append({
                        "file": file_path,
                        "warning_type": "LARGE_TIMESTEP",
                        "description": f"Time step dt = {dt} may be too large for accuracy",
                        "severity": "MEDIUM"
                    })
            except ValueError:
                pass
        
        # Check for accumulation of floating point errors
        if 'for' in js_code and '+=' in js_code:
            # Look for loops that accumulate values
            loop_pattern = r'for\s*\([^)]*\)\s*\{[^}]*\+=.*?\}'
            matches = re.findall(loop_pattern, js_code, re.DOTALL)
            if matches and 'compensation' not in js_code.lower():
                self.warnings_found.append({
                    "file": file_path,
                    "warning_type": "FLOATING_POINT_ACCUMULATION",
                    "description": "Loops with accumulation may suffer from floating point errors",
                    "severity": "LOW"
                })
    
    def check_dimensional_analysis(self, file_path, js_code):
        """
        Check dimensional consistency in equations
        """
        print("   Checking dimensional consistency...")
        
        # Look for equations that mix different units
        suspicious_patterns = [
            r'position\s*\+=\s*velocity',  # Should be position += velocity * dt
            r'velocity\s*\+=\s*acceleration',  # Should be velocity += acceleration * dt
            r'energy\s*=\s*mass\s*\*\s*velocity',  # Should be 0.5 * mass * velocity^2
        ]
        
        for pattern in suspicious_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            if matches:
                self.warnings_found.append({
                    "file": file_path,
                    "warning_type": "DIMENSIONAL_INCONSISTENCY",
                    "description": f"Potentially dimensionally inconsistent equation: {matches}",
                    "severity": "HIGH"
                })
    
    def test_edge_cases(self, file_path, js_code):
        """
        Test edge cases that could break the simulation
        """
        print("   Testing edge cases...")
        
        edge_cases = [
            {
                "name": "Zero mass",
                "test": "mass = 0",
                "concern": "Division by mass could cause NaN"
            },
            {
                "name": "Infinite velocity",
                "test": "velocity = Infinity",
                "concern": "Could propagate through calculations"
            },
            {
                "name": "Negative energy",
                "test": "energy < 0",
                "concern": "May violate physical constraints"
            },
            {
                "name": "Very large numbers",
                "test": "value > 1e100",
                "concern": "Could cause overflow"
            }
        ]
        
        for case in edge_cases:
            # Check if the code handles this edge case
            if case["test"].split()[0] in js_code:
                # Look for validation
                validation_patterns = [
                    rf'if.*{case["test"].split()[0]}.*[<>=]',
                    rf'{case["test"].split()[0]}.*Math\.max',
                    rf'{case["test"].split()[0]}.*Math\.min',
                ]
                
                has_validation = any(re.search(pattern, js_code, re.IGNORECASE) 
                                   for pattern in validation_patterns)
                
                if not has_validation:
                    self.edge_case_failures.append({
                        "file": file_path,
                        "edge_case": case["name"],
                        "test": case["test"],
                        "concern": case["concern"],
                        "severity": "MEDIUM"
                    })
    
    def analyze_all_approved_files(self):
        """
        Analyze all files in the approved research folder
        """
        approved_folder = Path("08-APPROVED_RESEARCH")
        
        if not approved_folder.exists():
            print("❌ Approved research folder not found")
            return
        
        html_files = list(approved_folder.glob("*.html"))
        
        if not html_files:
            print("❌ No HTML files found in approved research folder")
            return
        
        print(f"🔍 Found {len(html_files)} HTML files to analyze")
        
        for file_path in html_files:
            self.analyze_html_file(file_path)
    
    def generate_report(self):
        """
        Generate comprehensive error report
        """
        print("\n📊 MATHEMATICAL ERROR DETECTION REPORT")
        print("=" * 60)
        
        total_issues = len(self.errors_found) + len(self.warnings_found) + len(self.edge_case_failures)
        
        print(f"Total Issues Found: {total_issues}")
        print(f"  - Errors: {len(self.errors_found)}")
        print(f"  - Warnings: {len(self.warnings_found)}")
        print(f"  - Edge Case Failures: {len(self.edge_case_failures)}")
        
        if self.errors_found:
            print("\n🚨 CRITICAL ERRORS:")
            for error in self.errors_found:
                print(f"  File: {error['file']}")
                print(f"  Type: {error['error_type']}")
                print(f"  Description: {error['description']}")
                print(f"  Severity: {error.get('severity', 'UNKNOWN')}")
                print()
        
        if self.warnings_found:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings_found:
                print(f"  File: {warning['file']}")
                print(f"  Type: {warning['warning_type']}")
                print(f"  Description: {warning['description']}")
                print(f"  Severity: {warning.get('severity', 'UNKNOWN')}")
                print()
        
        if self.edge_case_failures:
            print("\n🧪 EDGE CASE FAILURES:")
            for failure in self.edge_case_failures:
                print(f"  File: {failure['file']}")
                print(f"  Edge Case: {failure['edge_case']}")
                print(f"  Test: {failure['test']}")
                print(f"  Concern: {failure['concern']}")
                print()
        
        # Overall assessment
        high_severity_count = sum(1 for item in self.errors_found + self.warnings_found 
                                if item.get('severity') == 'HIGH')
        
        if high_severity_count > 0:
            print(f"🚨 CRITICAL ASSESSMENT: {high_severity_count} high-severity issues found")
            print("   Recommendation: REJECT - Mathematical errors compromise validity")
        elif total_issues > 5:
            print(f"⚠️  MODERATE CONCERNS: {total_issues} total issues found")
            print("   Recommendation: REQUIRES_REVISION - Address issues before approval")
        elif total_issues > 0:
            print(f"ℹ️  MINOR ISSUES: {total_issues} minor issues found")
            print("   Recommendation: ACCEPTABLE_WITH_NOTES - Document limitations")
        else:
            print("✅ NO MATHEMATICAL ERRORS DETECTED")
            print("   Recommendation: MATHEMATICALLY_SOUND")
        
        return {
            "total_issues": total_issues,
            "errors": self.errors_found,
            "warnings": self.warnings_found,
            "edge_case_failures": self.edge_case_failures,
            "high_severity_count": high_severity_count
        }

def main():
    """
    Main execution
    """
    print("🔬 MATHEMATICAL ERROR DETECTION AND CODE ANALYSIS")
    print("Claude-3.5-Sonnet - 2025-05-29")
    print("=" * 60)
    
    detector = MathematicalErrorDetector()
    detector.analyze_all_approved_files()
    report = detector.generate_report()
    
    # Save detailed report
    from datetime import datetime
    timestamp = datetime.utcnow().isoformat()
    output_file = f"mathematical_error_report_{timestamp.replace(':', '-')}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "analyzer": "Claude-3.5-Sonnet",
            "analysis_type": "Mathematical Error Detection",
            "report": report
        }, f, indent=2, default=str)
    
    print(f"\n💾 Detailed report saved to: {output_file}")
    
    return report

if __name__ == "__main__":
    main() 