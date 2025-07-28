import cv2
import mediapipe as mp
import numpy as np
import json
import logging
from basketball_analysis_service import *

# Set up logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise

# Test the analysis on your specific video
video_path = r'C:\Users\rickd\Downloads\analyzed_shot_6f1f7e19-934c-4516-a140-e2e1f069a17d.mp4'

print("="*60)
print("BASKETBALL SHOT ANALYSIS RESULTS")
print("="*60)
print(f"Video: {video_path}")
print()

# Create a job and run analysis
job = VideoAnalysisJob('test_job', 'test_user', video_path)
ideal_shot_data = load_ideal_shot_data('ideal_guide.json')

try:
    result = process_video_for_analysis(job, ideal_shot_data)
    
    # Check what the analysis actually returned
    if 'detailed_flaws' in result and result['detailed_flaws']:
        print(f"🎯 DETECTED FLAWS ({len(result['detailed_flaws'])} total):")
        print("-" * 50)
        
        for i, flaw in enumerate(result['detailed_flaws'], 1):
            severity = flaw['severity']
            flaw_type = flaw['flaw_type'].replace('_', ' ').title()
            
            # Use severity-based coloring indicators
            if severity >= 40:
                priority = "🔴 CRITICAL"
            elif severity >= 25:
                priority = "🟡 MAJOR"
            else:
                priority = "🟢 MINOR"
                
            print(f"{i}. {priority} - {flaw_type}")
            print(f"   Severity: {severity:.1f}/100")
            print(f"   Frame: {flaw['frame_number']}")
            print(f"   Issue: {flaw['plain_language']}")
            print(f"   Fix: {flaw.get('coaching_tip', 'Work on this aspect of your shot.')}")
            print()
    else:
        print("❌ NO DETAILED FLAWS DETECTED")
        
    # Also check feedback points
    if 'feedback_points' in result and result['feedback_points']:
        print(f"📋 FEEDBACK POINTS ({len(result['feedback_points'])} total):")
        print("-" * 50)
        
        for i, point in enumerate(result['feedback_points'], 1):
            severity = getattr(point, 'severity', 0)
            
            if severity >= 40:
                priority = "🔴 CRITICAL"
            elif severity >= 25:
                priority = "🟡 MAJOR"
            else:
                priority = "🟢 MINOR"
                
            print(f"{i}. {priority} - {point.discrepancy}")
            print(f"   Severity: {severity:.1f}/100" if severity > 0 else "   Severity: Not specified")
            print(f"   Frame: {point.frame_number}")
            print(f"   Fix: {point.remedy_tips}")
            print()
    else:
        print("❌ NO FEEDBACK POINTS GENERATED")

    # Check if elbow flare specifically was detected
    elbow_detected = False
    if 'detailed_flaws' in result:
        for flaw in result['detailed_flaws']:
            if 'elbow' in flaw['flaw_type'].lower():
                elbow_detected = True
                print(f"✅ ELBOW ISSUE DETECTED: {flaw['flaw_type']} (severity {flaw['severity']:.1f})")
                break
                
    if 'feedback_points' in result:
        for point in result['feedback_points']:
            if 'elbow' in point.discrepancy.lower():
                elbow_detected = True
                severity = getattr(point, 'severity', 0)
                print(f"✅ ELBOW FEEDBACK FOUND: {point.discrepancy} (severity {severity:.1f})")
                break
                
    if not elbow_detected:
        print("❌ NO ELBOW FLARE DETECTED - This indicates a problem!")
        
    print("="*60)

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
