#!/usr/bin/env python3
"""
Test script for elbow flare detection from front view
"""

import cv2
import os
import sys
import logging
from basketball_analysis_service import process_video_for_analysis, VideoAnalysisJob, load_ideal_shot_data

# Configure logging to see debug info
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_front_view_elbow_analysis():
    """Test elbow flare detection with a sample video"""
    
    # Look for any mp4 video files in the current directory
    video_files = [f for f in os.listdir('.') if f.endswith('.mp4')]
    
    if not video_files:
        print("No MP4 video files found in current directory.")
        print("Please place a basketball shot video (preferably front view) in this directory.")
        return
    
    # Use the first video file found, or try user_shot.mp4 specifically
    test_video = "user_shot.mp4" if "user_shot.mp4" in video_files else video_files[0]
    print(f"Testing elbow flare detection with: {test_video}")
    
    try:
        # Create a VideoAnalysisJob object
        job = VideoAnalysisJob(
            job_id="test_elbow_front_view",
            user_id="test_user",
            video_url=test_video
        )
        
        # Load ideal shot data
        ideal_shot_data = load_ideal_shot_data("ideal_shot_guide.json")
        
        # Process the video with enhanced elbow analysis
        result = process_video_for_analysis(job, ideal_shot_data)
        
        print(f"\nAnalysis completed successfully!")
        print(f"Camera angle detected: {result.get('camera_angle', 'unknown')}")
        
        # Check for elbow flare in detailed flaws
        detailed_flaws = result.get('detailed_flaws', [])
        elbow_flaws = [flaw for flaw in detailed_flaws if 'elbow' in flaw.get('flaw_type', '')]
        
        if elbow_flaws:
            print(f"\n✅ ELBOW FLAWS DETECTED: {len(elbow_flaws)}")
            for flaw in elbow_flaws:
                print(f"  - {flaw['flaw_type']}: Severity {flaw['severity']:.1f}")
                print(f"    {flaw['plain_language']}")
                print(f"    Camera context: {flaw.get('camera_context', 'N/A')}")
        else:
            print(f"\n❌ NO ELBOW FLAWS DETECTED")
            
        # Show all detected flaws for context
        if detailed_flaws:
            print(f"\nAll detected flaws ({len(detailed_flaws)}):")
            for i, flaw in enumerate(detailed_flaws, 1):
                print(f"  {i}. {flaw['flaw_type']}: {flaw['severity']:.1f}")
        else:
            print("\nNo flaws detected at all.")
            
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_front_view_elbow_analysis()
