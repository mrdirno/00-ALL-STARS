#!/usr/bin/env python3
"""
Scientific Validation Pipeline - Demonstration Script for AI Agents

This script demonstrates how AI agents can execute the validation pipeline
in Cursor IDE to validate scientific research with computational rigor.

Usage:
    python run_validation_demo.py

Requirements:
    - Python 3.7+
    - All packages in VALIDATION_TOOLS/requirements.txt
    - Optional: MATLAB (for enhanced physics simulations)
"""

import os
import sys
import json
from pathlib import Path
import logging
import time
from datetime import datetime

# Add validation tools to path
sys.path.append(str(Path(__file__).parent / "VALIDATION_TOOLS"))

try:
    from validation_framework import ScientificValidationFramework
    from matlab_simulation_interface import MATLABSimulationInterface
    print("✅ Successfully imported validation framework")
except ImportError as e:
    print(f"❌ Failed to import validation framework: {e}")
    print("Please install requirements: pip install -r VALIDATION_TOOLS/requirements.txt")
    sys.exit(1)

def setup_logging():
    """Setup logging for demonstration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('validation_demo.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def check_system_requirements():
    """Check system requirements for validation"""
    logger = logging.getLogger(__name__)
    requirements = {
        "python_version": sys.version_info >= (3, 7),
        "validation_pipeline": Path("VALIDATION_TOOLS").exists(),
        "intake_directory": Path("00-INTAKE").exists(),
        "sample_research": Path("00-INTAKE/sample_physics_research.txt").exists()
    }
    
    logger.info("🔍 Checking system requirements...")
    
    for requirement, status in requirements.items():
        status_icon = "✅" if status else "❌"
        logger.info(f"  {status_icon} {requirement}: {status}")
    
    # Check MATLAB availability
    matlab_interface = MATLABSimulationInterface()
    matlab_available = matlab_interface.matlab_executable is not None
    matlab_icon = "✅" if matlab_available else "⚠️"
    logger.info(f"  {matlab_icon} MATLAB: {'Available' if matlab_available else 'Not found (will use Python fallbacks)'}")
    
    all_required = all(requirements.values())
    if not all_required:
        logger.error("❌ System requirements not met. Please fix the issues above.")
        return False
    
    logger.info("✅ All system requirements satisfied!")
    return True

def demonstrate_validation_pipeline():
    """Demonstrate the complete validation pipeline"""
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting Scientific Validation Pipeline Demonstration")
    logger.info("=" * 70)
    
    # Initialize validation framework
    logger.info("📋 Initializing validation framework...")
    framework = ScientificValidationFramework()
    
    # Check for items in intake
    intake_path = Path("00-INTAKE")
    items = list(intake_path.iterdir())
    
    if not items:
        logger.warning("⚠️  No items found in intake directory")
        logger.info("Creating a sample research item for demonstration...")
        
        # Create sample research if none exists
        sample_content = """
TITLE: Energy Conservation in Simple Harmonic Oscillator

HYPOTHESIS: We hypothesize that the total mechanical energy E = (1/2)mv² + (1/2)kx² 
remains constant throughout the oscillation cycle of a simple harmonic oscillator.

EQUATIONS:
Newton's second law: F = ma = -kx
Total energy: E = (1/2)mv² + (1/2)kx²
Angular frequency: ω = √(k/m)

PREDICTIONS:
1. Energy conservation should hold within numerical precision
2. Maximum kinetic energy equals maximum potential energy
3. Period T = 2π/ω should be observed

PARAMETERS:
m = 1.0 kg, k = 1.0 N/m, x₀ = 1.0 m, v₀ = 0.0 m/s
"""
        
        sample_file = intake_path / "demo_harmonic_oscillator.txt"
        with open(sample_file, 'w') as f:
            f.write(sample_content)
        
        items = [sample_file]
        logger.info(f"✅ Created sample research: {sample_file.name}")
    
    # Process each item
    for item in items:
        if item.is_file() or item.is_dir():
            logger.info(f"🔬 Processing research item: {item.name}")
            logger.info("-" * 50)
            
            start_time = time.time()
            
            # Run validation
            result = framework.validate_research_item(str(item))
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Display results
            display_validation_results(result, processing_time, logger)
            
            # Save detailed results
            save_validation_report(result, item.name, logger)
            
            logger.info("-" * 50)
    
    logger.info("🎉 Validation pipeline demonstration completed!")
    logger.info("=" * 70)

def display_validation_results(result, processing_time, logger):
    """Display validation results in a user-friendly format"""
    
    status = result.get("final_status", "UNKNOWN")
    status_icon = "✅" if status == "APPROVED" else "❌" if status == "REJECTED" else "⚠️"
    
    logger.info(f"📊 VALIDATION RESULTS:")
    logger.info(f"  {status_icon} Final Status: {status}")
    logger.info(f"  ⏱️  Processing Time: {processing_time:.2f} seconds")
    logger.info(f"  🏁 Stages Completed: {len(result.get('stages_completed', []))}/8")
    
    if status == "APPROVED":
        logger.info(f"  🏆 Quality Score: {result.get('quality_score', 'N/A')}")
        logger.info(f"  🎯 Confidence Level: {result.get('confidence_level', 'N/A')}")
        logger.info("  📁 Item moved to: 08-APPROVED_RESEARCH/")
    
    elif status == "REJECTED":
        rejection_reason = result.get("rejection_reason", "Unknown")
        rejection_stage = result.get("rejection_stage", "Unknown")
        logger.info(f"  ❌ Rejection Reason: {rejection_reason}")
        logger.info(f"  🚫 Failed at Stage: {rejection_stage}")
        logger.info("  📁 Item moved to: 09-REJECTED_ITEMS/")
    
    elif status == "ERROR":
        error_message = result.get("error", "Unknown error")
        logger.info(f"  ⚠️  Error: {error_message}")
    
    # Show stage details
    logger.info("  📋 Stage Details:")
    validation_results = result.get("validation_results", {})
    
    stage_names = {
        "00-INTAKE": "Intake Processing",
        "01-INITIAL_SCREENING": "Initial Screening", 
        "02-COMPUTATIONAL_VALIDATION": "Computational Validation",
        "03-MULTI_METHOD_VERIFICATION": "Multi-Method Verification",
        "04-PEER_SIMULATION_REVIEW": "Peer Simulation Review",
        "05-STRESS_TESTING": "Stress Testing",
        "06-REPRODUCIBILITY_VALIDATION": "Reproducibility Validation",
        "07-FINAL_SCIENTIFIC_REVIEW": "Final Scientific Review"
    }
    
    for stage_code, stage_name in stage_names.items():
        if stage_code in validation_results:
            stage_result = validation_results[stage_code]
            stage_status = "✅ PASSED" if stage_result.get("passed", False) else "❌ FAILED"
            logger.info(f"    {stage_status} {stage_name}")
            
            # Show specific details for failed stages
            if not stage_result.get("passed", False) and "failure_reason" in stage_result:
                logger.info(f"      Reason: {stage_result['failure_reason']}")

def save_validation_report(result, item_name, logger):
    """Save detailed validation report to file"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"validation_report_{item_name}_{timestamp}.json"
    
    try:
        with open(report_filename, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        logger.info(f"📄 Detailed report saved: {report_filename}")
        
    except Exception as e:
        logger.warning(f"⚠️  Could not save report: {str(e)}")

def demonstrate_physics_simulation():
    """Demonstrate physics simulation capabilities"""
    logger = logging.getLogger(__name__)
    
    logger.info("🧮 Demonstrating Physics Simulation Capabilities")
    logger.info("-" * 50)
    
    # Initialize MATLAB interface
    matlab_interface = MATLABSimulationInterface()
    
    # Test different physics simulations
    test_cases = [
        {
            "name": "Harmonic Oscillator",
            "description": {"type": "harmonic_oscillator", "frequency": 1.0}
        },
        {
            "name": "Wave Equation",
            "description": {"type": "wave_equation", "wave_speed": 1.0}
        },
        {
            "name": "Heat Equation",
            "description": {"type": "heat_equation", "diffusivity": 0.01}
        },
        {
            "name": "Projectile Motion",
            "description": {"type": "projectile_motion", "initial_velocity": 50, "launch_angle": 45}
        }
    ]
    
    for test_case in test_cases:
        logger.info(f"🔬 Testing: {test_case['name']}")
        
        result = matlab_interface.validate_physics_simulation(test_case["description"])
        
        if result.get("success", False):
            validation_score = result.get("validation_metrics", {}).get("validation_score", 0)
            logger.info(f"  ✅ Simulation successful (Score: {validation_score:.3f})")
            
            # Show key metrics
            sim_results = result.get("simulation_results", {})
            for key, value in sim_results.items():
                if isinstance(value, (int, float)):
                    logger.info(f"    {key}: {value:.4f}")
        else:
            error_msg = result.get("error_message", "Unknown error")
            logger.info(f"  ❌ Simulation failed: {error_msg}")
    
    logger.info("-" * 50)

def show_usage_examples():
    """Show usage examples for AI agents"""
    logger = logging.getLogger(__name__)
    
    logger.info("💡 Usage Examples for AI Agents")
    logger.info("-" * 50)
    
    examples = [
        {
            "title": "Basic Validation",
            "code": """
# Submit research for validation
research_file = "my_research.txt"
shutil.copy(research_file, "VALIDATION_PIPELINE/00-INTAKE/")

# Run validation
os.chdir("VALIDATION_PIPELINE/VALIDATION_TOOLS")
framework = ScientificValidationFramework()
result = framework.validate_research_item("../00-INTAKE/my_research.txt")

# Check result
if result["final_status"] == "APPROVED":
    print("Research validated successfully!")
else:
    print(f"Validation failed: {result['rejection_reason']}")
"""
        },
        {
            "title": "Custom Physics Simulation",
            "code": """
# Run custom physics simulation
matlab_interface = MATLABSimulationInterface()
physics_desc = {
    "type": "harmonic_oscillator",
    "frequency": 2.0,
    "damping": 0.1
}
result = matlab_interface.validate_physics_simulation(physics_desc)
"""
        },
        {
            "title": "Batch Processing",
            "code": """
# Process multiple research items
framework = ScientificValidationFramework()
intake_dir = Path("../00-INTAKE")

for item in intake_dir.iterdir():
    if item.is_file():
        result = framework.validate_research_item(str(item))
        print(f"{item.name}: {result['final_status']}")
"""
        }
    ]
    
    for i, example in enumerate(examples, 1):
        logger.info(f"Example {i}: {example['title']}")
        logger.info("```python")
        logger.info(example['code'].strip())
        logger.info("```")
        logger.info("")

def main():
    """Main demonstration function"""
    # Setup
    logger = setup_logging()
    
    print("🔬 Scientific Validation Pipeline - AI Agent Demonstration")
    print("=" * 70)
    print("This demonstration shows how AI agents can execute rigorous")
    print("scientific validation using computational methods and simulations.")
    print("=" * 70)
    print()
    
    # Check requirements
    if not check_system_requirements():
        return 1
    
    print()
    
    # Show usage examples
    show_usage_examples()
    
    # Demonstrate physics simulations
    demonstrate_physics_simulation()
    
    # Run main validation demo
    demonstrate_validation_pipeline()
    
    print()
    print("📚 For more information, see VALIDATION_PIPELINE/README.md")
    print("🔧 To customize validation criteria, edit VALIDATION_TOOLS/validation_framework.py")
    print("🧮 To add custom simulations, extend VALIDATION_TOOLS/matlab_simulation_interface.py")
    print()
    print("✨ Thank you for using the Scientific Validation Pipeline!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 