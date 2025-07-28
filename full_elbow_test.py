#!/usr/bin/env python3
"""Comprehensive test to verify elbow flare phase timing fix"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=== Comprehensive Elbow Flare Phase Timing Test ===")

try:
    from basketball_analysis_service import detect_specific_flaw, ShotPhase, FrameData
    print("✅ Successfully imported basketball_analysis_service components")
    
    # Test configuration
    shot_phases = [
        ShotPhase('Load/Dip', 0, 10, 5),
        ShotPhase('Release', 11, 25, 18),
        ShotPhase('Follow-Through', 16, 30, 23)
    ]
    
    flaw_config = {
        'threshold': 15,
        'check_phase': 'Release'
    }
    
    ideal_shot_data = {
        'release_elbow_angle': {'min': 160, 'max': 180}
    }
    
    # Test elbow flare metrics that should trigger detection
    elbow_flare_metrics = {
        'elbow_angle': 140,  # Low elbow angle (should trigger)
        'elbow_flare_front_view': 50,  # High front view angle (should trigger)
        'elbow_lateral_angle': 25  # High lateral angle (should trigger)
    }
    
    print("\nTesting elbow flare detection across different phases:")
    print("Using metrics that should trigger detection if in correct phase:")
    print(f"  • elbow_angle: {elbow_flare_metrics['elbow_angle']}° (should be >160°)")
    print(f"  • elbow_flare_front_view: {elbow_flare_metrics['elbow_flare_front_view']}° (should be <40°)")
    print(f"  • elbow_lateral_angle: {elbow_flare_metrics['elbow_lateral_angle']}° (should be <15°)")
    print()
    
    # Test frames in different phases
    test_cases = [
        {"phase": "Load/Dip", "frame": 5, "should_detect": False},
        {"phase": "Release", "frame": 15, "should_detect": True},
        {"phase": "Follow-Through", "frame": 25, "should_detect": True},
        {"phase": "Post-shot", "frame": 35, "should_detect": False}
    ]
    
    results = []
    
    for test_case in test_cases:
        frame_num = test_case["frame"]
        phase_name = test_case["phase"]
        should_detect = test_case["should_detect"]
        
        print(f"Testing {phase_name} phase (frame {frame_num}):")
        
        # Create frame data
        frame_data = FrameData(frame_num, {}, elbow_flare_metrics.copy())
        
        try:
            # Run detection
            flaw_detected, worst_frame, worst_severity = detect_specific_flaw(
                [(frame_num, frame_data)], 'elbow_flare', flaw_config, ideal_shot_data, shot_phases, shot_start_frame=0
            )
            
            # Check result
            is_correct = (should_detect and flaw_detected) or (not should_detect and not flaw_detected)
            status = "✅ CORRECT" if is_correct else "❌ WRONG"
            
            print(f"  {status} - Detected: {flaw_detected}, Expected: {should_detect}")
            if flaw_detected:
                print(f"    Severity: {worst_severity}, Frame: {worst_frame}")
            
            results.append({
                "phase": phase_name,
                "frame": frame_num,
                "expected": should_detect,
                "detected": flaw_detected,
                "correct": is_correct,
                "severity": worst_severity if flaw_detected else 0
            })
            
        except Exception as e:
            print(f"  ❌ ERROR - {e}")
            results.append({
                "phase": phase_name,
                "frame": frame_num,
                "expected": should_detect,
                "detected": False,
                "correct": False,
                "error": str(e)
            })
        
        print()
    
    # Summary
    print("=" * 60)
    print("RESULTS SUMMARY:")
    print("=" * 60)
    
    all_correct = True
    for result in results:
        if result["correct"]:
            print(f"✅ {result['phase']} (frame {result['frame']}): Expected {result['expected']}, Got {result['detected']}")
        else:
            print(f"❌ {result['phase']} (frame {result['frame']}): Expected {result['expected']}, Got {result['detected']}")
            all_correct = False
    
    print()
    print("=" * 60)
    
    if all_correct:
        print("🎯 SUCCESS: Elbow flare detection timing is CORRECT!")
        print()
        print("Key improvements verified:")
        print("  ✅ Load/Dip phase: No false positive detection")
        print("  ✅ Release phase: Proper detection when elbow flares")
        print("  ✅ Follow-Through phase: Continued detection")
        print("  ✅ Post-shot phase: No detection after shot completion")
        print()
        print("The elbow flare will now only be flagged during the actual")
        print("upward shooting motion, not during the setup/loading phase.")
    else:
        print("❌ ISSUES FOUND: Elbow flare detection timing needs adjustment!")
        print()
        incorrect_results = [r for r in results if not r["correct"]]
        for result in incorrect_results:
            if result["expected"] and not result["detected"]:
                print(f"  • Missing detection in {result['phase']} phase")
            elif not result["expected"] and result["detected"]:
                print(f"  • False positive in {result['phase']} phase")
    
    print("=" * 60)

except ImportError as e:
    print(f"❌ Failed to import basketball_analysis_service: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
