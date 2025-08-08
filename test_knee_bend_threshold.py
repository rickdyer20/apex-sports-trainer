#!/usr/bin/env python3
"""
Test Updated Knee Bend Thresholds
Verify the new 130° threshold for insufficient knee bend detection
"""

import sys
sys.path.append('.')

def test_knee_bend_thresholds():
    """Test the updated knee bend detection thresholds"""
    print("🏀 Testing Updated Knee Bend Detection")
    print("=" * 50)
    
    # Test cases for different knee angles
    test_angles = [
        115,  # Good knee bend
        120,  # Good knee bend  
        125,  # Good knee bend
        128,  # Good knee bend (just under threshold)
        130,  # At threshold - should NOT flag
        131,  # Just over threshold - should flag
        135,  # Clearly insufficient - should flag
        140,  # Very insufficient - should flag
        150   # Extremely insufficient - should flag
    ]
    
    # Ideal range from system
    ideal_min = 110  # From ideal_shot_guide.json
    ideal_max = 130  # From ideal_shot_guide.json
    
    print(f"📊 Ideal Range: {ideal_min}° - {ideal_max}°")
    print(f"🎯 New Threshold: Insufficient knee bend when > 130°")
    print(f"🎯 Excessive knee bend when < 105° (unchanged)")
    print()
    
    print("Test Results:")
    print("-" * 40)
    
    for angle in test_angles:
        # Test insufficient knee bend logic
        if angle > 130:  # New threshold
            severity_factor = (angle - ideal_min - 15) * 1.2
            severity = min(severity_factor, 40)
            status = f"⚠️  INSUFFICIENT (severity: {severity:.1f})"
        elif angle < 105:  # Excessive threshold (unchanged)
            severity_factor = (ideal_max - angle - 20) * 1.2
            severity = min(severity_factor, 35)
            status = f"⚠️  EXCESSIVE (severity: {severity:.1f})"
        else:
            status = "✅ GOOD"
        
        print(f"Angle {angle:3d}°: {status}")
    
    print()
    print("📋 Summary of Changes:")
    print("-" * 40)
    print("BEFORE: Insufficient knee bend when > 135°")
    print("AFTER:  Insufficient knee bend when > 130°")
    print()
    print("Impact:")
    print("• 131° - 135°: Now flagged as insufficient (was previously OK)")
    print("• 130° and below: Still considered acceptable")
    print("• More strict detection for better coaching")
    print()
    print("✅ New tolerance ranges:")
    print("• Excessive:     < 105°  [Unchanged]")
    print("• Acceptable:  105° - 130°  [Narrowed from 105° - 135°]")
    print("• Insufficient:  > 130°  [Stricter from > 135°]")

if __name__ == "__main__":
    test_knee_bend_thresholds()
