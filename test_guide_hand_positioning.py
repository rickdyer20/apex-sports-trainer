#!/usr/bin/env python3
"""
Test script for enhanced guide hand positioning detection
Tests the new logic that distinguishes between "on top", "under", and "on side" positioning
"""

import sys
import logging
from basketball_analysis_service import detect_specific_flaw

# Set up logging to see detailed analysis
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_guide_hand_positioning():
    """Test different guide hand positioning scenarios"""
    
    print("=== TESTING ENHANCED GUIDE HAND POSITIONING DETECTION ===\n")
    
    # Get flaw configurations
    flaw_configs = {
        'guide_hand_under_ball': {
            'description': 'Guide hand positioned underneath ball instead of on side',
            'check_phase': 'Release',
            'threshold': 25,
            'plain_language': 'Your guide hand is too far under the ball. Keep it on the side for proper support without interference.',
            'requires_visibility': ['guide_hand'],
            'camera_angles': ['right_side_view', 'front_view']
        },
        'guide_hand_on_top': {
            'description': 'Guide hand positioned on top of ball instead of on side',
            'check_phase': 'Release',
            'threshold': 15,  # More sensitive for on-top detection
            'plain_language': 'Your guide hand is positioned on top of the ball. Move it to the side for better control and cleaner release.',
            'requires_visibility': ['guide_hand'],
            'camera_angles': ['right_side_view', 'front_view']
        }
    }
    
    # Create a simple shot phase for testing
    class MockPhase:
        def __init__(self, name, key_moment_frame):
            self.name = name
            self.key_moment_frame = key_moment_frame
    
    shot_phases = [MockPhase('Release', 10)]
    
    # Create a simple frame data class
    class MockFrameData:
        def __init__(self, metrics):
            self.metrics = metrics
    
    # Test scenarios
    test_scenarios = [
        {
            'name': 'Guide Hand ON TOP (should detect guide_hand_on_top)',
            'metrics': {
                'guide_hand_position_angle': -120,  # Angle indicating position
                'guide_hand_vertical_offset': -25,  # Negative = guide hand above shooting hand
                'guide_hand_horizontal_offset': 40   # Good horizontal separation
            },
            'expected_flaw': 'guide_hand_on_top'
        },
        {
            'name': 'Guide Hand UNDER BALL (should detect guide_hand_under_ball)',
            'metrics': {
                'guide_hand_position_angle': 45,
                'guide_hand_vertical_offset': 30,   # Positive = guide hand below shooting hand
                'guide_hand_horizontal_offset': 35
            },
            'expected_flaw': 'guide_hand_under_ball'
        },
        {
            'name': 'Guide Hand PROPER SIDE (should detect neither)',
            'metrics': {
                'guide_hand_position_angle': 90,
                'guide_hand_vertical_offset': 5,    # Close to same height
                'guide_hand_horizontal_offset': 45  # Good horizontal separation
            },
            'expected_flaw': 'neither'
        },
        {
            'name': 'Guide Hand TOO CENTERED (should detect interference)',
            'metrics': {
                'guide_hand_position_angle': 95,
                'guide_hand_vertical_offset': 0,
                'guide_hand_horizontal_offset': 15  # Too close horizontally
            },
            'expected_flaw': 'guide_hand_under_ball'  # Current logic flags this as under_ball
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n--- Testing: {scenario['name']} ---")
        print(f"Metrics: {scenario['metrics']}")
        
        frame_data = MockFrameData(scenario['metrics'])
        frame_pairs = [(10, frame_data), (11, frame_data)]  # Use 2 frames to meet min_evidence_frames requirement
        
        # Test guide_hand_under_ball detection
        print("\nTesting guide_hand_under_ball detection:")
        try:
            flaw_detected, worst_frame, severity = detect_specific_flaw(
                frame_pairs, 'guide_hand_under_ball', flaw_configs['guide_hand_under_ball'], 
                None, shot_phases, shot_start_frame=0
            )
            print(f"guide_hand_under_ball result: detected={flaw_detected}, frame={worst_frame}, severity={severity}")
        except Exception as e:
            print(f"Error in guide_hand_under_ball: {e}")
        
        # Test guide_hand_on_top detection
        print("\nTesting guide_hand_on_top detection:")
        try:
            flaw_detected, worst_frame, severity = detect_specific_flaw(
                frame_pairs, 'guide_hand_on_top', flaw_configs['guide_hand_on_top'], 
                None, shot_phases, shot_start_frame=0
            )
            print(f"guide_hand_on_top result: detected={flaw_detected}, frame={worst_frame}, severity={severity}")
        except Exception as e:
            print(f"Error in guide_hand_on_top: {e}")
            
        print("-" * 50)

if __name__ == "__main__":
    test_guide_hand_positioning()
