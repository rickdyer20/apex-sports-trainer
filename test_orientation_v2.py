#!/usr/bin/env python3
"""
Test script for enhanced orientation detection v2.0
Tests the new multi-heuristic approach to orientation correction
"""

import numpy as np
import cv2
import sys
import os

# Add current directory to path to import the function
sys.path.append('.')
from basketball_analysis_service import detect_and_correct_orientation

def create_test_frame(width, height, content_type="gradient"):
    """Create a test frame with specific dimensions and content"""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    if content_type == "gradient":
        # Create a horizontal gradient
        for x in range(width):
            intensity = int(255 * x / width)
            frame[:, x] = [intensity, intensity//2, 255-intensity]
    
    elif content_type == "vertical_bars":
        # Create vertical bars (strong vertical gradients)
        bar_width = width // 5
        for i in range(5):
            start_x = i * bar_width
            end_x = min((i + 1) * bar_width, width)
            color = [255 if i % 2 == 0 else 0] * 3
            frame[:, start_x:end_x] = color
    
    elif content_type == "basketball_scene":
        # Simulate a basketball court scene (horizontal elements)
        # Court floor (bottom third)
        frame[int(height*0.66):, :] = [139, 69, 19]  # Brown court
        # Sky/background (top third)
        frame[:int(height*0.33), :] = [135, 206, 235]  # Sky blue
        # Player silhouette (middle)
        center_x, center_y = width//2, height//2
        cv2.circle(frame, (center_x, center_y), min(width, height)//10, (0, 0, 0), -1)
    
    return frame

def test_orientation_detection():
    """Test the enhanced orientation detection with various scenarios"""
    print("🧪 Testing Enhanced Orientation Detection v2.0")
    print("=" * 50)
    
    test_cases = [
        # (width, height, expected_rotation, description)
        (1920, 1080, None, "Standard landscape video (16:9)"),
        (1080, 1920, "90° clockwise", "Portrait phone recording"),
        (720, 1280, "90° clockwise", "Portrait HD phone recording"),
        (1080, 1080, None, "Square video (1:1)"),
        (640, 480, None, "Standard 4:3 video"),
        (480, 640, "90° clockwise", "Rotated 4:3 video"),
        (2560, 1440, None, "Wide QHD landscape"),
        (1440, 2560, "90° clockwise", "Portrait QHD"),
        (3840, 2160, None, "4K landscape"),
        (800, 600, None, "Normal 4:3 resolution"),
        (600, 800, "90° clockwise", "Portrait 4:3"),
        (1920, 800, "90° counter-clockwise", "Ultra-wide aspect (2.4:1)"),
    ]
    
    results = []
    
    for width, height, expected, description in test_cases:
        print(f"\n📐 Testing: {description}")
        print(f"   Dimensions: {width}x{height}")
        print(f"   Aspect ratio: {width/height:.2f}")
        print(f"   Expected: {expected or 'No rotation'}")
        
        # Test with different content types
        for content_type in ["gradient", "vertical_bars", "basketball_scene"]:
            test_frame = create_test_frame(width, height, content_type)
            original_shape = test_frame.shape
            
            # Apply orientation detection
            corrected_frame = detect_and_correct_orientation(test_frame)
            new_shape = corrected_frame.shape
            
            # Determine what happened
            if original_shape == new_shape:
                actual_rotation = None
            elif original_shape[0] == new_shape[1] and original_shape[1] == new_shape[0]:
                # Dimensions were swapped - rotation applied
                if original_shape[0] > original_shape[1]:  # Was landscape, now portrait
                    actual_rotation = "90° counter-clockwise"
                else:  # Was portrait, now landscape
                    actual_rotation = "90° clockwise"
            else:
                actual_rotation = "unknown"
            
            match = "✅" if actual_rotation == expected else "❌"
            print(f"   {match} {content_type}: {actual_rotation or 'No rotation'}")
            
            results.append({
                'description': f"{description} ({content_type})",
                'expected': expected,
                'actual': actual_rotation,
                'match': actual_rotation == expected
            })
    
    # Summary
    print(f"\n📊 Test Results Summary")
    print("=" * 30)
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['match'])
    
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {passed_tests/total_tests*100:.1f}%")
    
    # Show failures
    failures = [r for r in results if not r['match']]
    if failures:
        print(f"\n❌ Failed tests:")
        for failure in failures:
            print(f"   • {failure['description']}")
            print(f"     Expected: {failure['expected']}, Got: {failure['actual']}")
    else:
        print(f"\n🎉 All tests passed!")
    
    return passed_tests == total_tests

def test_real_world_scenarios():
    """Test with realistic basketball video scenarios"""
    print(f"\n🏀 Real-world Basketball Video Scenarios")
    print("=" * 40)
    
    # Common phone recording scenarios
    scenarios = [
        {
            'name': 'iPhone vertical recording',
            'width': 1080, 'height': 1920,
            'description': 'User holds phone vertically while recording'
        },
        {
            'name': 'Android vertical recording', 
            'width': 720, 'height': 1280,
            'description': 'Android phone held vertically'
        },
        {
            'name': 'Tablet landscape',
            'width': 1920, 'height': 1080,
            'description': 'Proper landscape orientation'
        },
        {
            'name': 'Rotated tablet',
            'width': 1080, 'height': 1920,
            'description': 'Tablet accidentally held vertically'
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📱 {scenario['name']}")
        print(f"   {scenario['description']}")
        print(f"   Resolution: {scenario['width']}x{scenario['height']}")
        
        # Create basketball court scene
        test_frame = create_test_frame(scenario['width'], scenario['height'], 'basketball_scene')
        
        print(f"   Original dimensions: {test_frame.shape[:2]}")
        corrected = detect_and_correct_orientation(test_frame)
        print(f"   After correction: {corrected.shape[:2]}")
        
        if test_frame.shape != corrected.shape:
            print(f"   ✅ Rotation applied - should improve viewing experience")
        else:
            print(f"   ℹ️  No rotation needed - already properly oriented")

if __name__ == "__main__":
    print("🔧 Enhanced Orientation Detection Test Suite")
    print("=" * 50)
    
    try:
        # Test basic functionality
        success = test_orientation_detection()
        
        # Test real-world scenarios
        test_real_world_scenarios()
        
        print(f"\n🏁 Testing Complete!")
        if success:
            print("✅ Enhanced orientation detection is working correctly")
            print("💡 Ready for deployment with improved sideways video detection")
        else:
            print("⚠️  Some tests failed - review the detection logic")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
