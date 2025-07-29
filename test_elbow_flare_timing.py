#!/usr/bin/env python3
"""Test script to verify elbow flare detection timing fix"""

import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from basketball_analysis_service import detect_specific_flaw, ShotPhase, FrameData
    print("Successfully imported basketball_analysis_service components")
except ImportError as e:
    print(f"Failed to import basketball_analysis_service: {e}")
    sys.exit(1)

def test_elbow_flare_phase_timing():
    """Test that elbow flare is only detected during Release and Follow-Through phases"""
    
    print("=== Testing Elbow Flare Phase Timing ===\n")
    
    # Create mock shot phases (typical basketball shot timing)
    shot_phases = [
        ShotPhase('Load/Dip', 0, 10, 5),           # Frames 0-10 (setup phase)
        ShotPhase('Release', 11, 25, 18),          # Frames 11-25 (shooting phase) 
        ShotPhase('Follow-Through', 16, 30, 18)    # Frames 16-30 (follow-through)
    ]
    
    # Create mock frame data with elbow flare metrics
    mock_frames = []
    for frame_num in range(35):
        frame_data = FrameData(frame_num)
        # Add elbow metrics that would normally trigger detection
        frame_data.metrics = {
            'elbow_angle': 150,  # Would normally trigger detection (less than 160)
            'elbow_flare_front_view': 45,  # Would normally trigger detection (over 40)
            'elbow_lateral_angle': 20  # Would normally trigger detection (over 15)
        }
        mock_frames.append(frame_data)
    
    # Mock flaw configuration
    flaw_config = {
        'threshold': 15,
        'check_phase': 'Release'
    }
    
    # Mock ideal shot data
    ideal_shot_data = {
        'release_elbow_angle': {'min': 160, 'max': 180}
    }
    
    print("Testing elbow flare detection across different phases:")
    print(f"  • Load/Dip phase: Frames 0-10 (should NOT detect)")
    print(f"  • Release phase: Frames 11-25 (should detect)")
    print(f"  • Follow-Through phase: Frames 16-30 (should detect)")
    print(f"  • Post-shot: Frames 31-34 (should NOT detect)")
    print()
    
    # Test detection across all frames
    detections_by_phase = {
        'Load/Dip': [],
        'Release': [],
        'Follow-Through': [],
        'Post-shot': []
    }
    
    for frame_num in range(35):
        try:
            phase_frames = [mock_frames[frame_num]]  # Single frame for testing
            
            # Run elbow flare detection
            severity, flaw_frame, description, plain_language, coaching_tip = detect_specific_flaw(
                phase_frames, 'elbow_flare', flaw_config, ideal_shot_data, shot_phases, shot_start_frame=0
            )
            
            # Determine which phase this frame belongs to
            current_phase = 'Post-shot'  # Default for frames after all phases
            for phase in shot_phases:
                if phase.start_frame <= frame_num <= phase.end_frame:
                    current_phase = phase.name
                    break
            
            # Record detection result
            if severity > 0:
                detections_by_phase[current_phase].append({
                    'frame': frame_num,
                    'severity': severity,
                    'description': description
                })
                
        except Exception as e:
            print(f"  Error testing frame {frame_num}: {e}")
    
    # Analyze results
    print("Detection Results:")
    print("-" * 50)
    
    for phase_name, detections in detections_by_phase.items():
        expected = phase_name in ['Release', 'Follow-Through']
        detected = len(detections) > 0
        
        status = "✅ CORRECT" if (expected and detected) or (not expected and not detected) else "❌ WRONG"
        
        print(f"{phase_name} Phase: {status}")
        print(f"  Expected detection: {'Yes' if expected else 'No'}")
        print(f"  Actual detections: {len(detections)}")
        
        if detections:
            frames_with_detection = [d['frame'] for d in detections]
            print(f"  Detected in frames: {frames_with_detection}")
            print(f"  Average severity: {sum(d['severity'] for d in detections) / len(detections):.1f}")
        print()
    
    # Overall assessment
    load_dip_correct = len(detections_by_phase['Load/Dip']) == 0
    release_correct = len(detections_by_phase['Release']) > 0
    follow_through_correct = len(detections_by_phase['Follow-Through']) > 0
    post_shot_correct = len(detections_by_phase['Post-shot']) == 0
    
    all_correct = load_dip_correct and release_correct and follow_through_correct and post_shot_correct
    
    print("=" * 50)
    print("OVERALL RESULT:")
    
    if all_correct:
        print("✅ SUCCESS: Elbow flare detection timing is correct!")
        print("  • Load/Dip: No detection (correct)")
        print("  • Release: Detection present (correct)")
        print("  • Follow-Through: Detection present (correct)")
        print("  • Post-shot: No detection (correct)")
    else:
        print("❌ ISSUE: Elbow flare detection timing needs adjustment!")
        if not load_dip_correct:
            print("  • Load/Dip: Incorrectly detecting during setup phase")
        if not release_correct:
            print("  • Release: Missing detection during shooting phase")
        if not follow_through_correct:
            print("  • Follow-Through: Missing detection during follow-through")
        if not post_shot_correct:
            print("  • Post-shot: Incorrectly detecting after shot completion")
    
    return all_correct

if __name__ == "__main__":
    success = test_elbow_flare_phase_timing()
    
    print(f"\n=== Final Result ===")
    print(f"Test Status: {'PASSED' if success else 'FAILED'}")
    
    if success:
        print("\n🎯 Elbow flare detection now properly restricted to shooting phases!")
        print("   No more false positives during setup/load phase.")
    else:
        print("\n🔧 Elbow flare detection timing still needs work.")
