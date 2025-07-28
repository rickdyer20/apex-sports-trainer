import cv2
import mediapipe as mp
import numpy as np
import json
import logging
from basketball_analysis_service import *

# Set up logging
logging.basicConfig(level=logging.INFO)

# Test the analysis pipeline
video_path = r'C:\Users\rickd\Downloads\analyzed_shot_6f1f7e19-934c-4516-a140-e2e1f069a17d.mp4'
print(f'Testing analysis on: {video_path}')

# Create a job and run analysis
job = VideoAnalysisJob('test_job', 'test_user', video_path)
ideal_shot_data = load_ideal_shot_data('ideal_guide.json')

try:
    result = process_video_for_analysis(job, ideal_shot_data)
    
    print('\n=== ANALYSIS RESULTS ===')
    print(f'Result type: {type(result)}')
    if isinstance(result, dict):
        print(f'Keys: {list(result.keys())}')
    
    if 'detailed_flaws' in result:
        detailed_flaws = result['detailed_flaws']
        print(f'\nFound {len(detailed_flaws)} detailed flaws:')
        
        for i, flaw in enumerate(detailed_flaws):
            flaw_type = flaw['flaw_type']
            severity = flaw['severity']
            frame_num = flaw['frame_number']
            description = flaw['plain_language']
            
            print(f'{i+1}. {flaw_type} - Severity: {severity:.1f}')
            print(f'   Frame: {frame_num}')
            print(f'   Description: {description}')
            print()
            
        # Check specifically for elbow flare
        elbow_flaws = [f for f in detailed_flaws if 'elbow' in f['flaw_type']]
        if elbow_flaws:
            print(f'ELBOW FLAWS FOUND: {len(elbow_flaws)}')
            for flaw in elbow_flaws:
                print(f'- {flaw["flaw_type"]}: severity {flaw["severity"]:.1f} at frame {flaw["frame_number"]}')
        else:
            print('NO ELBOW FLAWS DETECTED IN DETAILED ANALYSIS')
    else:
        print('No detailed_flaws found in result')
        
    if 'feedback_points' in result:
        feedback_points = result['feedback_points']
        print(f'\nFound {len(feedback_points)} feedback points:')
        for i, point in enumerate(feedback_points):
            print(f'{i+1}. {point.discrepancy}')
            
        # Check if elbow flare made it to feedback points
        elbow_feedback = [f for f in feedback_points if 'elbow' in f.discrepancy.lower()]
        if elbow_feedback:
            print(f'ELBOW FEEDBACK FOUND: {len(elbow_feedback)}')
        else:
            print('NO ELBOW FEEDBACK IN FINAL POINTS')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
