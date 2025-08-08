#!/usr/bin/env python3
"""
Debug script to test thumb flick frame selection with detailed analysis
"""
import sys
import logging
import os
from basketball_analysis_service import analyze_basketball_shot

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_frame_selection(video_path):
    """Test frame selection for thumb flick with detailed logging"""
    print(f"🏀 DEBUG: Testing thumb flick frame selection for: {video_path}")
    
    if not os.path.exists(video_path):
        print(f"❌ ERROR: Video file not found: {video_path}")
        return
    
    print("Starting analysis with ABSOLUTE FINAL FRAMES restriction...")
    print("🔍 Thumb flick detection now ONLY targets final 10% of Follow-Through phase (90-100%)")
    print("📋 Frames before 90% Follow-Through progress are COMPLETELY REJECTED")
    print("🎯 Frame selection: 99% illustration quality, 1% severity weighting")
    print("🚀 ABSOLUTE EXTREME: 95-100% gets 300 points, 90-95% gets 200 points")
    print("⚠️  DEVASTATING penalties for any frames before 90% Follow-Through")
    print("🎯 ABSOLUTE RESTRICTION: Thumb flick can ONLY be detected in final 10% of Follow-Through")
    results = analyze_basketball_shot(video_path, "debug_frame_selection")
    
    # Check all flaws
    print(f"\n📊 TOTAL FLAWS DETECTED: {len(results.get('detailed_flaws', []))}")
    for flaw in results.get('detailed_flaws', []):
        print(f"- {flaw['flaw_type']}: Frame {flaw['frame_number']}, Severity {flaw['severity']}")
        if flaw['flaw_type'] == 'guide_hand_thumb_flick':
            print(f"  🎯 THUMB FLICK FOUND - Frame: {flaw['frame_number']}, Phase: {flaw.get('phase', 'Unknown')}")
            print(f"  📝 Description: {flaw['plain_language']}")
            return flaw['frame_number']
    
    print("❌ No thumb flick detected - Check log output above for thumb angle measurements")
    print("Look for 'guide_hand_thumb_angle' or 'THUMB FLICK' in the debug output")
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_thumb_flick.py <video_path>")
        sys.exit(1)
    
    debug_frame_selection(sys.argv[1])
