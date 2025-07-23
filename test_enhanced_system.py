"""
Test script to demonstrate the enhanced flaw detection system with real video analysis
"""
import os
import uuid
from basketball_analysis_service import VideoAnalysisJob, process_video_for_analysis, load_ideal_shot_data

def test_enhanced_flaw_detection():
    """Test the enhanced flaw detection system"""
    print("🏀 Testing Enhanced Flaw Detection System")
    print("=" * 50)
    
    # Use existing video or create dummy one
    test_video_path = 'user_shot.mp4'
    if not os.path.exists(test_video_path):
        print(f"Creating dummy video for testing...")
        import cv2
        import numpy as np
        
        # Create a simple test video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(test_video_path, fourcc, 20.0, (640, 480))
        
        for i in range(100):  # 5 seconds at 20fps
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            # Add some simple graphics to simulate motion
            cv2.circle(frame, (320 + i*2, 240 - i), 20, (255, 255, 255), -1)
            out.write(frame)
        
        out.release()
        print(f"✅ Created test video: {test_video_path}")
    
    # Create test job
    job_id = f"enhanced_test_{uuid.uuid4().hex[:8]}"
    test_job = VideoAnalysisJob(
        job_id=job_id,
        user_id="test_user",
        video_url=test_video_path
    )
    
    # Load ideal shot data
    ideal_data = load_ideal_shot_data('ideal_shot_guide.json')
    
    print(f"\n📋 Processing Job: {job_id}")
    print(f"📁 Video: {test_video_path}")
    
    # Process the video
    try:
        results = process_video_for_analysis(test_job, ideal_data)
        
        if results:
            print(f"\n✅ Analysis Complete!")
            print(f"📊 Results Summary:")
            print(f"   • Output Video: {results.get('output_video_path', 'N/A')}")
            print(f"   • Detailed Flaws: {len(results.get('detailed_flaws', []))}")
            print(f"   • Flaw Stills: {len(results.get('flaw_stills', []))}")
            print(f"   • Feedback Stills: {len(results.get('feedback_stills', {}))}")
            print(f"   • Shot Phases: {len(results.get('shot_phases', []))}")
            print(f"   • Feedback Points: {len(results.get('feedback_points', []))}")
            
            # List flaw stills created
            flaw_stills = results.get('flaw_stills', [])
            if flaw_stills:
                print(f"\n🎯 Flaw Analysis Stills Created:")
                for i, still in enumerate(flaw_stills, 1):
                    flaw_data = still.get('flaw_data', {})
                    print(f"   {i}. {still.get('file_path', 'N/A')}")
                    print(f"      Flaw: {flaw_data.get('flaw_type', 'Unknown')}")
                    print(f"      Frame: {still.get('frame_number', 'N/A')}")
                    print(f"      Severity: {flaw_data.get('severity', 'N/A')}")
                    print(f"      Issue: {flaw_data.get('plain_language', 'N/A')}")
            
            # Check if files exist
            print(f"\n📁 File Verification:")
            output_video = results.get('output_video_path')
            if output_video and os.path.exists(output_video):
                file_size = os.path.getsize(output_video) / (1024*1024)  # MB
                print(f"   ✅ Output Video: {output_video} ({file_size:.1f} MB)")
            else:
                print(f"   ❌ Output Video: Not found")
            
            for still in flaw_stills:
                still_path = still.get('file_path')
                if still_path and os.path.exists(still_path):
                    file_size = os.path.getsize(still_path) / 1024  # KB
                    print(f"   ✅ Still: {os.path.basename(still_path)} ({file_size:.1f} KB)")
                else:
                    print(f"   ❌ Still: {still_path} - Not found")
                    
        else:
            print("❌ No results returned from analysis")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🎯 Test Complete!")
    print(f"💡 To see the enhanced system in action:")
    print(f"   1. Open http://127.0.0.1:5000 in your browser")
    print(f"   2. Upload a real basketball shot video")
    print(f"   3. View results with downloadable flaw analysis stills")

if __name__ == "__main__":
    test_enhanced_flaw_detection()
