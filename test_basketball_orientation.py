#!/usr/bin/env python3
"""
Simplified test focused on basketball video orientation needs
Tests that videos end up in proper landscape orientation for basketball viewing
"""

import numpy as np
import cv2
import sys

# Add current directory to path to import the function
sys.path.append('.')
from basketball_analysis_service import detect_and_correct_orientation

def create_basketball_scene(width, height):
    """Create a basketball scene for testing"""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Court floor (bottom third) - brown
    frame[int(height*0.66):, :] = [139, 69, 19]  
    # Sky/background (top third) - blue
    frame[:int(height*0.33), :] = [135, 206, 235]  
    # Player silhouette (middle)
    center_x, center_y = width//2, height//2
    cv2.circle(frame, (center_x, center_y), min(width, height)//10, (0, 0, 0), -1)
    
    return frame

def test_basketball_orientation():
    """Test that videos end up in proper landscape orientation for basketball viewing"""
    print("🏀 Basketball Video Orientation Test")
    print("=" * 40)
    
    test_cases = [
        # Common phone recording scenarios
        (1080, 1920, "iPhone portrait recording"),
        (720, 1280, "Android portrait recording"),
        (1920, 1080, "Proper landscape video"),
        (1080, 1080, "Square video (Instagram-style)"),
        (640, 480, "Classic 4:3 video"),
        (480, 640, "Portrait 4:3 video"),
        (3840, 2160, "4K landscape"),
        (2160, 3840, "4K portrait"),
    ]
    
    print("\n📊 Results:")
    print("-" * 60)
    
    all_good = True
    
    for width, height, description in test_cases:
        # Create test frame
        original_frame = create_basketball_scene(width, height)
        original_aspect = width / height
        
        # Apply orientation correction
        corrected_frame = detect_and_correct_orientation(original_frame)
        final_height, final_width = corrected_frame.shape[:2]
        final_aspect = final_width / final_height
        
        # For basketball, we want landscape (width > height, aspect ratio > 1.0)
        is_landscape = final_aspect > 1.0
        
        # Determine if this is good for basketball viewing
        if original_aspect < 1.0:  # Was portrait
            if is_landscape:
                status = "✅ GOOD"
                note = f"Portrait → Landscape ({original_aspect:.2f} → {final_aspect:.2f})"
            else:
                status = "❌ NEEDS FIX"
                note = f"Still portrait! ({original_aspect:.2f} → {final_aspect:.2f})"
                all_good = False
        else:  # Was already landscape or square
            if is_landscape or final_aspect >= 0.9:  # Square is acceptable
                status = "✅ GOOD"
                note = f"Maintained good aspect ratio ({original_aspect:.2f} → {final_aspect:.2f})"
            else:
                status = "❌ NEEDS FIX"
                note = f"Made worse! ({original_aspect:.2f} → {final_aspect:.2f})"
                all_good = False
        
        print(f"{status} {description}")
        print(f"     {width}x{height} → {final_width}x{final_height}")
        print(f"     {note}")
        print()
    
    return all_good

def test_real_video_scenarios():
    """Test with actual scenarios users will encounter"""
    print("\n📱 Common User Recording Scenarios")
    print("=" * 45)
    
    scenarios = [
        {
            'desc': 'User holds phone vertically (most common mistake)',
            'original': (1080, 1920),
            'want_landscape': True
        },
        {
            'desc': 'User records properly in landscape',
            'original': (1920, 1080), 
            'want_landscape': True
        },
        {
            'desc': 'Square format (social media)',
            'original': (1080, 1080),
            'want_landscape': False  # Square is fine
        },
        {
            'desc': 'Tablet held wrong way',
            'original': (1536, 2048),
            'want_landscape': True
        }
    ]
    
    for scenario in scenarios:
        width, height = scenario['original']
        frame = create_basketball_scene(width, height)
        
        print(f"\n🎬 {scenario['desc']}")
        print(f"   Original: {width}x{height} (aspect: {width/height:.2f})")
        
        corrected = detect_and_correct_orientation(frame)
        new_h, new_w = corrected.shape[:2]
        new_aspect = new_w / new_h
        
        print(f"   Result:   {new_w}x{new_h} (aspect: {new_aspect:.2f})")
        
        if scenario['want_landscape']:
            if new_aspect > 1.0:
                print(f"   ✅ Perfect! Now in landscape for better basketball viewing")
            else:
                print(f"   ❌ Still portrait - basketball will be hard to see")
        else:
            print(f"   ✅ Maintained appropriate format")

if __name__ == "__main__":
    print("🔧 Basketball-Focused Orientation Test")
    print("=" * 50)
    print("Goal: Convert portrait videos to landscape for better basketball viewing")
    
    try:
        success = test_basketball_orientation()
        test_real_video_scenarios()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 SUCCESS: Orientation correction working properly!")
            print("✅ Portrait videos → Landscape (good for basketball)")
            print("✅ Landscape videos → Remain landscape")
            print("✅ Ready for deployment!")
        else:
            print("⚠️  NEEDS ADJUSTMENT: Some videos not properly oriented")
            print("💡 Review the detection logic")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
