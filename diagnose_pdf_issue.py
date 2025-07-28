"""
Diagnostic test to identify PDF generation issues
"""
import logging
import traceback
from pdf_generator import generate_improvement_plan_pdf

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_pdf_generation_with_realistic_data():
    """Test PDF generation with realistic analysis data that should work"""
    
    print("🔍 DIAGNOSTIC TEST: PDF Generation Issue")
    print("=" * 60)
    
    # Create realistic analysis data similar to what the system would generate
    realistic_analysis_results = {
        'detailed_flaws': [
            {
                'flaw_type': 'elbow_flare',
                'severity': 32.5,
                'phase': 'Release', 
                'frame_number': 28,
                'plain_language': 'Your shooting elbow is positioned too far from your body.',
                'coaching_tip': 'Keep your elbow directly under the ball throughout the shooting motion.',
                'drill_suggestion': 'Practice wall shooting drill to maintain proper elbow alignment.',
                'description': 'Shooting elbow positioned too far from body'
            },
            {
                'flaw_type': 'shot_timing_inefficient',
                'severity': 28.3,
                'phase': 'Load/Dip',
                'frame_number': 15,
                'plain_language': 'Your shot timing could be more efficient.',
                'coaching_tip': 'Focus on smooth rhythm from catch to release.',
                'drill_suggestion': 'Practice metronome shooting for consistent timing.',
                'description': 'Inefficient timing in shooting motion'
            },
            {
                'flaw_type': 'guide_hand_under_ball',
                'severity': 24.7,
                'phase': 'Load/Dip',
                'frame_number': 12,
                'plain_language': 'Your guide hand is positioned under the ball instead of on the side.',
                'coaching_tip': 'Position your guide hand on the side of the ball.',
                'drill_suggestion': 'Tennis ball drill to train proper guide hand placement.',
                'description': 'Guide hand incorrectly positioned under ball'
            }
        ],
        'shot_phases': [
            {'name': 'Load/Dip', 'start_frame': 10, 'end_frame': 20, 'key_moment_frame': 15},
            {'name': 'Release', 'start_frame': 25, 'end_frame': 35, 'key_moment_frame': 30},
            {'name': 'Follow-Through', 'start_frame': 36, 'end_frame': 45, 'key_moment_frame': 40}
        ],
        'feedback_points': [
            {
                'frame_number': 28,
                'discrepancy': 'Elbow Flare: Elbow positioned too far from body',
                'ideal_range': 'Severity: 32.5/100',
                'user_value': 'Your shooting elbow is sticking out too far from your body. This reduces accuracy and consistency.',
                'remedy_tips': 'Keep your elbow directly under the ball throughout the shooting motion.'
            },
            {
                'frame_number': 15,
                'discrepancy': 'Shot Timing Inefficient: Timing could be improved',
                'ideal_range': 'Severity: 28.3/100', 
                'user_value': 'Your shot timing could be more efficient.',
                'remedy_tips': 'Focus on smooth rhythm from catch to release.'
            }
        ]
    }
    
    job_id = "diagnostic_test_" + str(int(time.time()))
    
    print(f"📊 Test Data Summary:")
    print(f"   • Flaws: {len(realistic_analysis_results['detailed_flaws'])}")
    print(f"   • Shot Phases: {len(realistic_analysis_results['shot_phases'])}")
    print(f"   • Feedback Points: {len(realistic_analysis_results['feedback_points'])}")
    print(f"   • Job ID: {job_id}")
    
    print(f"\n🔧 Attempting PDF Generation...")
    
    try:
        # Test the PDF generation
        pdf_path = generate_improvement_plan_pdf(realistic_analysis_results, job_id)
        
        if pdf_path:
            import os
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                print(f"✅ SUCCESS: PDF generated successfully!")
                print(f"   📁 Path: {pdf_path}")
                print(f"   📊 Size: {file_size:,} bytes")
                return True
            else:
                print(f"❌ ERROR: Function returned path but file doesn't exist: {pdf_path}")
                return False
        else:
            print(f"❌ ERROR: PDF generation function returned None")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        print(f"📋 Traceback:")
        traceback.print_exc()
        return False

def test_minimal_data():
    """Test PDF generation with minimal but valid data"""
    
    print(f"\n🧪 Testing with minimal data...")
    
    minimal_data = {
        'detailed_flaws': [
            {
                'flaw_type': 'elbow_flare',
                'severity': 25.0,
                'phase': 'Release',
                'frame_number': 30,
                'plain_language': 'Elbow flare detected.',
                'coaching_tip': 'Keep elbow under ball.',
                'description': 'Elbow positioning issue'
            }
        ],
        'shot_phases': [],
        'feedback_points': []
    }
    
    try:
        pdf_path = generate_improvement_plan_pdf(minimal_data, "minimal_test")
        if pdf_path:
            print(f"✅ Minimal data test: SUCCESS")
            return True
        else:
            print(f"❌ Minimal data test: FAILED")
            return False
    except Exception as e:
        print(f"❌ Minimal data test: EXCEPTION - {e}")
        return False

if __name__ == "__main__":
    import time
    
    print("Starting comprehensive PDF generation diagnostics...\n")
    
    # Test 1: Realistic data
    success1 = test_pdf_generation_with_realistic_data()
    
    # Test 2: Minimal data
    success2 = test_minimal_data()
    
    print(f"\n📋 DIAGNOSTIC SUMMARY:")
    print(f"   Realistic Data Test: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"   Minimal Data Test: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 and success2:
        print(f"\n🎉 PDF generation is working correctly!")
        print(f"   The issue may be with the data being passed to the function.")
    else:
        print(f"\n💥 PDF generation has issues that need to be addressed.")
        print(f"   Check the error messages above for details.")
