#!/usr/bin/env python3
"""Debug elbow flare detection thresholds"""

import os
import sys

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=== Elbow Flare Threshold Debug ===")

try:
    from basketball_analysis_service import detect_specific_flaw, ShotPhase, FrameData
    print("✅ Successfully imported basketball_analysis_service components")
    
    # Test different elbow flare ratios to see what gets detected
    shot_phases = [
        ShotPhase('Load/Dip', 0, 10, 5),
        ShotPhase('Release', 11, 25, 18),
        ShotPhase('Follow-Through', 16, 30, 18)
    ]
    
    ideal_shot_data = {
        'release_elbow_angle': {'min': 160, 'max': 180}
    }
    
    flaw_config = {
        'threshold': 15,
        'check_phase': 'Release'
    }
    
    # Test various elbow flare scenarios
    test_cases = [
        ("Mild flare", 25),
        ("Moderate flare", 35), 
        ("Obvious flare", 45),
        ("Severe flare", 60),
        ("Extreme flare", 80)
    ]
    
    print("\nTesting different elbow flare scenarios:")
    print("=" * 50)
    
    for case_name, flare_ratio in test_cases:
        print(f"\n{case_name} (elbow_flare_front_view: {flare_ratio}%):")
        
        # Create test frame with specific flare ratio
        frame_data = FrameData(18, {}, {  # Release phase frame
            'elbow_angle': 150,
            'elbow_flare_front_view': flare_ratio,
            'elbow_lateral_angle': flare_ratio * 0.3  # Proportional lateral angle
        })
        
        # Run detection
        result = detect_specific_flaw(
            [(18, frame_data)], 'elbow_flare', flaw_config, ideal_shot_data, shot_phases, shot_start_frame=0
        )
        
        flaw_detected, worst_frame, worst_severity = result
        
        if flaw_detected:
            print(f"  ✅ DETECTED - Severity: {worst_severity:.1f}")
        else:
            print(f"  ❌ NOT DETECTED")
    
    print("\n" + "=" * 50)
    print("ANALYSIS:")
    print("Current threshold: elbow_flare_front_view > 40%")
    print("If 'obvious flare (45%)' is detected but real video isn't,")
    print("the issue might be:")
    print("1. Video elbow_flare_front_view calculation is incorrect")
    print("2. Timing issue (not checking right phase)")
    print("3. Missing landmarks causing metric not to be calculated")
    
    print("\nRECOMMENDATION:")
    print("Lower the threshold from 40% to 25-30% for better sensitivity")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
