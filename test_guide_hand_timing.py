#!/usr/bin/env python3
"""Test to verify guide hand detection timing improvements"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=== Guide Hand Detection Timing Test ===")

try:
    from basketball_analysis_service import detect_specific_flaw, ShotPhase, FrameData
    print("✅ Successfully imported basketball_analysis_service components")
    
    # Create shot phases with realistic basketball timing
    fps = 30
    shot_phases = [
        ShotPhase('Load/Dip', 0, 15, 15),           # Frames 0-15
        ShotPhase('Release', 16, 24, 20),           # Frames 16-24, peak at frame 20
        ShotPhase('Follow-Through', 18, 30, 20)     # Frames 18-30, overlaps with release
    ]
    
    print(f"✅ Created shot phases with Release phase ending at frame 24")
    print(f"   Release peak: frame 20")
    print(f"   Should only analyze guide hand within ±3 frames of peak (frames 17-23)")
    print()
    
    # Test guide hand configuration
    flaw_config = {
        'threshold': 25,
        'check_phase': 'Release'
    }
    
    ideal_shot_data = {
        'release_elbow_angle': {'min': 160, 'max': 180}
    }
    
    # Test frames at different distances from release point
    test_cases = [
        {
            'frame': 17, 
            'description': 'Core release moment (3 frames before peak)',
            'should_analyze': True,
            'guide_hand_angle': 45  # Under ball (should detect)
        },
        {
            'frame': 20, 
            'description': 'Peak release moment',
            'should_analyze': True,
            'guide_hand_angle': 45  # Under ball (should detect)
        },
        {
            'frame': 23, 
            'description': 'End of release moment (3 frames after peak)',
            'should_analyze': True,
            'guide_hand_angle': 45  # Under ball (should detect)
        },
        {
            'frame': 26, 
            'description': 'Post-release (6 frames after peak, hands dropping)',
            'should_analyze': False,
            'guide_hand_angle': 30  # Would normally trigger, but should be skipped
        },
        {
            'frame': 29, 
            'description': 'Late follow-through (9 frames after peak)',
            'should_analyze': False,
            'guide_hand_angle': 20  # Hands by side, should be skipped
        }
    ]
    
    print("Testing guide hand detection at different timing points:")
    print("-" * 60)
    
    results = []
    
    for test_case in test_cases:
        frame_num = test_case['frame']
        description = test_case['description']
        should_analyze = test_case['should_analyze']
        guide_angle = test_case['guide_hand_angle']
        
        print(f"\nFrame {frame_num}: {description}")
        print(f"  Guide hand angle: {guide_angle}° (45°+ = under ball issue)")
        print(f"  Should analyze: {'Yes' if should_analyze else 'No (too far from release)'}")
        
        # Create frame data
        frame_data = FrameData(frame_num, {}, {
            'guide_hand_position_angle': guide_angle
        })
        
        try:
            # Run detection
            flaw_detected, worst_frame, worst_severity = detect_specific_flaw(
                [(frame_num, frame_data)], 'guide_hand_under_ball', flaw_config, ideal_shot_data, shot_phases, shot_start_frame=0
            )
            
            # Analyze result
            if should_analyze:
                if flaw_detected:
                    status = "✅ CORRECT - Detected guide hand issue during release"
                    result_type = "correct_detection"
                else:
                    status = "⚠️ UNEXPECTED - Should have detected issue but didn't"
                    result_type = "missed_detection"
            else:
                if not flaw_detected:
                    status = "✅ CORRECT - Skipped post-release analysis"  
                    result_type = "correct_skip"
                else:
                    status = "❌ WRONG - Detected issue during post-release (too strict!)"
                    result_type = "false_positive"
            
            print(f"  Result: {status}")
            if flaw_detected:
                print(f"  Severity: {worst_severity}, Frame: {worst_frame}")
            
            results.append({
                'frame': frame_num,
                'expected_analysis': should_analyze,
                'detected': flaw_detected,
                'result_type': result_type,
                'description': description
            })
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results.append({
                'frame': frame_num,
                'expected_analysis': should_analyze,
                'detected': False,
                'result_type': 'error',
                'error': str(e)
            })
    
    # Summary
    print("\n" + "="*60)
    print("GUIDE HAND TIMING TEST RESULTS:")
    print("="*60)
    
    correct_results = [r for r in results if r['result_type'] in ['correct_detection', 'correct_skip']]
    false_positives = [r for r in results if r['result_type'] == 'false_positive']
    missed_detections = [r for r in results if r['result_type'] == 'missed_detection']
    
    print(f"\n✅ Correct Results: {len(correct_results)}/{len(results)}")
    for result in correct_results:
        action = "Detected" if result['detected'] else "Skipped"
        print(f"   • Frame {result['frame']}: {action} ({result['description']})")
    
    if false_positives:
        print(f"\n❌ False Positives: {len(false_positives)}")
        for result in false_positives:
            print(f"   • Frame {result['frame']}: Incorrectly detected ({result['description']})")
    
    if missed_detections:
        print(f"\n⚠️ Missed Detections: {len(missed_detections)}")
        for result in missed_detections:
            print(f"   • Frame {result['frame']}: Should have detected ({result['description']})")
    
    print("\n" + "="*60)
    
    if len(correct_results) == len(results):
        print("🎯 SUCCESS: Guide hand detection timing is now properly restricted!")
        print("   ✅ Only analyzes guide hand position during core release moment")
        print("   ✅ Skips post-release frames when hands naturally drop")
        print("   ✅ No more false positives from natural follow-through motion")
    elif len(false_positives) == 0:
        print("✅ GOOD: No false positives detected")
        print("   Guide hand detection no longer flags post-release hand positions")
    else:
        print("⚠️ ISSUES REMAIN: Some timing problems still present")
        
    print("\n" + "="*60)
    
    if len(correct_results) == len(results):
        print("🎯 SUCCESS: Guide hand detection timing is now properly restricted!")
        print("   ✅ Only analyzes guide hand position during core release moment")
        print("   ✅ Skips post-release frames when hands naturally drop")
        print("   ✅ No more false positives from natural follow-through motion")
    elif len(false_positives) == 0:
        print("✅ GOOD: No false positives detected")
        print("   Guide hand detection no longer flags post-release hand positions")
    else:
        print("⚠️ ISSUES REMAIN: Some timing problems still present")

except ImportError as e:
    print(f"❌ Failed to import: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
