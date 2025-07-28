#!/usr/bin/env python3
"""
Debug Elbow Flare Detection
Test script to analyze why elbow flare detection might be failing
"""

import cv2
import mediapipe as mp
import numpy as np
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize MediaPipe
mp_pose = mp.solutions.pose
pose_model = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

def get_landmark_coords(landmarks, landmark_enum, width, height):
    """Extracts pixel coordinates for a given landmark."""
    lm = landmarks.landmark[landmark_enum.value]
    return [int(lm.x * width), int(lm.y * height)]

def calculate_angle(p1, p2, p3):
    """Calculates the angle (in degrees) between three 2D points, p2 is the vertex."""
    p1 = np.array(p1)
    p2 = np.array(p2)
    p3 = np.array(p3)

    v1 = p1 - p2
    v2 = p3 - p2

    dot_product = np.dot(v1, v2)
    magnitude_v1 = np.linalg.norm(v1)
    magnitude_v2 = np.linalg.norm(v2)

    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return 0

    angle_rad = np.arccos(np.clip(dot_product / (magnitude_v1 * magnitude_v2), -1.0, 1.0))
    angle_deg = np.degrees(angle_rad)

    return angle_deg

def analyze_elbow_flare_in_video(video_path):
    """Analyze elbow flare metrics in the given video"""
    print(f"🎥 Analyzing elbow flare in: {video_path}")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error: Could not open video file: {video_path}")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"📊 Video info: {width}x{height}, {fps:.1f} FPS, {total_frames} frames")
    
    frame_count = 0
    elbow_flare_data = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        
        # Process every 5th frame to speed up analysis
        if frame_count % 5 != 0:
            continue
            
        # Apply MediaPipe pose detection
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose_model.process(rgb_frame)
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # Extract key landmarks
            try:
                r_shoulder = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_SHOULDER, width, height)
                l_shoulder = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.LEFT_SHOULDER, width, height)
                r_elbow = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_ELBOW, width, height)
                r_wrist = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_WRIST, width, height)
                
                # Calculate elbow extension angle (side view metric)
                elbow_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
                
                # Calculate front view elbow flare metrics
                shoulder_midpoint = [(r_shoulder[0] + l_shoulder[0]) / 2, (r_shoulder[1] + l_shoulder[1]) / 2]
                elbow_deviation_x = abs(r_elbow[0] - shoulder_midpoint[0])
                shoulder_width = abs(r_shoulder[0] - l_shoulder[0])
                
                elbow_flare_ratio = 0
                elbow_lateral_angle = 0
                
                if shoulder_width > 0:
                    elbow_flare_ratio = (elbow_deviation_x / shoulder_width) * 100
                    
                    # Calculate lateral angle
                    elbow_vector = [r_elbow[0] - shoulder_midpoint[0], r_elbow[1] - shoulder_midpoint[1]]
                    elbow_lateral_angle = abs(np.degrees(np.arctan2(elbow_vector[0], elbow_vector[1])))
                
                # Store data for this frame
                frame_data = {
                    'frame': frame_count,
                    'time_seconds': frame_count / fps,
                    'elbow_angle': elbow_angle,
                    'elbow_flare_ratio': elbow_flare_ratio,
                    'elbow_lateral_angle': elbow_lateral_angle,
                    'shoulder_width_px': shoulder_width,
                    'elbow_deviation_px': elbow_deviation_x,
                    'visibility_right_elbow': landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].visibility,
                    'visibility_right_shoulder': landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].visibility,
                    'visibility_left_shoulder': landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].visibility
                }
                
                elbow_flare_data.append(frame_data)
                
                # Print detailed info for frames with potential elbow flare
                if elbow_flare_ratio > 70 or elbow_lateral_angle > 20 or elbow_angle < 150:
                    print(f"🚨 Frame {frame_count} ({frame_count/fps:.1f}s): POTENTIAL ELBOW FLARE")
                    print(f"   💪 Elbow extension angle: {elbow_angle:.1f}° (ideal: 160-180°)")
                    print(f"   📐 Elbow flare ratio: {elbow_flare_ratio:.1f}% (threshold: 80%)")
                    print(f"   📏 Elbow lateral angle: {elbow_lateral_angle:.1f}° (threshold: 25°)")
                    print(f"   👀 Landmarks visibility - R.Elbow: {landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].visibility:.2f}, R.Shoulder: {landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].visibility:.2f}, L.Shoulder: {landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].visibility:.2f}")
                    print()
                
            except Exception as e:
                print(f"⚠️  Frame {frame_count}: Error extracting landmarks - {e}")
                continue
    
    cap.release()
    
    # Analysis summary
    print(f"\n📋 ANALYSIS SUMMARY")
    print(f"Total frames analyzed: {len(elbow_flare_data)}")
    
    if elbow_flare_data:
        # Find frames with highest elbow flare indicators
        max_flare_ratio = max(elbow_flare_data, key=lambda x: x['elbow_flare_ratio'])
        max_lateral_angle = max(elbow_flare_data, key=lambda x: x['elbow_lateral_angle'])
        min_elbow_angle = min(elbow_flare_data, key=lambda x: x['elbow_angle'])
        
        print(f"\n🔍 WORST ELBOW FLARE INDICATORS:")
        print(f"   📐 Highest flare ratio: {max_flare_ratio['elbow_flare_ratio']:.1f}% (Frame {max_flare_ratio['frame']}, {max_flare_ratio['time_seconds']:.1f}s)")
        print(f"   📏 Highest lateral angle: {max_lateral_angle['elbow_lateral_angle']:.1f}° (Frame {max_lateral_angle['frame']}, {max_lateral_angle['time_seconds']:.1f}s)")
        print(f"   💪 Lowest extension angle: {min_elbow_angle['elbow_angle']:.1f}° (Frame {min_elbow_angle['frame']}, {min_elbow_angle['time_seconds']:.1f}s)")
        
        # Count frames that would trigger elbow flare detection
        flare_triggers = [
            f for f in elbow_flare_data 
            if f['elbow_flare_ratio'] > 80 or f['elbow_lateral_angle'] > 25 or f['elbow_angle'] < 140
        ]
        
        print(f"\n✅ DETECTION ANALYSIS:")
        print(f"   🎯 Frames that SHOULD trigger elbow flare detection: {len(flare_triggers)}")
        print(f"   📊 Detection rate: {len(flare_triggers) / len(elbow_flare_data) * 100:.1f}%")
        
        if len(flare_triggers) == 0:
            print(f"\n❌ NO ELBOW FLARE DETECTED - This indicates a potential issue!")
            print(f"   🔧 Possible causes:")
            print(f"      - Thresholds too high (current: flare_ratio > 80%, lateral_angle > 25°, elbow_angle < 140°)")
            print(f"      - Camera angle not suitable for detection")
            print(f"      - Pose detection quality issues")
            print(f"      - Code logic problems in detect_specific_flaw()")
        else:
            print(f"\n✅ ELBOW FLARE SHOULD BE DETECTED")
            print(f"   The metrics show clear elbow flare indicators.")
            print(f"   If analysis didn't detect it, check:")
            print(f"      - Camera angle detection logic")
            print(f"      - Phase identification (elbow_flare only checked in 'Release' phase)")
            print(f"      - Minimum evidence frames requirement")
        
        # Save detailed data to JSON for further analysis
        with open('elbow_flare_debug.json', 'w') as f:
            json.dump(elbow_flare_data, f, indent=2)
        print(f"\n💾 Detailed frame data saved to: elbow_flare_debug.json")

if __name__ == "__main__":
    video_path = r"C:\Users\rickd\Downloads\analyzed_shot_6f1f7e19-934c-4516-a140-e2e1f069a17d.mp4"
    analyze_elbow_flare_in_video(video_path)
