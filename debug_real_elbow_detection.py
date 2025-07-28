#!/usr/bin/env python3
"""Debug elbow flare detection on real video analysis"""

import os
import sys
import logging

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging to see debug messages
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

print("=== Real Video Elbow Flare Debug ===")
print("This script will run analysis and show detailed elbow flare detection logs")
print("Look for:")
print("1. 'elbow_flare_front_view' and 'elbow_lateral_angle' values")
print("2. Phase detection (Release/Follow-Through)")
print("3. Any warnings about missing metrics")
print("=" * 60)

try:
    from basketball_analysis_service import process_video_for_analysis, VideoAnalysisJob
    import json
    
    # Load ideal shot data
    with open('ideal_shot_guide.json', 'r') as f:
        ideal_shot_data = json.load(f)
    
    # Find a test video file
    test_videos = []
    for file in os.listdir('.'):
        if file.endswith(('.mp4', '.mov', '.avi')):
            test_videos.append(file)
    
    if not test_videos:
        print("❌ No test video found")
        sys.exit(1)
    
    test_video = test_videos[0]
    print(f"🎥 Testing with video: {test_video}")
    print("=" * 60)
    
    # Run analysis with debug logging enabled
    print("Starting video analysis...")
    
    # Create job object
    job = VideoAnalysisJob("debug_job", "debug_user", test_video)
    
    result = process_video_for_analysis(job, ideal_shot_data)
    
    print("=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    
    if result and hasattr(result, 'feedback_points'):
        # Extract flaws from feedback points
        flaws_detected = {}
        for feedback in result.feedback_points:
            if hasattr(feedback, 'flaw_type') and hasattr(feedback, 'severity'):
                if feedback.flaw_type not in flaws_detected or feedback.severity > flaws_detected[feedback.flaw_type]['severity']:
                    flaws_detected[feedback.flaw_type] = {
                        'severity': feedback.severity,
                        'worst_frame': getattr(feedback, 'frame_number', 'unknown')
                    }
        
        if 'elbow_flare' in flaws_detected:
            print(f"✅ ELBOW FLARE DETECTED!")
            print(f"   Severity: {flaws_detected['elbow_flare']['severity']}")
            print(f"   Worst frame: {flaws_detected['elbow_flare']['worst_frame']}")
        else:
            print("❌ ELBOW FLARE NOT DETECTED")
            print("Available flaws detected:")
            for flaw_name in flaws_detected.keys():
                print(f"   - {flaw_name}")
    else:
        print("❌ Analysis failed or returned no results")
        
    print("\n📋 DEBUGGING CHECKLIST:")
    print("1. Check logs above for 'ELBOW FLARE DEBUG' messages")
    print("2. Look for elbow_flare_front_view values during Release/Follow-Through phases")
    print("3. Check if pose landmarks are being detected properly")
    print("4. Verify shot phases are identified correctly")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
