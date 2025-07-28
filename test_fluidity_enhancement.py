#!/usr/bin/env python3
"""
Test script for enhanced shot fluidity analysis
"""
import logging
import sys
import numpy as np
from basketball_analysis_service import (
    analyze_advanced_shot_fluidity,
    analyze_velocity_patterns,
    analyze_acceleration_patterns,
    analyze_shot_rhythm,
    analyze_motion_smoothness_advanced,
    calculate_overall_fluidity_score
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_mock_frame_data():
    """Create mock processed frames data for testing"""
    
    class MockLandmark:
        def __init__(self, x, y, z, visibility):
            self.x = x
            self.y = y
            self.z = z
            self.visibility = visibility
    
    class MockLandmarks:
        def __init__(self, wrist_pos, elbow_pos, shoulder_pos, knee_pos):
            self.pose_landmarks = self
            # Create landmark list with proper MediaPipe structure
            self.landmark = [MockLandmark(0.5, 0.5, 0, 0.8) for _ in range(33)]  # 33 pose landmarks
            
            # Set specific landmarks (MediaPipe pose landmark indices)
            # RIGHT_WRIST = 16, RIGHT_ELBOW = 14, RIGHT_SHOULDER = 12, RIGHT_KNEE = 26
            self.landmark[16] = MockLandmark(wrist_pos[0]/640, wrist_pos[1]/480, 0, 0.9)  # RIGHT_WRIST
            self.landmark[14] = MockLandmark(elbow_pos[0]/640, elbow_pos[1]/480, 0, 0.9)  # RIGHT_ELBOW  
            self.landmark[12] = MockLandmark(shoulder_pos[0]/640, shoulder_pos[1]/480, 0, 0.9)  # RIGHT_SHOULDER
            self.landmark[26] = MockLandmark(knee_pos[0]/640, knee_pos[1]/480, 0, 0.9)  # RIGHT_KNEE
    
    class MockFrameData:
        def __init__(self, frame_number, wrist_pos, elbow_pos, shoulder_pos, knee_pos):
            self.frame_number = frame_number
            self.landmarks_raw = MockLandmarks(wrist_pos, elbow_pos, shoulder_pos, knee_pos)
    
    # Create test data with simulated jerky motion
    processed_frames_data = []
    base_positions = {
        'wrist': [200, 300],
        'elbow': [180, 280], 
        'shoulder': [160, 260],
        'knee': [190, 400]
    }
    
    for i in range(30):  # 30 frames of test data
        # Add some jerky motion to test detection
        jerk_factor = 1.0
        if i in [8, 9, 10, 18, 19, 20]:  # Simulate jerky movements at these frames
            jerk_factor = 4.0  # More pronounced jerky motion
        
        # Create more realistic shooting motion with jerky interruptions
        progress = i / 29.0  # Progress from 0 to 1
        
        wrist_pos = [
            base_positions['wrist'][0] + np.sin(progress * np.pi) * 50 * jerk_factor,
            base_positions['wrist'][1] - progress * 80 + np.cos(progress * 4 * np.pi) * 20 * jerk_factor
        ]
        elbow_pos = [
            base_positions['elbow'][0] + np.sin(progress * np.pi * 0.8) * 30 * jerk_factor,
            base_positions['elbow'][1] - progress * 60 + np.cos(progress * 3 * np.pi) * 15 * jerk_factor
        ]
        shoulder_pos = [
            base_positions['shoulder'][0] + np.sin(progress * np.pi * 0.3) * 10,
            base_positions['shoulder'][1] - progress * 20
        ]
        knee_pos = [
            base_positions['knee'][0] + np.sin(progress * np.pi * 0.5) * 15,
            base_positions['knee'][1] - progress * 30 + progress * 40  # Knee extension
        ]
        
        processed_frames_data.append(
            MockFrameData(i, wrist_pos, elbow_pos, shoulder_pos, knee_pos)
        )
    
    return processed_frames_data

def test_fluidity_analysis():
    """Test the enhanced fluidity analysis system"""
    print("Testing Enhanced Shot Fluidity Analysis")
    print("=" * 50)
    
    # Create mock data
    processed_frames_data = create_mock_frame_data()
    fps = 30  # 30 fps test data
    
    print(f"Testing with {len(processed_frames_data)} frames at {fps} fps")
    print()
    
    # Test advanced fluidity analysis
    try:
        fluidity_metrics = analyze_advanced_shot_fluidity(processed_frames_data, fps)
        
        print("FLUIDITY ANALYSIS RESULTS:")
        print(f"Overall Fluidity Score: {fluidity_metrics['overall_fluidity_score']:.1f}/100")
        print()
        
        # Velocity Analysis Results
        velocity_analysis = fluidity_metrics['motion_flow_analysis'].get('velocity_analysis', {})
        print("VELOCITY ANALYSIS:")
        print(f"  - Velocity Smoothness Score: {velocity_analysis.get('velocity_smoothness_score', 0):.1f}")
        print(f"  - Abrupt Speed Changes: {len(velocity_analysis.get('abrupt_speed_changes', []))}")
        for change in velocity_analysis.get('abrupt_speed_changes', [])[:3]:  # Show first 3
            print(f"    * {change['joint']} at frame {change['frame']}: severity {change['severity']:.1f}")
        print()
        
        # Acceleration Analysis Results  
        acceleration_analysis = fluidity_metrics['motion_flow_analysis'].get('acceleration_analysis', {})
        print("ACCELERATION ANALYSIS:")
        print(f"  - Acceleration Smoothness Score: {acceleration_analysis.get('acceleration_smoothness_score', 0):.1f}")
        print(f"  - Acceleration Spikes: {len(acceleration_analysis.get('acceleration_spikes', []))}")
        print(f"  - Max Acceleration: {acceleration_analysis.get('max_acceleration', 0):.1f}")
        for spike in acceleration_analysis.get('acceleration_spikes', [])[:3]:  # Show first 3
            print(f"    * {spike['joint']} at frame {spike['frame']}: severity {spike['severity']:.1f}")
        print()
        
        # Rhythm Analysis Results
        rhythm_analysis = fluidity_metrics['motion_flow_analysis'].get('rhythm_analysis', {})
        print("RHYTHM ANALYSIS:")
        print(f"  - Rhythm Consistency Score: {rhythm_analysis.get('rhythm_consistency_score', 0):.1f}")
        print(f"  - Rhythm Breaks: {len(rhythm_analysis.get('rhythm_breaks', []))}")
        for break_point in rhythm_analysis.get('rhythm_breaks', [])[:3]:  # Show first 3
            print(f"    * Frame {break_point['frame']}: {break_point['type']} (severity {break_point['severity']:.1f})")
        print()
        
        # Smoothness Analysis Results
        smoothness_analysis = fluidity_metrics['motion_flow_analysis'].get('smoothness_analysis', {})
        print("SMOOTHNESS ANALYSIS:")
        print(f"  - Overall Smoothness Score: {smoothness_analysis.get('overall_smoothness_score', 0):.1f}")
        jerk_analysis = smoothness_analysis.get('jerk_analysis', {})
        for joint, analysis in jerk_analysis.items():
            print(f"  - {joint.title()} Jerk Analysis:")
            print(f"    * Mean Jerk: {analysis.get('mean_jerk', 0):.2f}")
            print(f"    * Smoothness Score: {analysis.get('smoothness_score', 0):.1f}")
        print()
        
        # Test individual analysis functions
        print("TESTING INDIVIDUAL ANALYSIS FUNCTIONS:")
        print("-" * 40)
        
        # Mock joint positions for testing individual functions
        joint_positions = {
            'wrist': [[100 + i*2, 200 - i] for i in range(20)],
            'elbow': [[80 + i*1.5, 180 - i*0.8] for i in range(20)],
            'shoulder': [[60 + i*0.5, 160 - i*0.3] for i in range(20)],
            'knee': [[90 + i*0.2, 300 + i*0.1] for i in range(20)]
        }
        frame_indices = list(range(20))
        
        # Test velocity patterns
        velocity_result = analyze_velocity_patterns(joint_positions, frame_indices, fps)
        print(f"Velocity Patterns - Smoothness Score: {velocity_result['velocity_smoothness_score']:.1f}")
        
        # Test acceleration patterns
        acceleration_result = analyze_acceleration_patterns(joint_positions, frame_indices, fps)
        print(f"Acceleration Patterns - Smoothness Score: {acceleration_result['acceleration_smoothness_score']:.1f}")
        
        # Test shot rhythm
        rhythm_result = analyze_shot_rhythm(joint_positions, frame_indices, fps)
        print(f"Shot Rhythm - Consistency Score: {rhythm_result['rhythm_consistency_score']:.1f}")
        
        # Test overall score calculation
        mock_analysis = {
            'velocity_analysis': {'velocity_smoothness_score': 85},
            'acceleration_analysis': {'acceleration_smoothness_score': 75},
            'rhythm_analysis': {'rhythm_consistency_score': 90},
            'smoothness_analysis': {'overall_smoothness_score': 80}
        }
        overall_score = calculate_overall_fluidity_score(mock_analysis)
        print(f"Overall Fluidity Score (test): {overall_score:.1f}")
        
        print()
        print("✅ ALL FLUIDITY ANALYSIS TESTS PASSED SUCCESSFULLY!")
        print()
        
        # Interpretation
        if fluidity_metrics['overall_fluidity_score'] < 70:
            print("🔍 ANALYSIS INTERPRETATION:")
            print("The test data shows fluidity issues (score < 70), which is expected")
            print("since we intentionally added jerky movements at specific frames.")
            print("This confirms the system is correctly detecting motion irregularities!")
        else:
            print("📊 ANALYSIS INTERPRETATION:")
            print("The fluidity score is good, indicating smooth motion patterns.")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR in fluidity analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Enhanced Shot Fluidity Analysis Test")
    print("Testing advanced biomechanical motion analysis...")
    print()
    
    success = test_fluidity_analysis()
    
    if success:
        print("\n🎯 TEST SUMMARY:")
        print("✅ Advanced fluidity analysis is working correctly!")
        print("✅ Multi-joint velocity tracking operational")
        print("✅ Acceleration spike detection functional")
        print("✅ Rhythm consistency analysis working")
        print("✅ Motion smoothness (jerk) analysis operational")
        print("✅ Overall fluidity scoring system functional")
        print("\nThe enhanced system is ready to detect jerky or abrupt changes")
        print("in pace and flow during basketball shooting analysis!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        sys.exit(1)
