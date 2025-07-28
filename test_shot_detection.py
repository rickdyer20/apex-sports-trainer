#!/usr/bin/env python3
"""
Test script to verify intelligent shot detection system.
Tests the system's ability to identify when shooting motion begins and truncate videos appropriately.
"""

import cv2
import numpy as np
import logging
import os
import time
from basketball_analysis_service import (
    detect_shot_start_frame, 
    find_shot_start_from_activity,
    VideoAnalysisJob,
    process_video_for_analysis,
    load_ideal_shot_data
)

# Configure logging for testing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_test_video_with_delay(output_path, delay_seconds=3, shot_duration=4, fps=30):
    """
    Create a synthetic test video with initial delay followed by shooting motion.
    This simulates real-world videos where there's movement before the shot.
    """
    logging.info(f"Creating test video: {delay_seconds}s delay + {shot_duration}s shot at {fps} FPS")
    
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    total_frames = int((delay_seconds + shot_duration) * fps)
    delay_frames = int(delay_seconds * fps)
    
    # Generate frames
    for frame_idx in range(total_frames):
        # Create a simple background
        frame = np.ones((height, width, 3), dtype=np.uint8) * 50  # Dark gray background
        
        # Add court lines for context
        cv2.line(frame, (100, height//2), (width-100, height//2), (255, 255, 255), 2)  # Court line
        cv2.circle(frame, (width//2, height//2 + 100), 50, (255, 255, 255), 2)  # Hoop
        
        if frame_idx < delay_frames:
            # Pre-shot phase: minimal movement, person standing/walking
            person_y = height - 200 + int(5 * np.sin(frame_idx * 0.1))  # Subtle movement
            person_x = width//2 + int(10 * np.sin(frame_idx * 0.05))    # Slight side movement
            
            # Draw simple stick figure (standing)
            # Head
            cv2.circle(frame, (person_x, person_y - 120), 20, (0, 255, 0), -1)
            # Body
            cv2.line(frame, (person_x, person_y - 100), (person_x, person_y - 40), (0, 255, 0), 5)
            # Arms (relaxed)
            cv2.line(frame, (person_x, person_y - 80), (person_x - 30, person_y - 50), (0, 255, 0), 3)  # Left arm
            cv2.line(frame, (person_x, person_y - 80), (person_x + 30, person_y - 50), (0, 255, 0), 3)  # Right arm
            # Legs
            cv2.line(frame, (person_x, person_y - 40), (person_x - 20, person_y), (0, 255, 0), 3)      # Left leg
            cv2.line(frame, (person_x, person_y - 40), (person_x + 20, person_y), (0, 255, 0), 3)      # Right leg
            
            # Add "PRE-SHOT" label
            cv2.putText(frame, "PRE-SHOT MOVEMENT", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
        else:
            # Shot phase: active shooting motion
            shot_progress = (frame_idx - delay_frames) / (total_frames - delay_frames)
            
            # Animate shooting motion
            person_x = width//2
            # Upward motion during shot
            lift_amount = int(50 * np.sin(shot_progress * np.pi))  # Goes up then down
            person_y = height - 200 - lift_amount
            
            # Arms move upward during shot
            arm_lift = int(40 * shot_progress)
            right_arm_y = person_y - 50 - arm_lift
            right_arm_x = person_x + 30 + int(20 * shot_progress)  # Arm extends forward
            
            # Draw animated stick figure (shooting)
            # Head
            cv2.circle(frame, (person_x, person_y - 120), 20, (0, 255, 255), -1)  # Yellow during shot
            # Body
            cv2.line(frame, (person_x, person_y - 100), (person_x, person_y - 40), (0, 255, 255), 5)
            # Arms (shooting motion)
            cv2.line(frame, (person_x, person_y - 80), (person_x - 25, person_y - 60 - arm_lift//2), (0, 255, 255), 3)  # Left arm (guide)
            cv2.line(frame, (person_x, person_y - 80), (right_arm_x, right_arm_y), (255, 0, 0), 4)  # Right arm (shooting) - RED
            # Legs (slight bend then extension)
            knee_bend = int(15 * np.sin(shot_progress * np.pi * 2))
            cv2.line(frame, (person_x, person_y - 40), (person_x - 20, person_y + knee_bend), (0, 255, 255), 3)
            cv2.line(frame, (person_x, person_y - 40), (person_x + 20, person_y + knee_bend), (0, 255, 255), 3)
            
            # Add "SHOOTING" label with progress
            cv2.putText(frame, f"SHOOTING MOTION ({shot_progress*100:.0f}%)", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
        # Add frame counter
        cv2.putText(frame, f"Frame: {frame_idx}", (50, height - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        out.write(frame)
    
    out.release()
    logging.info(f"Test video created: {output_path}")
    return delay_frames  # Return expected shot start frame

def test_shot_detection_accuracy():
    """Test the shot detection system with synthetic videos of varying delay lengths."""
    
    logging.info("🎯 Testing Shot Detection Accuracy")
    logging.info("=" * 60)
    
    test_cases = [
        {"delay": 1, "shot": 3, "name": "short_delay"},
        {"delay": 3, "shot": 4, "name": "medium_delay"},
        {"delay": 5, "shot": 3, "name": "long_delay"},
        {"delay": 0.5, "shot": 2, "name": "minimal_delay"}
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases):
        logging.info(f"\n📋 Test Case {i+1}: {test_case['name']}")
        logging.info(f"   Expected delay: {test_case['delay']}s, Shot duration: {test_case['shot']}s")
        
        # Create test video
        test_video_path = f"test_video_{test_case['name']}.mp4"
        expected_shot_start = create_test_video_with_delay(
            test_video_path, 
            delay_seconds=test_case['delay'], 
            shot_duration=test_case['shot'],
            fps=30
        )
        
        # Test shot detection
        cap = cv2.VideoCapture(test_video_path)
        if cap.isOpened():
            detected_shot_start = detect_shot_start_frame(cap, fps=30, max_detection_frames=300)
            cap.release()
            
            # Calculate accuracy
            frame_error = abs(detected_shot_start - expected_shot_start)
            time_error = frame_error / 30.0  # Convert to seconds
            accuracy_percentage = max(0, 100 - (time_error * 20))  # 20% penalty per second error
            
            result = {
                'test_case': test_case['name'],
                'expected_frame': expected_shot_start,
                'detected_frame': detected_shot_start,
                'frame_error': frame_error,
                'time_error_seconds': time_error,
                'accuracy_percentage': accuracy_percentage
            }
            results.append(result)
            
            # Log results
            status = "✅ EXCELLENT" if accuracy_percentage >= 90 else "✅ GOOD" if accuracy_percentage >= 70 else "⚠️ NEEDS IMPROVEMENT"
            logging.info(f"   Expected shot start: Frame {expected_shot_start}")
            logging.info(f"   Detected shot start: Frame {detected_shot_start}")
            logging.info(f"   Error: {frame_error} frames ({time_error:.2f} seconds)")
            logging.info(f"   Accuracy: {accuracy_percentage:.1f}% {status}")
        else:
            logging.error(f"   ❌ Failed to open test video: {test_video_path}")
        
        # Cleanup
        try:
            os.remove(test_video_path)
        except:
            pass
    
    # Overall results
    logging.info("\n📊 OVERALL SHOT DETECTION RESULTS")
    logging.info("=" * 60)
    
    if results:
        avg_accuracy = sum(r['accuracy_percentage'] for r in results) / len(results)
        avg_time_error = sum(r['time_error_seconds'] for r in results) / len(results)
        
        logging.info(f"Average Accuracy: {avg_accuracy:.1f}%")
        logging.info(f"Average Time Error: {avg_time_error:.2f} seconds")
        
        if avg_accuracy >= 85:
            logging.info("🎉 Shot detection system performing EXCELLENTLY!")
        elif avg_accuracy >= 70:
            logging.info("✅ Shot detection system performing WELL!")
        else:
            logging.info("⚠️ Shot detection system needs improvement")
            
        return avg_accuracy >= 70
    else:
        logging.error("❌ No test results available")
        return False

def test_real_video_analysis():
    """Test with actual video file if available."""
    
    logging.info("\n🎬 Testing with Real Video")
    logging.info("=" * 40)
    
    # Look for test video files
    test_videos = ['user_shot.mp4', 'basketball_shot_demo.mp4', 'test_shot.mp4']
    
    for video_name in test_videos:
        if os.path.exists(video_name):
            logging.info(f"Found test video: {video_name}")
            
            # Create a test job
            job = VideoAnalysisJob(
                job_id="shot_detection_test",
                user_id="test_user",
                video_url=video_name
            )
            
            # Load ideal shot data
            try:
                ideal_shot_data = load_ideal_shot_data("ideal_shot_guide.json")
            except:
                logging.warning("Could not load ideal shot data, using defaults")
                ideal_shot_data = {
                    "release_elbow_angle": {"min": 160, "max": 180},
                    "load_knee_angle": {"min": 110, "max": 130}
                }
            
            # Test the full analysis with shot detection
            start_time = time.time()
            results = process_video_for_analysis(job, ideal_shot_data)
            processing_time = time.time() - start_time
            
            logging.info(f"Analysis completed in {processing_time:.1f} seconds")
            
            if 'error' not in results:
                logging.info("✅ Shot detection integration successful!")
                logging.info(f"   Output video: {results.get('output_video_path', 'None')}")
                logging.info(f"   Detected flaws: {len(results.get('detailed_flaws', []))}")
                logging.info(f"   Shot phases: {len(results.get('shot_phases', []))}")
                return True
            else:
                logging.error(f"❌ Analysis failed: {results['error']}")
                return False
    
    logging.info("No test video files found, skipping real video test")
    return True

def main():
    """Run all shot detection tests."""
    
    logging.info("🏀 Basketball Shot Detection Test Suite")
    logging.info("=" * 80)
    
    all_tests_passed = True
    
    # Test 1: Shot detection accuracy
    try:
        accuracy_test_passed = test_shot_detection_accuracy()
        all_tests_passed = all_tests_passed and accuracy_test_passed
    except Exception as e:
        logging.error(f"❌ Shot detection accuracy test failed: {e}")
        all_tests_passed = False
    
    # Test 2: Real video integration
    try:
        real_video_test_passed = test_real_video_analysis()
        all_tests_passed = all_tests_passed and real_video_test_passed
    except Exception as e:
        logging.error(f"❌ Real video test failed: {e}")
        all_tests_passed = False
    
    # Final results
    logging.info("\n🏁 FINAL TEST RESULTS")
    logging.info("=" * 50)
    
    if all_tests_passed:
        logging.info("🎉 ALL TESTS PASSED! Shot detection system is ready for production.")
        logging.info("✅ The system can now intelligently detect shot start and truncate videos appropriately.")
        logging.info("✅ Analysis will begin when actual shooting motion starts, not during pre-shot movement.")
    else:
        logging.info("⚠️ Some tests failed. Please review the shot detection implementation.")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
