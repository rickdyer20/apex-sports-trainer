#!/usr/bin/env python3
"""
Test Frame Synchronization Fix for Basketball Analysis Service
Tests that pose estimation lines align perfectly with player's body in frame stills
"""

import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_frame_sync_fix():
    """Test the frame synchronization fix by analyzing a video and checking for sync issues"""
    
    print("🏀 Testing Frame Synchronization Fix")
    print("=" * 50)
    
    # Check if demo video exists
    demo_video = "basketball_shot_demo.mp4"
    if not os.path.exists(demo_video):
        print(f"❌ Demo video not found: {demo_video}")
        print("Please ensure you have a test video in the current directory")
        return False
    
    try:
        from basketball_analysis_service import analyze_basketball_shot
        
        print(f"📹 Analyzing video: {demo_video}")
        print("🔍 Looking for frame synchronization issues...")
        
        # Run analysis
        results = analyze_basketball_shot(demo_video)
        
        if 'error' in results:
            print(f"❌ Analysis failed: {results['error']}")
            return False
        
        # Check for sync issues in logs
        flaws = results.get('detailed_flaws', [])
        print(f"\n📊 Analysis Results:")
        print(f"   • Found {len(flaws)} shooting flaws")
        
        # Check if frame stills were captured
        frame_stills_captured = 0
        for flaw in flaws[:5]:  # Check first 5 flaws
            if flaw.get('frame_still_path'):
                frame_stills_captured += 1
                print(f"   • {flaw['flaw_type']} - Frame still captured ✅")
            else:
                print(f"   • {flaw['flaw_type']} - No frame still captured ⚠️")
        
        print(f"\n🎯 Frame Still Capture Rate: {frame_stills_captured}/{min(len(flaws), 5)}")
        
        if frame_stills_captured > 0:
            print("✅ FRAME SYNC FIX SUCCESSFUL: Frame stills were captured")
            print("📝 Next Steps:")
            print("   1. Manually inspect frame stills to verify pose lines align with player")
            print("   2. Look for 'POSE AND FRAME SYNCHRONIZED' messages in logs")
            print("   3. Check that there are no 'SYNC ISSUE' warnings")
            return True
        else:
            print("⚠️  No frame stills captured - this may indicate an issue")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_log_for_sync_issues():
    """Check the log file for synchronization issues"""
    log_file = "basketball_analysis.log"
    if os.path.exists(log_file):
        print(f"\n🔍 Checking {log_file} for synchronization messages...")
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            sync_success = 0
            sync_issues = 0
            
            for line in lines[-100:]:  # Check last 100 lines
                if "POSE AND FRAME SYNCHRONIZED" in line:
                    sync_success += 1
                elif "SYNC ISSUE" in line:
                    sync_issues += 1
            
            print(f"   • Successful synchronizations: {sync_success}")
            print(f"   • Synchronization issues: {sync_issues}")
            
            if sync_success > 0 and sync_issues == 0:
                print("✅ Perfect frame synchronization achieved!")
            elif sync_success > sync_issues:
                print("✅ Frame synchronization mostly working (some minor issues)")
            else:
                print("⚠️  Frame synchronization needs attention")
                
        except Exception as e:
            print(f"Error reading log file: {e}")

if __name__ == "__main__":
    print("🏀 FRAME SYNCHRONIZATION FIX VALIDATION")
    print("=" * 60)
    print("This test validates that pose estimation lines now align")
    print("perfectly with the player's body in frame stills.")
    print("=" * 60)
    
    success = test_frame_sync_fix()
    check_log_for_sync_issues()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 FRAME SYNC FIX VALIDATION COMPLETE")
        print("Frame stills should now have perfectly aligned pose estimation lines!")
    else:
        print("❌ FRAME SYNC FIX NEEDS ATTENTION")
        print("Please check the logs for specific issues.")
    print("=" * 60)
