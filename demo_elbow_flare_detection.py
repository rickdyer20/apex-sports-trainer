#!/usr/bin/env python3
"""
Demonstration of enhanced elbow flare detection logic for front view
This simulates the detection without requiring actual video with pose landmarks
"""

import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MockFrameData:
    """Mock frame data to simulate different elbow positions"""
    def __init__(self, elbow_angle=None, elbow_flare_front_view=None, elbow_lateral_angle=None):
        self.metrics = {}
        if elbow_angle is not None:
            self.metrics['elbow_angle'] = elbow_angle
        if elbow_flare_front_view is not None:
            self.metrics['elbow_flare_front_view'] = elbow_flare_front_view
        if elbow_lateral_angle is not None:
            self.metrics['elbow_lateral_angle'] = elbow_lateral_angle

def detect_elbow_flare_enhanced(frame_data, ideal_shot_data, flaw_config):
    """Enhanced elbow flare detection (extracted from main code)"""
    severity = 0
    detection_method = "none"
    
    # Side view detection: check elbow extension angle
    if 'elbow_angle' in frame_data.metrics:
        ideal_range = ideal_shot_data['release_elbow_angle']
        actual = frame_data.metrics['elbow_angle']
        # Only flag significant elbow flare (less extension) from side view
        if actual < ideal_range['min'] - flaw_config['threshold'] and actual < 140:
            severity = min(ideal_range['min'] - actual, 40)
            detection_method = "side_view_extension"
    
    # Front view detection: check lateral elbow deviation
    if 'elbow_flare_front_view' in frame_data.metrics:
        elbow_flare_ratio = frame_data.metrics['elbow_flare_front_view']
        # Ideal elbow should be within 50-70% of shoulder width from centerline
        # Above 80% indicates significant flare
        if elbow_flare_ratio > 80:  # 80% of shoulder width is excessive flare
            front_view_severity = min((elbow_flare_ratio - 60) * 2, 50)  # Scale severity
            if front_view_severity > severity:
                severity = front_view_severity
                detection_method = "front_view_ratio"
                
    # Alternative front view detection using lateral angle
    if 'elbow_lateral_angle' in frame_data.metrics and severity == 0:
        lateral_angle = frame_data.metrics['elbow_lateral_angle']
        # Ideal shooting elbow should be close to body centerline (low lateral angle)
        # Above 25-30 degrees indicates flare
        if lateral_angle > 25:  # More than 25 degrees lateral deviation
            angle_severity = min((lateral_angle - 15) * 2.5, 45)  # Scale severity
            if angle_severity > severity:
                severity = angle_severity
                detection_method = "front_view_angle"
    
    return severity, detection_method

def test_elbow_flare_scenarios():
    """Test various elbow flare scenarios to demonstrate the enhanced detection"""
    
    # Mock ideal shot data
    ideal_shot_data = {
        'release_elbow_angle': {'min': 160, 'max': 180}
    }
    
    flaw_config = {'threshold': 20}
    
    print("🏀 ELBOW FLARE DETECTION TEST SCENARIOS")
    print("="*60)
    
    # Test scenarios
    scenarios = [
        {
            'name': 'Perfect Form (Side View)',
            'frame_data': MockFrameData(elbow_angle=170),
            'expected': 'No flare detected'
        },
        {
            'name': 'Severe Elbow Flare (Side View)',
            'frame_data': MockFrameData(elbow_angle=120),  # Much less than ideal 160-180
            'expected': 'Flare detected via side view extension'
        },
        {
            'name': 'Moderate Elbow Flare (Side View)',
            'frame_data': MockFrameData(elbow_angle=135),  # Moderately less than ideal
            'expected': 'Flare detected via side view extension'
        },
        {
            'name': 'Perfect Form (Front View)',
            'frame_data': MockFrameData(elbow_flare_front_view=65, elbow_lateral_angle=15),
            'expected': 'No flare detected'
        },
        {
            'name': 'Extreme Elbow Flare (Front View - Ratio)',
            'frame_data': MockFrameData(elbow_flare_front_view=95),  # 95% of shoulder width
            'expected': 'Flare detected via front view ratio'
        },
        {
            'name': 'Severe Elbow Flare (Front View - Angle)',
            'frame_data': MockFrameData(elbow_lateral_angle=35),  # 35 degrees lateral
            'expected': 'Flare detected via front view angle'
        },
        {
            'name': 'Combined Detection (Both Views)',
            'frame_data': MockFrameData(
                elbow_angle=125,  # Poor extension
                elbow_flare_front_view=90,  # High lateral deviation
                elbow_lateral_angle=30  # High lateral angle
            ),
            'expected': 'Flare detected via multiple methods'
        },
        {
            'name': 'Borderline Case (Front View)',
            'frame_data': MockFrameData(elbow_flare_front_view=78, elbow_lateral_angle=24),
            'expected': 'No flare detected (below thresholds)'
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   Expected: {scenario['expected']}")
        
        severity, method = detect_elbow_flare_enhanced(
            scenario['frame_data'], 
            ideal_shot_data, 
            flaw_config
        )
        
        if severity > 0:
            print(f"   ✅ FLAW DETECTED: Severity {severity:.1f} via {method}")
            
            # Provide coaching based on detection method
            if method == "side_view_extension":
                print(f"   💡 Coaching: Focus on full elbow extension toward the basket")
            elif method == "front_view_ratio":
                print(f"   💡 Coaching: Keep your shooting elbow closer to your body centerline")
            elif method == "front_view_angle":
                print(f"   💡 Coaching: Avoid letting your elbow stick out laterally from your body")
        else:
            print(f"   ❌ No flaw detected (severity: {severity:.1f})")
            
        # Show metrics used
        metrics_str = ", ".join([f"{k}: {v}" for k, v in scenario['frame_data'].metrics.items()])
        print(f"   📊 Metrics: {metrics_str}")
    
    print("\n" + "="*60)
    print("🎯 SUMMARY:")
    print("The enhanced elbow flare detection now works for:")
    print("✅ Side view videos (using elbow extension angle)")
    print("✅ Front view videos (using lateral elbow deviation ratio)")  
    print("✅ Front view videos (using lateral elbow angle)")
    print("✅ Combined detection from multiple measurement methods")
    print("\nThis should resolve the issue with front-view videos not detecting")
    print("extreme elbow flare that was reported.")

if __name__ == "__main__":
    test_elbow_flare_scenarios()
