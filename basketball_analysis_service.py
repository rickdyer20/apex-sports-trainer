# --- Configuration & Imports (Conceptual) ---
# These would be handled via environment variables, configuration files,
# and dependency injection in a real service.
import os
import cv2
import mediapipe as mp
import numpy as np
import json
import logging # For robust logging
import time
import subprocess
import shutil
from datetime import datetime
from pdf_generator import generate_improvement_plan_pdf

# Try to import psutil for resource monitoring
try:
    import psutil
except ImportError:
    psutil = None

# --- Service Initialization (on service startup) ---
mp_pose = mp.solutions.pose
pose_model = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Add a global flag to check if ffmpeg is available
FFMPEG_AVAILABLE = shutil.which('ffmpeg') is not None

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

def save_frames_for_ffmpeg(frames, job_id):
    """Saves frames to a temporary directory for ffmpeg processing."""
    frame_dir = f"temp_{job_id}_frames"
    os.makedirs(frame_dir, exist_ok=True)
    for i, frame in enumerate(frames):
        cv2.imwrite(os.path.join(frame_dir, f"frame_{i:04d}.png"), frame)
    return frame_dir

def create_video_from_frames_ffmpeg(frame_dir, output_path, fps):
    """Creates a video from frames using ffmpeg."""
    if not FFMPEG_AVAILABLE:
        logging.error("ffmpeg not found, cannot create video from frames.")
        return False
        
    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-framerate', str(fps),
        '-i', os.path.join(frame_dir, 'frame_%04d.png'),
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'ultrafast',
        output_path
    ]
    try:
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            logging.info(f"Successfully created video with ffmpeg: {output_path}")
            return True
        else:
            logging.error(f"ffmpeg failed to create video: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Exception during ffmpeg video creation: {e}")
        return False
    finally:
        # Clean up frames
        try:
            shutil.rmtree(frame_dir)
        except Exception as e:
            logging.warning(f"Failed to remove temp frame directory: {e}")

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

def fix_video_orientation(video_path):
    """Fix video orientation based on metadata rotation info"""
    try:
        import subprocess
        
        # Get video rotation metadata
        probe_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', video_path]
        result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            import json
            probe_data = json.loads(result.stdout)
            
            # Check for rotation metadata
            rotation = 0
            for stream in probe_data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    # Check for rotation in side_data
                    side_data = stream.get('side_data_list', [])
                    for data in side_data:
                        if data.get('side_data_type') == 'Display Matrix':
                            rotation_str = data.get('rotation', '0')
                            try:
                                rotation = int(float(rotation_str))
                            except (ValueError, TypeError):
                                rotation = 0
                    
                    # Also check tags for rotation
                    tags = stream.get('tags', {})
                    if 'rotate' in tags:
                        try:
                            rotation = int(tags['rotate'])
                        except (ValueError, TypeError):
                            rotation = 0
                    break
            
            # If rotation detected, fix it
            if rotation != 0 and rotation % 90 == 0:
                corrected_path = video_path.replace('.mp4', '_corrected.mp4')
                
                # Determine transpose filter based on rotation
                if rotation == 90:
                    transpose_filter = 'transpose=1'  # 90° clockwise
                elif rotation == 180:
                    transpose_filter = 'transpose=2,transpose=2'  # 180°
                elif rotation == 270:
                    transpose_filter = 'transpose=2'  # 90° counter-clockwise
                else:
                    transpose_filter = None
                
                if transpose_filter:
                    fix_cmd = [
                        'ffmpeg', '-y',
                        '-i', video_path,
                        '-vf', transpose_filter,
                        '-c:a', 'copy',  # Copy audio without re-encoding
                        '-metadata:s:v:0', 'rotate=0',  # Remove rotation metadata
                        corrected_path
                    ]
                    
                    fix_result = subprocess.run(fix_cmd, capture_output=True, text=True, timeout=120)
                    
                    if fix_result.returncode == 0 and os.path.exists(corrected_path):
                        # Replace original with corrected version
                        os.remove(video_path)
                        os.rename(corrected_path, video_path)
                        logging.info(f"Fixed video orientation (rotated {rotation}°): {video_path}")
                        return True
                    else:
                        logging.warning(f"Failed to fix video orientation: {fix_result.stderr}")
                        
    except Exception as e:
        logging.warning(f"Could not check/fix video orientation: {e}")
    
    return False

def process_video_for_analysis(job: VideoAnalysisJob, ideal_shot_data):
    """
    Main function to process a single video analysis job.
    Optimized for cloud deployment with error handling and resource management.
    """
    logging.info(f"Starting analysis for job: {job.job_id} from {job.video_url}")
    
    # Add memory and resource monitoring
    try:
        if psutil:
            memory_info = psutil.virtual_memory()
            logging.info(f"Available memory: {memory_info.available / (1024**3):.2f} GB")
            disk_info = psutil.disk_usage('.')
            logging.info(f"Disk space: {disk_info.free / (1024**3):.2f} GB free")
        else:
            logging.info("psutil not available, skipping resource monitoring")
    except Exception as e:
        logging.warning(f"Resource monitoring failed: {e}")

    local_video_path = f"temp_{job.job_id}_raw.mp4"
    
    try:
        download_video_from_storage(job.video_url, local_video_path)
        if os.path.exists(local_video_path):
            file_size = os.path.getsize(local_video_path) / (1024**2)
            logging.info(f"Downloaded video: {local_video_path}, size: {file_size:.2f} MB")
        else:
            logging.error(f"Video file not found after download: {local_video_path}")
            return {
                'error': 'Failed to download or locate video file'
            }
    except Exception as e:
        logging.error(f"Failed to download video: {e}")
        return {
            'error': f'Failed to download video: {str(e)}'
        }
    
    # Fix video orientation if needed
    try:
        fix_video_orientation(local_video_path)
        logging.info(f"Video orientation check completed")
    except Exception as e:
        logging.warning(f"Video orientation fix failed: {e}")

    # Initialize video capture with error handling
    cap = None
    try:
        cap = cv2.VideoCapture(local_video_path)
        if not cap.isOpened():
            logging.error(f"Failed to open video file: {local_video_path}")
            return {
                'error': 'Failed to open video file - file may be corrupted or in unsupported format'
            }

        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logging.info(f"Video properties - FPS: {fps}, Size: {width}x{height}, Frames: {total_frames}")
        
        # Validate video properties
        if fps <= 0 or width <= 0 or height <= 0 or total_frames <= 0:
            logging.error(f"Invalid video properties: FPS={fps}, Size={width}x{height}, Frames={total_frames}")
            cap.release()
            return {
                'error': 'Invalid video format or corrupted video file'
            }
        
        # Limit processing for deployment efficiency
        max_frames = min(total_frames, 300)  # Process max 300 frames (10-15 seconds at 30fps)
        if total_frames > max_frames:
            logging.info(f"Limiting processing to {max_frames} frames (original: {total_frames}) for deployment efficiency")

    except Exception as e:
        logging.error(f"Error initializing video processing: {e}")
        if cap:
            cap.release()
        return {
            'error': f'Error initializing video processing: {str(e)}'
        }

    processed_frames_data = []
    current_frame_idx = 0
    frames_processed = 0
    frames_with_pose = 0
    
    # Process frames with timeout protection
    import time
    start_time = time.time()
    max_processing_time = 120  # 2 minutes max processing time

    try:
        while cap.isOpened() and current_frame_idx < max_frames:
            # Check for timeout
            if time.time() - start_time > max_processing_time:
                logging.warning(f"Processing timeout reached after {max_processing_time} seconds")
                break
                
            ret, frame = cap.read()
            if not ret:
                break

            try:
                # Log progress every 25 frames for deployment monitoring
                if current_frame_idx % 25 == 0:
                    elapsed = time.time() - start_time
                    logging.info(f"Processing frame {current_frame_idx}/{max_frames} ({elapsed:.1f}s elapsed)")
                    
                # Convert the BGR image to RGB
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                
                # Process with MediaPipe
                results = pose_model.process(image)
                image.flags.writeable = True

                frame_metrics = {}
                if results and results.pose_landmarks:
                    frames_with_pose += 1
                    landmarks = results.pose_landmarks.landmark

                    # Calculate key angles and store them
                    try:
                        r_shoulder = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_SHOULDER, width, height)
                        r_elbow = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_ELBOW, width, height)
                        r_wrist = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_WRIST, width, height)
                        r_hip = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_HIP, width, height)
                        r_knee = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_KNEE, width, height)
                        r_ankle = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_ANKLE, width, height)

                        # Calculate angles with error handling
                        elbow_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
                        knee_angle = calculate_angle(r_hip, r_knee, r_ankle)
                        wrist_angle = calculate_angle(r_elbow, r_wrist, [r_wrist[0], r_wrist[1] - 50])
                        
                        frame_metrics['elbow_angle'] = elbow_angle
                        frame_metrics['knee_angle'] = knee_angle
                        frame_metrics['wrist_angle_simplified'] = wrist_angle

                        # Calculate velocities with bounds checking
                        if current_frame_idx > 0 and len(processed_frames_data) > 0:
                            prev_frame = processed_frames_data[-1]
                            if prev_frame.landmarks_raw and prev_frame.landmarks_raw.pose_landmarks:
                                prev_r_wrist_y = get_landmark_coords(prev_frame.landmarks_raw.pose_landmarks, mp_pose.PoseLandmark.RIGHT_WRIST, width, height)[1]
                                wrist_vertical_velocity = (prev_r_wrist_y - r_wrist[1]) * fps
                                frame_metrics['wrist_vertical_velocity'] = wrist_vertical_velocity
                            else:
                                frame_metrics['wrist_vertical_velocity'] = 0
                        else:
                            frame_metrics['wrist_vertical_velocity'] = 0

                        processed_frames_data.append(FrameData(current_frame_idx, results, frame_metrics))
                        
                    except Exception as e:
                        logging.warning(f"Error calculating metrics for frame {current_frame_idx}: {e}")
                        processed_frames_data.append(FrameData(current_frame_idx, results, {}))
                else:
                    # Handle frames where pose is not detected
                    processed_frames_data.append(FrameData(current_frame_idx, None, {}))
                    
            except Exception as e:
                logging.error(f"Error processing frame {current_frame_idx}: {e}")
                processed_frames_data.append(FrameData(current_frame_idx, None, {}))

            current_frame_idx += 1
            frames_processed += 1

    except Exception as e:
        logging.error(f"Critical error during frame processing: {e}")
        return {
            'error': f'Critical error during video processing: {str(e)}'
        }
    finally:
        if cap:
            cap.release()

    processing_time = time.time() - start_time
    logging.info(f"Finished pose estimation for {frames_processed} frames in {processing_time:.1f}s. Poses detected in {frames_with_pose} frames.")
    
    # Check if we have sufficient pose data
    if frames_with_pose < 5:
        logging.warning(f"Very few poses detected ({frames_with_pose}). Analysis may be limited.")
        return {
            'error': f'Insufficient pose detection ({frames_with_pose} frames). Please ensure the player is clearly visible in good lighting and the camera is steady.'
        }

    # Continue with analysis only if we have good data
    try:
        # Phase identification (simplified for deployment)
        shot_phases = []
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

        # Create phases
        if max_knee_bend_frame != -1:
            shot_phases.append(ShotPhase('Load/Dip', max(0, max_knee_bend_frame - 15), max_knee_bend_frame, max_knee_bend_frame))
        if max_wrist_vel_frame != -1:
            shot_phases.append(ShotPhase('Release', max_wrist_vel_frame, min(frames_processed - 1, max_wrist_vel_frame + 15), max_wrist_vel_frame))

        logging.info(f"Identified {len(shot_phases)} shot phases.")

        # Generate feedback points
        feedback_points = []
        for phase in shot_phases:
            if phase.name == 'Release' and phase.key_moment_frame is not None:
                if phase.key_moment_frame < len(processed_frames_data):
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
                                remedy_tips=ideal_shot_data['common_remedies'].get('elbow_extension', 'Focus on full elbow extension.'),
                                critical_landmarks=[mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST]
                            ))

        logging.info(f"Generated {len(feedback_points)} feedback points.")

        # Simplified flaw detection for deployment
        detailed_flaws = analyze_detailed_flaws(processed_frames_data, ideal_shot_data, shot_phases, fps)

    except Exception as e:
        logging.error(f"Error during analysis phase: {e}")
        return {
            'error': f'Error during shot analysis: {str(e)}'
        }

    # --- Video Generation (Robust Pipeline) ---
    output_video_path = f"temp_{job.job_id}_analyzed.mp4"
    video_generated = False
    
    try:
        logging.info(f"Starting robust video generation pipeline: {output_video_path}")
        
        # Re-open video to get raw frames for processing
        cap_reprocess = cv2.VideoCapture(local_video_path)
        if not cap_reprocess.isOpened():
            raise IOError("Failed to reopen video for processing")

        # --- Stage 1: Attempt to write video with cv2.VideoWriter ---
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc, max(fps / 4, 5), (width, height))
        
        if not out.isOpened():
            logging.warning("cv2.VideoWriter failed to open with 'mp4v'. Will fallback to ffmpeg.")
            out.release()
            out = None
        
        frame_buffer = [] # To hold frames for ffmpeg fallback
        frame_for_still_capture = {}
        flaw_stills_captured = []
        current_frame_idx_output = 0

        while cap_reprocess.isOpened() and current_frame_idx_output < len(processed_frames_data):
            ret, frame = cap_reprocess.read()
            if not ret:
                break

            # --- Apply overlays to the frame ---
            try:
                if current_frame_idx_output < len(processed_frames_data) and processed_frames_data[current_frame_idx_output].landmarks_raw:
                    results_to_draw = processed_frames_data[current_frame_idx_output].landmarks_raw
                    mp_drawing.draw_landmarks(frame, results_to_draw.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                             mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                                             mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2))
                    
                    # Add phase overlay
                    for phase in shot_phases:
                        if phase.start_frame <= current_frame_idx_output <= phase.end_frame:
                            cv2.putText(frame, f"Phase: {phase.name}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                            break
                    
                    # Capture flaw stills
                    for flaw in detailed_flaws[:3]:
                        if current_frame_idx_output == flaw['frame_number']:
                            flaw_overlay_frame = create_flaw_overlay(frame.copy(), flaw, results_to_draw, width, height)
                            flaw_still_name = f"temp_{job.job_id}_flaw_{flaw['flaw_type']}_frame_{flaw['frame_number']}.png"
                            cv2.imwrite(flaw_still_name, flaw_overlay_frame)
                            flaw_stills_captured.append({
                                'file_path': flaw_still_name,
                                'flaw_data': flaw,
                                'frame_number': flaw['frame_number']
                            })
            except Exception as e:
                logging.warning(f"Error applying overlay to frame {current_frame_idx_output}: {e}")

            # --- Write frame or buffer it ---
            if out:
                out.write(frame)
            else:
                frame_buffer.append(frame)
            
            current_frame_idx_output += 1

        cap_reprocess.release()
        if out:
            out.release()
            video_generated = True
            logging.info(f"Successfully generated video with cv2.VideoWriter.")

        # --- Stage 2: Fallback to ffmpeg if cv2.VideoWriter failed ---
        if not video_generated and FFMPEG_AVAILABLE:
            logging.info("cv2.VideoWriter failed. Attempting to build video with ffmpeg.")
            frame_dir = save_frames_for_ffmpeg(frame_buffer, job.job_id)
            if create_video_from_frames_ffmpeg(frame_dir, output_video_path, max(fps / 4, 5)):
                video_generated = True
            else:
                logging.error("ffmpeg fallback also failed. No video will be available.")
        
    except Exception as e:
        logging.error(f"Critical error in video generation pipeline: {e}")
        video_generated = False

    # Clean up input video early to save space
    try:
        if os.path.exists(local_video_path):
            os.remove(local_video_path)
            logging.info(f"Cleaned up input video: {local_video_path}")
    except Exception as e:
        logging.warning(f"Failed to cleanup input video: {e}")

    # --- Stage 3: Convert to web-compatible format if a video was generated ---
    if video_generated:
        try:
            web_compatible_path = f"temp_{job.job_id}_web_analyzed.mp4"
            logging.info(f"Converting to web format: {output_video_path} -> {web_compatible_path}")
            
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-i', output_video_path,
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-profile:v', 'baseline',
                '-level', '3.0',
                '-pix_fmt', 'yuv420p',
                '-crf', '28',
                '-movflags', '+faststart',
                web_compatible_path
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=90)
            
            if result.returncode == 0 and os.path.exists(web_compatible_path):
                try:
                    os.remove(output_video_path)
                except:
                    pass
                os.rename(web_compatible_path, output_video_path)
                logging.info(f"Successfully converted to web format")
            else:
                logging.warning(f"FFmpeg web conversion failed: {result.stderr}. Using original video.")
                
        except Exception as e:
            logging.warning(f"Web format conversion failed: {e}. Using original video.")
    else:
        logging.warning("Skipping web conversion because no video was generated.")
        output_video_path = None # Ensure no broken video path is returned

    # Generate PDF with error handling
    improvement_plan_pdf = None
    try:
        pdf_results = {
            'analysis_report': None,
            'output_video_path': output_video_path,
            'feedback_stills': frame_for_still_capture,
            'flaw_stills': flaw_stills_captured,
            'detailed_flaws': detailed_flaws,
            'shot_phases': shot_phases,
            'feedback_points': feedback_points
        }
        improvement_plan_pdf = generate_improvement_plan_pdf(pdf_results, job.job_id)
        if improvement_plan_pdf:
            logging.info(f"Generated PDF: {improvement_plan_pdf}")
    except Exception as e:
        logging.warning(f"PDF generation failed: {e}")

    # Move final video to results folder with correct naming
    if output_video_path and os.path.exists(output_video_path):
        try:
            os.makedirs('results', exist_ok=True)
            final_video_path = os.path.join('results', f"{job.job_id}_analyzed.mp4")
            shutil.move(output_video_path, final_video_path)
            output_video_path = final_video_path
            logging.info(f"Moved final video to: {final_video_path}")
        except Exception as e:
            logging.error(f"Failed to move video to results folder: {e}")
    else:
        logging.info("No final video to move.")
        output_video_path = None

    logging.info(f"Analysis completed for job {job.job_id}")
    
    # Return comprehensive results
    return {
        'analysis_report': None,  # Simplified for deployment
        'output_video_path': output_video_path,
        'feedback_stills': frame_for_still_capture,
        'flaw_stills': flaw_stills_captured,
        'detailed_flaws': detailed_flaws,
        'shot_phases': shot_phases,
        'feedback_points': feedback_points,
        'improvement_plan_pdf': improvement_plan_pdf
    }
