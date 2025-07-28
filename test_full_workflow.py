#!/usr/bin/env python3
"""Comprehensive test to simulate full web app PDF workflow"""

import os
import sys
import tempfile
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_generator import generate_improvement_plan_pdf

def test_full_pdf_workflow():
    """Test the full PDF workflow as it happens in web_app.py"""
    
    print("=== Testing Full PDF Workflow ===\n")
    
    # Create test data that simulates real analysis results
    analysis_results = {
        'detailed_flaws': [
            {
                'flaw_type': 'poor_wrist_snap',
                'severity': 42.1,
                'phase': 'Follow-Through',
                'frame_number': 28,
                'plain_language': 'Your wrist snap needs improvement. Snap your wrist down aggressively for better backspin and soft touch.',
                'coaching_tip': 'Snap your wrist down aggressively after release. Your fingers should point to the floor.',
                'description': 'Insufficient wrist snap on follow-through'
            },
            {
                'flaw_type': 'elbow_flare',
                'severity': 31.4,
                'phase': 'Release',
                'frame_number': 25,
                'plain_language': 'Your shooting elbow is positioned too far from your body.',
                'coaching_tip': 'Keep your elbow directly under the ball throughout the shooting motion.',
                'description': 'Shooting elbow flares out instead of staying under ball'
            }
        ],
        'shot_phases': [
            {
                'name': 'Load/Dip',
                'start_frame': 15,
                'end_frame': 20,
                'key_moment_frame': 18,
                'description': 'Player loading up for the shot'
            },
            {
                'name': 'Release',
                'start_frame': 21,
                'end_frame': 30,
                'key_moment_frame': 25,
                'description': 'Ball release phase'
            },
            {
                'name': 'Follow-Through',
                'start_frame': 23,
                'end_frame': 35,
                'key_moment_frame': 25,
                'description': 'Follow-through and wrist snap'
            }
        ],
        'feedback_points': [
            {
                'frame_number': 25,
                'feedback_text': 'Focus on keeping elbow under the ball',
                'feedback_type': 'form_correction',
                'severity': 'medium'
            },
            {
                'frame_number': 28,
                'feedback_text': 'Aggressive wrist snap needed here',
                'feedback_type': 'follow_through',
                'severity': 'high'
            }
        ]
    }
    
    test_job_id = "workflow_test_001"
    
    print(f"Step 1: Test data preparation")
    print(f"  Job ID: {test_job_id}")
    print(f"  Flaws: {len(analysis_results['detailed_flaws'])}")
    print(f"  Phases: {len(analysis_results['shot_phases'])}")
    print(f"  Feedback points: {len(analysis_results['feedback_points'])}")
    
    # Step 2: Generate PDF (as done in basketball_analysis_service.py)
    print(f"\nStep 2: Generating PDF...")
    try:
        improvement_plan_pdf = generate_improvement_plan_pdf(analysis_results, test_job_id)
        
        if improvement_plan_pdf and os.path.exists(improvement_plan_pdf):
            file_size = os.path.getsize(improvement_plan_pdf)
            print(f"  ✅ PDF generated successfully: {improvement_plan_pdf}")
            print(f"  📄 File size: {file_size:,} bytes")
        else:
            print(f"  ❌ PDF generation failed - no file created")
            return False
            
    except Exception as e:
        print(f"  ❌ PDF generation exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Simulate web_app.py file movement logic
    print(f"\nStep 3: Simulating web_app.py file movement...")
    
    RESULTS_FOLDER = "results"  # Same as in web_app.py
    os.makedirs(RESULTS_FOLDER, exist_ok=True)
    
    # Simulate the logic from web_app.py lines 368-379
    improvement_plan_pdf_result = None
    if analysis_results and 'improvement_plan_pdf' not in analysis_results:
        # Add the PDF path to analysis_results (as would be done by basketball_analysis_service.py)
        analysis_results['improvement_plan_pdf'] = improvement_plan_pdf
    
    original_pdf_path = analysis_results.get('improvement_plan_pdf')
    print(f"  Original PDF path: {original_pdf_path}")
    
    if original_pdf_path and os.path.exists(original_pdf_path):
        new_pdf_filename = f"{test_job_id}_60_Day_Improvement_Plan.pdf"
        new_pdf_path = os.path.join(RESULTS_FOLDER, new_pdf_filename)
        
        print(f"  Moving PDF from: {original_pdf_path}")
        print(f"  Moving PDF to: {new_pdf_path}")
        
        try:
            # Use rename (as in web_app.py line 375)
            os.rename(original_pdf_path, new_pdf_path)
            
            improvement_plan_pdf_result = {
                'file_path': new_pdf_path,
                'filename': new_pdf_filename
            }
            
            print(f"  ✅ PDF moved successfully")
            print(f"  📁 Final location: {new_pdf_path}")
            
            # Verify the moved file
            if os.path.exists(new_pdf_path):
                final_size = os.path.getsize(new_pdf_path)
                print(f"  📄 Final file size: {final_size:,} bytes")
            else:
                print(f"  ❌ File not found at final location!")
                return False
                
        except Exception as e:
            print(f"  ❌ File move failed: {e}")
            return False
    else:
        print(f"  ❌ Original PDF path invalid: {original_pdf_path}")
        return False
    
    # Step 4: Simulate results structure
    print(f"\nStep 4: Creating final results structure...")
    
    job_results = {
        'video_path': None,
        'analysis_complete': True,
        'processed_at': datetime.now(),
        'flaw_stills': [],
        'feedback_stills': [],
        'detailed_flaws': analysis_results.get('detailed_flaws', []),
        'shot_phases': analysis_results.get('shot_phases', []),
        'feedback_points': analysis_results.get('feedback_points', []),
        'improvement_plan_pdf': improvement_plan_pdf_result
    }
    
    print(f"  ✅ Final results structure created")
    print(f"  📊 Analysis complete: {job_results['analysis_complete']}")
    print(f"  📄 PDF info: {job_results['improvement_plan_pdf']}")
    
    # Step 5: Verify final state
    print(f"\nStep 5: Final verification...")
    
    if job_results['improvement_plan_pdf']:
        pdf_info = job_results['improvement_plan_pdf']
        pdf_path = pdf_info['file_path']
        
        if os.path.exists(pdf_path):
            size = os.path.getsize(pdf_path)
            print(f"  ✅ PDF exists at final location: {pdf_path}")
            print(f"  📄 Size: {size:,} bytes")
            
            # Clean up
            print(f"  🧹 Cleaning up test file...")
            os.remove(pdf_path)
            
            return True
        else:
            print(f"  ❌ PDF missing at final location: {pdf_path}")
            return False
    else:
        print(f"  ❌ No PDF info in final results")
        return False

if __name__ == "__main__":
    success = test_full_pdf_workflow()
    
    print(f"\n=== Final Result ===")
    print(f"{'✅ PASSED' if success else '❌ FAILED'}: Full PDF workflow test")
    
    if success:
        print(f"\n📋 Summary:")
        print(f"  • PDF generation: Working")
        print(f"  • File movement: Working")
        print(f"  • Results structure: Working")
        print(f"  • Final verification: Working")
        print(f"\n💡 The PDF generation workflow should be working properly!")
    else:
        print(f"\n🔍 The issue may be in a different part of the workflow.")
        print(f"   Check logs and status transitions in the web application.")
