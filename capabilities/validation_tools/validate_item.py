#!/usr/bin/env python3
"""
Simple validation script to process pending items
"""

from validation_framework import ScientificValidationFramework
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 validate_item.py <item_path>")
        return
    
    item_path = sys.argv[1]
    framework = ScientificValidationFramework()
    
    print(f"Validating: {item_path}")
    result = framework.validate_research_item(item_path)
    
    print(f"Final Status: {result['final_status']}")
    print(f"Stages Completed: {len(result['stages_completed'])}")
    
    if result['final_status'] == 'APPROVED':
        print(f"Quality Score: {result.get('quality_score', 'N/A')}")
        print(f"Confidence Level: {result.get('confidence_level', 'N/A')}")
    elif result['final_status'] == 'REJECTED':
        print(f"Rejection Stage: {result.get('rejection_stage', 'N/A')}")
        print(f"Rejection Reason: {result.get('rejection_reason', 'N/A')}")
    
    return result

if __name__ == "__main__":
    main() 