#!/usr/bin/env python3
"""
Check approved research items for pseudoscientific claims
"""

import sys
import os
sys.path.append('VALIDATION_TOOLS')
from validation_framework import ScientificValidationFramework

def main():
    # Initialize framework
    framework = ScientificValidationFramework()
    
    # Check approved items
    approved_dir = '08-APPROVED_RESEARCH'
    rejected_dir = '09-REJECTED_ITEMS'
    
    print("VALIDATION PIPELINE: Checking approved items for pseudoscientific claims")
    print("=" * 70)
    
    items_to_reject = []
    
    if os.path.exists(approved_dir):
        for item in os.listdir(approved_dir):
            if item.endswith('.json'):
                print(f"\nChecking approved item: {item}")
                
                # Extract original file name
                original_name = item.replace('_final_scientific_review_validation.json', '.html')
                rejected_path = os.path.join(rejected_dir, original_name)
                
                if os.path.exists(rejected_path):
                    print(f"Found original file: {rejected_path}")
                    
                    # Read content and check for pseudoscientific claims
                    content = framework.read_item_content(rejected_path)
                    pseudoscience_result = framework.detect_pseudoscientific_claims(content)
                    
                    print(f"Pseudoscience violations found: {pseudoscience_result['violation_count']}")
                    print(f"Is pseudoscientific: {pseudoscience_result['is_pseudoscientific']}")
                    
                    if pseudoscience_result['is_pseudoscientific']:
                        print("❌ SHOULD BE REJECTED - Contains pseudoscientific claims:")
                        for violation in pseudoscience_result['violations_found']:
                            print(f"  - {violation['description']}: {violation['count']} instances")
                        items_to_reject.append(item)
                    else:
                        print("✅ VALID - No pseudoscientific claims detected")
                else:
                    print(f"⚠️  Original file not found: {rejected_path}")
    
    print("\n" + "=" * 70)
    print("SUMMARY:")
    print(f"Total approved items checked: {len(os.listdir(approved_dir)) if os.path.exists(approved_dir) else 0}")
    print(f"Items that should be rejected: {len(items_to_reject)}")
    
    if items_to_reject:
        print("\nItems requiring rejection:")
        for item in items_to_reject:
            print(f"  - {item}")
        
        print("\nRecommendation: Remove these items from approved research")
        print("Reason: Contains pseudoscientific claims that violate scientific integrity requirements")

if __name__ == "__main__":
    main() 