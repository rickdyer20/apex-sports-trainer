#!/usr/bin/env python3
"""Test script to verify PDF generation works with all flaw types"""

import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_generator import generate_improvement_plan_pdf

def test_pdf_generation():
    """Test PDF generation with various flaw types"""
    
    # Test data with multiple flaw types including the previously missing ones
    test_analysis_results = {
        'detailed_flaws': [
            {
                'flaw_type': 'poor_wrist_snap',
                'severity': 35.2,
                'phase': 'Follow-Through',
                'frame_number': 28,
                'plain_language': 'Your wrist snap needs improvement. Snap your wrist down aggressively for better backspin and soft touch.',
                'coaching_tip': 'Snap your wrist down aggressively after release. Your fingers should point to the floor.',
                'description': 'Insufficient wrist snap on follow-through'
            },
            {
                'flaw_type': 'elbow_flare',
                'severity': 28.7,
                'phase': 'Release',
                'frame_number': 25,
                'plain_language': 'Your shooting elbow is positioned too far from your body.',
                'coaching_tip': 'Keep your elbow directly under the ball.',
                'description': 'Shooting elbow flares out instead of staying under ball'
            },
            {
                'flaw_type': 'guide_hand_thumb_flick',
                'severity': 22.4,
                'phase': 'Follow-Through',
                'frame_number': 30,
                'plain_language': 'Your guide hand thumb is interfering with the shot during follow-through. Keep your thumb passive - no flicking motion.',
                'coaching_tip': 'Keep your guide hand passive during follow-through.',
                'description': 'Guide hand thumb interfering with ball trajectory'
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
    
    test_job_id = "test_pdf_001"
    
    print(f"Testing PDF generation with job ID: {test_job_id}")
    print(f"Test data includes {len(test_analysis_results['detailed_flaws'])} flaws:")
    for flaw in test_analysis_results['detailed_flaws']:
        print(f"  - {flaw['flaw_type']} (severity: {flaw['severity']})")
    
    try:
        pdf_path = generate_improvement_plan_pdf(test_analysis_results, test_job_id)
        
        if pdf_path and os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"\n✅ SUCCESS: PDF generated successfully!")
            print(f"   File: {pdf_path}")
            print(f"   Size: {file_size:,} bytes")
            
            # Additional validation
            if file_size > 10000:  # At least 10KB for a proper PDF
                print(f"✅ File size looks good ({file_size:,} bytes)")
            else:
                print(f"⚠️  File size seems small ({file_size:,} bytes) - might be incomplete")
                
            return True
        else:
            print(f"\n❌ FAILED: PDF generation returned None or file doesn't exist")
            print(f"   Expected path: {pdf_path}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: PDF generation failed with exception:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== PDF Generation Test ===\n")
    
    success = test_pdf_generation()
    
    print(f"\n=== Test Result ===")
    if success:
        print("✅ PDF generation test PASSED")
        
        # Clean up test file
        test_file = os.path.join("results", "60_Day_Improvement_Plan_test_pdf_001.pdf")
        if os.path.exists(test_file):
            print(f"Cleaning up test file: {test_file}")
            os.remove(test_file)
            
    else:
        print("❌ PDF generation test FAILED")
        
    print(f"Status: {'PASS' if success else 'FAIL'}")
