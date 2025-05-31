#!/usr/bin/env python3
"""
Validation Pipeline Runner

This script processes all items in the 00-INTAKE folder through the complete
8-stage validation pipeline using real computational analysis.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add the validation tools directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from validation_framework import ScientificValidationFramework

def main():
    """Main validation pipeline runner"""
    print("=" * 80)
    print("SCIENTIFIC VALIDATION PIPELINE - AUTONOMOUS OPERATION")
    print("=" * 80)
    print(f"Started at: {datetime.utcnow().isoformat()} UTC")
    print()
    
    # Initialize validation framework
    framework = ScientificValidationFramework()
    
    # Find all items in intake folder
    intake_path = Path("../00-INTAKE")
    if not intake_path.exists():
        print(f"ERROR: Intake folder not found at {intake_path}")
        return
    
    # Get all items (files and directories) in intake
    intake_items = []
    for item in intake_path.iterdir():
        if item.name.startswith('.'):
            continue  # Skip hidden files
        intake_items.append(item)
    
    print(f"Found {len(intake_items)} items in intake folder:")
    for i, item in enumerate(intake_items, 1):
        print(f"  {i:2d}. {item.name} ({'DIR' if item.is_dir() else 'FILE'})")
    print()
    
    if not intake_items:
        print("No items found in intake folder. Exiting.")
        return
    
    # Process each item through validation pipeline
    validation_results = []
    
    for i, item in enumerate(intake_items, 1):
        print(f"Processing item {i}/{len(intake_items)}: {item.name}")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            # Run validation
            result = framework.validate_research_item(str(item))
            
            processing_time = time.time() - start_time
            
            # Display results
            print(f"Status: {result['final_status']}")
            print(f"Processing time: {processing_time:.2f} seconds")
            
            if result['final_status'] == 'APPROVED':
                print(f"Quality score: {result.get('quality_score', 'N/A')}")
                print(f"Confidence level: {result.get('confidence_level', 'N/A')}")
                print(f"Destination: {result.get('destination', 'N/A')}")
            elif result['final_status'] == 'REJECTED':
                print(f"Rejection stage: {result.get('rejection_stage', 'N/A')}")
                print(f"Rejection reason: {result.get('rejection_reason', 'N/A')}")
                print(f"Destination: {result.get('destination', 'N/A')}")
            elif result['final_status'] == 'ERROR':
                print(f"Error: {result.get('error', 'N/A')}")
            
            print(f"Stages completed: {len(result.get('stages_completed', []))}")
            
            validation_results.append({
                'item_name': item.name,
                'item_path': str(item),
                'result': result,
                'processing_time': processing_time
            })
            
        except Exception as e:
            print(f"ERROR processing {item.name}: {str(e)}")
            validation_results.append({
                'item_name': item.name,
                'item_path': str(item),
                'result': {'final_status': 'ERROR', 'error': str(e)},
                'processing_time': time.time() - start_time
            })
        
        print()
    
    # Generate summary report
    print("=" * 80)
    print("VALIDATION PIPELINE SUMMARY")
    print("=" * 80)
    
    approved_count = sum(1 for r in validation_results if r['result']['final_status'] == 'APPROVED')
    rejected_count = sum(1 for r in validation_results if r['result']['final_status'] == 'REJECTED')
    error_count = sum(1 for r in validation_results if r['result']['final_status'] == 'ERROR')
    
    print(f"Total items processed: {len(validation_results)}")
    print(f"Approved: {approved_count}")
    print(f"Rejected: {rejected_count}")
    print(f"Errors: {error_count}")
    print()
    
    if approved_count > 0:
        print("APPROVED ITEMS:")
        for result in validation_results:
            if result['result']['final_status'] == 'APPROVED':
                item_result = result['result']
                print(f"  • {result['item_name']}")
                print(f"    Quality: {item_result.get('quality_score', 'N/A'):.1f}")
                print(f"    Confidence: {item_result.get('confidence_level', 'N/A'):.3f}")
                print(f"    Time: {result['processing_time']:.2f}s")
        print()
    
    if rejected_count > 0:
        print("REJECTED ITEMS:")
        for result in validation_results:
            if result['result']['final_status'] == 'REJECTED':
                item_result = result['result']
                print(f"  • {result['item_name']}")
                print(f"    Stage: {item_result.get('rejection_stage', 'N/A')}")
                print(f"    Reason: {item_result.get('rejection_reason', 'N/A')[:100]}...")
                print(f"    Time: {result['processing_time']:.2f}s")
        print()
    
    if error_count > 0:
        print("ERROR ITEMS:")
        for result in validation_results:
            if result['result']['final_status'] == 'ERROR':
                print(f"  • {result['item_name']}")
                print(f"    Error: {result['result'].get('error', 'N/A')[:100]}...")
                print(f"    Time: {result['processing_time']:.2f}s")
        print()
    
    # Save detailed results
    results_file = f"validation_pipeline_results_{int(time.time())}.json"
    results_path = Path("../VALIDATION_REPORTS") / results_file
    results_path.parent.mkdir(exist_ok=True)
    
    with open(results_path, 'w') as f:
        json.dump({
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_items': len(validation_results),
                'approved': approved_count,
                'rejected': rejected_count,
                'errors': error_count
            },
            'detailed_results': validation_results
        }, f, indent=2, default=str)
    
    print(f"Detailed results saved to: {results_path}")
    print()
    
    # Calculate performance metrics
    total_time = sum(r['processing_time'] for r in validation_results)
    avg_time = total_time / len(validation_results) if validation_results else 0
    
    print("PERFORMANCE METRICS:")
    print(f"Total processing time: {total_time:.2f} seconds")
    print(f"Average time per item: {avg_time:.2f} seconds")
    print(f"Items per minute: {60 / avg_time:.1f}" if avg_time > 0 else "N/A")
    print()
    
    print("Validation pipeline completed successfully!")
    print(f"Finished at: {datetime.utcnow().isoformat()} UTC")

if __name__ == "__main__":
    main() 