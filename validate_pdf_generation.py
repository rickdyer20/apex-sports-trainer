#!/usr/bin/env python3
"""
PDF Generation Validation
Ensures PDF generation works correctly after fixes
"""

import logging
import sys
import os

# Configure logging to avoid Unicode errors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_validation.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def validate_pdf_generation():
    """Validate PDF generation with various data scenarios"""
    from pdf_generator import generate_improvement_plan_pdf
    
    print("🏀 Basketball Analysis PDF Validation")
    print("=" * 50)
    
    test_cases = [
        {
            'name': 'Full Analysis Data',
            'data': {
                'detailed_flaws': [
                    {
                        'flaw_type': 'elbow_flare',
                        'severity': 25.5,
                        'phase': 'Release',
                        'frame_number': 42,
                        'plain_language': 'Your shooting elbow is positioned too far from your body.',
                        'coaching_tip': 'Keep your elbow directly under the ball.'
                    }
                ],
                'shot_phases': [{'phase': 'Release', 'start_frame': 30, 'end_frame': 45}],
                'feedback_points': [{'category': 'Elbow', 'message': 'Focus on elbow position'}]
            }
        },
        {
            'name': 'Missing Optional Fields',
            'data': {
                'detailed_flaws': [
                    {
                        'flaw_type': 'guide_hand_thumb_flick',
                        'severity': 18.2
                        # Missing optional fields like plain_language, coaching_tip
                    }
                ],
                'shot_phases': [],
                'feedback_points': []
            }
        },
        {
            'name': 'Minimal Data',
            'data': {
                'detailed_flaws': [{'flaw_type': 'unknown_flaw'}],  # Missing severity
                'shot_phases': [],
                'feedback_points': []
            }
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        try:
            job_id = f"validation_test_{i}"
            result = generate_improvement_plan_pdf(test_case['data'], job_id)
            
            if result and os.path.exists(result):
                size = os.path.getsize(result)
                print(f"✅ PDF generated: {result}")
                print(f"📊 Size: {size:,} bytes")
                
                # Clean up test file
                os.remove(result)
                passed += 1
            else:
                print(f"❌ PDF generation failed")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All PDF generation tests PASSED!")
        print("🎉 PDF generation is working correctly for Bill front video analysis")
        return True
    else:
        print("❌ Some tests failed - PDF generation needs attention")
        return False

if __name__ == "__main__":
    success = validate_pdf_generation()
    sys.exit(0 if success else 1)
