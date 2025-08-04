#!/usr/bin/env python3
"""
Test script for refined elbow flare detection
Tests the new stricter thresholds and Release-phase-only analysis
"""

import logging
import cv2
from basketball_analysis_service import analyze_video

def test_refined_elbow_detection():
    """Test the refined elbow flare detection with existing demo video"""
    
    # Configure logging to see detection details
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    video_path = 'basketball_shot_demo.mp4'
    
    try:
        print("🏀 Testing REFINED Elbow Flare Detection")
        print("=" * 50)
        print("Changes implemented:")
        print("✓ Release phase ONLY analysis (no Follow-Through)")
        print("✓ STRICTER thresholds: 30% front view (was 25%), 15° lateral (was 10°)")
        print("✓ Consistency requirement: 60% of Release frames must show flare")
        print("✓ Higher minimum severity: 5.0 (was 3.0)")
        print("=" * 50)
        
        # Run analysis
        result = analyze_video(video_path)
        
        if result and result.get('success'):
            analysis_report = result.get('analysis_report', {})
            detected_flaws = analysis_report.get('detected_flaws', [])
            
            print(f"\n📊 ANALYSIS RESULTS:")
            print(f"Total flaws detected: {len(detected_flaws)}")
            
            # Look specifically for elbow flare
            elbow_flare_found = False
            for flaw in detected_flaws:
                if flaw['type'] == 'elbow_flare':
                    elbow_flare_found = True
                    print(f"\n🚨 ELBOW FLARE DETECTED:")
                    print(f"   Severity: {flaw['severity']:.1f}")
                    print(f"   Frame: {flaw['frame']}")
                    print(f"   Description: {flaw['description']}")
                    print(f"   Tip: {flaw['coaching_tip']}")
                    break
            
            if not elbow_flare_found:
                print(f"\n✅ NO ELBOW FLARE DETECTED")
                print("   This could indicate:")
                print("   • Good shooting form in this video")
                print("   • Refined detection successfully filtered out false positives")
                print("   • Stricter thresholds working as intended")
            
            # Show all detected flaws for context
            print(f"\n📋 ALL DETECTED FLAWS:")
            for i, flaw in enumerate(detected_flaws, 1):
                print(f"{i}. {flaw['type']}: severity {flaw['severity']:.1f}")
                
        else:
            print("❌ Analysis failed")
            if result:
                print(f"Error: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        logging.exception("Test error details:")

def compare_detection_logs():
    """Helper to analyze the detection logs for insights"""
    print(f"\n🔍 DETECTION ANALYSIS TIPS:")
    print("Look in the logs above for these key indicators:")
    print("• 'ELBOW FLARE SKIPPED' - frames excluded (non-Release phase)")
    print("• 'ELBOW FLARE NOT DETECTED' - frames that passed strict thresholds")
    print("• 'ELBOW FLARE DETECTED' - frames with severity calculations")
    print("• 'ELBOW FLARE CONFIRMED/REJECTED' - final consistency check results")

if __name__ == '__main__':
    test_refined_elbow_detection()
    compare_detection_logs()
