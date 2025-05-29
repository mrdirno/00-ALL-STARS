#!/usr/bin/env python3
"""
Scientific Validation Pipeline - Direct Execution

Processes all items in the 00-INTAKE folder through the complete validation pipeline.
"""

import os
import sys
from pathlib import Path
import logging

# Add validation tools to path
sys.path.append(str(Path(__file__).parent / "VALIDATION_TOOLS"))

try:
    from validation_framework import ScientificValidationFramework
    print("✅ Successfully imported validation framework")
except ImportError as e:
    print(f"❌ Failed to import validation framework: {e}")
    sys.exit(1)

def setup_logging():
    """Setup logging for validation"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('validation_execution.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def main():
    """Main validation execution"""
    logger = setup_logging()
    
    logger.info("🚀 Starting Scientific Validation Pipeline Execution")
    logger.info("=" * 70)
    
    # Initialize validation framework
    framework = ScientificValidationFramework()
    
    # Get items from intake
    intake_path = Path("00-INTAKE")
    items = list(intake_path.iterdir())
    
    if not items:
        logger.warning("⚠️  No items found in intake directory")
        return
    
    logger.info(f"📋 Found {len(items)} items to validate")
    
    # Process each item
    approved_count = 0
    rejected_count = 0
    error_count = 0
    
    for item in items:
        if item.is_file() and item.suffix in ['.txt', '.html', '.md']:
            logger.info(f"🔬 Processing: {item.name}")
            logger.info("-" * 50)
            
            try:
                # Run validation
                result = framework.validate_research_item(str(item))
                
                # Display results
                status = result.get("final_status", "UNKNOWN")
                
                if status == "APPROVED":
                    approved_count += 1
                    logger.info(f"✅ APPROVED: {item.name}")
                    if "quality_score" in result:
                        logger.info(f"   Quality Score: {result['quality_score']}")
                    if "confidence_level" in result:
                        logger.info(f"   Confidence: {result['confidence_level']}")
                        
                elif status == "REJECTED":
                    rejected_count += 1
                    logger.info(f"❌ REJECTED: {item.name}")
                    if "rejection_reason" in result:
                        logger.info(f"   Reason: {result['rejection_reason']}")
                    if "rejection_stage" in result:
                        logger.info(f"   Failed at: {result['rejection_stage']}")
                        
                else:
                    error_count += 1
                    logger.info(f"⚠️  ERROR: {item.name}")
                    if "error" in result:
                        logger.info(f"   Error: {result['error']}")
                
                # Show stages completed
                stages_completed = result.get("stages_completed", [])
                logger.info(f"   Stages completed: {len(stages_completed)}/8")
                
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Exception processing {item.name}: {str(e)}")
            
            logger.info("-" * 50)
    
    # Summary
    logger.info("📊 VALIDATION SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total items processed: {approved_count + rejected_count + error_count}")
    logger.info(f"✅ Approved: {approved_count}")
    logger.info(f"❌ Rejected: {rejected_count}")
    logger.info(f"⚠️  Errors: {error_count}")
    
    if approved_count > 0:
        logger.info(f"📁 Approved items moved to: 08-APPROVED_RESEARCH/")
    if rejected_count > 0:
        logger.info(f"📁 Rejected items moved to: 09-REJECTED_ITEMS/")
    
    logger.info("🎉 Validation pipeline execution completed!")
    logger.info("=" * 70)

if __name__ == "__main__":
    main() 