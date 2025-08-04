#!/usr/bin/env python3
"""
Debug thumb flick detection for Brandon front video analysis
"""

import sys
import os
import logging
import json
from basketball_analysis_service import analyze_basketball_shot

# Configure logging to see detailed thumb flick analysis
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('thumb_flick_debug.log')
    ]
)

def debug_thumb_flick_detection():
    """Debug thumb flick detection with detailed logging"""
    
    # Test video file
    video_file = "basketball_shot_demo.mp4"
    
    if not os.path.exists(video_file):
        print(f"❌ Video file not found: {video_file}")
        return False
    
    print(f"🔍 Debugging thumb flick detection for: {video_file}")
    
    # Analyze the video with focus on guide hand metrics
    try:
        results = analyze_basketball_shot(video_file)
        
        if results and 'detailed_flaws' in results:
            print(f"\n📊 Found {len(results['detailed_flaws'])} total flaws:")
            
            # Check for thumb flick specifically
            thumb_flick_found = False
            for flaw in results['detailed_flaws']:
                print(f"  - {flaw['flaw_type']}: {flaw['plain_language']} (Severity: {flaw['severity']})")
                if flaw['flaw_type'] == 'guide_hand_thumb_flick':
                    thumb_flick_found = True
                    print(f"    ✅ THUMB FLICK DETECTED at frame {flaw['frame_number']}")
            
            if not thumb_flick_found:
                print("  ❌ NO THUMB FLICK DETECTED")
                
                # Let's examine the raw metrics to see what's happening
                if 'processed_frames_data' in results:
                    print("\n🔬 Examining guide hand thumb angles in processed frames:")
                    thumb_angles = []
                    for i, frame_data in enumerate(results['processed_frames_data']):
                        if frame_data.metrics and 'guide_hand_thumb_angle' in frame_data.metrics:
                            angle = frame_data.metrics['guide_hand_thumb_angle']
                            thumb_angles.append(angle)
                            if angle > 20:  # Show significant angles
                                print(f"    Frame {i}: thumb angle = {angle:.1f}°")
                    
                    if thumb_angles:
                        max_angle = max(thumb_angles)
                        avg_angle = sum(thumb_angles) / len(thumb_angles)
                        print(f"\n📈 Thumb angle statistics:")
                        print(f"    Max: {max_angle:.1f}°")
                        print(f"    Avg: {avg_angle:.1f}°")
                        print(f"    Current threshold: 35°")
                        
                        if max_angle > 25:
                            print(f"    ⚠️  Max angle {max_angle:.1f}° suggests thumb movement but below threshold!")
                    else:
                        print("    ❌ No guide hand thumb angles found in metrics")
        else:
            print("❌ No analysis results or detailed flaws found")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def examine_current_thresholds():
    """Show current detection thresholds"""
    print("\n🎯 Current thumb flick detection settings:")
    print("   - Phase restriction: Follow-Through only")
    print("   - Threshold: 35° (very strict)")
    print("   - Previous threshold was: 25°")
    print("\n💡 Suggestion: Lower threshold to 25° or 20° to catch more obvious cases")

if __name__ == "__main__":
    print("🏀 Basketball Shot Analysis - Thumb Flick Debug")
    print("=" * 50)
    
    success = debug_thumb_flick_detection()
    examine_current_thresholds()
    
    if success:
        print("\n✅ Debug completed successfully")
    else:
        print("\n❌ Debug failed")
