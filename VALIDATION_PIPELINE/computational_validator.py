#!/usr/bin/env python3
"""
Computational Validation Stage - Professional Validation Pipeline
Agent: Claude-3.5-Sonnet
Stage 2: Computational Validation with Mathematical Rigor
"""

import os
import sys
import json
import time
import logging
import re
import ast
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import hashlib
import subprocess

class ComputationalValidator:
    """Stage 2: Computational validation with mathematical rigor"""
    
    def __init__(self):
        self.agent_id = "Claude-3.5-Sonnet"
        self.stage = "02-COMPUTATIONAL_VALIDATION"
        self.start_time = datetime.now(timezone.utc)
        self.setup_logging()
        
        # Validation criteria for computational analysis
        self.validation_criteria = {
            "mathematical_consistency": 0.0,
            "computational_correctness": 0.0,
            "physics_accuracy": 0.0,
            "algorithmic_efficiency": 0.0,
            "numerical_stability": 0.0
        }
        
    def setup_logging(self):
        """Setup professional logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s UTC - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        self.logger = logging.getLogger(__name__)
        
    def validate_computational_content(self, file_path: Path) -> Dict:
        """Perform computational validation on physics simulation"""
        self.logger.info(f"Computational validation: {file_path.name}")
        
        validation_result = {
            "file_path": str(file_path),
            "validation_stage": self.stage,
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": self.agent_id,
            "validation_criteria": {}
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Mathematical consistency analysis
            math_score = self.analyze_mathematical_consistency(content)
            validation_result["validation_criteria"]["mathematical_consistency"] = math_score
            
            # Computational correctness analysis
            comp_score = self.analyze_computational_correctness(content)
            validation_result["validation_criteria"]["computational_correctness"] = comp_score
            
            # Physics accuracy analysis
            physics_score = self.analyze_physics_accuracy(content)
            validation_result["validation_criteria"]["physics_accuracy"] = physics_score
            
            # Algorithmic efficiency analysis
            algo_score = self.analyze_algorithmic_efficiency(content)
            validation_result["validation_criteria"]["algorithmic_efficiency"] = algo_score
            
            # Numerical stability analysis
            stability_score = self.analyze_numerical_stability(content)
            validation_result["validation_criteria"]["numerical_stability"] = stability_score
            
            # Calculate overall validation score
            overall_score = self.calculate_overall_score(validation_result["validation_criteria"])
            validation_result["overall_validation_score"] = overall_score
            
            # Determine next stage
            if overall_score >= 0.8:
                validation_result["recommendation"] = "ADVANCE_TO_MULTI_METHOD_VERIFICATION"
                validation_result["next_stage"] = "03-MULTI_METHOD_VERIFICATION"
            elif overall_score >= 0.6:
                validation_result["recommendation"] = "ADVANCE_TO_PEER_REVIEW"
                validation_result["next_stage"] = "04-PEER_SIMULATION_REVIEW"
            elif overall_score >= 0.4:
                validation_result["recommendation"] = "REQUIRES_STRESS_TESTING"
                validation_result["next_stage"] = "05-STRESS_TESTING"
            else:
                validation_result["recommendation"] = "REJECT"
                validation_result["next_stage"] = "09-REJECTED_ITEMS"
                validation_result["rejection_reason"] = "Failed computational validation criteria"
            
            # Extract key computational features
            validation_result["computational_features"] = self.extract_computational_features(content)
            
        except Exception as e:
            validation_result.update({
                "error": str(e),
                "recommendation": "ERROR",
                "next_stage": "09-REJECTED_ITEMS",
                "rejection_reason": f"Computational validation error: {str(e)}"
            })
            self.logger.error(f"Error in computational validation of {file_path.name}: {e}")
        
        return validation_result
    
    def analyze_mathematical_consistency(self, content: str) -> float:
        """Analyze mathematical consistency in the simulation"""
        score = 0.0
        
        # Check for mathematical functions and constants
        math_functions = re.findall(r'Math\.(sin|cos|tan|sqrt|pow|exp|log|PI|E)', content)
        if math_functions:
            score += 0.2
        
        # Check for proper mathematical operations
        operations = re.findall(r'[+\-*/]\s*=|[+\-*/]\s*\d+', content)
        if len(operations) > 10:
            score += 0.2
        
        # Check for physics constants
        physics_constants = ['PI', 'Math.PI', '3.14159', '2.71828', '9.81', '299792458']
        for constant in physics_constants:
            if constant in content:
                score += 0.1
        
        # Check for proper variable declarations
        variables = re.findall(r'(let|const|var)\s+\w+\s*=', content)
        if len(variables) > 5:
            score += 0.2
        
        # Check for mathematical equations in comments
        equations = re.findall(r'//.*[=+\-*/].*\w+', content)
        if equations:
            score += 0.2
        
        return min(score, 1.0)
    
    def analyze_computational_correctness(self, content: str) -> float:
        """Analyze computational correctness"""
        score = 0.0
        
        # Check for proper function definitions
        functions = re.findall(r'function\s+\w+\s*\([^)]*\)\s*{', content)
        if len(functions) >= 3:
            score += 0.3
        
        # Check for proper loop structures
        loops = re.findall(r'for\s*\([^)]*\)\s*{|while\s*\([^)]*\)\s*{', content)
        if loops:
            score += 0.2
        
        # Check for array operations
        arrays = re.findall(r'new\s+(Array|Float32Array|Float64Array)', content)
        if arrays:
            score += 0.2
        
        # Check for proper error handling
        error_handling = re.findall(r'try\s*{|catch\s*\(', content)
        if error_handling:
            score += 0.1
        
        # Check for proper initialization
        initialization = re.findall(r'(let|const|var)\s+\w+\s*=\s*[0-9]', content)
        if len(initialization) >= 5:
            score += 0.2
        
        return min(score, 1.0)
    
    def analyze_physics_accuracy(self, content: str) -> float:
        """Analyze physics accuracy and realism"""
        score = 0.0
        
        # Check for physics equations
        physics_patterns = [
            r'F\s*=\s*m\s*\*\s*a',  # Newton's second law
            r'E\s*=\s*m\s*\*\s*c\s*\*\s*c',  # E=mc²
            r'v\s*=\s*u\s*\+\s*a\s*\*\s*t',  # Kinematic equation
            r'KE\s*=\s*0\.5\s*\*\s*m\s*\*\s*v\s*\*\s*v',  # Kinetic energy
            r'PE\s*=\s*m\s*\*\s*g\s*\*\s*h'  # Potential energy
        ]
        
        for pattern in physics_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 0.1
        
        # Check for conservation laws
        conservation_terms = ['conservation', 'conserved', 'energy', 'momentum']
        for term in conservation_terms:
            if term.lower() in content.lower():
                score += 0.05
        
        # Check for proper units and dimensions
        units = ['m/s', 'kg', 'N', 'J', 'Hz', 'rad', 'deg']
        for unit in units:
            if unit in content:
                score += 0.05
        
        # Check for realistic physical values
        realistic_values = re.findall(r'9\.8\d*|3\.14\d*|2\.99\d*e8', content)
        if realistic_values:
            score += 0.2
        
        return min(score, 1.0)
    
    def analyze_algorithmic_efficiency(self, content: str) -> float:
        """Analyze algorithmic efficiency"""
        score = 0.0
        
        # Check for efficient data structures
        efficient_structures = ['Float32Array', 'Float64Array', 'Uint16Array', 'Uint32Array']
        for structure in efficient_structures:
            if structure in content:
                score += 0.2
        
        # Check for optimization techniques
        optimizations = ['requestAnimationFrame', 'webgl', 'GPU', 'parallel', 'vectorized']
        for opt in optimizations:
            if opt.lower() in content.lower():
                score += 0.1
        
        # Check for proper memory management
        memory_management = ['delete', 'null', 'dispose', 'cleanup']
        for mgmt in memory_management:
            if mgmt in content:
                score += 0.1
        
        # Penalize inefficient patterns
        inefficient_patterns = re.findall(r'for.*for.*for', content)  # Triple nested loops
        if inefficient_patterns:
            score -= 0.2
        
        return max(min(score, 1.0), 0.0)
    
    def analyze_numerical_stability(self, content: str) -> float:
        """Analyze numerical stability"""
        score = 0.0
        
        # Check for proper numerical precision
        precision_checks = re.findall(r'Math\.abs\(.*\)\s*<\s*\d+e-\d+', content)
        if precision_checks:
            score += 0.3
        
        # Check for boundary condition handling
        boundary_checks = re.findall(r'if\s*\([^)]*[<>]=?[^)]*\)', content)
        if len(boundary_checks) >= 3:
            score += 0.2
        
        # Check for division by zero protection
        division_protection = re.findall(r'if\s*\([^)]*!=\s*0\)|Math\.abs\([^)]*\)\s*>\s*\d+e-\d+', content)
        if division_protection:
            score += 0.2
        
        # Check for proper time step handling
        time_step = re.findall(r'dt|deltaTime|timeStep', content)
        if time_step:
            score += 0.2
        
        # Check for stability conditions
        stability_terms = ['stable', 'stability', 'convergence', 'damping']
        for term in stability_terms:
            if term.lower() in content.lower():
                score += 0.1
        
        return min(score, 1.0)
    
    def extract_computational_features(self, content: str) -> Dict:
        """Extract key computational features"""
        features = {
            "function_count": len(re.findall(r'function\s+\w+', content)),
            "loop_count": len(re.findall(r'for\s*\(|while\s*\(', content)),
            "array_operations": len(re.findall(r'new\s+\w*Array', content)),
            "math_operations": len(re.findall(r'Math\.\w+', content)),
            "webgl_usage": 'webgl' in content.lower() or 'gl.' in content,
            "three_js_usage": 'THREE.' in content or 'three.js' in content.lower(),
            "animation_frame": 'requestAnimationFrame' in content,
            "canvas_usage": 'canvas' in content.lower() or 'getContext' in content,
            "physics_simulation": any(term in content.lower() for term in [
                'particle', 'force', 'velocity', 'acceleration', 'energy'
            ]),
            "wave_simulation": any(term in content.lower() for term in [
                'wave', 'frequency', 'amplitude', 'oscillation', 'harmonic'
            ])
        }
        
        return features
    
    def calculate_overall_score(self, criteria: Dict) -> float:
        """Calculate overall validation score with weights"""
        weights = {
            "mathematical_consistency": 0.25,
            "computational_correctness": 0.25,
            "physics_accuracy": 0.25,
            "algorithmic_efficiency": 0.15,
            "numerical_stability": 0.10
        }
        
        overall_score = sum(criteria[key] * weights[key] for key in weights)
        return overall_score
    
    def process_computational_validation_stage(self) -> Dict:
        """Process all items in computational validation stage"""
        stage_path = Path(f"VALIDATION_PIPELINE/{self.stage}")
        
        if not stage_path.exists():
            self.logger.error(f"Stage folder not found: {self.stage}")
            return {"error": f"Stage folder not found: {self.stage}"}
        
        results = {
            "processing_start": datetime.now(timezone.utc).isoformat(),
            "agent_id": self.agent_id,
            "stage": self.stage,
            "items_processed": [],
            "summary": {}
        }
        
        # Get all files in stage (excluding analysis reports)
        files = [f for f in stage_path.iterdir() 
                if f.is_file() and not f.name.endswith('_analysis.json')]
        
        self.logger.info(f"Found {len(files)} items for computational validation")
        
        # Process each file
        for file_path in files:
            self.logger.info(f"Validating: {file_path.name}")
            
            # Perform computational validation
            validation_result = self.validate_computational_content(file_path)
            
            # Move file to next stage
            self.move_to_next_stage(file_path, validation_result)
            
            results["items_processed"].append(validation_result)
        
        # Generate summary
        results["summary"] = self.generate_validation_summary(results["items_processed"])
        results["processing_end"] = datetime.now(timezone.utc).isoformat()
        
        return results
    
    def move_to_next_stage(self, file_path: Path, validation: Dict):
        """Move file to the next validation stage"""
        next_stage = validation.get("next_stage", "09-REJECTED_ITEMS")
        target_dir = Path(f"VALIDATION_PIPELINE/{next_stage}")
        
        # Ensure target directory exists
        target_dir.mkdir(exist_ok=True)
        
        # Move file
        target_path = target_dir / file_path.name
        try:
            file_path.rename(target_path)
            self.logger.info(f"Moved {file_path.name} to {next_stage}")
            
            # Create validation report
            report_path = target_dir / f"{file_path.stem}_computational_validation.json"
            with open(report_path, 'w') as f:
                json.dump(validation, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error moving {file_path.name}: {e}")
    
    def generate_validation_summary(self, processed_items: List[Dict]) -> Dict:
        """Generate summary of validation results"""
        summary = {
            "total_items": len(processed_items),
            "by_recommendation": {},
            "by_next_stage": {},
            "average_scores": {},
            "criteria_averages": {}
        }
        
        # Count by recommendation
        for item in processed_items:
            rec = item.get("recommendation", "UNKNOWN")
            summary["by_recommendation"][rec] = summary["by_recommendation"].get(rec, 0) + 1
            
            stage = item.get("next_stage", "UNKNOWN")
            summary["by_next_stage"][stage] = summary["by_next_stage"].get(stage, 0) + 1
        
        # Calculate average scores
        if processed_items:
            valid_items = [item for item in processed_items if "overall_validation_score" in item]
            
            if valid_items:
                summary["average_scores"]["overall"] = sum(
                    item["overall_validation_score"] for item in valid_items
                ) / len(valid_items)
                
                # Calculate criteria averages
                criteria_keys = ["mathematical_consistency", "computational_correctness", 
                               "physics_accuracy", "algorithmic_efficiency", "numerical_stability"]
                
                for criterion in criteria_keys:
                    scores = [item.get("validation_criteria", {}).get(criterion, 0) 
                             for item in valid_items]
                    if scores:
                        summary["criteria_averages"][criterion] = sum(scores) / len(scores)
        
        return summary

def main():
    """Main execution function"""
    validator = ComputationalValidator()
    
    validator.logger.info("Starting Computational Validation Stage")
    validator.logger.info("=" * 60)
    validator.logger.info(f"Agent: {validator.agent_id}")
    validator.logger.info(f"Stage: {validator.stage}")
    validator.logger.info(f"Start Time: {validator.start_time.isoformat()}")
    validator.logger.info("=" * 60)
    
    # Process computational validation stage
    results = validator.process_computational_validation_stage()
    
    # Display results
    validator.logger.info("COMPUTATIONAL VALIDATION COMPLETE")
    validator.logger.info("=" * 60)
    
    if "error" not in results:
        summary = results["summary"]
        validator.logger.info(f"Total Items Processed: {summary['total_items']}")
        validator.logger.info("Recommendations:")
        for rec, count in summary["by_recommendation"].items():
            validator.logger.info(f"  {rec}: {count}")
        
        validator.logger.info("Next Stages:")
        for stage, count in summary["by_next_stage"].items():
            validator.logger.info(f"  {stage}: {count}")
        
        if summary.get("average_scores"):
            avg_score = summary["average_scores"]["overall"]
            validator.logger.info(f"Average Overall Score: {avg_score:.3f}")
            
        if summary.get("criteria_averages"):
            validator.logger.info("Criteria Averages:")
            for criterion, score in summary["criteria_averages"].items():
                validator.logger.info(f"  {criterion}: {score:.3f}")
    
    validator.logger.info("=" * 60)
    
    # Save complete results
    results_path = Path("VALIDATION_PIPELINE/computational_validation_results.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    validator.logger.info(f"Complete results saved to: {results_path}")

if __name__ == "__main__":
    main() 