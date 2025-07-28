#!/usr/bin/env python3
"""
Direct Elbow Flare Detection Test
Test the elbow flare detection logic directly without camera angle requirements
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from basketball_analysis_service import detect_specific_flaw, load_ideal_shot_data, FrameData
import json

def test_direct_elbow_detection():
    """Test the detect_specific_flaw function directly"""
    print("🧪 Testing Direct Elbow Flare Detection Logic")
    
    # Load ideal shot data
    ideal_shot_data = load_ideal_shot_data("ideal_shot_guide.json")
    
    # Create mock frame data based on debug output
    phase_frames = []
    
    # Frame 5 data (extreme elbow flare from debug)
    frame5_metrics = {
        'elbow_angle': 76.9,  # Very low extension angle - should trigger
        'elbow_flare_front_view': 105.0,  # Extreme lateral deviation - should trigger  
        'elbow_lateral_angle': 120.3,  # Very high lateral angle - should trigger
        'wrist_angle_simplified': 60
    }
    frame5_data = FrameData(5, None, frame5_metrics)
    phase_frames.append((5, frame5_data))
    
    # Frame 10 data (moderate elbow flare)
    frame10_metrics = {
        'elbow_angle': 157.4,  # Better extension but still issues
        'elbow_flare_front_view': 51.6,  # Below 70% threshold 
        'elbow_lateral_angle': 146.9,  # Very high lateral angle - should trigger
        'wrist_angle_simplified': 65
    }
    frame10_data = FrameData(10, None, frame10_metrics)
    phase_frames.append((10, frame10_data))
    
    # Frame 15 data (mild elbow flare)  
    frame15_metrics = {
        'elbow_angle': 177.5,  # Good extension
        'elbow_flare_front_view': 71.9,  # Just above 70% threshold - should trigger
        'elbow_lateral_angle': 48.5,  # Above 20° threshold - should trigger
        'wrist_angle_simplified': 70
    }
    frame15_data = FrameData(15, None, frame15_metrics)
    phase_frames.append((15, frame15_data))
    
    # Elbow flare configuration
    elbow_flare_config = {
        'description': 'Shooting elbow positioned too far from body',
        'check_phase': 'ANY',
        'threshold': 15,
        'plain_language': 'Your shooting elbow is sticking out too far from your body.'
    }
    
    print(f"📊 Testing with {len(phase_frames)} frames")
    print(f"🎯 Expected triggers:")
    print(f"   Frame 5: elbow_angle=76.9° (<150°), flare_ratio=105.0% (>70%), lateral=120.3° (>20°)")
    print(f"   Frame 10: lateral=146.9° (>20°)")  
    print(f"   Frame 15: flare_ratio=71.9% (>70%), lateral=48.5° (>20°)")
    
    # Test the detection
    flaw_detected, worst_frame, severity = detect_specific_flaw(
        phase_frames, 'elbow_flare', elbow_flare_config, ideal_shot_data
    )
    
    print(f"\n🔍 DETECTION RESULTS:")
    print(f"   Flaw detected: {flaw_detected}")
    print(f"   Worst frame: {worst_frame}")
    print(f"   Severity: {severity:.1f}")
    
    if flaw_detected and severity > 8:  # Our minimum threshold
        print(f"\n✅ SUCCESS! Elbow flare detection is working!")
        print(f"   The system correctly identified the elbow flare")
        print(f"   Severity of {severity:.1f} exceeds minimum threshold of 8")
    else:
        print(f"\n❌ DETECTION FAILED!")
        if not flaw_detected:
            print(f"   No flaw was detected at all")
        else:
            print(f"   Severity {severity:.1f} is below minimum threshold of 8")
        
        # Debug each frame individually
        print(f"\n🔧 DEBUGGING EACH FRAME:")
        for frame_num, frame_data in phase_frames:
            print(f"\n   Frame {frame_num}:")
            severity = 0
            
            # Test side view detection
            if 'elbow_angle' in frame_data.metrics:
                angle = frame_data.metrics['elbow_angle']
                if angle < 150:
                    side_severity = min((150 - angle) * 1.5, 50)
                    severity = max(severity, side_severity)
                    print(f"     Side view: angle={angle:.1f}° -> severity={side_severity:.1f}")
                else:
                    print(f"     Side view: angle={angle:.1f}° (no trigger)")
            
            # Test front view ratio detection
            if 'elbow_flare_front_view' in frame_data.metrics:
                ratio = frame_data.metrics['elbow_flare_front_view']
                if ratio > 70:
                    front_severity = min((ratio - 50) * 1.5, 50)
                    severity = max(severity, front_severity)
                    print(f"     Front ratio: {ratio:.1f}% -> severity={front_severity:.1f}")
                else:
                    print(f"     Front ratio: {ratio:.1f}% (no trigger)")
            
            # Test lateral angle detection
            if 'elbow_lateral_angle' in frame_data.metrics:
                lateral = frame_data.metrics['elbow_lateral_angle']
                if lateral > 20:
                    lateral_severity = min((lateral - 15) * 2.0, 45)
                    severity = max(severity, lateral_severity)
                    print(f"     Lateral angle: {lateral:.1f}° -> severity={lateral_severity:.1f}")
                else:
                    print(f"     Lateral angle: {lateral:.1f}° (no trigger)")
            
            print(f"     Total severity: {severity:.1f}")
    
    return flaw_detected and severity > 8

if __name__ == "__main__":
    success = test_direct_elbow_detection()
    
    if success:
        print(f"\n🎉 DIRECT DETECTION TEST PASSED!")
        print(f"   The elbow flare detection logic is working correctly.")
        print(f"   The issue in your video analysis is likely:")
        print(f"   • Camera angle detection not recognizing front view")
        print(f"   • Visibility requirements not being met")
        print(f"   • Phase detection issues")
    else:
        print(f"\n❌ DETECTION IS STILL BROKEN")
        print(f"   Need to fix the core detection logic")
