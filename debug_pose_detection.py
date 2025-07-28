#!/usr/bin/env python3
"""
Debug script to check video content and pose detection
"""

import cv2
import mediapipe as mp
import numpy as np

def debug_video_and_pose_detection(video_path):
    """Debug what's happening with video and pose detection"""
    
    print(f"🔍 Debugging video: {video_path}")
    
    # Initialize MediaPipe
    mp_pose = mp.solutions.pose
    pose_model = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("❌ Could not open video file")
        return
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"📹 Video properties:")
    print(f"   FPS: {fps}")
    print(f"   Frames: {frame_count}")
    print(f"   Size: {width}x{height}")
    
    poses_detected = 0
    frames_processed = 0
    sample_frames = []
    
    # Process first 10 frames to check pose detection
    for i in range(min(10, frame_count)):
        ret, frame = cap.read()
        if not ret:
            break
            
        frames_processed += 1
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        
        # Try pose detection
        results = pose_model.process(rgb_frame)
        
        if results and results.pose_landmarks:
            poses_detected += 1
            print(f"✅ Frame {i}: Pose detected!")
            
            # Get landmark visibility scores
            landmarks = results.pose_landmarks.landmark
            right_wrist_vis = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].visibility
            right_elbow_vis = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].visibility
            right_shoulder_vis = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].visibility
            
            print(f"   Right arm visibility - Wrist: {right_wrist_vis:.2f}, Elbow: {right_elbow_vis:.2f}, Shoulder: {right_shoulder_vis:.2f}")
        else:
            print(f"❌ Frame {i}: No pose detected")
            
        # Save a sample frame for manual inspection
        if i < 3:
            sample_frames.append(frame.copy())
    
    cap.release()
    
    print(f"\n📊 Summary:")
    print(f"   Frames processed: {frames_processed}")
    print(f"   Poses detected: {poses_detected}")
    print(f"   Detection rate: {poses_detected/frames_processed*100:.1f}%")
    
    # Save sample frames for manual inspection
    for i, frame in enumerate(sample_frames):
        output_path = f"debug_frame_{i}.jpg"
        cv2.imwrite(output_path, frame)
        print(f"💾 Saved sample frame: {output_path}")
    
    if poses_detected == 0:
        print("\n🚨 NO POSES DETECTED!")
        print("Possible issues:")
        print("   - Video too dark/blurry")
        print("   - Person not clearly visible")
        print("   - Video corrupted")
        print("   - Person wearing clothing that interferes with pose detection")
        print("   - Camera angle too extreme")
        
        # Basic frame analysis
        print(f"\n🔍 Frame analysis (first frame):")
        if sample_frames:
            frame = sample_frames[0]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            contrast = np.std(gray)
            print(f"   Brightness: {brightness:.1f} (0-255, ideal: 80-200)")
            print(f"   Contrast: {contrast:.1f} (higher is better)")
            
            if brightness < 50:
                print("   ⚠️  Video appears too dark")
            elif brightness > 220:
                print("   ⚠️  Video appears overexposed")
                
            if contrast < 20:
                print("   ⚠️  Video appears to have low contrast")

if __name__ == "__main__":
    # Test both videos
    videos = ["basketball_shot_demo.mp4", "user_shot.mp4"]
    
    for video in videos:
        try:
            debug_video_and_pose_detection(video)
            print("\n" + "="*50 + "\n")
        except Exception as e:
            print(f"Error analyzing {video}: {e}")
