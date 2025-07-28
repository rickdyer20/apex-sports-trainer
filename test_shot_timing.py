#!/usr/bin/env python3
"""Test script to analyze shot detection timing for Bill front.mov"""

import os
import sys
import cv2
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from basketball_analysis_service import (
        detect_shot_start_frame, 
        detect_shot_start_pose_based,
        detect_shot_start_motion_based, 
        detect_shot_start_frame_diff,
        find_shot_start_from_activity
    )
    print("✅ Successfully imported shot detection functions")
except ImportError as e:
    print(f"❌ Failed to import: {e}")
    sys.exit(1)

def analyze_shot_detection_timing():
    """Analyze shot detection for the specific video that had timing issues"""
    
    video_path = r"c:\Users\rickd\Downloads\Bill front.mov"
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False
        
    print(f"=== Analyzing Shot Detection Timing ===")
    print(f"Video: {video_path}")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Failed to open video: {video_path}")
        return False
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    print(f"Video Properties:")
    print(f"  • FPS: {fps}")
    print(f"  • Size: {width}x{height}")
    print(f"  • Total frames: {total_frames}")
    print(f"  • Duration: {duration:.2f} seconds")
    print()
    
    # Test current shot detection
    print("Testing current shot detection methods...")
    
    # Test all three detection methods individually
    pose_result = detect_shot_start_pose_based(cap, fps, max_detection_frames=min(total_frames, 300))
    motion_result = detect_shot_start_motion_based(cap, fps, max_detection_frames=min(total_frames, 300))
    frame_diff_result = detect_shot_start_frame_diff(cap, fps, max_detection_frames=min(total_frames, 300))
    
    print(f"Individual Detection Results:")
    print(f"  • Pose-based: Frame {pose_result['frame']} ({pose_result['frame']/fps:.2f}s) - Confidence: {pose_result['confidence']:.3f}")
    print(f"  • Motion-based: Frame {motion_result['frame']} ({motion_result['frame']/fps:.2f}s) - Confidence: {motion_result['confidence']:.3f}")
    print(f"  • Frame-diff: Frame {frame_diff_result['frame']} ({frame_diff_result['frame']/fps:.2f}s) - Confidence: {frame_diff_result['confidence']:.3f}")
    print()
    
    # Test combined detection (what system actually uses)
    detected_start_frame = detect_shot_start_frame(cap, fps, max_detection_frames=min(total_frames, 300))
    detected_start_time = detected_start_frame / fps if fps > 0 else 0
    
    print(f"CURRENT SYSTEM DETECTION:")
    print(f"  🎯 Detected shot start: Frame {detected_start_frame} ({detected_start_time:.2f}s)")
    print(f"  📝 Skipped frames: {detected_start_frame} ({detected_start_frame/fps:.2f}s of video)")
    print(f"  ⏱️  Analysis starts: {detected_start_time:.2f}s into video")
    print()
    
    # Analyze what phases might be missing
    expected_shot_phases = {
        "Setup/Ready": "0.0-1.0s (player positioning, ball handling)",
        "Load/Dip": "1.0-1.5s (knee bend, ball loading phase)", 
        "Release": "1.5-2.0s (upward motion, ball release)",
        "Follow-Through": "2.0-2.5s (wrist snap, landing)"
    }
    
    print("Expected Basketball Shot Phases:")
    for phase, description in expected_shot_phases.items():
        print(f"  • {phase}: {description}")
    print()
    
    # Check what might be missed
    if detected_start_time > 1.0:
        print("⚠️  POTENTIAL ISSUE DETECTED:")
        print(f"   Shot detection starts at {detected_start_time:.2f}s")
        print("   This may MISS crucial early phases:")
        
        if detected_start_time > 0.5:
            print("   ❌ Setup phase likely missed")
        if detected_start_time > 1.0:
            print("   ❌ Load/Dip phase likely missed or incomplete")
        if detected_start_time > 1.5:
            print("   ❌ Early release phase missed")
            
        print()
        print("🔧 RECOMMENDATION:")
        print("   Modify shot detection to start earlier in the motion")
        print("   Load/Dip phase is CRITICAL for biomechanical analysis")
        print("   Current detection appears too aggressive in skipping 'pre-shot' frames")
    else:
        print("✅ Shot detection timing looks reasonable")
    
    print()
    print("=" * 60)
    
    cap.release()
    
    return detected_start_frame, detected_start_time

if __name__ == "__main__":
    print("Testing shot detection timing for specific video...")
    try:
        analyze_shot_detection_timing()
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
