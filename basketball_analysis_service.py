# --- Configuration & Imports (Conceptual) ---
# These would be handled via environment variables, configuration files,
# and dependency injection in a real service.
import os
import cv2
import mediapipe as mp
import numpy as np
import json
import logging # For robust logging
from datetime import datetime
from pdf_generator import generate_improvement_plan_pdf

# --- Service Initialization (on service startup) ---
mp_pose = mp.solutions.pose
pose_model = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# --- Data Structures (Conceptual - how data would be stored in a DB/object storage) ---

class VideoAnalysisJob:
    """Represents a single video analysis request."""
    def __init__(self, job_id, user_id, video_url, status="PENDING"):
        self.job_id = job_id
        self.user_id = user_id
        self.video_url = video_url # URL to the raw uploaded video in cloud storage
        self.status = status # PENDING, PROCESSING, COMPLETED, FAILED
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.results_url = None # URL to the final analysis video/report

class FrameData:
    """Stores pose landmarks and calculated metrics for a single frame."""
    def __init__(self, frame_number, landmarks_raw, metrics):
        self.frame_number = frame_number
        self.landmarks_raw = landmarks_raw # Raw MediaPipe landmarks
        self.metrics = metrics # Dictionary of calculated angles, velocities etc.

class ShotPhase:
    """Defines a distinct phase of the shot."""
    def __init__(self, name, start_frame, end_frame, key_moment_frame=None):
        self.name = name
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.key_moment_frame = key_moment_frame # E.g., peak of jump, release frame

class FeedbackPoint:
    """Details a discrepancy and suggested remedy."""
    def __init__(self, frame_number, discrepancy, ideal_range, user_value, remedy_tips, critical_landmarks=None):
        self.frame_number = frame_number
        self.discrepancy = discrepancy
        self.ideal_range = ideal_range
        self.user_value = user_value
        self.remedy_tips = remedy_tips # Specific drills or mental cues
        self.critical_landmarks = critical_landmarks # Landmarks relevant to this feedback

class AnalysisReport:
    """Aggregates all analysis results for a video."""
    def __init__(self, job_id, user_id, video_url, phases, feedback_points, overall_score=None):
        self.job_id = job_id
        self.user_id = user_id
        self.video_url = video_url
        self.phases = phases
        self.feedback_points = feedback_points
        self.overall_score = overall_score # Optional, e.g., an overall shot score
        self.created_at = datetime.now()

# --- Helper Functions (as part of the service's utility module) ---

def download_video_from_storage(video_url, local_path):
    """Simulates downloading video from S3/GCS."""
    logging.info(f"Downloading video from {video_url} to {local_path}")
    # In a real system: use AWS S3 client, Google Cloud Storage client etc.
    # For this pseudo-code, we'll simulate by copying if source exists
    if os.path.exists(video_url) and video_url != local_path:
        # Copy the file to simulate download
        import shutil
        shutil.copy2(video_url, local_path)
        print(f"Copied {video_url} to {local_path}")
    elif not os.path.exists(local_path):
        # Dummy file creation for demonstration
        print(f"Creating a dummy video file at {local_path} as placeholder.")
        # This would be a proper download in production
        # Example: a placeholder for a real video file
        # You'd need a small sample video named 'user_shot.mp4' for local testing
        pass
    return True

def upload_file_to_storage(local_path, destination_url):
    """Simulates uploading processed video/report to S3/GCS."""
    logging.info(f"Uploading {local_path} to {destination_url}")
    # In a real system: use AWS S3 client, Google Cloud Storage client etc.
    return destination_url

def calculate_angle(p1, p2, p3):
    """Calculates the angle (in degrees) between three 2D points, p2 is the vertex."""
    # Ensure points are numpy arrays for vector operations
    p1 = np.array(p1)
    p2 = np.array(p2)
    p3 = np.array(p3)

    v1 = p1 - p2
    v2 = p3 - p2

    dot_product = np.dot(v1, v2)
    magnitude_v1 = np.linalg.norm(v1)
    magnitude_v2 = np.linalg.norm(v2)

    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return 0 # Handle division by zero if points are identical

    angle_rad = np.arccos(np.clip(dot_product / (magnitude_v1 * magnitude_v2), -1.0, 1.0))
    angle_deg = np.degrees(angle_rad)

    return angle_deg

def get_landmark_coords(landmarks, landmark_enum, width, height):
    """Extracts pixel coordinates for a given landmark."""
    lm = landmarks.landmark[landmark_enum.value]
    return [int(lm.x * width), int(lm.y * height)]

def load_ideal_shot_data(ideal_guide_path):
    """
    Loads pre-defined ideal shot metrics or a processed ideal shot reference.
    In a real system, this could be a sophisticated model or lookup table.
    """
    logging.info(f"Loading ideal shot data from {ideal_guide_path}")
    # This JSON would contain ideal angle ranges, timing thresholds, etc.
    # Example structure for part of the ideal data:
    # {
    #   "release_elbow_angle": {"min": 160, "max": 180},
    #   "load_knee_angle": {"min": 110, "max": 130},
    #   "follow_through_wrist_snap_angle": {"min": 70, "max": 90},
    #   "common_remedies": {
    #       "elbow_flare": "Keep elbow tucked. Imagine 'shooting through a tunnel'.",
    #       "no_wrist_snap": "Finish with fingers pointing down, 'reach for the cookie jar'.",
    #       ...
    #   }
    # }
    try:
        with open(ideal_guide_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Ideal shot guide not found at {ideal_guide_path}. Using dummy data.")
        return {
            "release_elbow_angle": {"min": 160, "max": 180},
            "load_knee_angle": {"min": 110, "max": 130},
            "follow_through_wrist_snap_angle": {"min": 70, "max": 90},
            "common_remedies": {
                "elbow_extension": "Focus on fully extending your elbow towards the basket.",
                "knee_drive": "Explode upwards by pushing through your heels.",
                "wrist_snap": "Finish with your fingers pointing down at the rim after release.",
                "balance": "Land in the same spot you jumped from, maintaining good balance."
            }
        }


def analyze_detailed_flaws(processed_frames_data, ideal_shot_data, shot_phases, fps):
    """
    Analyze video frames for specific shooting flaws and identify key problematic frames
    Returns detailed flaw analysis with frame numbers and descriptions
    """
    detailed_flaws = []
    
    # Define common shooting flaws to detect
    flaw_detectors = {
        'elbow_flare': {
            'description': 'Shooting elbow positioned too far from body',
            'check_phase': 'Release',
            'threshold': 15,  # degrees from ideal
            'plain_language': 'Your shooting elbow is sticking out too far from your body. This reduces accuracy and consistency.'
        },
        'inconsistent_release_point': {
            'description': 'Release point varies significantly between frames',
            'check_phase': 'Release',
            'threshold': 30,  # pixel variance
            'plain_language': 'Your release point is not consistent. Try to release the ball from the same spot every time.'
        },
        'insufficient_knee_bend': {
            'description': 'Knee bend too shallow for proper power generation',
            'check_phase': 'Load/Dip',
            'threshold': 20,  # degrees less than ideal minimum
            'plain_language': 'You\'re not bending your knees enough. Get lower to generate more power and improve your shooting range.'
        },
        'excessive_knee_bend': {
            'description': 'Knee bend too deep, wasting energy',
            'check_phase': 'Load/Dip',
            'threshold': 20,  # degrees more than ideal maximum
            'plain_language': 'You\'re bending your knees too much. This wastes energy and can make your shot inconsistent.'
        },
        'poor_follow_through': {
            'description': 'Insufficient wrist snap on follow-through',
            'check_phase': 'Release',
            'threshold': 15,  # degrees from ideal
            'plain_language': 'Your follow-through needs work. Snap your wrist down like you\'re reaching into a cookie jar.'
        },
        'rushing_shot': {
            'description': 'Shot release too quick, lacks rhythm',
            'check_phase': 'Release',
            'threshold': 200,  # milliseconds faster than ideal
            'plain_language': 'You\'re rushing your shot. Slow down and find your shooting rhythm for better consistency.'
        },
        'balance_issues': {
            'description': 'Poor balance affecting shot accuracy',
            'check_phase': 'Release',
            'threshold': 10,  # degrees of body lean
            'plain_language': 'Your balance is off during the shot. Focus on staying centered and landing where you started.'
        },
        'guide_hand_interference': {
            'description': 'Off-hand affecting ball trajectory',
            'check_phase': 'Release',
            'threshold': 5,   # degrees of hand deviation
            'plain_language': 'Your guide hand is interfering with the shot. Keep it on the side of the ball, not underneath.'
        }
    }
    
    # Analyze each phase for specific flaws
    for phase in shot_phases:
        phase_frames = []
        for i, frame_data in enumerate(processed_frames_data):
            if phase.start_frame <= i <= phase.end_frame and frame_data.metrics:
                phase_frames.append((i, frame_data))
        
        if not phase_frames:
            continue
            
        # Check for specific flaws in this phase
        for flaw_key, flaw_config in flaw_detectors.items():
            if flaw_config['check_phase'] != phase.name:
                continue
                
            flaw_detected, worst_frame, severity = detect_specific_flaw(
                phase_frames, flaw_key, flaw_config, ideal_shot_data
            )
            
            if flaw_detected:
                detailed_flaws.append({
                    'flaw_type': flaw_key,
                    'frame_number': worst_frame,
                    'phase': phase.name,
                    'severity': severity,
                    'description': flaw_config['description'],
                    'plain_language': flaw_config['plain_language'],
                    'coaching_tip': get_coaching_tip(flaw_key),
                    'drill_suggestion': get_drill_suggestion(flaw_key)
                })
    
    # Sort by severity (worst first) and limit to top 8
    detailed_flaws.sort(key=lambda x: x['severity'], reverse=True)
    return detailed_flaws[:8]

def detect_specific_flaw(phase_frames, flaw_key, flaw_config, ideal_shot_data):
    """Detect if a specific flaw exists in the given frames"""
    worst_severity = 0
    worst_frame = None
    flaw_detected = False
    
    for frame_num, frame_data in phase_frames:
        severity = 0
        
        if flaw_key == 'insufficient_knee_bend':
            if 'knee_angle' in frame_data.metrics:
                ideal_min = ideal_shot_data['load_knee_angle']['min']
                actual = frame_data.metrics['knee_angle']
                if actual > ideal_min + flaw_config['threshold']:
                    severity = actual - ideal_min
                    flaw_detected = True
                    
        elif flaw_key == 'excessive_knee_bend':
            if 'knee_angle' in frame_data.metrics:
                ideal_max = ideal_shot_data['load_knee_angle']['max']
                actual = frame_data.metrics['knee_angle']
                if actual < ideal_max - flaw_config['threshold']:
                    severity = ideal_max - actual
                    flaw_detected = True
                    
        elif flaw_key == 'poor_follow_through':
            if 'wrist_angle_simplified' in frame_data.metrics:
                ideal_range = ideal_shot_data['follow_through_wrist_snap_angle']
                actual = frame_data.metrics['wrist_angle_simplified']
                if actual < ideal_range['min'] - flaw_config['threshold']:
                    severity = ideal_range['min'] - actual
                    flaw_detected = True
                    
        elif flaw_key == 'elbow_flare':
            if 'elbow_angle' in frame_data.metrics:
                ideal_range = ideal_shot_data['release_elbow_angle']
                actual = frame_data.metrics['elbow_angle']
                # Simplified elbow flare detection
                if actual < ideal_range['min'] - flaw_config['threshold']:
                    severity = ideal_range['min'] - actual
                    flaw_detected = True
        
        # Add more flaw detection logic here for other flaw types
        
        if severity > worst_severity:
            worst_severity = severity
            worst_frame = frame_num
    
    return flaw_detected, worst_frame, worst_severity

def get_coaching_tip(flaw_key):
    """Get specific coaching tip for each flaw type"""
    tips = {
        'elbow_flare': 'Keep your shooting elbow directly under the ball. Imagine shooting through a narrow tunnel.',
        'insufficient_knee_bend': 'Bend your knees more to get into a proper athletic position. Think "sit back" into your shot.',
        'excessive_knee_bend': 'Don\'t over-bend your knees. Find a comfortable athletic stance that you can repeat consistently.',
        'poor_follow_through': 'Snap your wrist down aggressively. Hold your follow-through until the ball hits the rim.',
        'rushing_shot': 'Slow down your shooting motion. Count "1-2-shoot" to develop better rhythm.',
        'balance_issues': 'Focus on your base. Keep your feet shoulder-width apart and land in the same spot.',
        'guide_hand_interference': 'Your guide hand should be a passenger. Remove it just before release.',
        'inconsistent_release_point': 'Practice your shooting pocket. Release from the same spot every time.'
    }
    return tips.get(flaw_key, 'Work with a coach to improve this aspect of your shot.')

def get_drill_suggestion(flaw_key):
    """Get specific drill suggestion for each flaw type"""
    drills = {
        'elbow_flare': 'Wall shooting drill: Stand close to a wall and practice your shooting motion without hitting the wall.',
        'insufficient_knee_bend': 'Chair shooting: Practice shooting while sitting on a chair, then stand up as you shoot.',
        'excessive_knee_bend': 'Mirror work: Practice your shooting stance in front of a mirror to find the right knee bend.',
        'poor_follow_through': 'Bed shooting: Lie on your back and practice shooting straight up, focusing on wrist snap.',
        'rushing_shot': 'Slow motion shooting: Practice your entire shooting motion in slow motion 10 times.',
        'balance_issues': 'One-foot shooting: Practice shooting while standing on one foot to improve balance.',
        'guide_hand_interference': 'One-handed shooting: Practice shooting with only your shooting hand.',
        'inconsistent_release_point': 'Form shooting: Stand close to the basket and focus only on perfect form.'
    }
    return drills.get(flaw_key, 'Practice basic shooting fundamentals daily.')

def create_flaw_overlay(frame, flaw_data, landmarks, width, height):
    """Create detailed overlay on frame showing specific flaw analysis"""
    # Create overlay frame
    overlay_frame = frame.copy()
    
    # Add semi-transparent background for text
    cv2.rectangle(overlay_frame, (10, 10), (width-10, 200), (0, 0, 0), -1)
    cv2.rectangle(overlay_frame, (10, 10), (width-10, 200), (255, 255, 255), 2)
    
    # Add flaw title
    cv2.putText(overlay_frame, f"FLAW DETECTED: {flaw_data['flaw_type'].replace('_', ' ').upper()}", 
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    # Add phase information
    cv2.putText(overlay_frame, f"Phase: {flaw_data['phase']}", 
                (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Add severity
    severity_color = (0, 255, 255) if flaw_data['severity'] < 20 else (0, 165, 255) if flaw_data['severity'] < 40 else (0, 0, 255)
    cv2.putText(overlay_frame, f"Severity: {flaw_data['severity']:.1f}", 
                (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, severity_color, 2)
    
    # Add description (wrapped text)
    description_lines = wrap_text(flaw_data['plain_language'], 60)
    for i, line in enumerate(description_lines[:3]):  # Max 3 lines
        cv2.putText(overlay_frame, line, 
                    (20, 130 + i*25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Highlight relevant body parts based on flaw type
    if landmarks and landmarks.pose_landmarks:
        highlight_relevant_landmarks(overlay_frame, landmarks, flaw_data['flaw_type'], width, height)
    
    # Add bottom overlay with coaching tip
    cv2.rectangle(overlay_frame, (10, height-120), (width-10, height-10), (0, 100, 0), -1)
    cv2.rectangle(overlay_frame, (10, height-120), (width-10, height-10), (255, 255, 255), 2)
    
    cv2.putText(overlay_frame, "COACHING TIP:", 
                (20, height-90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    tip_lines = wrap_text(flaw_data['coaching_tip'], 70)
    for i, line in enumerate(tip_lines[:2]):  # Max 2 lines
        cv2.putText(overlay_frame, line, 
                    (20, height-65 + i*20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    return overlay_frame

def highlight_relevant_landmarks(frame, landmarks, flaw_type, width, height):
    """Highlight body landmarks relevant to the specific flaw"""
    # Define which landmarks to highlight for each flaw type
    landmark_groups = {
        'elbow_flare': [mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST],
        'insufficient_knee_bend': [mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE, mp_pose.PoseLandmark.RIGHT_ANKLE],
        'excessive_knee_bend': [mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE, mp_pose.PoseLandmark.RIGHT_ANKLE],
        'poor_follow_through': [mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST],
        'balance_issues': [mp_pose.PoseLandmark.LEFT_ANKLE, mp_pose.PoseLandmark.RIGHT_ANKLE, mp_pose.PoseLandmark.NOSE],
        'guide_hand_interference': [mp_pose.PoseLandmark.LEFT_WRIST, mp_pose.PoseLandmark.LEFT_ELBOW]
    }
    
    relevant_landmarks = landmark_groups.get(flaw_type, [])
    
    # Draw highlighted landmarks
    for landmark in relevant_landmarks:
        coords = get_landmark_coords(landmarks.pose_landmarks, landmark, width, height)
        cv2.circle(frame, tuple(coords), 15, (0, 255, 255), 3)  # Yellow highlight
        cv2.circle(frame, tuple(coords), 8, (255, 0, 0), -1)   # Blue center
    
    # Draw lines between relevant landmarks
    if len(relevant_landmarks) >= 2:
        for i in range(len(relevant_landmarks) - 1):
            start_coords = get_landmark_coords(landmarks.pose_landmarks, relevant_landmarks[i], width, height)
            end_coords = get_landmark_coords(landmarks.pose_landmarks, relevant_landmarks[i+1], width, height)
            cv2.line(frame, tuple(start_coords), tuple(end_coords), (0, 255, 255), 4)

def wrap_text(text, max_chars):
    """Wrap text to fit within specified character limit"""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line + " " + word) <= max_chars:
            current_line += " " + word if current_line else word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines

# --- Core Processing Logic (within the Pose Estimation & Analysis Service) ---

def process_video_for_analysis(job: VideoAnalysisJob, ideal_shot_data):
    """
    Main function to process a single video analysis job.
    This function would be triggered by a message from the processing queue.
    """
    logging.info(f"Starting analysis for job: {job.job_id} from {job.video_url}")

    local_video_path = f"temp_{job.job_id}_raw.mp4" # Use local temp for Windows compatibility
    download_video_from_storage(job.video_url, local_video_path) # Assumes successful download

    cap = cv2.VideoCapture(local_video_path)
    if not cap.isOpened():
        logging.error(f"Failed to open video file: {local_video_path}")
        job.status = "FAILED"
        # Update job status in DB
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    processed_frames_data = [] # List of FrameData objects
    current_frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the BGR image to RGB.
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose_model.process(image)
        image.flags.writeable = True

        frame_metrics = {}
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Calculate key angles and store them
            # Right arm (assuming right-handed shot for now)
            r_shoulder = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_SHOULDER, width, height)
            r_elbow = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_ELBOW, width, height)
            r_wrist = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_WRIST, width, height)
            r_hip = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_HIP, width, height)
            r_knee = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_KNEE, width, height)
            r_ankle = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_ANKLE, width, height)

            # Elbow angle
            elbow_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
            frame_metrics['elbow_angle'] = elbow_angle

            # Knee angle
            knee_angle = calculate_angle(r_hip, r_knee, r_ankle)
            frame_metrics['knee_angle'] = knee_angle

            # Wrist snap potential (simplified: angle between elbow, wrist, and a point representing ball direction)
            # This would need more sophisticated logic for actual wrist snap
            # For now, let's consider the general wrist angle:
            wrist_angle = calculate_angle(r_elbow, r_wrist, [r_wrist[0], r_wrist[1] - 50]) # Point straight up from wrist
            frame_metrics['wrist_angle_simplified'] = wrist_angle

            # Calculate velocities (requires previous frame data)
            if current_frame_idx > 0:
                prev_landmarks = processed_frames_data[-1].landmarks_raw.pose_landmarks.landmark
                # Example: Vertical velocity of wrist
                prev_r_wrist_y = get_landmark_coords(processed_frames_data[-1].landmarks_raw.pose_landmarks, mp_pose.PoseLandmark.RIGHT_WRIST, width, height)[1]
                wrist_vertical_velocity = (prev_r_wrist_y - r_wrist[1]) * fps # Pixels per second
                frame_metrics['wrist_vertical_velocity'] = wrist_vertical_velocity
                # More velocities (knee, hip, etc.) would be calculated here
            else:
                frame_metrics['wrist_vertical_velocity'] = 0

            # Store the data for this frame
            processed_frames_data.append(FrameData(current_frame_idx, results, frame_metrics))

        else:
            # Handle frames where pose is not detected (e.g., player out of frame)
            processed_frames_data.append(FrameData(current_frame_idx, None, {}))

        current_frame_idx += 1
        # In a real service, emit progress updates to the database or a separate status service

    cap.release()
    logging.info(f"Finished pose estimation for {total_frames} frames.")

    # --- Phase Identification ---
    # More sophisticated logic here would use thresholds on joint velocities and angles over time
    # This is a conceptual example based on the analysis of `processed_frames_data`
    shot_phases = []
    # Dummy logic: find the frame with max knee bend for 'Load', max wrist velocity for 'Release'
    max_knee_bend_frame = -1
    min_knee_angle = float('inf')
    max_wrist_vel_frame = -1
    max_wrist_vel = -float('inf')

    for i, frame_data in enumerate(processed_frames_data):
        if 'knee_angle' in frame_data.metrics and frame_data.metrics['knee_angle'] < min_knee_angle:
            min_knee_angle = frame_data.metrics['knee_angle']
            max_knee_bend_frame = i
        if 'wrist_vertical_velocity' in frame_data.metrics and frame_data.metrics['wrist_vertical_velocity'] > max_wrist_vel:
            max_wrist_vel = frame_data.metrics['wrist_vertical_velocity']
            max_wrist_vel_frame = i
            
    # Simple phase definitions based on identified key frames
    if max_knee_bend_frame != -1:
        shot_phases.append(ShotPhase('Load/Dip', max(0, max_knee_bend_frame - int(fps/2)), max_knee_bend_frame, max_knee_bend_frame))
    if max_wrist_vel_frame != -1:
         shot_phases.append(ShotPhase('Release', max_wrist_vel_frame, min(total_frames - 1, max_wrist_vel_frame + int(fps/2)), max_wrist_vel_frame))
    # You'd add more sophisticated logic for ascent, follow-through, etc.

    logging.info(f"Identified {len(shot_phases)} shot phases.")

    # --- Analysis & Comparison with Ideal Form ---
    feedback_points = []
    # Iterate through critical phases/frames and compare metrics
    for phase in shot_phases:
        if phase.name == 'Release' and phase.key_moment_frame is not None:
            release_frame_data = processed_frames_data[phase.key_moment_frame]
            if 'elbow_angle' in release_frame_data.metrics:
                user_elbow_angle = release_frame_data.metrics['elbow_angle']
                ideal_range = ideal_shot_data['release_elbow_angle']
                if not (ideal_range['min'] <= user_elbow_angle <= ideal_range['max']):
                    feedback_points.append(FeedbackPoint(
                        frame_number=phase.key_moment_frame,
                        discrepancy=f"Elbow extension at release ({user_elbow_angle:.1f}°) is outside the ideal range ({ideal_range['min']}-{ideal_range['max']}°).",
                        ideal_range=ideal_range,
                        user_value=user_elbow_angle,
                        remedy_tips=ideal_shot_data['common_remedies'].get('elbow_extension', 'Consult a coach for specific drills.'),
                        critical_landmarks=[mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST]
                    ))
            # Add more checks for wrist snap, balance, etc. at release
        if phase.name == 'Load/Dip' and phase.key_moment_frame is not None:
            load_frame_data = processed_frames_data[phase.key_moment_frame]
            if 'knee_angle' in load_frame_data.metrics:
                user_knee_angle = load_frame_data.metrics['knee_angle']
                ideal_range = ideal_shot_data['load_knee_angle']
                if not (ideal_range['min'] <= user_knee_angle <= ideal_range['max']):
                    feedback_points.append(FeedbackPoint(
                        frame_number=phase.key_moment_frame,
                        discrepancy=f"Knee bend during load ({user_knee_angle:.1f}°) is outside the ideal range ({ideal_range['min']}-{ideal_range['max']}°).",
                        ideal_range=ideal_range,
                        user_value=user_knee_angle,
                        remedy_tips=ideal_shot_data['common_remedies'].get('knee_drive', 'Focus on getting a deeper or shallower knee bend.'),
                        critical_landmarks=[mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE, mp_pose.PoseLandmark.RIGHT_ANKLE]
                    ))
    logging.info(f"Generated {len(feedback_points)} feedback points.")

    # --- Enhanced Flaw Detection and Analysis ---
    detailed_flaws = analyze_detailed_flaws(processed_frames_data, ideal_shot_data, shot_phases, fps)
    
    # --- Generate Visual Output (Slow-motion Video with Overlays & Stills) ---
    output_video_path = f"temp_{job.job_id}_analyzed.mp4"
    cap_reprocess = cv2.VideoCapture(local_video_path) # Re-open raw video for overlaying
    
    # Use H.264 codec for web compatibility
    fourcc = cv2.VideoWriter_fourcc(*'avc1') # H.264 codec (better web support than mp4v)
    
    # Slower FPS for slow-motion playback
    out = cv2.VideoWriter(output_video_path, fourcc, fps / 4, (width, height)) # SLOW_MOTION_FACTOR = 4

    frame_for_still_capture = {} # Dict to prevent capturing same frame multiple times
    flaw_stills_captured = [] # Track detailed flaw analysis stills

    current_frame_idx_output = 0
    while cap_reprocess.isOpened():
        ret, frame = cap_reprocess.read()
        if not ret:
            break

        # Get stored pose landmarks for current frame
        if current_frame_idx_output < len(processed_frames_data) and processed_frames_data[current_frame_idx_output].landmarks_raw:
            results_to_draw = processed_frames_data[current_frame_idx_output].landmarks_raw
            
            # Draw skeleton
            mp_drawing.draw_landmarks(frame, results_to_draw.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                     mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                                     mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2))

            # Overlay phase information
            for phase in shot_phases:
                if phase.start_frame <= current_frame_idx_output <= phase.end_frame:
                    cv2.putText(frame, f"Phase: {phase.name}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    break

            # Overlay feedback points and capture stills
            for feedback in feedback_points:
                # Check if this frame is close to a feedback point (considering slow-motion)
                # This logic is simplified; in production, you might want to show feedback for a few frames around the key moment.
                if current_frame_idx_output == feedback.frame_number: # For precise frame match
                    # Highlight critical landmarks for this discrepancy
                    if results_to_draw.pose_landmarks and feedback.critical_landmarks:
                        for i in range(len(feedback.critical_landmarks) - 1):
                            lm1_coords = get_landmark_coords(results_to_draw.pose_landmarks, feedback.critical_landmarks[i], width, height)
                            lm2_coords = get_landmark_coords(results_to_draw.pose_landmarks, feedback.critical_landmarks[i+1], width, height)
                            cv2.line(frame, tuple(lm1_coords), tuple(lm2_coords), (0, 0, 255), 3) # Red line for discrepancy

                    # Add text explanation
                    feedback_text_lines = [
                        feedback.discrepancy,
                        f"Tip: {feedback.remedy_tips}"
                    ]
                    y_offset = height - 120
                    for line in feedback_text_lines:
                        cv2.putText(frame, line, (50, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
                        y_offset += 25

                    # Capture still frame
                    if feedback.frame_number not in frame_for_still_capture:
                        still_frame_name = f"temp_{job.job_id}_still_feedback_{feedback.frame_number}.png"
                        cv2.imwrite(still_frame_name, frame)
                        frame_for_still_capture[feedback.frame_number] = still_frame_name
                        logging.info(f"Captured still frame: {still_frame_name}")
            
            # Process detailed flaw analysis stills
            for flaw in detailed_flaws:
                if current_frame_idx_output == flaw['frame_number']:
                    # Create detailed flaw overlay
                    flaw_overlay_frame = create_flaw_overlay(frame.copy(), flaw, results_to_draw, width, height)
                    
                    # Save the detailed flaw analysis still
                    flaw_still_name = f"temp_{job.job_id}_flaw_{flaw['flaw_type']}_frame_{flaw['frame_number']}.png"
                    cv2.imwrite(flaw_still_name, flaw_overlay_frame)
                    flaw_stills_captured.append({
                        'file_path': flaw_still_name,
                        'flaw_data': flaw,
                        'frame_number': flaw['frame_number']
                    })
                    logging.info(f"Captured detailed flaw analysis: {flaw_still_name}")
                    
                    # Also add flaw indicator to main video
                    cv2.putText(frame, f"FLAW: {flaw['flaw_type'].replace('_', ' ').upper()}", 
                               (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        out.write(frame)
        current_frame_idx_output += 1

    cap_reprocess.release()
    out.release()
    logging.info(f"Generated output video: {output_video_path}")

    # Convert to web-compatible format using FFmpeg if needed
    web_compatible_path = f"temp_{job.job_id}_web_analyzed.mp4"
    try:
        import subprocess
        # Convert to H.264 with web-compatible settings
        ffmpeg_cmd = [
            'ffmpeg', '-y',  # -y overwrites output file
            '-i', output_video_path,
            '-c:v', 'libx264',  # H.264 video codec
            '-profile:v', 'baseline',  # Baseline profile for maximum compatibility
            '-level', '3.0',  # Compatibility level
            '-pix_fmt', 'yuv420p',  # Pixel format for web compatibility
            '-movflags', '+faststart',  # Move metadata to beginning for fast web streaming
            '-preset', 'medium',  # Encoding preset
            '-crf', '23',  # Quality setting (lower = better quality)
            web_compatible_path
        ]
        
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists(web_compatible_path):
            # Replace original with web-compatible version
            os.remove(output_video_path)
            os.rename(web_compatible_path, output_video_path)
            logging.info(f"Converted video to web-compatible format: {output_video_path}")
        else:
            logging.warning(f"FFmpeg conversion failed, using original format. Error: {result.stderr}")
            
    except Exception as e:
        logging.warning(f"Could not convert video to web format: {e}. Using original format.")
        # Continue with original video if FFmpeg fails

    # --- Store Results & Notify User ---
    # Upload the analyzed video and still frames to cloud storage
    final_video_url = upload_file_to_storage(output_video_path, f"analyzed_videos/{job.job_id}_analyzed.mp4")
    
    still_urls = {}
    for frame_num, still_path in frame_for_still_capture.items():
        still_urls[frame_num] = upload_file_to_storage(still_path, f"still_frames/{job.job_id}_still_{frame_num}.png")

    # Create the final analysis report object
    analysis_report = AnalysisReport(
        job_id=job.job_id,
        user_id=job.user_id,
        video_url=job.video_url,
        phases=shot_phases,
        feedback_points=feedback_points,
        overall_score=None # Placeholder for a future scoring system
    )
    
    # Generate comprehensive 60-day improvement plan PDF
    pdf_results = {
        'analysis_report': analysis_report,
        'output_video_path': output_video_path,
        'feedback_stills': frame_for_still_capture,
        'flaw_stills': flaw_stills_captured,
        'detailed_flaws': detailed_flaws,
        'shot_phases': shot_phases,
        'feedback_points': feedback_points
    }
    
    improvement_plan_pdf = None
    try:
        improvement_plan_pdf = generate_improvement_plan_pdf(pdf_results, job.job_id)
        if improvement_plan_pdf:
            logging.info(f"Generated 60-day improvement plan PDF: {improvement_plan_pdf}")
        else:
            logging.warning("Failed to generate improvement plan PDF")
    except Exception as e:
        logging.error(f"Error generating improvement plan PDF: {e}")
    
    # Return analysis results including flaw stills for web app integration
    return {
        'analysis_report': analysis_report,
        'output_video_path': output_video_path,
        'feedback_stills': frame_for_still_capture,
        'flaw_stills': flaw_stills_captured,
        'detailed_flaws': detailed_flaws,
        'shot_phases': shot_phases,
        'feedback_points': feedback_points,
        'improvement_plan_pdf': improvement_plan_pdf
    }

    # Print summary of analysis
    print(f"\n=== ANALYSIS COMPLETE FOR JOB {job.job_id} ===")
    print(f"Phases identified: {len(shot_phases)}")
    for phase in shot_phases:
        print(f"  - {phase.name}: frames {phase.start_frame}-{phase.end_frame}")
    print(f"Feedback points: {len(feedback_points)}")
    for feedback in feedback_points:
        print(f"  - Frame {feedback.frame_number}: {feedback.discrepancy}")
    print(f"Detailed flaw analysis: {len(detailed_flaws)} flaws detected")
    for flaw in detailed_flaws:
        print(f"  - {flaw['flaw_type']} (Frame {flaw['frame_number']}): {flaw['plain_language']}")
    print(f"Output video: {output_video_path}")
    print(f"Still frames captured: {len(frame_for_still_capture)}")
    print(f"Detailed flaw stills: {len(flaw_stills_captured)}")
    
    # Generate detailed flaw report
    if detailed_flaws:
        print(f"\n=== DETAILED FLAW ANALYSIS ===")
        for i, flaw in enumerate(detailed_flaws, 1):
            print(f"\n{i}. {flaw['flaw_type'].replace('_', ' ').title()}")
            print(f"   Phase: {flaw['phase']}")
            print(f"   Frame: {flaw['frame_number']}")
            print(f"   Severity: {flaw['severity']:.1f}")
            print(f"   Issue: {flaw['plain_language']}")
            print(f"   Coaching Tip: {flaw['coaching_tip']}")
            print(f"   Recommended Drill: {flaw['drill_suggestion']}")
            if i <= len(flaw_stills_captured):
                print(f"   Analysis Image: {flaw_stills_captured[i-1]['file_path']}")

    # Clean up local temporary files
    if os.path.exists(local_video_path):
        os.remove(local_video_path)
    
    logging.info(f"Analysis for job {job.job_id} completed successfully and results stored/notified.")

# --- Entry Point (Conceptual for a serverless function or containerized service) ---
def handler(event, context):
    """
    This function would be the entry point, e.g., for an AWS Lambda or Google Cloud Function.
    'event' would contain information from the message queue (e.g., SQS message, Pub/Sub message)
    """
    # Parse the event to get job details
    job_data = json.loads(event['body']) # Assuming JSON payload from a queue
    job = VideoAnalysisJob(
        job_id=job_data['job_id'],
        user_id=job_data['user_id'],
        video_url=job_data['video_url']
    )

    # Load ideal shot data (could be cached or loaded from a central config service)
    ideal_shot_data = load_ideal_shot_data('ideal_shot_guide.json') # Path in the deployment package

    try:
        process_video_for_analysis(job, ideal_shot_data)
        return {"statusCode": 200, "body": json.dumps({"message": "Processing started"})}
    except Exception as e:
        logging.error(f"Error processing job {job.job_id}: {e}")
        job.status = "FAILED"
        # Update job status in DB
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

# --- Local Testing/Demonstration ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Running local demonstration of shot analysis process...")

    # Create a dummy video file for testing if it doesn't exist
    test_video_path = 'user_shot.mp4'
    if not os.path.exists(test_video_path):
        print(f"Please place a test video file named '{test_video_path}' in this directory.")
        print("Creating a dummy file for demonstration purposes (you'll need a real video for full functionality).")
        # Create a blank video for testing the flow
        dummy_video_writer = cv2.VideoWriter(test_video_path, cv2.VideoWriter_fourcc(*'mp4v'), 20, (640, 480))
        for _ in range(50): # 50 frames, 2.5 seconds
            dummy_video_writer.write(np.zeros((480, 640, 3), dtype=np.uint8))
        dummy_video_writer.release()
        print(f"Dummy video '{test_video_path}' created.")

    # Simulate a job being triggered
    dummy_job_id = "test_shot_123"
    dummy_user_id = "user_abc"
    dummy_video_url = test_video_path # In production, this would be a cloud storage URL

    test_job = VideoAnalysisJob(job_id=dummy_job_id, user_id=dummy_user_id, video_url=dummy_video_url)

    # Simulate ideal shot data loading
    # You would need a 'ideal_shot_guide.json' file with your ideal ranges
    # For quick testing, the function has a dummy fallback
    ideal_data = load_ideal_shot_data('ideal_shot_guide.json')

    process_video_for_analysis(test_job, ideal_data)
    print("Local demonstration finished. Check current directory for output files.")
    print(f"For a full test, ensure '{test_video_path}' is a real basketball shot video.")
