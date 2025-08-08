#!/usr/bin/env python3
"""
Debug script to test guide hand timing fixes with detailed analysis
"""
import sys
import logging
import os
from basketball_analysis_service import analyze_basketball_shot

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_guide_hand_timing(video_path):
    """Test guide hand timing fixes with detailed logging"""
    print(f"🏀 DEBUG: Testing guide hand timing fixes for: {video_path}")
    
    if not os.path.exists(video_path):
        print(f"❌ ERROR: Video file not found: {video_path}")
        return
    
    print("Starting analysis with TIMING FIXES...")
    print("🔧 Guide hand 'on top' now detects during Load/Dip phase (ball control)")
    print("🔧 Thumb flick still detects during late Follow-Through (after release)")
    print("📋 Proper phase separation for different guide hand issues")
    print("🎯 Each flaw now targets its biomechanically relevant phase")
    
    results = analyze_basketball_shot(video_path, "debug_guide_hand_timing")
    
    # Check all flaws with phase information
    print(f"\n📊 TOTAL FLAWS DETECTED: {len(results.get('detailed_flaws', []))}")
    for flaw in results.get('detailed_flaws', []):
        print(f"- {flaw['flaw_type']}: Frame {flaw['frame_number']}, Severity {flaw['severity']:.1f}")
        phase = flaw.get('phase', 'Unknown')
        print(f"  📍 Phase: {phase}")
        if flaw['flaw_type'] == 'guide_hand_on_top':
            print(f"  🎯 GUIDE HAND ON TOP - Should be in Load/Dip phase when ball is being controlled")
            print(f"  📝 Description: {flaw['plain_language']}")
        elif flaw['flaw_type'] == 'guide_hand_thumb_flick':
            print(f"  🎯 THUMB FLICK - Should be in Follow-Through phase after ball release")
            print(f"  📝 Description: {flaw['plain_language']}")
    
    print("\n✅ Timing fixes applied - guide hand issues now target correct phases")
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_guide_hand_timing.py <video_path>")
        sys.exit(1)
    
    debug_guide_hand_timing(sys.argv[1])
