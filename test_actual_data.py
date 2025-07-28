#!/usr/bin/env python3
"""Test PDF generation with actual failed job data"""

import os
import sys
import json

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_generator import generate_improvement_plan_pdf

def test_with_actual_failed_data():
    """Test PDF generation with the data from the failed job"""
    
    print("=== Testing PDF Generation with Actual Failed Job Data ===\n")
    
    # Load the actual failed job data
    result_file = "jobs/40c2f541-0eaf-46f2-9873-c1491ad074d1_results.json"
    
    if not os.path.exists(result_file):
        print(f"❌ Result file not found: {result_file}")
        return False
    
    try:
        with open(result_file, 'r') as f:
            actual_results = json.load(f)
            
        print(f"Loaded actual results from: {result_file}")
        print(f"Data contains:")
        print(f"  • detailed_flaws: {len(actual_results.get('detailed_flaws', []))}")
        print(f"  • shot_phases: {len(actual_results.get('shot_phases', []))}")
        print(f"  • feedback_points: {len(actual_results.get('feedback_points', []))}")
        
        # Show flaw types
        detailed_flaws = actual_results.get('detailed_flaws', [])
        if detailed_flaws:
            print(f"\nFlaw types detected:")
            for i, flaw in enumerate(detailed_flaws, 1):
                print(f"  {i}. {flaw.get('flaw_type', 'Unknown')} - Severity: {flaw.get('severity', 'N/A')}")
        
        # Test PDF generation with this data
        test_job_id = "actual_data_test"
        
        print(f"\nGenerating PDF with job ID: {test_job_id}")
        
        pdf_path = generate_improvement_plan_pdf(actual_results, test_job_id)
        
        if pdf_path and os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"\n✅ SUCCESS: PDF generated successfully!")
            print(f"   File: {pdf_path}")
            print(f"   Size: {file_size:,} bytes")
            
            # Clean up
            print(f"Cleaning up test file...")
            os.remove(pdf_path)
            
            return True
        else:
            print(f"\n❌ FAILED: PDF generation returned None or file doesn't exist")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_with_actual_failed_data()
    
    print(f"\n=== Result ===")
    if success:
        print("✅ PDF generation works with actual failed job data!")
        print("The issue has been fixed by adding missing flaw type drills.")
    else:
        print("❌ PDF generation still failing - needs further investigation.")
