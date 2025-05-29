#!/usr/bin/env python3
"""
Test validation script for quantum cosmic resonance framework
"""

import sys
import os
sys.path.append('VALIDATION_TOOLS')

from validation_framework import ScientificValidationFramework

def main():
    # Initialize framework
    framework = ScientificValidationFramework()
    
    # Run validation
    item_path = '../knowledge_base/synthesis/quantum_cosmic_resonance_framework_synthesis.md'
    result = framework.validate_research_item(item_path)
    
    print("=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)
    print(f"Status: {result['final_status']}")
    print(f"Stages completed: {result['stages_completed']}")
    
    if result['final_status'] == 'REJECTED':
        print(f"Rejection reason: {result.get('rejection_reason', 'N/A')}")
        print(f"Rejection stage: {result.get('rejection_stage', 'N/A')}")
    else:
        print(f"Quality score: {result.get('quality_score', 'N/A')}")
        print(f"Confidence level: {result.get('confidence_level', 'N/A')}")
    
    # Print detailed results
    print("\nDetailed Results:")
    for stage, stage_result in result.get('validation_results', {}).items():
        print(f"\n{stage}:")
        if isinstance(stage_result, dict):
            for key, value in stage_result.items():
                print(f"  {key}: {value}")
    
    return result

if __name__ == "__main__":
    main() 