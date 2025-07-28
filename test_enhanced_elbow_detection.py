#!/usr/bin/env python3
"""
Test Enhanced Elbow Flare Detection
Test the updated elbow flare detection system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from basketball_analysis_service import (
    analyze_detailed_flaws,
    detect_camera_angle_and_visibility,
    load_ideal_shot_data,
    FrameData,
    ShotPhase
)
import json

def test_elbow_flare_detection():
    """Test the elbow flare detection with mock data based on the debug output"""
    print("🧪 Testing Enhanced Elbow Flare Detection")
    
    # Load ideal shot data
    ideal_shot_data = load_ideal_shot_data("ideal_shot_guide.json")
    
    # Create mock frame data based on debug output
    mock_frames = []
    
    # Frame 5 data (extreme elbow flare from debug)
    frame5_metrics = {
        'elbow_angle': 76.9,  # Very low extension angle
        'elbow_flare_front_view': 105.0,  # Extreme lateral deviation
        'elbow_lateral_angle': 120.3,  # Very high lateral angle
        'wrist_angle_simplified': 60
    }
    
    # Create mock landmarks (we'll use None since we're just testing metrics)
    frame5_data = FrameData(5, None, frame5_metrics)
    mock_frames.append(frame5_data)
    
    # Frame 10 data (moderate elbow flare)
    frame10_metrics = {
        'elbow_angle': 157.4,  # Better extension but still issues
        'elbow_flare_front_view': 51.6,  # Moderate lateral deviation
        'elbow_lateral_angle': 146.9,  # High lateral angle
        'wrist_angle_simplified': 65
    }
    frame10_data = FrameData(10, None, frame10_metrics)
    mock_frames.append(frame10_data)
    
    # Frame 15 data (mild elbow flare)
    frame15_metrics = {
        'elbow_angle': 177.5,  # Good extension
        'elbow_flare_front_view': 71.9,  # Just above threshold
        'elbow_lateral_angle': 48.5,  # Moderate lateral angle
        'wrist_angle_simplified': 70
    }
    frame15_data = FrameData(15, None, frame15_metrics)
    mock_frames.append(frame15_data)
    
    # Create mock shot phases
    shot_phases = [
        ShotPhase('Load/Dip', 0, 5),
        ShotPhase('Release', 6, 10),
        ShotPhase('Follow-Through', 11, 15)
    ]
    
    print(f"📊 Created {len(mock_frames)} mock frames with elbow flare data")
    print(f"🎬 Created {len(shot_phases)} shot phases")
    
    # Run the analysis
    detailed_flaws = analyze_detailed_flaws(mock_frames, ideal_shot_data, shot_phases, 30.0)
    
    print(f"\n🔍 ANALYSIS RESULTS:")
    print(f"   Total flaws detected: {len(detailed_flaws)}")
    
    # Check if elbow flare was detected
    elbow_flare_detected = False
    for flaw in detailed_flaws:
        if flaw['flaw_type'] == 'elbow_flare':
            elbow_flare_detected = True
            print(f"\n✅ ELBOW FLARE DETECTED!")
            print(f"   Phase: {flaw['phase']}")
            print(f"   Severity: {flaw['severity']:.1f}")
            print(f"   Frame: {flaw['frame_number']}")
            print(f"   Description: {flaw['plain_language']}")
            print(f"   Camera Context: {flaw['camera_context']}")
            break
    
    if not elbow_flare_detected:
        print(f"\n❌ ELBOW FLARE NOT DETECTED - Still have issues!")
        print(f"   All detected flaws: {[f['flaw_type'] for f in detailed_flaws]}")
        
        # Debug: Print frame metrics
        print(f"\n🔧 DEBUG INFO:")
        for i, frame in enumerate(mock_frames):
            print(f"   Frame {frame.frame_number}: {frame.metrics}")
    else:
        print(f"\n🎉 SUCCESS! The enhanced elbow flare detection is working!")
        
    return elbow_flare_detected

def test_camera_angle_detection():
    """Test camera angle detection with mock data"""
    print(f"\n📷 Testing Camera Angle Detection")
    
    # Since we don't have real landmarks, we'll assume front view detection works
    # The real test would be with actual MediaPipe landmarks
    print(f"   Camera angle detection requires real MediaPipe landmarks")
    print(f"   In your video, it should detect 'front_view' based on both hands being visible")
    
if __name__ == "__main__":
    elbow_detected = test_elbow_flare_detection()
    test_camera_angle_detection()
    
    if elbow_detected:
        print(f"\n✅ ENHANCED ELBOW FLARE DETECTION IS READY!")
        print(f"   The system should now detect the obvious elbow flare in your video.")
        print(f"   Key improvements made:")
        print(f"   • Elbow flare checked in ALL phases (not just Release)")
        print(f"   • Lowered detection thresholds (70% flare ratio, 20° lateral angle, 150° extension)")
        print(f"   • Reduced minimum evidence frames requirement")
        print(f"   • Lowered severity thresholds for reporting")
    else:
        print(f"\n❌ STILL ISSUES WITH DETECTION")
        print(f"   Need to investigate further...")
