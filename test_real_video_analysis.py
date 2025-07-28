#!/usr/bin/env python3
"""
Test Real Video Elbow Detection
Test the enhanced system with the actual video
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cv2  
import mediapipe as mp
from basketball_analysis_service import (
    process_video_for_analysis,
    analyze_detailed_flaws,
    load_ideal_shot_data,
    FrameData,
    ShotPhase,
    get_landmark_coords,
    calculate_angle
)
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

mp_pose = mp.solutions.pose
pose_model = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

def quick_video_analysis(video_path):
    """Quick analysis focusing on elbow flare detection"""
    print(f"🎥 Quick Analysis: {video_path}")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Could not open video")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"📊 Video: {width}x{height}, {fps:.1f} FPS, {total_frames} frames")
    
    # Process frames and extract metrics
    processed_frames = []
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Process every frame for short videos
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose_model.process(rgb_frame)
        
        frame_metrics = {}
        
        if results.pose_landmarks:
            try:
                # Extract landmarks
                r_shoulder = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_SHOULDER, width, height)
                l_shoulder = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.LEFT_SHOULDER, width, height)
                r_elbow = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_ELBOW, width, height)
                r_wrist = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_WRIST, width, height)
                
                # Calculate elbow extension angle
                elbow_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
                frame_metrics['elbow_angle'] = elbow_angle
                
                # Calculate front view metrics
                shoulder_midpoint = [(r_shoulder[0] + l_shoulder[0]) / 2, (r_shoulder[1] + l_shoulder[1]) / 2]
                elbow_deviation_x = abs(r_elbow[0] - shoulder_midpoint[0])
                shoulder_width = abs(r_shoulder[0] - l_shoulder[0])
                
                if shoulder_width > 0:
                    elbow_flare_ratio = (elbow_deviation_x / shoulder_width) * 100
                    frame_metrics['elbow_flare_front_view'] = elbow_flare_ratio
                    
                    # Calculate lateral angle
                    elbow_vector = [r_elbow[0] - shoulder_midpoint[0], r_elbow[1] - shoulder_midpoint[1]]
                    elbow_lateral_angle = abs(np.degrees(np.arctan2(elbow_vector[0], elbow_vector[1])))
                    frame_metrics['elbow_lateral_angle'] = elbow_lateral_angle
                    
                print(f"Frame {frame_count}: elbow_angle={elbow_angle:.1f}°, flare_ratio={elbow_flare_ratio:.1f}%, lateral_angle={elbow_lateral_angle:.1f}°")
                
            except Exception as e:
                print(f"Frame {frame_count}: Error extracting metrics - {e}")
        
        # Create frame data
        frame_data = FrameData(frame_count, results, frame_metrics)
        processed_frames.append(frame_data)
        frame_count += 1
    
    cap.release()
    
    # Create simple shot phases (since video is short)
    shot_phases = [
        ShotPhase('Shot Motion', 0, len(processed_frames) - 1)
    ]
    
    # Load ideal shot data
    ideal_shot_data = load_ideal_shot_data("ideal_shot_guide.json")
    
    # Run flaw analysis
    print(f"\n🔍 Running flaw analysis...")
    detailed_flaws = analyze_detailed_flaws(processed_frames, ideal_shot_data, shot_phases, fps)
    
    print(f"\n📋 ANALYSIS RESULTS:")
    print(f"   Total flaws detected: {len(detailed_flaws)}")
    
    elbow_flare_found = False
    for flaw in detailed_flaws:
        print(f"\n   🚨 {flaw['flaw_type'].upper()}")
        print(f"      Phase: {flaw['phase']}")
        print(f"      Severity: {flaw['severity']:.1f}")
        print(f"      Frame: {flaw['frame_number']}")
        print(f"      Description: {flaw['plain_language']}")
        
        if flaw['flaw_type'] == 'elbow_flare':
            elbow_flare_found = True
    
    if elbow_flare_found:
        print(f"\n✅ SUCCESS! Elbow flare detected in your video!")
    else:
        print(f"\n❌ Elbow flare still not detected")
        
        # Show what flaws were found instead
        if detailed_flaws:
            print(f"   Other flaws found: {[f['flaw_type'] for f in detailed_flaws]}")
        else:
            print(f"   No flaws detected at all - may need further debugging")

if __name__ == "__main__":
    video_path = r"C:\Users\rickd\Downloads\analyzed_shot_6f1f7e19-934c-4516-a140-e2e1f069a17d.mp4"  
    quick_video_analysis(video_path)
