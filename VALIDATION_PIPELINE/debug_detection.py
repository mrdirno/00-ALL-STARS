#!/usr/bin/env python3
"""
Debug pseudoscience detection
"""

import sys
import os
import re
sys.path.append('VALIDATION_TOOLS')
from validation_framework import ScientificValidationFramework

def main():
    framework = ScientificValidationFramework()
    
    # Test file
    test_file = '09-REJECTED_ITEMS/quantum-vacuum-fluctuations.html'
    
    print(f"Debugging pseudoscience detection for: {test_file}")
    print("=" * 60)
    
    if os.path.exists(test_file):
        content = framework.read_item_content(test_file)
        print(f"Content length: {len(content)} characters")
        
        # Manual search for breakthrough claims
        breakthrough_matches = re.findall(r'breakthrough', content, re.IGNORECASE)
        discovery_matches = re.findall(r'discovery', content, re.IGNORECASE)
        
        print(f"\nManual search results:")
        print(f"'breakthrough' found: {len(breakthrough_matches)} times")
        print(f"'discovery' found: {len(discovery_matches)} times")
        
        if breakthrough_matches:
            print(f"First few breakthrough matches: {breakthrough_matches[:3]}")
        
        # Test the detection method
        print(f"\nTesting detection method:")
        pseudoscience_result = framework.detect_pseudoscientific_claims(content)
        print(f"Detection result: {pseudoscience_result}")
        
        # Check specific patterns
        print(f"\nTesting specific patterns:")
        patterns = [
            (r"major breakthrough", "Major breakthrough claims"),
            (r"breakthrough", "Any breakthrough claims"),
            (r"novel discovery", "Novel discovery claims"),
            (r"discovery", "Any discovery claims"),
            (r"quantum-cosmic resonance", "Quantum-cosmic resonance"),
            (r"unified.*field.*theory", "Unified field theory")
        ]
        
        for pattern, description in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            print(f"  {description}: {len(matches)} matches")
            if matches and len(matches) <= 3:
                print(f"    Examples: {matches}")
            elif matches:
                print(f"    Examples: {matches[:3]} (and {len(matches)-3} more)")
    
    else:
        print(f"File not found: {test_file}")

if __name__ == "__main__":
    main() 