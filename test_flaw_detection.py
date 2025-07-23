"""
Create a sample basketball shot video with simulated pose data for testing flaw detection
"""
import cv2
import numpy as np
import json
from basketball_analysis_service import VideoAnalysisJob, process_video_for_analysis, load_ideal_shot_data

def create_basketball_shot_demo():
    """Create a demo video that simulates basketball shot motion"""
    
    # Video parameters
    width, height = 640, 480
    fps = 30
    duration_seconds = 3
    total_frames = fps * duration_seconds
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('basketball_shot_demo.mp4', fourcc, fps, (width, height))
    
    print(f"Creating basketball shot demo video...")
    print(f"Frames: {total_frames}, Duration: {duration_seconds}s")
    
    # Create frames with simulated basketball player
    for frame_num in range(total_frames):
        # Create black frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Progress through shot phases
        progress = frame_num / total_frames
        
        # Draw court
        cv2.rectangle(frame, (0, height-50), (width, height), (139, 69, 19), -1)  # Court
        cv2.line(frame, (width//2, 0), (width//2, height), (255, 255, 255), 2)    # Center line
        
        # Simulate player shooting motion
        if progress < 0.3:  # Loading phase
            # Player in set position
            torso_x = width // 2
            torso_y = height - 200
            knee_bend = int(20 * progress / 0.3)  # Gradual knee bend
            
        elif progress < 0.7:  # Release phase  
            # Player jumping and releasing
            torso_x = width // 2
            torso_y = height - 200 - int(30 * (progress - 0.3) / 0.4)  # Jump up
            knee_bend = 20 - int(20 * (progress - 0.3) / 0.4)  # Extend legs
            
        else:  # Follow-through
            # Player landing
            torso_x = width // 2
            torso_y = height - 200 - 30 + int(30 * (progress - 0.7) / 0.3)  # Come down
            knee_bend = int(10 * (progress - 0.7) / 0.3)  # Slight knee bend on landing
        
        # Draw simplified stick figure
        # Head
        cv2.circle(frame, (torso_x, torso_y - 80), 20, (255, 255, 255), 2)
        
        # Torso
        cv2.line(frame, (torso_x, torso_y - 60), (torso_x, torso_y + 40), (255, 255, 255), 3)
        
        # Arms (simulate shooting motion)
        if progress < 0.5:  # Preparing to shoot
            # Right arm (shooting arm)
            shoulder_x, shoulder_y = torso_x + 25, torso_y - 40
            elbow_x, elbow_y = torso_x + 40, torso_y - 10
            wrist_x, wrist_y = torso_x + 30, torso_y - 50
        else:  # Shooting/follow-through
            # Right arm extended
            shoulder_x, shoulder_y = torso_x + 25, torso_y - 40
            elbow_x, elbow_y = torso_x + 50, torso_y - 60
            wrist_x, wrist_y = torso_x + 60, torso_y - 80
            
        cv2.line(frame, (torso_x + 25, torso_y - 40), (elbow_x, elbow_y), (255, 255, 255), 3)
        cv2.line(frame, (elbow_x, elbow_y), (wrist_x, wrist_y), (255, 255, 255), 3)
        
        # Left arm (guide hand)
        cv2.line(frame, (torso_x - 25, torso_y - 40), (torso_x - 35, torso_y - 20), (255, 255, 255), 3)
        cv2.line(frame, (torso_x - 35, torso_y - 20), (torso_x - 25, torso_y - 50), (255, 255, 255), 3)
        
        # Legs
        hip_y = torso_y + 40
        knee_y = hip_y + 60 + knee_bend
        ankle_y = knee_y + 60
        
        # Right leg
        cv2.line(frame, (torso_x + 10, hip_y), (torso_x + 15, knee_y), (255, 255, 255), 3)
        cv2.line(frame, (torso_x + 15, knee_y), (torso_x + 20, ankle_y), (255, 255, 255), 3)
        
        # Left leg  
        cv2.line(frame, (torso_x - 10, hip_y), (torso_x - 15, knee_y), (255, 255, 255), 3)
        cv2.line(frame, (torso_x - 15, knee_y), (torso_x - 20, ankle_y), (255, 255, 255), 3)
        
        # Add basketball if in shooting phase
        if 0.4 < progress < 0.8:
            ball_x = wrist_x + int(20 * (progress - 0.4) / 0.4)
            ball_y = wrist_y - int(50 * (progress - 0.4) / 0.4)
            cv2.circle(frame, (ball_x, ball_y), 8, (255, 165, 0), -1)  # Orange basketball
            cv2.circle(frame, (ball_x, ball_y), 8, (0, 0, 0), 1)       # Black outline
        
        # Add frame counter
        cv2.putText(frame, f"Frame: {frame_num}/{total_frames}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add phase indicator
        if progress < 0.3:
            phase = "LOAD/DIP"
            color = (0, 255, 255)  # Yellow
        elif progress < 0.7:
            phase = "RELEASE"
            color = (0, 255, 0)    # Green
        else:
            phase = "FOLLOW-THROUGH"
            color = (255, 0, 255)  # Magenta
            
        cv2.putText(frame, f"Phase: {phase}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        out.write(frame)
    
    out.release()
    print("Demo video created: basketball_shot_demo.mp4")
    return "basketball_shot_demo.mp4"

def test_flaw_detection():
    """Test the enhanced flaw detection system"""
    # Create demo video
    demo_video = create_basketball_shot_demo()
    
    # Load ideal shot data
    ideal_data = load_ideal_shot_data('ideal_shot_guide.json')
    
    # Create analysis job
    test_job = VideoAnalysisJob(
        job_id="flaw_detection_test",
        user_id="demo_user",
        video_url=demo_video
    )
    
    print(f"\n=== TESTING ENHANCED FLAW DETECTION ===")
    print(f"Video: {demo_video}")
    print(f"Expected features:")
    print(f"  • Detailed flaw analysis")
    print(f"  • Frame-by-frame breakdown")
    print(f"  • Visual overlays with explanations")
    print(f"  • Coaching tips and drill suggestions")
    print(f"  • Up to 8 key flaw detection stills")
    
    # Process with enhanced analysis
    process_video_for_analysis(test_job, ideal_data)
    
    print(f"\n=== FLAW DETECTION TEST COMPLETE ===")
    print(f"Check the current directory for:")
    print(f"  • temp_flaw_detection_test_analyzed.mp4 (main analysis video)")
    print(f"  • temp_flaw_detection_test_flaw_*.png (detailed flaw stills)")

if __name__ == "__main__":
    test_flaw_detection()
