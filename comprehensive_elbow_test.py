"""
Comprehensive test to trace exactly where elbow flare detection might be failing
"""
import cv2
import mediapipe as mp
import numpy as np
import json
import logging
from basketball_analysis_service import *

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def comprehensive_elbow_test():
    video_path = r'C:\Users\rickd\Downloads\analyzed_shot_6f1f7e19-934c-4516-a140-e2e1f069a17d.mp4'
    
    print("=" * 80)
    print("COMPREHENSIVE ELBOW FLARE DETECTION TEST")
    print("=" * 80)
    print(f"Video: {video_path}")
    print()
    
    # Create job and load ideal data
    job = VideoAnalysisJob('test_job', 'test_user', video_path)
    ideal_shot_data = load_ideal_shot_data('ideal_guide.json')
    
    try:
        # 1. Test the full analysis pipeline
        print("🔍 STEP 1: Running full analysis pipeline...")
        result = process_video_for_analysis(job, ideal_shot_data)
        
        print(f"✅ Analysis completed. Result type: {type(result)}")
        print(f"✅ Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        # 2. Check detailed_flaws specifically
        if 'detailed_flaws' in result:
            detailed_flaws = result['detailed_flaws']
            print(f"✅ Found detailed_flaws: {len(detailed_flaws)} total")
            
            for i, flaw in enumerate(detailed_flaws, 1):
                print(f"\n  Flaw {i}:")
                print(f"    Type: {flaw.get('flaw_type', 'N/A')}")
                print(f"    Severity: {flaw.get('severity', 'N/A')}")
                print(f"    Frame: {flaw.get('frame_number', 'N/A')}")
                print(f"    Phase: {flaw.get('phase', 'N/A')}")
                print(f"    Description: {flaw.get('plain_language', 'N/A')}")
                print(f"    Has coaching_tip: {'coaching_tip' in flaw}")
                
                # Check specifically for elbow flaws
                if 'elbow' in flaw.get('flaw_type', '').lower():
                    print(f"    🎯 ELBOW FLAW DETECTED!")
                    
        else:
            print("❌ No detailed_flaws found in result")
            
        # 3. Check feedback_points
        if 'feedback_points' in result:
            feedback_points = result['feedback_points']
            print(f"✅ Found feedback_points: {len(feedback_points)} total")
            
            elbow_feedback_count = 0
            for i, point in enumerate(feedback_points, 1):
                if hasattr(point, 'discrepancy') and 'elbow' in point.discrepancy.lower():
                    elbow_feedback_count += 1
                    severity = getattr(point, 'severity', 'N/A')
                    print(f"  🎯 Elbow feedback {elbow_feedback_count}: {point.discrepancy} (severity: {severity})")
                    
            if elbow_feedback_count == 0:
                print("  ❌ No elbow-related feedback found")
        else:
            print("❌ No feedback_points found in result")
            
        # 4. Test if the issue is in the analyze_detailed_flaws function directly
        print("\n🔍 STEP 2: Testing analyze_detailed_flaws function directly...")
        
        # We need to recreate the processed_frames_data and shot_phases
        # This is a simplified test, but will help isolate the issue
        print("Note: Direct function testing would require full frame processing setup")
        
        # 5. Summary
        print("\n" + "=" * 80)
        print("SUMMARY:")
        
        elbow_in_detailed = any('elbow' in flaw.get('flaw_type', '').lower() 
                              for flaw in result.get('detailed_flaws', []))
        elbow_in_feedback = any(hasattr(point, 'discrepancy') and 'elbow' in point.discrepancy.lower() 
                               for point in result.get('feedback_points', []))
        
        if elbow_in_detailed:
            print("✅ ELBOW FLARE DETECTED in detailed_flaws")
        else:
            print("❌ ELBOW FLARE NOT FOUND in detailed_flaws")
            
        if elbow_in_feedback:
            print("✅ ELBOW FEEDBACK FOUND in feedback_points")
        else:
            print("❌ ELBOW FEEDBACK NOT FOUND in feedback_points")
            
        if elbow_in_detailed or elbow_in_feedback:
            print("\n🎯 CONCLUSION: Elbow flare IS being detected by the analysis engine!")
            print("   The issue must be in how results are displayed in your application.")
            print("   Check your web interface, PDF generation, or result processing.")
        else:
            print("\n❌ CONCLUSION: Elbow flare is NOT being detected at all!")
            print("   This indicates a deeper issue in the analysis logic.")
            
        return result
        
    except Exception as e:
        print(f"❌ ERROR during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    comprehensive_elbow_test()
