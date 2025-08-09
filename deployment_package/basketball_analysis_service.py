# --- Configuration & Imports ---
import os
# Performance optimizations for TensorFlow
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import cv2
import mediapipe as mp
import numpy as np
import json
import logging
import time
import subprocess
import shutil
import gc
from datetime import datetime

# 🎯 FEATURE FLAGS FOR EASY REVERSIBILITY
# Set these to False to disable new features if issues arise
ENABLE_SHOULDER_ALIGNMENT_DETECTION = True  # New shoulder squaring detection

# Optional imports with graceful fallbacks
try:
    import psutil
except ImportError:
    psutil = None

try:
    from pdf_generator import generate_improvement_plan_pdf
except ImportError:
    def generate_improvement_plan_pdf(*args, **kwargs):
        logging.warning("PDF generator not available")
        return None

# --- Service Initialization (on service startup) ---
mp_pose = mp.solutions.pose

# PRODUCTION FIX: Lazy initialization to avoid Docker startup permission issues
pose_model = None

def get_pose_model():
    """Lazy initialization of MediaPipe pose model to avoid Docker startup issues"""
    global pose_model
    if pose_model is None:
        pose_model = mp_pose.Pose(
            static_image_mode=False, 
            model_complexity=0,  # Use faster, less accurate model
            min_detection_confidence=0.5, 
            min_tracking_confidence=0.5,
            enable_segmentation=False  # Disable segmentation for better performance
        )
    return pose_model

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
    """Creates a video from frames using ffmpeg with better codec options."""
    if not FFMPEG_AVAILABLE:
        logging.error("ffmpeg not found, cannot create video from frames.")
        return False
        
    # Try multiple ffmpeg encoding options for better compatibility
    ffmpeg_options = [
        # Option 1: H.264 with high compatibility
        [
            'ffmpeg', '-y',
            '-framerate', str(fps),
            '-i', os.path.join(frame_dir, 'frame_%04d.png'),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-profile:v', 'baseline',  # Better compatibility
            '-level', '3.0',
            '-preset', 'ultrafast',
            output_path
        ],
        # Option 2: Standard H.264 encoding
        [
            'ffmpeg', '-y',
            '-framerate', str(fps),
            '-i', os.path.join(frame_dir, 'frame_%04d.png'),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'ultrafast',
            output_path
        ],
        # Option 3: MPEG-4 fallback
        [
            'ffmpeg', '-y',
            '-framerate', str(fps),
            '-i', os.path.join(frame_dir, 'frame_%04d.png'),
            '-c:v', 'mpeg4',
            '-pix_fmt', 'yuv420p',
            '-preset', 'ultrafast',
            output_path
        ]
    ]
    
    for i, ffmpeg_cmd in enumerate(ffmpeg_options):
        try:
            logging.info(f"Attempting ffmpeg encoding option {i+1}")
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                logging.info(f"Successfully created video with ffmpeg option {i+1}: {output_path}")
                return True
            else:
                logging.warning(f"ffmpeg option {i+1} failed: {result.stderr}")
        except Exception as e:
            logging.warning(f"ffmpeg option {i+1} exception: {e}")
            continue
    
    logging.error("All ffmpeg encoding options failed")
    return False

def download_video_from_storage(video_url, local_path):
    """Simulates downloading video from S3/GCS."""
    logging.info(f"Downloading video from {video_url} to {local_path}")
    # In a real system: use AWS S3 client, Google Cloud Storage client etc.
    # For this pseudo-code, simulate by copying if source exists
    if os.path.exists(video_url) and video_url != local_path:
        # Copy the file to simulate download
        shutil.copy2(video_url, local_path)
        print(f"Copied {video_url} to {local_path}")
    elif not os.path.exists(local_path):
        # Dummy file creation for demonstration
        print(f"Creating a dummy video file at {local_path} as placeholder.")
        # This would be a proper download in production
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

def analyze_advanced_shot_fluidity(processed_frames_data, fps):
    """
    Advanced analysis of shot fluidity and flow patterns
    Detects jerky movements, rhythm inconsistencies, and pace variations
    """
    logging.info("Starting advanced shot fluidity analysis")
    
    fluidity_metrics = {
        'overall_fluidity_score': 100.0,  # Start with perfect score
        'jerky_segments': [],
        'rhythm_inconsistencies': [],
        'pace_variations': [],
        'acceleration_anomalies': [],
        'motion_flow_analysis': {}
    }
    
    if len(processed_frames_data) < 10:  # Need minimum frames for analysis
        return fluidity_metrics
    
    # Extract key joint positions over time
    joint_positions = {
        'wrist': [],
        'elbow': [],
        'shoulder': [],
        'knee': []
    }
    
    frame_indices = []
    
    for frame_data in processed_frames_data:
        if frame_data.landmarks_raw and frame_data.landmarks_raw.pose_landmarks:
            landmarks = frame_data.landmarks_raw.pose_landmarks.landmark
            
            # Extract joint positions
            try:
                r_wrist = get_landmark_coords(frame_data.landmarks_raw.pose_landmarks, mp_pose.PoseLandmark.RIGHT_WRIST, 640, 480)
                r_elbow = get_landmark_coords(frame_data.landmarks_raw.pose_landmarks, mp_pose.PoseLandmark.RIGHT_ELBOW, 640, 480)
                r_shoulder = get_landmark_coords(frame_data.landmarks_raw.pose_landmarks, mp_pose.PoseLandmark.RIGHT_SHOULDER, 640, 480)
                r_knee = get_landmark_coords(frame_data.landmarks_raw.pose_landmarks, mp_pose.PoseLandmark.RIGHT_KNEE, 640, 480)
                
                joint_positions['wrist'].append(r_wrist)
                joint_positions['elbow'].append(r_elbow)
                joint_positions['shoulder'].append(r_shoulder)
                joint_positions['knee'].append(r_knee)
                frame_indices.append(frame_data.frame_number)
            except:
                # Fill with None for missing data
                for joint in joint_positions:
                    joint_positions[joint].append(None)
                frame_indices.append(frame_data.frame_number)
    
    # 1. VELOCITY ANALYSIS - Detect abrupt speed changes
    fluidity_metrics['motion_flow_analysis']['velocity_analysis'] = analyze_velocity_patterns(
        joint_positions, frame_indices, fps
    )
    
    # 2. ACCELERATION ANALYSIS - Detect jerky movements  
    fluidity_metrics['motion_flow_analysis']['acceleration_analysis'] = analyze_acceleration_patterns(
        joint_positions, frame_indices, fps
    )
    
    # 3. RHYTHM ANALYSIS - Detect timing inconsistencies
    fluidity_metrics['motion_flow_analysis']['rhythm_analysis'] = analyze_shot_rhythm(
        joint_positions, frame_indices, fps
    )
    
    # 4. SMOOTHNESS ANALYSIS - Overall motion quality
    fluidity_metrics['motion_flow_analysis']['smoothness_analysis'] = analyze_motion_smoothness_advanced(
        joint_positions, frame_indices, fps
    )
    
    # Calculate overall fluidity score based on all analyses
    fluidity_metrics['overall_fluidity_score'] = calculate_overall_fluidity_score(
        fluidity_metrics['motion_flow_analysis']
    )
    
    logging.info(f"Advanced fluidity analysis complete. Overall score: {fluidity_metrics['overall_fluidity_score']:.1f}")
    
    return fluidity_metrics


def analyze_velocity_patterns(joint_positions, frame_indices, fps):
    """Analyze velocity patterns to detect abrupt speed changes"""
    velocity_analysis = {
        'wrist_velocity_variance': 0,
        'elbow_velocity_variance': 0,
        'abrupt_speed_changes': [],
        'velocity_smoothness_score': 100.0
    }
    
    for joint_name, positions in joint_positions.items():
        if len(positions) < 3:
            continue
            
        velocities = []
        valid_positions = []
        
        # Calculate velocities between consecutive frames
        for i in range(1, len(positions)):
            if positions[i] is not None and positions[i-1] is not None:
                pos_current = np.array(positions[i])
                pos_previous = np.array(positions[i-1])
                
                # Calculate 2D velocity magnitude
                velocity = np.linalg.norm(pos_current - pos_previous) * fps
                velocities.append(velocity)
                valid_positions.append(i)
        
        if len(velocities) < 5:
            continue
            
        # Detect abrupt velocity changes (jerky movements)
        velocity_changes = []
        for i in range(1, len(velocities)):
            velocity_change = abs(velocities[i] - velocities[i-1])
            velocity_changes.append(velocity_change)
            
            # Flag significant velocity changes
            if velocity_change > np.mean(velocities) * 1.5:  # 150% above average
                velocity_analysis['abrupt_speed_changes'].append({
                    'joint': joint_name,
                    'frame': frame_indices[valid_positions[i]] if valid_positions[i] < len(frame_indices) else valid_positions[i],
                    'velocity_change': velocity_change,
                    'severity': min(velocity_change / (np.mean(velocities) + 0.1) * 20, 100)
                })
        
        # Calculate velocity variance for this joint
        if len(velocity_changes) > 0:
            variance = np.var(velocity_changes)
            velocity_analysis[f'{joint_name}_velocity_variance'] = variance
            
            # Penalize high variance (indicates jerky movement)
            if variance > 50:  # Threshold for concerning variance
                velocity_analysis['velocity_smoothness_score'] -= min(variance / 2, 30)
    
    return velocity_analysis


def analyze_acceleration_patterns(joint_positions, frame_indices, fps):
    """Analyze acceleration patterns to detect jerky movements"""
    acceleration_analysis = {
        'acceleration_spikes': [],
        'deceleration_spikes': [],
        'acceleration_smoothness_score': 100.0,
        'max_acceleration': 0
    }
    
    for joint_name, positions in joint_positions.items():
        if len(positions) < 4:
            continue
            
        accelerations = []
        valid_positions = []
        
        # Calculate accelerations (second derivative of position)
        for i in range(2, len(positions)):
            if (positions[i] is not None and positions[i-1] is not None and positions[i-2] is not None):
                pos_current = np.array(positions[i])
                pos_previous = np.array(positions[i-1])
                pos_previous2 = np.array(positions[i-2])
                
                # Calculate acceleration using finite differences
                velocity_current = (pos_current - pos_previous) * fps
                velocity_previous = (pos_previous - pos_previous2) * fps
                acceleration = np.linalg.norm(velocity_current - velocity_previous) * fps
                
                accelerations.append(acceleration)
                valid_positions.append(i)
        
        if len(accelerations) < 3:
            continue
            
        # Detect acceleration spikes (jerky movements)
        mean_acceleration = np.mean(accelerations)
        std_acceleration = np.std(accelerations)
        acceleration_threshold = mean_acceleration + 2 * std_acceleration
        
        for i, acceleration in enumerate(accelerations):
            if acceleration > acceleration_threshold and acceleration > 10:  # Minimum threshold
                frame_idx = frame_indices[valid_positions[i]] if valid_positions[i] < len(frame_indices) else valid_positions[i]
                
                acceleration_analysis['acceleration_spikes'].append({
                    'joint': joint_name,
                    'frame': frame_idx,
                    'acceleration': acceleration,
                    'severity': min((acceleration / (mean_acceleration + 1)) * 15, 100)
                })
                
                # Update max acceleration
                acceleration_analysis['max_acceleration'] = max(
                    acceleration_analysis['max_acceleration'], acceleration
                )
        
        # Penalize excessive acceleration spikes
        if len(acceleration_analysis['acceleration_spikes']) > 2:
            penalty = len(acceleration_analysis['acceleration_spikes']) * 8
            acceleration_analysis['acceleration_smoothness_score'] -= min(penalty, 40)
    
    return acceleration_analysis


def analyze_shot_rhythm(joint_positions, frame_indices, fps):
    """Analyze shot rhythm and timing consistency"""
    rhythm_analysis = {
        'rhythm_consistency_score': 100.0,
        'timing_variations': [],
        'phase_duration_analysis': {},
        'rhythm_breaks': []
    }
    
    wrist_positions = joint_positions.get('wrist', [])
    if len(wrist_positions) < 10:
        return rhythm_analysis
    
    # Analyze vertical wrist movement to detect rhythm
    wrist_y_positions = []
    valid_frames = []
    
    for i, pos in enumerate(wrist_positions):
        if pos is not None:
            wrist_y_positions.append(pos[1])
            valid_frames.append(frame_indices[i] if i < len(frame_indices) else i)
    
    if len(wrist_y_positions) < 8:
        return rhythm_analysis
    
    # Detect movement phases based on vertical velocity
    velocities = []
    for i in range(1, len(wrist_y_positions)):
        velocity = (wrist_y_positions[i] - wrist_y_positions[i-1]) * fps
        velocities.append(velocity)
    
    # Find rhythm breaks (sudden stops or starts)
    velocity_threshold = np.std(velocities) * 1.5
    
    for i in range(1, len(velocities)):
        velocity_change = abs(velocities[i] - velocities[i-1])
        
        if velocity_change > velocity_threshold and velocity_change > 20:
            rhythm_analysis['rhythm_breaks'].append({
                'frame': valid_frames[i] if i < len(valid_frames) else i,
                'velocity_change': velocity_change,
                'severity': min(velocity_change / 5, 100),
                'type': 'sudden_stop' if velocities[i] < velocities[i-1] else 'sudden_acceleration'
            })
    
    # Calculate rhythm consistency score
    if len(rhythm_analysis['rhythm_breaks']) > 0:
        penalty = len(rhythm_analysis['rhythm_breaks']) * 12
        rhythm_analysis['rhythm_consistency_score'] -= min(penalty, 50)
    
    return rhythm_analysis


def analyze_motion_smoothness_advanced(joint_positions, frame_indices, fps):
    """Advanced motion smoothness analysis using multiple metrics"""
    smoothness_analysis = {
        'overall_smoothness_score': 100.0,
        'jerk_analysis': {},  # Third derivative analysis
        'trajectory_smoothness': {},
        'coordination_analysis': {}
    }
    
    # Analyze jerk (third derivative) for each joint
    for joint_name, positions in joint_positions.items():
        if len(positions) < 5:
            continue
            
        jerks = []
        valid_positions = []
        
        # Calculate jerk using finite differences
        for i in range(3, len(positions)):
            if all(pos is not None for pos in positions[i-3:i+1]):
                pos_sequence = [np.array(pos) for pos in positions[i-3:i+1]]
                
                # Calculate jerk (rate of change of acceleration)
                vel1 = (pos_sequence[1] - pos_sequence[0]) * fps
                vel2 = (pos_sequence[2] - pos_sequence[1]) * fps
                vel3 = (pos_sequence[3] - pos_sequence[2]) * fps
                
                acc1 = (vel2 - vel1) * fps
                acc2 = (vel3 - vel2) * fps
                
                jerk = np.linalg.norm(acc2 - acc1) * fps
                jerks.append(jerk)
                valid_positions.append(i)
        
        if len(jerks) > 0:
            mean_jerk = np.mean(jerks)
            std_jerk = np.std(jerks)
            
            smoothness_analysis['jerk_analysis'][joint_name] = {
                'mean_jerk': mean_jerk,
                'jerk_variance': np.var(jerks),
                'smoothness_score': max(0, 100 - mean_jerk * 2)  # Higher jerk = lower score
            }
            
            # Penalize high jerk values
            if mean_jerk > 15:
                smoothness_analysis['overall_smoothness_score'] -= min(mean_jerk, 25)
    
    return smoothness_analysis


def calculate_overall_fluidity_score(motion_flow_analysis):
    """Calculate overall fluidity score from all analyses"""
    base_score = 100.0
    
    # Velocity analysis impact
    velocity_score = motion_flow_analysis.get('velocity_analysis', {}).get('velocity_smoothness_score', 100)
    
    # Acceleration analysis impact  
    acceleration_score = motion_flow_analysis.get('acceleration_analysis', {}).get('acceleration_smoothness_score', 100)
    
    # Rhythm analysis impact
    rhythm_score = motion_flow_analysis.get('rhythm_analysis', {}).get('rhythm_consistency_score', 100)
    
    # Smoothness analysis impact
    smoothness_score = motion_flow_analysis.get('smoothness_analysis', {}).get('overall_smoothness_score', 100)
    
    # Weighted average of all scores
    overall_score = (velocity_score * 0.3 + acceleration_score * 0.3 + rhythm_score * 0.25 + smoothness_score * 0.15)
    
    return max(0, min(100, overall_score))


def detect_and_correct_orientation(frame):
    """
    Enhanced orientation detection and correction for video frames and stills.
    Uses multiple heuristics to detect sideways videos more accurately.
    Can be easily disabled by setting ENABLE_ORIENTATION_CORRECTION = False
    """
    # Easy toggle to disable this feature if it doesn't work well
    # 🎯 ORIENTATION STRATEGY: Guide users to record properly instead of auto-correction
    # Set to False to encourage proper recording technique for consistent analysis
    # This ensures users learn proper video recording for basketball analysis
    ENABLE_ORIENTATION_CORRECTION = False  # Disabled - guide users to record correctly
    
    if not ENABLE_ORIENTATION_CORRECTION:
        return frame
    
    try:
        height, width = frame.shape[:2]
        aspect_ratio = width / height
        
        logging.debug(f"Original frame dimensions: {width}x{height}, aspect ratio: {aspect_ratio:.2f}")
        
        # Enhanced detection logic for sideways videos
        needs_rotation = False
        rotation_type = None
        
        # Method 1: Aspect ratio analysis (detect portrait videos that should be landscape)
        if aspect_ratio < 0.8:  # Portrait-like (height > width)
            # Portrait video likely needs to become landscape
            needs_rotation = True
            rotation_type = cv2.ROTATE_90_COUNTERCLOCKWISE  # This makes portrait -> landscape
            reason = f"portrait aspect ratio {aspect_ratio:.2f} - rotating to landscape"
            
        elif aspect_ratio > 1.7:  # Very wide landscape
            # Check if it's too wide and might be sideways
            if aspect_ratio > 2.2:  # Extremely wide, likely rotated
                needs_rotation = True
                rotation_type = cv2.ROTATE_90_CLOCKWISE  # This makes ultra-wide -> normal
                reason = f"ultra-wide aspect ratio {aspect_ratio:.2f} - likely sideways"
            
        # Method 2: Check for common phone video resolutions that indicate vertical recording
        elif (height == 1920 and width == 1080) or (height == 1280 and width == 720):
            # These are portrait phone resolutions that should be landscape for basketball
            needs_rotation = True
            rotation_type = cv2.ROTATE_90_COUNTERCLOCKWISE  # Portrait -> landscape
            reason = f"detected vertical phone recording ({width}x{height}) - rotating to landscape"
            
        # Method 3: Additional check for square-ish videos that might be rotated
        elif 0.9 <= aspect_ratio <= 1.1:
            # For near-square videos, use content analysis
            # Check pixel intensity distribution to guess orientation
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
            
            # Analyze vertical vs horizontal gradient strength
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            vertical_strength = np.mean(np.abs(grad_y))
            horizontal_strength = np.mean(np.abs(grad_x))
            
            # If vertical gradients are much stronger, content might be rotated
            if vertical_strength > horizontal_strength * 1.8:
                needs_rotation = True
                rotation_type = cv2.ROTATE_90_COUNTERCLOCKWISE  # Try to make content more horizontal
                reason = f"content analysis suggests rotation needed (v:{vertical_strength:.1f} vs h:{horizontal_strength:.1f})"
        
        if needs_rotation and rotation_type is not None:
            corrected_frame = cv2.rotate(frame, rotation_type)
            rotation_name = "90° clockwise" if rotation_type == cv2.ROTATE_90_CLOCKWISE else "90° counter-clockwise"
            logging.info(f"Applied {rotation_name} rotation - {reason}")
            
            # Verify the correction improved the aspect ratio for basketball viewing
            new_height, new_width = corrected_frame.shape[:2]
            new_aspect_ratio = new_width / new_height
            logging.debug(f"After rotation: {new_width}x{new_height}, new aspect ratio: {new_aspect_ratio:.2f}")
            
            # For basketball videos, we want landscape orientation (aspect ratio > 1.0)
            if new_aspect_ratio > 1.0 and aspect_ratio < 1.0:
                logging.info("Rotation successful: converted portrait to landscape for better basketball viewing")
            elif new_aspect_ratio < 2.5:  # Reasonable landscape ratio
                logging.info("Rotation successful: normalized ultra-wide aspect ratio")
            
            return corrected_frame
        else:
            logging.debug(f"No rotation needed - aspect ratio {aspect_ratio:.2f} seems appropriate for basketball viewing")
            return frame
            
    except Exception as e:
        logging.warning(f"Orientation correction failed: {e}, using original frame")
        return frame


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


def detect_camera_angle_and_visibility(processed_frames_data):
    """
    Analyze the video to determine camera angle and what body parts are clearly visible
    Returns dict with camera_angle and visible_features
    """
    visibility_analysis = {
        'camera_angle': 'unknown',
        'visible_features': {
            'guide_hand': False,
            'shooting_hand': False,
            'face_profile': False,
            'full_body_side': False,
            'front_view': False
        },
        'confidence': 0.0
    }
    
    # Analyze frames with good pose detection
    good_frames = [f for f in processed_frames_data if f.landmarks_raw and f.landmarks_raw.pose_landmarks]
    if not good_frames:
        return visibility_analysis
    
    # Sample analysis from middle frames (most stable)
    sample_frames = good_frames[len(good_frames)//4:3*len(good_frames)//4]
    if not sample_frames:
        sample_frames = good_frames
    
    left_visible_count = 0
    right_visible_count = 0
    face_profile_count = 0
    
    for frame_data in sample_frames:
        landmarks = frame_data.landmarks_raw.pose_landmarks.landmark
        
        # Check visibility of left vs right side landmarks
        left_wrist_vis = landmarks[mp_pose.PoseLandmark.LEFT_WRIST].visibility
        right_wrist_vis = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].visibility
        left_elbow_vis = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].visibility
        right_elbow_vis = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].visibility
        
        # Count visible sides
        if left_wrist_vis > 0.5 and left_elbow_vis > 0.5:
            left_visible_count += 1
        if right_wrist_vis > 0.5 and right_elbow_vis > 0.5:
            right_visible_count += 1
            
        # Check face profile (nose position relative to ears)
        nose_vis = landmarks[mp_pose.PoseLandmark.NOSE].visibility
        left_ear_vis = landmarks[mp_pose.PoseLandmark.LEFT_EAR].visibility
        right_ear_vis = landmarks[mp_pose.PoseLandmark.RIGHT_EAR].visibility
        
        if nose_vis > 0.5 and (left_ear_vis > 0.5 or right_ear_vis > 0.5):
            face_profile_count += 1
    
    total_frames = len(sample_frames)
    left_ratio = left_visible_count / total_frames
    right_ratio = right_visible_count / total_frames
    face_ratio = face_profile_count / total_frames
    
    # Determine camera angle based on visibility ratios
    if right_ratio > 0.7 and left_ratio < 0.3:
        # Right side clearly visible, left side blocked - LEFT SIDE VIEW (showing right side)
        visibility_analysis['camera_angle'] = 'left_side_view'
        visibility_analysis['visible_features']['shooting_hand'] = True
        # Even if guide hand is mostly blocked, thumb movement might still be detectable
        visibility_analysis['visible_features']['guide_hand'] = left_ratio > 0.2  # Lowered from implicit 0.3
        visibility_analysis['visible_features']['full_body_side'] = True
        visibility_analysis['confidence'] = right_ratio
        
    elif left_ratio > 0.7 and right_ratio < 0.3:
        # Left side clearly visible, right side blocked - RIGHT SIDE VIEW (showing left side)  
        visibility_analysis['camera_angle'] = 'right_side_view'
        # Even if shooting hand is mostly blocked, some movement might still be detectable
        visibility_analysis['visible_features']['shooting_hand'] = right_ratio > 0.2  # Lowered from implicit 0.3
        visibility_analysis['visible_features']['guide_hand'] = True
        visibility_analysis['visible_features']['full_body_side'] = True
        visibility_analysis['confidence'] = left_ratio
        
    elif left_ratio > 0.5 and right_ratio > 0.5:
        # Both sides visible - FRONT/BACK VIEW (lowered threshold from 0.6 to 0.5)
        visibility_analysis['camera_angle'] = 'front_view'
        visibility_analysis['visible_features']['shooting_hand'] = True
        visibility_analysis['visible_features']['guide_hand'] = True
        visibility_analysis['visible_features']['front_view'] = True
        visibility_analysis['confidence'] = min(left_ratio, right_ratio)
        
    else:
        # Unclear or angled view
        visibility_analysis['camera_angle'] = 'angled_view'
        visibility_analysis['visible_features']['shooting_hand'] = right_ratio > 0.4  # Slightly lowered
        visibility_analysis['visible_features']['guide_hand'] = left_ratio > 0.4   # Slightly lowered
        visibility_analysis['confidence'] = max(left_ratio, right_ratio)
    
    # Check face profile visibility
    visibility_analysis['visible_features']['face_profile'] = face_ratio > 0.5
    
    return visibility_analysis

def analyze_detailed_flaws(processed_frames_data, ideal_shot_data, shot_phases, fps, shot_start_frame=0):
    """
    Analyze video frames for specific shooting flaws and identify key problematic frames
    Now includes camera angle awareness to only detect observable flaws
    
    Args:
        shot_start_frame: Frame number where shot motion begins (for motion-dependent analysis)
    """
    detailed_flaws = []
    
    # First, analyze what we can actually see from this camera angle
    visibility_info = detect_camera_angle_and_visibility(processed_frames_data)
    logging.info(f"Camera analysis: {visibility_info['camera_angle']} (confidence: {visibility_info['confidence']:.2f})")
    
    # Define comprehensive shooting flaws to detect with camera angle awareness
    flaw_detectors = {
        'elbow_flare': {
            'description': 'Shooting elbow positioned too far from body',
            'check_phase': 'Load_Release',  # Check during Load/Dip AND Release phases where it's most problematic
            'threshold': 15,  # Lowered from 20 to catch more subtle flares
            'plain_language': 'Your shooting elbow is sticking out too far from your body. This reduces accuracy and consistency.',
            'requires_visibility': [],  # Remove visibility requirements - elbow flare can be detected from any angle
            'camera_angles': ['left_side_view', 'front_view', 'angled_view', 'right_side_view', 'unknown']  # Accept all angles
        },
        'insufficient_knee_bend': {
            'description': 'Knee bend too shallow for proper power generation',
            'check_phase': 'Load/Dip',
            'threshold': 25,
            'plain_language': 'You\'re not bending your knees enough. Get lower to generate more power and improve your shooting range.',
            'requires_visibility': ['full_body_side'],
            'camera_angles': ['left_side_view', 'right_side_view', 'front_view']
        },
        'excessive_knee_bend': {
            'description': 'Knee bend too deep, wasting energy',
            'check_phase': 'Load/Dip',
            'threshold': 25,
            'plain_language': 'You\'re bending your knees too much. This wastes energy and can make your shot inconsistent.',
            'requires_visibility': ['full_body_side'],
            'camera_angles': ['left_side_view', 'right_side_view', 'front_view']
        },
        'poor_wrist_snap': {
            'description': 'Insufficient wrist snap on follow-through',
            'check_phase': 'Follow-Through',
            'threshold': 20,
            'plain_language': 'Your wrist snap needs improvement. Snap your wrist down aggressively for better backspin and soft touch.',
            'requires_visibility': ['shooting_hand'],
            'camera_angles': ['left_side_view', 'front_view', 'angled_view']
        },
        'guide_hand_thumb_flick': {
            'description': 'Guide hand thumb interfering with ball trajectory during follow-through',
            'check_phase': 'Follow-Through',
            'threshold': 10,  # ULTRA-LOWERED from 15 to 10 for very subtle movements
            'plain_language': 'Your guide hand thumb is interfering with the shot during follow-through. Keep your thumb passive - no flicking motion.',
            'requires_visibility': ['guide_hand'],
            'camera_angles': ['right_side_view', 'front_view', 'angled_view', 'left_side_view']  # Added left_side_view - thumb flicks can be visible from multiple angles
        },
        'guide_hand_under_ball': {
            'description': 'Guide hand positioned underneath ball instead of on side',
            'check_phase': 'Release',
            'threshold': 25,
            'plain_language': 'Your guide hand is too far under the ball. Keep it on the side for proper support without interference.',
            'requires_visibility': ['guide_hand'],
            'camera_angles': ['right_side_view', 'front_view']
        },
        'guide_hand_on_top': {
            'description': 'Guide hand positioned on top of ball instead of on side',
            'check_phase': 'Release',
            'threshold': 15,  # More sensitive for on-top detection
            'plain_language': 'Your guide hand is positioned on top of the ball. Move it to the side for better control and cleaner release.',
            'requires_visibility': ['guide_hand'],
            'camera_angles': ['right_side_view', 'front_view']
        },
        'shot_timing_inefficient': {
            'description': 'Shot timing could be more efficient for better rhythm',
            'check_phase': 'Release',
            'threshold': 40,
            'plain_language': 'Your shot timing could be more efficient. Work on smooth rhythm from catch to release.',
            'requires_visibility': ['shooting_hand'],  # Can observe from any angle with shooting hand
            'camera_angles': ['left_side_view', 'right_side_view', 'front_view', 'angled_view']
        },
        'shot_lacks_fluidity': {
            'description': 'Jerky or rushed shooting motion lacks smooth rhythm',
            'check_phase': 'Release',
            'threshold': 0.5,
            'plain_language': 'Your shot motion is not fluid. Focus on a smooth, rhythmic motion from start to finish.',
            'requires_visibility': ['shooting_hand'],
            'camera_angles': ['left_side_view', 'front_view', 'angled_view']
        },
        'eye_tracking_poor': {
            'description': 'Head/eye movement suggests looking away from target',
            'check_phase': 'Release',
            'threshold': 12,
            'plain_language': 'You\'re not maintaining focus on your target. Keep your eyes locked on the back of the rim throughout your shot.',
            'requires_visibility': ['face_profile'],
            'camera_angles': ['left_side_view', 'right_side_view', 'front_view']
        },
        'balance_issues': {
            'description': 'Poor balance affecting shot accuracy',
            'check_phase': 'Release',
            'threshold': 15,
            'plain_language': 'Your balance is off during the shot. Focus on staying centered and landing where you started.',
            'requires_visibility': ['full_body_side'],
            'camera_angles': ['left_side_view', 'right_side_view', 'front_view']
        },
        # 🎯 NEW FEATURE: Shoulder Alignment & Squaring Detection (EASILY DISABLED)
        # Set ENABLE_SHOULDER_ALIGNMENT_DETECTION = False to disable this feature
        'poor_shoulder_alignment': {
            'description': 'Shoulders not properly squared to basket for optimal shooting',
            'check_phase': 'Load_Release',  # Check during setup and release phases
            'threshold': 20,  # Degrees of deviation from ideal squaring
            'plain_language': 'Your shoulders aren\'t properly squared to the basket. Face the rim directly for better accuracy and consistency.',
            'requires_visibility': ['shoulders'],
            'camera_angles': ['front_view', 'angled_view'],  # Best detected from front/angled views
            'feature_flag': 'ENABLE_SHOULDER_ALIGNMENT_DETECTION'  # Easy disable mechanism
        },
        'follow_through_timing': {
            'description': 'Follow-through timing could be improved for better consistency',
            'check_phase': 'Follow-Through',
            'threshold': 150,
            'plain_language': 'Your follow-through timing needs work. Hold your form until the ball reaches the rim for consistent backspin.',
            'requires_visibility': ['shooting_hand'],
            'camera_angles': ['left_side_view', 'front_view', 'angled_view']
        }
    }
    
    # Analyze each phase for specific flaws, but only check flaws we can actually observe
    # Special handling for 'ANY' phase flaws - check them across all phases
    all_frames_for_any_phase = []
    any_phase_flaws_processed = set()  # Track which 'ANY' phase flaws have been processed
    detected_flaws = set()  # Track which flaws have already been detected to prevent duplicates
    
    for i, frame_data in enumerate(processed_frames_data):
        if frame_data.metrics:
            all_frames_for_any_phase.append((i, frame_data))
    
    # Handle special multi-phase flaws first (like Load_Release)
    special_phase_flaws = {}
    for flaw_key, flaw_config in flaw_detectors.items():
        # 🎯 FEATURE FLAG CHECK: Skip disabled features
        if 'feature_flag' in flaw_config:
            feature_flag_name = flaw_config['feature_flag']
            if feature_flag_name in globals() and not globals()[feature_flag_name]:
                logging.debug(f"Skipping {flaw_key}: feature flag {feature_flag_name} is disabled")
                continue
        
        if flaw_config['check_phase'] == 'Load_Release':
            # Collect frames from both Load/Dip and Release phases
            combined_frames = []
            for phase in shot_phases:
                if phase.name in ['Load/Dip', 'Release']:
                    for i, frame_data in enumerate(processed_frames_data):
                        if phase.start_frame <= i <= phase.end_frame and frame_data.metrics:
                            combined_frames.append((i, frame_data))
            special_phase_flaws[flaw_key] = combined_frames
    
    # Process special multi-phase flaws first
    for flaw_key, combined_frames in special_phase_flaws.items():
        if flaw_key in detected_flaws:
            continue
            
        flaw_config = flaw_detectors[flaw_key]
        
        # Check if we can actually observe this flaw from the current camera angle
        can_observe = True
        
        # Check camera angle compatibility
        if visibility_info['camera_angle'] not in flaw_config['camera_angles']:
            can_observe = False
            logging.debug(f"Skipping {flaw_key}: camera angle {visibility_info['camera_angle']} not suitable")
        
        # Check required feature visibility
        for required_feature in flaw_config['requires_visibility']:
            if not visibility_info['visible_features'].get(required_feature, False):
                can_observe = False
                logging.debug(f"Skipping {flaw_key}: required feature {required_feature} not visible")
                break
        
        if not can_observe:
            continue
            
        flaw_detected, worst_frame, severity = detect_specific_flaw(
            combined_frames, flaw_key, flaw_config, ideal_shot_data, shot_phases, shot_start_frame
        )
        
        # Only add flaws with meaningful severity (lowered threshold for core fundamentals)
        if flaw_detected and severity >= 5:  # Lowered from 8 to 5 for better detection
            detected_flaws.add(flaw_key)  # Mark as detected to prevent duplicates
            # FIXED: Convert relative frame index to absolute frame number
            absolute_frame_number = shot_start_frame + worst_frame
            detailed_flaws.append({
                'flaw_type': flaw_key,
                'frame_number': absolute_frame_number,
                'phase': 'Load/Dip & Release',  # Combined phase name for multi-phase flaws
                'severity': severity,
                'description': flaw_config['description'],
                'plain_language': flaw_config['plain_language'],
                'coaching_tip': get_coaching_tip(flaw_key),
                'drill_suggestion': get_drill_suggestion(flaw_key),
                'camera_context': f"Observed from {visibility_info['camera_angle'].replace('_', ' ')}"
            })
    
    # Now process regular phase-specific flaws
    for phase in shot_phases:
        phase_frames = []
        for i, frame_data in enumerate(processed_frames_data):
            if phase.start_frame <= i <= phase.end_frame and frame_data.metrics:
                phase_frames.append((i, frame_data))
        
        if not phase_frames:
            continue
            
        # Check for specific flaws in this phase, but only if we can observe them
        for flaw_key, flaw_config in flaw_detectors.items():
            # 🎯 FEATURE FLAG CHECK: Skip disabled features
            if 'feature_flag' in flaw_config:
                feature_flag_name = flaw_config['feature_flag']
                if feature_flag_name in globals() and not globals()[feature_flag_name]:
                    logging.debug(f"Skipping {flaw_key}: feature flag {feature_flag_name} is disabled")
                    continue
            
            # Skip if already processed
            if flaw_key in detected_flaws:
                continue
                
            # Handle 'ANY' phase flaws - check across all frames, but only once
            if flaw_config['check_phase'] == 'ANY':
                if flaw_key in any_phase_flaws_processed:
                    continue  # Skip if already processed
                any_phase_flaws_processed.add(flaw_key)
                current_phase_frames = all_frames_for_any_phase
                current_phase_name = 'Shot Motion'  # Generic name for ANY phase flaws
            # Skip multi-phase flaws as they were handled above
            elif flaw_config['check_phase'] == 'Load_Release':
                continue  # Already processed above
            elif flaw_config['check_phase'] != phase.name:
                continue
            else:
                current_phase_frames = phase_frames
                current_phase_name = phase.name
            
            # Check if we can actually observe this flaw from the current camera angle
            can_observe = True
            
            # Check camera angle compatibility
            if visibility_info['camera_angle'] not in flaw_config['camera_angles']:
                can_observe = False
                logging.debug(f"Skipping {flaw_key}: camera angle {visibility_info['camera_angle']} not suitable")
            
            # Check required feature visibility
            for required_feature in flaw_config['requires_visibility']:
                if not visibility_info['visible_features'].get(required_feature, False):
                    can_observe = False
                    logging.debug(f"Skipping {flaw_key}: required feature {required_feature} not visible")
                    break
            
            if not can_observe:
                continue
                
            flaw_detected, worst_frame, severity = detect_specific_flaw(
                current_phase_frames, flaw_key, flaw_config, ideal_shot_data, shot_phases, shot_start_frame
            )
            
            # Only add flaws with meaningful severity (lowered threshold for core fundamentals)
            if flaw_detected and severity >= 5:  # Lowered from 8 to 5 for better detection
                detected_flaws.add(flaw_key)  # Mark as detected to prevent duplicates
                # FIXED: Convert relative frame index to absolute frame number
                absolute_frame_number = shot_start_frame + worst_frame
                detailed_flaws.append({
                    'flaw_type': flaw_key,
                    'frame_number': absolute_frame_number,
                    'phase': current_phase_name,
                    'severity': severity,
                    'description': flaw_config['description'],
                    'plain_language': flaw_config['plain_language'],
                    'coaching_tip': get_coaching_tip(flaw_key),
                    'drill_suggestion': get_drill_suggestion(flaw_key),
                    'camera_context': f"Observed from {visibility_info['camera_angle'].replace('_', ' ')}"
                })
    
    # Sort by severity (worst first) and limit to top 5 most significant flaws
    detailed_flaws.sort(key=lambda x: x['severity'], reverse=True)
    
    # Additional filtering: lowered minimum severity threshold for final report
    significant_flaws = [flaw for flaw in detailed_flaws if flaw['severity'] >= 8]  # Lowered from 12 to 8
    
    # Return top 4 most significant flaws (reduced from 5 to be more focused)
    if significant_flaws:
        return significant_flaws[:4]
    elif detailed_flaws:
        # If no highly significant flaws, return top 2-3 moderate ones
        return detailed_flaws[:3]
    else:
        return []

def calculate_illustration_quality(frame_num, frame_data, severity, flaw_key, shot_phases):
    """Calculate how well a frame illustrates a specific flaw for coaching purposes"""
    score = 0
    
    # Base score starts with pose quality
    if hasattr(frame_data, 'pose_landmarks') and frame_data.pose_landmarks:
        score += 20  # Good pose detected
    
    # Phase-specific scoring - mid-phase frames are often more illustrative
    if shot_phases:
        for phase in shot_phases:
            if phase.start_frame <= frame_num <= phase.end_frame:
                phase_progress = (frame_num - phase.start_frame) / max(1, phase.end_frame - phase.start_frame)
                
                # Different flaw types benefit from different phase moments
                if flaw_key == 'elbow_flare':
                    # Elbow flare is most instructive during Load/Dip when ball is in hands
                    # and early Release when positioning is critical
                    if phase.name == 'Load/Dip' and 0.4 <= phase_progress <= 0.9:
                        score += 40  # HIGHEST priority: Deep load phase when elbow positioning is crucial
                    elif phase.name == 'Load/Dip':
                        score += 25  # Good illustration during any loading phase
                    elif phase.name == 'Release' and phase_progress <= 0.5:
                        score += 35  # Very high priority: Early release when ball still controlled
                    elif phase.name == 'Release' and phase_progress <= 0.7:
                        score += 20  # Moderate priority: Mid-release
                    # Note: Prioritizing phases when ball is in hands for better instruction
                        
                elif flaw_key in ['insufficient_knee_bend', 'excessive_knee_bend']:
                    # Knee bend is most illustrative at deepest point (Load/Dip phase)
                    if phase.name == 'Load/Dip' and 0.4 <= phase_progress <= 0.8:
                        score += 35
                    elif phase.name == 'Load/Dip':
                        score += 10
                        
                elif flaw_key == 'poor_wrist_snap':
                    # Wrist snap is best shown during follow-through
                    if phase.name == 'Follow-Through' and 0.2 <= phase_progress <= 0.6:
                        score += 30
                    elif phase.name == 'Follow-Through':
                        score += 15
                        
                elif flaw_key == 'guide_hand_thumb_flick':
                    # Thumb flick is most visible AFTER ball release during follow-through
                    # ABSOLUTE EXTREME LATE BIAS: Only target final 5% of Follow-Through when ball is definitely gone
                    if phase.name == 'Follow-Through' and 0.95 <= phase_progress <= 1.0:
                        score += 300  # ABSOLUTE MAXIMUM for final 5% of follow-through (95-100%)
                    elif phase.name == 'Follow-Through' and 0.9 <= phase_progress < 0.95:
                        score += 200  # ULTRA-MAXIMUM for near-end follow-through (90-95%)
                    elif phase.name == 'Follow-Through' and 0.8 <= phase_progress < 0.9:
                        score += 120  # EXTREME illustration - very late follow-through (80-90%)
                    elif phase.name == 'Follow-Through' and 0.7 <= phase_progress < 0.8:
                        score += 50   # Good illustration - late follow-through (70-80%)
                    elif phase.name == 'Follow-Through' and 0.6 <= phase_progress < 0.7:
                        score += 20   # Low illustration - mid-late follow-through (60-70%)
                    elif phase.name == 'Follow-Through' and 0.5 <= phase_progress < 0.6:
                        score -= 10   # Penalty for mid follow-through (50-60%)
                    elif phase.name == 'Follow-Through' and 0.4 <= phase_progress < 0.5:
                        score -= 50   # Strong penalty for early follow-through (40-50%)
                    elif phase.name == 'Follow-Through' and phase_progress < 0.4:
                        score -= 100  # DEVASTATING penalty for very early follow-through (<40%)
                    # Note: ABSOLUTE focus on final 5% of Follow-Through phase (95-100%)
                        
                elif flaw_key == 'guide_hand_on_top':
                    # Guide hand "on top" is most instructive during Load/Dip when ball positioning is set
                    # and early Release when hand placement affects shot mechanics
                    if phase.name == 'Load/Dip' and 0.3 <= phase_progress <= 0.8:
                        score += 45  # HIGHEST priority: Load phase when guide hand positioning is established
                    elif phase.name == 'Load/Dip':
                        score += 30  # High priority for any loading phase
                    elif phase.name == 'Release' and phase_progress <= 0.4:
                        score += 35  # Very high priority: Early release when ball still controlled
                    elif phase.name == 'Release' and phase_progress <= 0.6:
                        score += 20  # Moderate priority: Mid-early release
                    # Note: Focusing on ball-in-hands phases for maximum instructional value
                        
                elif flaw_key.startswith('guide_hand') and flaw_key != 'guide_hand_on_top':
                    # Other guide hand issues (thumb flick, interference) - different timing
                    if phase.name == 'Release' and 0.4 <= phase_progress <= 0.8:
                        score += 30
                    elif phase.name == 'Release':
                        score += 15
                        
                elif flaw_key == 'balance_issues':
                    # Balance issues are clearest during loading and release
                    if phase.name in ['Load/Dip', 'Release'] and 0.3 <= phase_progress <= 0.7:
                        score += 25
                        
                elif flaw_key == 'shot_lacks_fluidity':
                    # Fluidity issues can be seen throughout, but mid-phases are clearest
                    if 0.3 <= phase_progress <= 0.7:
                        score += 20
                break
    
    # Severity contribution (higher severity may mean clearer flaw visibility)
    score += min(severity * 0.5, 15)  # Cap severity contribution
    
    # Landmark visibility bonus - more visible landmarks = better illustration
    if hasattr(frame_data, 'metrics') and frame_data.metrics:
        visible_metrics = len([v for v in frame_data.metrics.values() if v is not None])
        score += min(visible_metrics * 2, 10)
    
    return score

def detect_specific_flaw(phase_frames, flaw_key, flaw_config, ideal_shot_data, shot_phases=None, shot_start_frame=0):
    """Detect if a specific flaw exists in the given frames with improved discernment
    
    Args:
        shot_start_frame: Frame number where shot motion begins (for motion-dependent analysis)
    """
    worst_severity = 0
    worst_frame = None
    best_illustration_frame = None  # Frame that best illustrates the flaw for coaching
    best_illustration_score = 0    # Combined score for illustration quality
    flaw_detected = False
    flaw_evidence_count = 0  # Count frames showing the flaw
    severity_values = []  # Track severity across frames for statistical analysis
    frame_scores = []  # Track frames with their scores for better selection
    
    # Minimum frames required to confirm a flaw (prevents false positives)
    # ULTRA-LOWERED requirements for subtle flaws like thumb flick
    if flaw_key == 'guide_hand_thumb_flick':
        min_evidence_frames = 1  # Accept even a single frame for thumb flick (it can be very brief)
    elif flaw_key in ['elbow_flare', 'insufficient_knee_bend', 'excessive_knee_bend', 'poor_wrist_snap']:
        min_evidence_frames = max(1, len(phase_frames) // 6)  # Very lenient for core fundamentals
    else:
        min_evidence_frames = max(2, len(phase_frames) // 4)  # Slightly more lenient for other flaws
    
    # Special handling for knee bend flaws - only analyze at the deepest point
    if flaw_key in ['insufficient_knee_bend', 'excessive_knee_bend']:
        # Find the Load/Dip phase to get the deepest knee bend frame
        deepest_knee_frame = None
        if shot_phases:
            for phase in shot_phases:
                if phase.name == 'Load/Dip' and phase.key_moment_frame is not None:
                    deepest_knee_frame = phase.key_moment_frame
                    logging.info(f"KNEE BEND ANALYSIS: Analyzing {flaw_key} only at deepest point (frame {deepest_knee_frame})")
                    break
        
        # Only analyze knee bend at the deepest point, not throughout the entire phase
        if deepest_knee_frame is not None:
            # Find the frame data for the deepest knee bend
            target_frame_data = None
            for frame_num, frame_data in phase_frames:
                if frame_num == deepest_knee_frame:
                    target_frame_data = (frame_num, frame_data)
                    break
            
            if target_frame_data:
                # Analyze only this single frame (the deepest knee bend point)
                frame_num, frame_data = target_frame_data
                severity = 0
                
                if flaw_key == 'insufficient_knee_bend':
                    if 'knee_angle' in frame_data.metrics:
                        ideal_min = ideal_shot_data['load_knee_angle']['min']  # 110°
                        actual = frame_data.metrics['knee_angle']
                        
                        # REFINED INSUFFICIENT KNEE BEND: Stricter threshold at 130°
                        # Only flag insufficient knee bend when angle > 130° (was 135°)
                        if actual > 130:  # Stricter: flag at 130° threshold
                            # CONSERVATIVE SEVERITY: Only for genuinely problematic form
                            severity_factor = (actual - ideal_min - 15) * 1.2  # Adjusted calculation
                            severity = min(severity_factor, 40)  # Lower max severity
                            logging.info(f"INSUFFICIENT KNEE BEND DETECTED - Frame {frame_num}: angle={actual:.1f}° (need <130°), severity={severity:.1f}")
                        else:
                            logging.debug(f"KNEE BEND OK - Frame {frame_num}: angle={actual:.1f}° within acceptable range (>130° would flag)")
                            
                elif flaw_key == 'excessive_knee_bend':
                    if 'knee_angle' in frame_data.metrics:
                        ideal_max = ideal_shot_data['load_knee_angle']['max']  # 130°
                        actual = frame_data.metrics['knee_angle']
                        
                        # REFINED EXCESSIVE KNEE BEND: Much stricter threshold  
                        # Only flag truly excessive knee bend (>25° below maximum)
                        if actual < ideal_max - 25:  # Must be <105° to flag (was <115°)
                            # CONSERVATIVE SEVERITY: Only for genuinely problematic form
                            severity_factor = (ideal_max - actual - 20) * 1.2  # Reduced sensitivity
                            severity = min(severity_factor, 35)  # Lower max severity
                            logging.info(f"EXCESSIVE KNEE BEND DETECTED - Frame {frame_num}: angle={actual:.1f}° (need >{ideal_max - 25}°), severity={severity:.1f}")
                        else:
                            logging.debug(f"KNEE BEND OK - Frame {frame_num}: angle={actual:.1f}° within acceptable range (<{ideal_max - 25}° would flag)")
                
                # For knee bend flaws, we only need one measurement (at the deepest point)
                if severity > 0:
                    flaw_detected = True
                    worst_frame = frame_num
                    worst_severity = severity
                    return flaw_detected, worst_frame, worst_severity
                else:
                    return False, None, 0
            else:
                logging.warning(f"Could not find frame data for deepest knee bend frame {deepest_knee_frame}")
                return False, None, 0
        else:
            logging.warning("Could not identify deepest knee bend frame for knee bend analysis")
            return False, None, 0
    
    # For all other flaws, use the original frame-by-frame analysis
    for frame_num, frame_data in phase_frames:
        severity = 0
        
        # Skip knee bend flaws as they are handled separately above
        if flaw_key in ['insufficient_knee_bend', 'excessive_knee_bend']:
            continue
                    
        if flaw_key == 'poor_wrist_snap':
            if 'wrist_angle_simplified' in frame_data.metrics:
                ideal_range = ideal_shot_data['follow_through_wrist_snap_angle']
                actual = frame_data.metrics['wrist_angle_simplified']
                
                # REFINED WRIST SNAP DETECTION: Focus on peak Follow-Through moment only
                is_peak_followthrough = False
                current_phase_name = "Unknown"
                
                if shot_phases:
                    for phase in shot_phases:
                        if phase.start_frame <= frame_num <= phase.end_frame:
                            current_phase_name = phase.name
                            # STRICT TIMING: Only analyze at the peak Follow-Through moment
                            if (phase.name == 'Follow-Through' and 
                                phase.key_moment_frame is not None and
                                abs(frame_num - phase.key_moment_frame) <= 2):  # ±2 frames from peak
                                is_peak_followthrough = True
                            break
                
                # Skip if not at peak Follow-Through moment - eliminates timing false positives
                if not is_peak_followthrough:
                    logging.debug(f"WRIST SNAP SKIPPED - Frame {frame_num}: in {current_phase_name} phase, only analyzing peak Follow-Through moment")
                    continue
                
                # MUCH STRICTER THRESHOLD: Only flag severely inadequate wrist snap
                # Wrist snap is critical for backspin, so we need meaningful deviation
                if actual < ideal_range['min'] - 20:  # Must be <50° to flag (was <60°)
                    # CONSERVATIVE SEVERITY: Focus on truly problematic wrist snap
                    severity_factor = (ideal_range['min'] - actual - 15) * 1.8  # Reduced sensitivity
                    severity = min(severity_factor, 30)  # Lower max severity (was 35)
                    logging.info(f"POOR WRIST SNAP DETECTED - Frame {frame_num} (peak Follow-Through): angle={actual:.1f}° (need >{ideal_range['min'] - 20}°), severity={severity:.1f}")
                else:
                    logging.debug(f"WRIST SNAP OK - Frame {frame_num} (peak Follow-Through): angle={actual:.1f}° within acceptable range")
                    
        elif flaw_key == 'elbow_flare':
            # CORRECTED ELBOW FLARE DETECTION - Focus on Load/Dip AND Release phases where it's most problematic
            # Skip frames before shot motion begins
            if frame_num < shot_start_frame:
                continue
            
            # PROPER PHASE RESTRICTION: Check during Load/Dip AND Release phases (NOT Follow-Through)
            is_analysis_phase = False
            current_phase_name = "Unknown"
            
            if shot_phases:
                for phase in shot_phases:
                    if phase.start_frame <= frame_num <= phase.end_frame:
                        current_phase_name = phase.name
                        # Accept Load/Dip and Release phases where elbow flare is most problematic
                        if phase.name in ['Load/Dip', 'Release']:
                            is_analysis_phase = True
                        break
            else:
                # If no phases detected, analyze all frames after shot start
                is_analysis_phase = True
                current_phase_name = "Shot Motion"
            
            # Skip Follow-Through phase where some elbow movement is natural
            if not is_analysis_phase:
                logging.debug(f"ELBOW FLARE SKIPPED - Frame {frame_num}: in {current_phase_name} phase, analyzing Load/Dip and Release only")
                continue
                
            # LENIENT THRESHOLDS for obvious flaws during critical phases
            frame_severity = 0
            
            # Side view detection: check elbow extension angle
            if 'elbow_angle' in frame_data.metrics:
                ideal_range = ideal_shot_data['release_elbow_angle']
                actual = frame_data.metrics['elbow_angle']
                # LENIENT: Flag obvious extension issues (>12° below ideal for clear coaching value)
                if actual < ideal_range['min'] - 12:  # Further reduced for Load/Release detection
                    side_severity = min((ideal_range['min'] - actual) * 1.8, 60)  # Enhanced sensitivity
                    frame_severity = max(frame_severity, side_severity)
                    logging.info(f"ELBOW FLARE DETECTED - Side view: actual={actual:.1f}°, ideal_min={ideal_range['min']}°, severity={side_severity:.1f}")
                else:
                    logging.debug(f"ELBOW EXTENSION OK - Side view: actual={actual:.1f}°, ideal_min={ideal_range['min']}°")
            
            # Front view detection: lateral elbow deviation with very lenient thresholds for obvious flaws
            if 'elbow_flare_front_view' in frame_data.metrics:
                elbow_flare_ratio = frame_data.metrics['elbow_flare_front_view']
                # VERY LENIENT THRESHOLD: Catch any noticeable elbow flares (>15% for obvious coaching value)
                if elbow_flare_ratio > 15:  # Very lenient for Load/Release detection
                    front_view_severity = min((elbow_flare_ratio - 12) * 2.5, 65)  # Enhanced sensitivity
                    frame_severity = max(frame_severity, front_view_severity)
                    logging.info(f"ELBOW FLARE DETECTED - Front view: ratio={elbow_flare_ratio:.1f}%, severity={front_view_severity:.1f}")
                else:
                    logging.debug(f"ELBOW FLARE NOT DETECTED - Front view: ratio={elbow_flare_ratio:.1f}% below threshold (15%)")
                    
            # Alternative front view: lateral angle with very lenient threshold
            if 'elbow_lateral_angle' in frame_data.metrics:
                lateral_angle = frame_data.metrics['elbow_lateral_angle']
                # VERY LENIENT THRESHOLD: Flag any noticeable lateral deviations (>6° for obvious coaching value)
                if lateral_angle > 6:  # Very lenient for Load/Release detection
                    angle_severity = min((lateral_angle - 4) * 5.0, 60)  # Enhanced sensitivity
                    frame_severity = max(frame_severity, angle_severity)
                    logging.info(f"ELBOW FLARE DETECTED - Lateral angle: {lateral_angle:.1f}°, severity={angle_severity:.1f}")
                else:
                    logging.debug(f"ELBOW FLARE NOT DETECTED - Lateral angle: {lateral_angle:.1f}° below threshold (6°)")
            
            # Only assign severity if we detected meaningful flare in Load/Release phases
            if frame_severity > 0:
                severity = frame_severity
                logging.info(f"ELBOW FLARE DETECTED - Frame {frame_num} ({current_phase_name} phase): severity={severity:.1f}")
            else:
                logging.debug(f"NO ELBOW FLARE - Frame {frame_num} ({current_phase_name} phase): passed lenient thresholds")
                    
        elif flaw_key == 'guide_hand_thumb_flick':
            # IMPROVED THUMB FLICK DETECTION: Focus on post-release thumb movement
            if 'guide_hand_thumb_angle' in frame_data.metrics:
                actual = frame_data.metrics['guide_hand_thumb_angle']
                
                # FOCUSED TIMING: Prioritize Follow-Through phase where thumb movement is most visible
                current_phase_name = None
                is_relevant_phase = False
                phase_bonus = 0  # Bonus for frames in optimal phase timing
                
                if shot_phases:
                    for phase in shot_phases:
                        # STRICT PHASE RESTRICTION: Only detect thumb flick in Follow-Through phase
                        # This prevents detection during Release phase when ball is still in contact
                        if phase.name == 'Follow-Through' and phase.start_frame <= frame_num <= phase.end_frame:
                            current_phase_name = phase.name
                            is_relevant_phase = True
                            
                            # Calculate phase progress for timing bonus
                            phase_progress = (frame_num - phase.start_frame) / max(1, phase.end_frame - phase.start_frame)
                            
                            # ULTRA-EXTREME LATE BIAS: Give massive bonus for very end of follow-through only
                            if phase.name == 'Follow-Through' and 0.95 <= phase_progress <= 1.0:
                                phase_bonus = 200  # ABSOLUTE MAXIMUM bonus for final 5% (95-100%) 
                            elif phase.name == 'Follow-Through' and 0.9 <= phase_progress < 0.95:
                                phase_bonus = 150  # ULTRA-MAXIMUM bonus for near-end (90-95%)
                            elif phase.name == 'Follow-Through' and 0.8 <= phase_progress < 0.9:
                                phase_bonus = 100  # EXTREME bonus for very late follow-through (80-90%)
                            elif phase.name == 'Follow-Through' and 0.7 <= phase_progress < 0.8:
                                phase_bonus = 40   # Strong bonus for late follow-through (70-80%)
                            elif phase.name == 'Follow-Through' and 0.6 <= phase_progress < 0.7:
                                phase_bonus = 10   # Low bonus for mid-late follow-through (60-70%)
                            elif phase.name == 'Follow-Through' and 0.5 <= phase_progress < 0.6:
                                phase_bonus = -20  # Strong penalty for mid follow-through (50-60%)
                            elif phase.name == 'Follow-Through' and 0.4 <= phase_progress < 0.5:
                                phase_bonus = -40  # Severe penalty for early follow-through (40-50%)
                            elif phase.name == 'Follow-Through' and phase_progress < 0.4:
                                phase_bonus = -100 # DEVASTATING penalty for very early follow-through (<40%)
                            # Note: ABSOLUTE focus on final 5% of Follow-Through phase (95-100%)
                            break
                
                # Skip if not in Follow-Through phase (thumb flick only happens AFTER ball release)
                # ABSOLUTE RESTRICTION: Only detect in final 10% of Follow-Through phase (90-100%)
                if not is_relevant_phase:
                    logging.debug(f"THUMB FLICK SKIPPED - Frame {frame_num}: not in Follow-Through phase (current phase: {current_phase_name or 'Unknown'})")
                    continue
                
                # EXTREME RESTRICTION: Only allow detection in final 10% of Follow-Through
                if shot_phases:
                    final_phase_only = False
                    for phase in shot_phases:
                        if phase.name == 'Follow-Through' and phase.start_frame <= frame_num <= phase.end_frame:
                            phase_progress = (frame_num - phase.start_frame) / max(1, phase.end_frame - phase.start_frame)
                            # ABSOLUTE FINAL FRAMES ONLY: Must be in final 10% (90-100%)
                            if phase_progress >= 0.9:
                                final_phase_only = True
                                logging.debug(f"THUMB FLICK ALLOWED - Frame {frame_num}: in final 10% of Follow-Through ({phase_progress:.2f})")
                            else:
                                logging.debug(f"THUMB FLICK REJECTED - Frame {frame_num}: too early in Follow-Through ({phase_progress:.2f}, need >=0.9)")
                            break
                    
                    if not final_phase_only:
                        continue  # Skip this frame - not in final 10% of Follow-Through
                
                # ULTRA-SENSITIVE THRESHOLD: Catch very subtle thumb movements
                # Use configured threshold from flaw_config (10°) for ultra-sensitive detection
                configured_threshold = flaw_config.get('threshold', 10)  # Use config threshold (10°)
                
                # ULTRA-SENSITIVE threshold for detecting subtle movements like O'Shea's
                effective_threshold = configured_threshold * 0.7  # 7° - ultra-sensitive for subtle flicks
                logging.debug(f"Using ultra-sensitive threshold for thumb flick detection: {effective_threshold:.1f}°")
                
                # ALSO check for ANY movement above 5° during Follow-Through (catches very subtle cases)
                subtle_threshold = 5.0  # Extremely low threshold for barely visible movements
                
                if actual > effective_threshold:
                    # Enhanced severity calculation - more sensitive to any violations
                    base_severity = (actual - (effective_threshold - 2)) * 1.5  # Start penalty at threshold-2°
                    severity = min(base_severity + phase_bonus, 40)  # Add phase bonus and cap at reasonable maximum
                    
                    # Extra penalty for any movement >25°
                    if actual > 25:
                        severity = min(severity + 8, 50)
                    
                    logging.info(f"THUMB FLICK DETECTED - Frame {frame_num}: {actual:.1f}° > {effective_threshold:.1f}° threshold ({current_phase_name}, progress={phase_progress:.2f}), severity={severity:.1f}")
                    
                elif actual > subtle_threshold and current_phase_name == 'Follow-Through' and phase_progress >= 0.3:
                    # ULTRA-SUBTLE detection for barely visible movements in late follow-through
                    base_severity = (actual - 3) * 2.0  # High sensitivity multiplier
                    severity = min(base_severity + phase_bonus, 25)  # Lower cap for subtle movements
                    
                    logging.info(f"SUBTLE THUMB FLICK DETECTED - Frame {frame_num}: {actual:.1f}° > {subtle_threshold:.1f}° subtle threshold ({current_phase_name}, progress={phase_progress:.2f}), severity={severity:.1f}")
                    
                else:
                    logging.debug(f"NO THUMB FLICK - Frame {frame_num}: {actual:.1f}° within acceptable range (<{effective_threshold:.1f}°, subtle:<{subtle_threshold:.1f}°)")
                    
        elif flaw_key == 'guide_hand_under_ball':
            # PHASE 5 REFINEMENT: Focused detection for ball-supporting violations
            if 'guide_hand_position_angle' in frame_data.metrics and 'guide_hand_vertical_offset' in frame_data.metrics:
                # STRICT TIMING: Only analyze at peak release moment (±2 frames)
                max_wrist_vel_frame = -1
                for phase in shot_phases:
                    if phase.name == 'Release' and phase.key_moment_frame is not None:
                        max_wrist_vel_frame = phase.key_moment_frame
                        break
                
                # TIGHTER TIMING WINDOW: Only ±2 frames from release (was ±3)
                if max_wrist_vel_frame != -1:
                    distance_from_release = abs(frame_num - max_wrist_vel_frame)
                    if distance_from_release > 2:  # Stricter timing requirement
                        logging.debug(f"GUIDE HAND UNDER SKIPPED - Frame {frame_num}: {distance_from_release} frames from release")
                        continue
                
                vertical_offset = frame_data.metrics['guide_hand_vertical_offset']
                horizontal_offset = frame_data.metrics.get('guide_hand_horizontal_offset', 0)
                
                # REFINED DETECTION: Focus only on genuinely problematic "under ball" positioning
                # Must be significantly underneath to indicate ball-supporting (not natural hand drop)
                is_significantly_underneath = vertical_offset > 25  # Stricter threshold (was 15)
                is_too_centered = horizontal_offset < 15  # Stricter centering threshold (was 20)
                
                # BIOMECHANICAL FOCUS: Only flag positions that would actually support ball weight
                if is_significantly_underneath:
                    # Guide hand is genuinely underneath ball, supporting weight - problematic
                    severity = min((vertical_offset - 20) / 3, 25)  # Conservative severity
                    logging.info(f"GUIDE HAND UNDER BALL CONFIRMED - Frame {frame_num}: {vertical_offset:.1f} below shooting hand, severity={severity:.1f}")
                elif is_too_centered and abs(vertical_offset) < 10:  # Centered AND at same height
                    # Both hands at same level and close together - dual control issue
                    severity = min((20 - horizontal_offset) / 2, 20)  # Lower severity for centering
                    logging.info(f"GUIDE HAND CENTERED CONFIRMED - Frame {frame_num}: hands too centered ({horizontal_offset:.1f}), severity={severity:.1f}")
                else:
                    logging.debug(f"GUIDE HAND UNDER OK - Frame {frame_num}: vertical={vertical_offset:.1f}, horizontal={horizontal_offset:.1f}")
                    
        elif flaw_key == 'guide_hand_on_top':
            # TIMING FIX: Guide hand "on top" should be detected during SETUP/LOADING phases, not at release
            # This flaw occurs when guide hand is improperly positioned on top of ball during ball handling/setup
            if 'guide_hand_position_angle' in frame_data.metrics and 'guide_hand_vertical_offset' in frame_data.metrics:
                
                # PHASE-BASED DETECTION: Focus on Load/Dip and early Release phases where ball is being controlled
                current_phase_name = None
                is_relevant_phase = False
                
                for phase in shot_phases:
                    if phase.start_frame <= frame_num <= phase.end_frame:
                        current_phase_name = phase.name
                        # Detect during setup and loading - NOT during follow-through
                        if phase.name in ['Load/Dip']:
                            is_relevant_phase = True
                        elif phase.name == 'Release':
                            # Only check early release when ball is still being controlled
                            phase_progress = (frame_num - phase.start_frame) / max(1, phase.end_frame - phase.start_frame)
                            if phase_progress <= 0.3:  # Only first 30% of release phase
                                is_relevant_phase = True
                        break
                
                # Skip if not in relevant phase (ball control phase)
                if not is_relevant_phase:
                    logging.debug(f"GUIDE HAND ON TOP SKIPPED - Frame {frame_num}: not in ball control phase (current phase: {current_phase_name or 'Unknown'})")
                    continue
                
                vertical_offset = frame_data.metrics['guide_hand_vertical_offset']
                horizontal_offset = frame_data.metrics.get('guide_hand_horizontal_offset', 0)
                
                # REFINED DETECTION: Only flag genuinely problematic "on top" positioning
                # Must be significantly above shooting hand to indicate control interference
                is_significantly_on_top = vertical_offset < -20  # Stricter threshold (was -15)
                
                # BIOMECHANICAL FOCUS: Only flag positions that would interfere with ball control
                if is_significantly_on_top:
                    severity = min(abs(vertical_offset - 15) / 2.5, 25)  # Conservative severity scaling
                    logging.info(f"GUIDE HAND ON TOP CONFIRMED - Frame {frame_num}: {vertical_offset:.1f} above shooting hand, severity={severity:.1f}")
                else:
                    logging.debug(f"GUIDE HAND ON TOP OK - Frame {frame_num}: vertical={vertical_offset:.1f} within acceptable range")
                    
        elif flaw_key == 'shot_timing_inefficient':
            # Analyze shot timing efficiency (renamed from rushing_shot for single shots)
            if 'wrist_vertical_velocity' in frame_data.metrics:
                velocity = frame_data.metrics['wrist_vertical_velocity']
                # Look for inefficient velocity patterns rather than comparing to multiple shots
                if abs(velocity) > 500:  # Very fast movement suggests rushed motion
                    severity = min(abs(velocity) / 20, 40)
                    
        elif flaw_key == 'follow_through_timing':
            # Analyze follow-through timing (replaced early_drop with timing analysis)
            if 'wrist_angle_simplified' in frame_data.metrics:
                wrist_angle = frame_data.metrics['wrist_angle_simplified']
                # In follow-through phase, wrist should maintain downward snap
                if wrist_angle > 100:  # Wrist coming back up too quickly
                    severity = min((wrist_angle - 90) / 2, 35)
                    
        elif flaw_key == 'shot_lacks_fluidity':
            # PHASE 4 REFINEMENT: Replace simple detection with biomechanically-focused approach
            # Skip per-frame detection - fluidity requires full motion analysis
            # This will be handled by the advanced fluidity analysis system which provides
            # proper acceleration analysis, rhythm detection, and velocity consistency checks
            # Only flag frames during Release phase for specific acceleration spikes
            severity = 0
            
            # Only detect specific acceleration anomalies during Release phase
            if shot_phases:
                in_release_phase = False
                for phase in shot_phases:
                    if (phase.name == 'Release' and 
                        phase.start_frame <= frame_num <= phase.end_frame):
                        in_release_phase = True
                        break
                
                if in_release_phase:
                    # Look for extreme velocity spikes that indicate jerky motion
                    if 'wrist_vertical_velocity' in frame_data.metrics:
                        velocity = abs(frame_data.metrics['wrist_vertical_velocity'])
                        # Much stricter threshold - only flag truly excessive velocities
                        if velocity > 600:  # Raised from 400 to 600
                            severity = min((velocity - 600) / 30, 25)  # Conservative severity
        
        # 🎯 NEW FEATURE: Poor Shoulder Alignment Detection (EASILY DISABLED)
        elif flaw_key == 'poor_shoulder_alignment':
            # Skip if feature is disabled
            if not ENABLE_SHOULDER_ALIGNMENT_DETECTION:
                continue
                
            # Check if we have shoulder alignment data
            if 'shoulder_squaring_deviation' in frame_data.metrics:
                shoulder_deviation = frame_data.metrics['shoulder_squaring_deviation']
                
                # Only flag significant deviations from square positioning
                # Threshold: 20° deviation from ideal (horizontal shoulder line)
                if shoulder_deviation > 20:  # More than 20° deviation from square
                    severity = min((shoulder_deviation - 20) / 2, 30)  # Conservative severity scaling
                    logging.info(f"POOR SHOULDER ALIGNMENT DETECTED - Frame {frame_num}: {shoulder_deviation:.1f}° deviation, severity={severity:.1f}")
                else:
                    logging.debug(f"SHOULDER ALIGNMENT OK - Frame {frame_num}: {shoulder_deviation:.1f}° deviation (within acceptable range)")
                    
        # Remove the problematic inconsistent_release_point check for single shots
        # Remove rushing_shot and follow_through_early_drop as they need multiple shots for context
        
        if severity > 0:
            flaw_evidence_count += 1
            severity_values.append(severity)
            
            # Calculate illustration quality score for this frame
            illustration_score = calculate_illustration_quality(
                frame_num, frame_data, severity, flaw_key, shot_phases
            )
            
            # Store frame with combined score
            frame_scores.append({
                'frame_num': frame_num,
                'severity': severity,
                'illustration_score': illustration_score,
                'combined_score': severity * 0.4 + illustration_score * 0.6  # Initial balanced weighting
            })
            
            if severity > worst_severity:
                worst_severity = severity
                worst_frame = frame_num
                
            # Track best illustration frame
            if illustration_score > best_illustration_score:
                best_illustration_score = illustration_score
                best_illustration_frame = frame_num
    
    # ENHANCED CONSISTENCY REQUIREMENTS - Apply stricter standards for elbow flare
    if flaw_evidence_count >= min_evidence_frames and severity_values:
        # Calculate average severity to ensure consistency
        avg_severity = sum(severity_values) / len(severity_values)
        
        # STRICTER REQUIREMENTS for elbow flare to reduce false positives
        if flaw_key == 'elbow_flare':
            # Require elbow flare to be detected in at least 60% of Release phase frames
            total_release_frames = 0
            if shot_phases:
                for phase in shot_phases:
                    if phase.name == 'Release':
                        total_release_frames = phase.end_frame - phase.start_frame + 1
                        break
            
            required_consistency = max(int(total_release_frames * 0.6), 2)  # At least 60% or minimum 2 frames
            consistency_met = flaw_evidence_count >= required_consistency
            severity_meaningful = avg_severity > 5  # Higher minimum severity for elbow flare
            
            if consistency_met and severity_meaningful:
                flaw_detected = True
                worst_severity = avg_severity
                logging.info(f"ELBOW FLARE CONFIRMED - Detected in {flaw_evidence_count}/{total_release_frames} Release frames ({flaw_evidence_count/max(total_release_frames,1)*100:.1f}%), avg severity: {avg_severity:.1f}")
            else:
                logging.info(f"ELBOW FLARE REJECTED - Consistency: {flaw_evidence_count}/{required_consistency}, severity: {avg_severity:.1f} (need >5)")
                
        # REFINED KNEE BEND REQUIREMENTS - Single-point analysis with higher severity threshold
        elif flaw_key in ['insufficient_knee_bend', 'excessive_knee_bend']:
            # Knee bend is analyzed at single deepest point, so different consistency logic
            severity_meaningful = avg_severity > 8  # Higher threshold for knee bend flaws
            
            if severity_meaningful:
                flaw_detected = True
                worst_severity = avg_severity
                logging.info(f"{flaw_key.upper()} CONFIRMED - Single-point analysis, severity: {avg_severity:.1f}")
            else:
                logging.info(f"{flaw_key.upper()} REJECTED - Severity: {avg_severity:.1f} (need >8 for single-point detection)")
                
        # REFINED WRIST SNAP REQUIREMENTS - Peak-moment analysis with higher severity threshold  
        elif flaw_key == 'poor_wrist_snap':
            # Wrist snap is analyzed at peak Follow-Through moment, so single-point logic
            severity_meaningful = avg_severity > 10  # Higher threshold for wrist snap (critical for backspin)
            
            if severity_meaningful:
                flaw_detected = True
                worst_severity = avg_severity
                logging.info(f"POOR WRIST SNAP CONFIRMED - Peak Follow-Through analysis, severity: {avg_severity:.1f}")
            else:
                logging.info(f"POOR WRIST SNAP REJECTED - Severity: {avg_severity:.1f} (need >10 for peak-moment detection)")
                
        # REFINED FLUIDITY REQUIREMENTS - Minimal per-frame detection, rely on advanced analysis
        elif flaw_key == 'shot_lacks_fluidity':
            # Very high threshold since advanced fluidity analysis handles main detection
            severity_meaningful = avg_severity > 15  # Only flag extreme velocity spikes
            
            if severity_meaningful:
                flaw_detected = True
                worst_severity = avg_severity
                logging.info(f"SHOT FLUIDITY CONFIRMED - Extreme velocity spike detected, severity: {avg_severity:.1f}")
            else:
                logging.info(f"SHOT FLUIDITY REJECTED - Severity: {avg_severity:.1f} (deferred to advanced fluidity analysis)")
                
        # REFINED GUIDE HAND REQUIREMENTS - Release-moment precision with higher severity thresholds
        elif flaw_key in ['guide_hand_thumb_flick', 'guide_hand_under_ball', 'guide_hand_on_top']:
            # Guide hand flaws require precise timing detection at release moment
            severity_meaningful = avg_severity > 12  # Higher threshold for guide hand flaws (critical for shot consistency)
            
            if severity_meaningful:
                flaw_detected = True
                worst_severity = avg_severity
                logging.info(f"{flaw_key.upper()} CONFIRMED - Release-moment analysis, severity: {avg_severity:.1f}")
            else:
                logging.info(f"{flaw_key.upper()} REJECTED - Severity: {avg_severity:.1f} (need >12 for guide hand precision detection)")
        else:
            # Standard requirements for other flaws
            if avg_severity > 3:  # Standard minimum severity threshold 
                flaw_detected = True
                worst_severity = avg_severity
    
    # Select the best frame for illustration (not just highest severity)
    selected_frame = worst_frame  # Default fallback
    
    if flaw_detected and frame_scores:
        # ENHANCED FRAME SELECTION FOR COACHING: Prioritize illustration quality for key fundamentals
        
        # For elbow flare and other core coaching flaws, heavily favor illustration clarity
        if flaw_key in ['elbow_flare', 'guide_hand_thumb_flick', 'poor_wrist_snap']:
            # ULTRA-EXTREME COACHING FOCUS FOR THUMB FLICK: Maximum preference for late follow-through illustration
            if flaw_key == 'guide_hand_thumb_flick':
                # 99% illustration quality, 1% severity for thumb flick coaching
                # This ensures we get the LATEST follow-through frames showing actual "flicking" motion
                for frame_data in frame_scores:
                    frame_data['combined_score'] = (frame_data['severity'] * 0.01) + (frame_data['illustration_score'] * 0.99)
                logging.info(f"THUMB FLICK ULTRA-EXTREME COACHING FRAME SELECTION: Almost entirely prioritizing illustration clarity (99%) over severity (1%)")
            else:
                # 75% illustration quality, 25% severity for other core fundamentals
                for frame_data in frame_scores:
                    frame_data['combined_score'] = (frame_data['severity'] * 0.25) + (frame_data['illustration_score'] * 0.75)
                logging.info(f"COACHING FRAME SELECTION for {flaw_key}: Prioritizing illustration clarity (75%) over severity (25%)")
        
        else:
            # Balanced approach for other flaws (60% illustration, 40% severity)
            for frame_data in frame_scores:
                frame_data['combined_score'] = (frame_data['severity'] * 0.4) + (frame_data['illustration_score'] * 0.6)
            
            logging.info(f"BALANCED FRAME SELECTION for {flaw_key}: Prioritizing illustration quality (60%) over severity (40%)")
        
        # Sort frames by recalculated combined score
        frame_scores.sort(key=lambda x: x['combined_score'], reverse=True)
        
        # Use the frame with highest combined score for better coaching value
        best_frame_data = frame_scores[0]
        selected_frame = best_frame_data['frame_num']
        
        # Additional validation: ensure the selected frame has meaningful illustration value
        if best_frame_data['illustration_score'] < 20:
            logging.warning(f"FRAME SELECTION WARNING for {flaw_key}: Best frame has low illustration score ({best_frame_data['illustration_score']:.1f})")
            # Try to find a frame with better illustration score even if lower severity
            better_illustration_frames = [f for f in frame_scores if f['illustration_score'] >= 25]
            if better_illustration_frames:
                best_frame_data = better_illustration_frames[0]
                selected_frame = best_frame_data['frame_num']
                logging.info(f"FRAME SELECTION ADJUSTED for {flaw_key}: Using frame {selected_frame} with better illustration score")
        
        logging.info(f"FINAL FRAME SELECTION for {flaw_key}: Selected frame {selected_frame} "
                    f"(severity: {best_frame_data['severity']:.1f}, "
                    f"illustration: {best_frame_data['illustration_score']:.1f}, "
                    f"combined: {best_frame_data['combined_score']:.1f}) "
                    f"over worst severity frame {worst_frame}")
    
    return flaw_detected, selected_frame, worst_severity

def get_coaching_tip(flaw_key):
    """Get specific coaching tip for each flaw type"""
    tips = {
        'elbow_flare': 'Keep your shooting elbow directly under the ball. Imagine shooting through a narrow tunnel.',
        'insufficient_knee_bend': 'Bend your knees more to get into a proper athletic position. Think "sit back" into your shot.',
        'excessive_knee_bend': 'Don\'t over-bend your knees. Find a comfortable athletic stance that you can repeat consistently.',
        'poor_wrist_snap': 'Snap your wrist down aggressively after release. Your fingers should point to the floor.',
        'guide_hand_thumb_flick': 'Keep your guide hand passive. No thumb movement - it should be completely still during release.',
        'guide_hand_under_ball': 'Position your guide hand on the side of the ball, not underneath. Think "passenger, not driver."',
        'guide_hand_on_top': 'Move your guide hand to the side of the ball, not on top. This allows for cleaner release and better ball control.',
        'shot_timing_inefficient': 'Focus on smooth rhythm from catch to release. Don\'t rush - let the shot flow naturally.',
        'balance_issues': 'Focus on your base. Keep your feet shoulder-width apart and land in the same spot.',
        'shot_lacks_fluidity': 'Work on smooth, continuous motion. No pauses or jerky movements from start to finish.',
        'eye_tracking_poor': 'Lock your eyes on the back of the rim. Don\'t follow the ball\'s flight with your eyes.',
        'follow_through_timing': 'Hold your follow-through until the ball hits the rim. Think "reach into the cookie jar."'
    }
    return tips.get(flaw_key, 'Work with a coach to improve this aspect of your shot.')

def get_drill_suggestion(flaw_key):
    """Get specific drill suggestion for each flaw type"""
    drills = {
        'elbow_flare': 'Wall shooting drill: Stand arm\'s length from a wall and practice your shooting motion without hitting the wall.',
        'insufficient_knee_bend': 'Chair shooting: Practice shooting while sitting, then stand up as you shoot to engage your legs.',
        'excessive_knee_bend': 'Mirror work: Practice your shooting stance in front of a mirror to find optimal knee bend.',
        'poor_wrist_snap': 'Bed shooting: Lie on your back and shoot straight up, focusing on aggressive wrist snap.',
        'guide_hand_thumb_flick': 'One-handed shooting: Practice with only your shooting hand to eliminate guide hand interference.',
        'guide_hand_under_ball': 'Tennis ball drill: Hold a tennis ball with your guide hand on the side while shooting with the other.',
        'guide_hand_on_top': 'Side placement drill: Practice positioning your guide hand on the side of the ball during form shooting.',
        'shot_timing_inefficient': 'Metronome shooting: Practice with consistent rhythm - catch, dip, and shoot with even timing.',
        'balance_issues': 'Eyes closed shooting: Practice form shooting with eyes closed to improve balance and proprioception.',
        'shot_lacks_fluidity': 'Slow motion shooting: Practice entire shooting motion in exaggerated slow motion.',
        'eye_tracking_poor': 'Target focus drill: Place a small target on the rim and maintain focus throughout your shot.',
        'follow_through_timing': 'Follow-through freeze: Hold your follow-through position for 3 seconds after each shot.'
    }
    return drills.get(flaw_key, 'Practice basic shooting fundamentals daily.')

def calculate_release_point_consistency(processed_frames_data, shot_phases):
    """Calculate average release point for consistency analysis"""
    release_points_x = []
    release_points_y = []
    
    # Find release phase frames
    release_phase = None
    for phase in shot_phases:
        if phase.name == 'Release':
            release_phase = phase
            break
    
    if not release_phase:
        return None
    
    # Collect release points from release phase
    for i, frame_data in enumerate(processed_frames_data):
        if release_phase.start_frame <= i <= release_phase.end_frame:
            if 'release_point_x' in frame_data.metrics and 'release_point_y' in frame_data.metrics:
                release_points_x.append(frame_data.metrics['release_point_x'])
                release_points_y.append(frame_data.metrics['release_point_y'])
    
    if release_points_x and release_points_y:
        avg_x = sum(release_points_x) / len(release_points_x)
        avg_y = sum(release_points_y) / len(release_points_y)
        # Store as function attribute for use in flaw detection
        detect_specific_flaw._avg_release_point = (avg_x, avg_y)
        return (avg_x, avg_y)
    
    return None

def calculate_shot_timing_metrics(processed_frames_data, shot_phases, fps):
    """Calculate shot timing and tempo metrics"""
    timing_metrics = {}
    
    # Find load/dip and release phases
    load_phase = None
    release_phase = None
    follow_through_phase = None
    
    for phase in shot_phases:
        if phase.name == 'Load/Dip':
            load_phase = phase
        elif phase.name == 'Release':
            release_phase = phase
        elif phase.name == 'Follow-Through':
            follow_through_phase = phase
    
    # Calculate load to release time
    if load_phase and release_phase:
        load_to_release_frames = release_phase.end_frame - load_phase.start_frame
        load_to_release_time_ms = (load_to_release_frames / fps) * 1000
        timing_metrics['shot_tempo'] = load_to_release_time_ms
        
        # Add tempo to relevant frames for flaw detection
        for i, frame_data in enumerate(processed_frames_data):
            if load_phase.start_frame <= i <= release_phase.end_frame:
                frame_data.metrics['shot_tempo'] = load_to_release_time_ms
    
    # Calculate follow-through duration
    if follow_through_phase:
        follow_through_duration_ms = ((follow_through_phase.end_frame - follow_through_phase.start_frame) / fps) * 1000
        timing_metrics['follow_through_duration'] = follow_through_duration_ms
        
        # Add to follow-through frames
        for i, frame_data in enumerate(processed_frames_data):
            if follow_through_phase.start_frame <= i <= follow_through_phase.end_frame:
                frame_data.metrics['follow_through_duration'] = follow_through_duration_ms
    
    return timing_metrics

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



def detect_shot_start_frame(cap, fps, max_detection_frames=300):
    """
    Analyze video to detect when the actual shooting motion begins.
    Uses multiple detection methods for robustness.
    Returns the frame number where the shot setup/loading phase starts.
    
    IMPROVED: Now adds buffer time before detected motion to capture setup phase.
    """
    logging.info("Starting intelligent shot detection...")
    
    # Method 1: MediaPipe pose-based detection (preferred when poses are detected)
    pose_based_result = detect_shot_start_pose_based(cap, fps, max_detection_frames)
    
    # Method 2: Motion-based detection (fallback for videos with poor pose detection)
    motion_based_result = detect_shot_start_motion_based(cap, fps, max_detection_frames)
    
    # Method 3: Frame difference analysis (most universal fallback)
    frame_diff_result = detect_shot_start_frame_diff(cap, fps, max_detection_frames)
    
    # Combine results using confidence-weighted approach
    results = [
        {'frame': pose_based_result['frame'], 'confidence': pose_based_result['confidence'], 'method': 'pose'},
        {'frame': motion_based_result['frame'], 'confidence': motion_based_result['confidence'], 'method': 'motion'},
        {'frame': frame_diff_result['frame'], 'confidence': frame_diff_result['confidence'], 'method': 'frame_diff'}
    ]
    
    # Select best result
    best_result = max(results, key=lambda x: x['confidence'])
    
    # 🎯 NEW: Add buffer time before detected shot start to capture setup phase
    # This ensures we don't miss the crucial Load/Dip phase that occurs before active motion
    buffer_frames = int(fps * 0.8)  # 0.8 second buffer (was causing phase issues)
    buffered_start_frame = max(0, best_result['frame'] - buffer_frames)
    
    logging.info(f"Shot detection methods - Pose: {pose_based_result['confidence']:.2f}, Motion: {motion_based_result['confidence']:.2f}, FrameDiff: {frame_diff_result['confidence']:.2f}")
    logging.info(f"Selected method: {best_result['method']} with confidence {best_result['confidence']:.2f}")
    logging.info(f"Raw detection: frame {best_result['frame']}, Buffered start: frame {buffered_start_frame} (added {buffer_frames} frame buffer)")
    logging.info(f"Shot detection complete. Starting analysis from frame {buffered_start_frame}")
    
    return buffered_start_frame

def detect_shot_start_pose_based(cap, fps, max_detection_frames):
    """Pose-based shot detection using MediaPipe landmarks."""
    wrist_positions = []
    knee_positions = []
    body_activity_scores = []
    valid_frames = []
    
    original_position = cap.get(cv2.CAP_PROP_POS_FRAMES)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    frame_idx = 0
    consecutive_good_poses = 0
    
    try:
        while frame_idx < max_detection_frames:
            ret, frame = cap.read()
            if not ret:
                break
                
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = get_pose_model().process(image)
            
            if results.pose_landmarks:
                consecutive_good_poses += 1
                landmarks = results.pose_landmarks.landmark
                
                try:
                    height, width = frame.shape[:2]
                    r_wrist = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_WRIST, width, height)
                    r_knee = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_KNEE, width, height)
                    r_shoulder = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_SHOULDER, width, height)
                    r_hip = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_HIP, width, height)
                    
                    wrist_positions.append(r_wrist)
                    knee_positions.append(r_knee)
                    valid_frames.append(frame_idx)
                    
                    # Calculate activity score
                    activity_score = 0
                    if len(wrist_positions) >= 2:
                        wrist_velocity = abs(r_wrist[1] - wrist_positions[-2][1])
                        activity_score += wrist_velocity * 2
                        
                        knee_velocity = abs(r_knee[1] - knee_positions[-2][1])
                        activity_score += knee_velocity
                    
                    if r_wrist[1] < r_shoulder[1]:
                        activity_score += 20
                    
                    knee_bend = abs(r_knee[1] - r_hip[1])
                    if knee_bend > 30:
                        activity_score += 10
                        
                    body_activity_scores.append(activity_score)
                    
                except Exception as e:
                    body_activity_scores.append(0)
            else:
                consecutive_good_poses = 0
                body_activity_scores.append(0)
                
            frame_idx += 1
            
            if len(body_activity_scores) >= 50 and consecutive_good_poses >= 10:
                break
    
    finally:
        cap.set(cv2.CAP_PROP_POS_FRAMES, original_position)
    
    if len(body_activity_scores) < 5:
        return {'frame': 0, 'confidence': 0.0}
    
    pose_count = sum(1 for score in body_activity_scores if score > 0)
    confidence = min(pose_count / len(body_activity_scores), 1.0)
    
    if confidence < 0.3:  # Not enough pose data
        return {'frame': 0, 'confidence': confidence}
    
    shot_start_frame = find_shot_start_from_activity(body_activity_scores, valid_frames, fps)
    return {'frame': shot_start_frame, 'confidence': confidence}

def detect_shot_start_motion_based(cap, fps, max_detection_frames):
    """Motion-based detection using optical flow."""
    original_position = cap.get(cv2.CAP_PROP_POS_FRAMES)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    prev_frame = None
    motion_scores = []
    frame_idx = 0
    
    try:
        while frame_idx < max_detection_frames:
            ret, frame = cap.read()
            if not ret:
                break
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_frame is not None:
                # Calculate optical flow
                flow = cv2.calcOpticalFlowPyrLK(
                    prev_frame, gray, 
                    np.array([[frame.shape[1]//2, frame.shape[0]//2]], dtype=np.float32).reshape(-1, 1, 2),
                    None
                )[0]
                
                # Calculate motion magnitude
                if flow is not None and len(flow) > 0:
                    motion_magnitude = np.linalg.norm(flow[0][0])
                    motion_scores.append(motion_magnitude)
                else:
                    motion_scores.append(0)
            else:
                motion_scores.append(0)
                
            prev_frame = gray
            frame_idx += 1
    
    finally:
        cap.set(cv2.CAP_PROP_POS_FRAMES, original_position)
    
    if len(motion_scores) < 10:
        return {'frame': 0, 'confidence': 0.0}
    
    # Find significant increase in motion
    baseline_motion = np.mean(motion_scores[:min(10, len(motion_scores))])
    motion_threshold = baseline_motion + np.std(motion_scores)
    
    for i, motion in enumerate(motion_scores):
        if motion > motion_threshold and motion > 2.0:  # Minimum motion threshold
            shot_start = max(0, i - int(fps * 0.5))  # Look back 0.5 seconds
            confidence = min(motion / (baseline_motion + 1), 1.0)
            return {'frame': shot_start, 'confidence': confidence * 0.7}  # Lower confidence than pose
    
    return {'frame': 0, 'confidence': 0.3}

def detect_shot_start_frame_diff(cap, fps, max_detection_frames):
    """Frame difference based detection - most universal method."""
    original_position = cap.get(cv2.CAP_PROP_POS_FRAMES)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    prev_frame = None
    diff_scores = []
    frame_idx = 0
    
    try:
        while frame_idx < max_detection_frames:
            ret, frame = cap.read()
            if not ret:
                break
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (5, 5), 0)  # Reduce noise
            
            if prev_frame is not None:
                # Calculate frame difference
                diff = cv2.absdiff(prev_frame, gray)
                diff_score = np.mean(diff)
                diff_scores.append(diff_score)
            else:
                diff_scores.append(0)
                
            prev_frame = gray
            frame_idx += 1
    
    finally:
        cap.set(cv2.CAP_PROP_POS_FRAMES, original_position)
    
    if len(diff_scores) < 10:
        return {'frame': 0, 'confidence': 0.5}
    
    # Smooth the difference scores
    window_size = max(3, int(fps * 0.2))  # 0.2 second window
    smoothed_scores = []
    for i in range(len(diff_scores) - window_size + 1):
        avg = np.mean(diff_scores[i:i + window_size])
        smoothed_scores.append(avg)
    
    if not smoothed_scores:
        return {'frame': 0, 'confidence': 0.5}
    
    # Find significant increase in activity
    baseline_diff = np.mean(smoothed_scores[:min(5, len(smoothed_scores))])
    activity_threshold = baseline_diff + np.std(smoothed_scores) * 1.5
    
    for i, diff_score in enumerate(smoothed_scores):
        if diff_score > activity_threshold and diff_score > baseline_diff * 1.8:
            # Look back to find the actual start
            lookback_frames = max(3, int(fps * 0.3))
            shot_start = max(0, i - lookback_frames)
            
            # Calculate confidence based on difference magnitude
            confidence = min((diff_score - baseline_diff) / (baseline_diff + 1), 1.0)
            confidence = max(0.4, confidence * 0.8)  # Ensure reasonable confidence range
            
            return {'frame': shot_start, 'confidence': confidence}
    
    # If no clear activity spike, look for gradual increase
    if len(smoothed_scores) >= 10:
        first_third = np.mean(smoothed_scores[:len(smoothed_scores)//3])
        last_third = np.mean(smoothed_scores[2*len(smoothed_scores)//3:])
        
        if last_third > first_third * 1.5:  # 50% increase in activity
            transition_point = len(smoothed_scores) // 2
            confidence = min((last_third - first_third) / (first_third + 1), 0.7)
            return {'frame': transition_point, 'confidence': confidence}
    
    return {'frame': 0, 'confidence': 0.5}

def find_shot_start_from_activity(activity_scores, valid_frames, fps):
    """
    Analyze activity scores to identify when shooting motion begins.
    Uses multiple heuristics to find the transition from idle/setup to active shooting.
    """
    if len(activity_scores) < 10:
        return 0
    
    # Method 1: Moving average analysis
    window_size = max(3, int(fps * 0.5))  # 0.5 second window
    moving_averages = []
    
    for i in range(len(activity_scores) - window_size + 1):
        avg = sum(activity_scores[i:i + window_size]) / window_size
        moving_averages.append(avg)
    
    if not moving_averages:
        return 0
    
    # Method 2: Find significant activity increase
    baseline_activity = sum(activity_scores[:min(10, len(activity_scores))]) / min(10, len(activity_scores))
    activity_threshold = baseline_activity + 15  # 15 points above baseline
    
    # Look for sustained activity above threshold
    for i, avg_activity in enumerate(moving_averages):
        if avg_activity > activity_threshold:
            # Found potential shot start, but look back for the actual beginning
            lookback_frames = max(5, int(fps * 0.3))  # Look back 0.3 seconds
            actual_start = max(0, i - lookback_frames)
            
            # Convert back to original frame numbers
            if actual_start < len(valid_frames):
                detected_frame = valid_frames[actual_start] if actual_start < len(valid_frames) else valid_frames[0]
                logging.info(f"Activity-based detection: baseline={baseline_activity:.1f}, threshold={activity_threshold:.1f}")
                logging.info(f"Shot activity detected at frame {i}, starting analysis from frame {detected_frame}")
                return detected_frame
    
    # Method 3: Gradient analysis - find steepest increase
    if len(moving_averages) >= 5:
        gradients = []
        for i in range(1, len(moving_averages)):
            gradient = moving_averages[i] - moving_averages[i-1]
            gradients.append(gradient)
        
        if gradients:
            max_gradient_idx = gradients.index(max(gradients))
            if gradients[max_gradient_idx] > 5:  # Significant increase
                # Look back from gradient peak
                lookback = max(3, int(fps * 0.2))
                gradient_based_start = max(0, max_gradient_idx - lookback)
                
                if gradient_based_start < len(valid_frames):
                    detected_frame = valid_frames[gradient_based_start]
                    logging.info(f"Gradient-based detection: max gradient {gradients[max_gradient_idx]:.1f} at frame {detected_frame}")
                    return detected_frame
    
    # Method 4: Percentile-based detection
    activity_75th = np.percentile(activity_scores, 75)
    if activity_75th > baseline_activity + 10:
        for i, score in enumerate(activity_scores):
            if score >= activity_75th:
                lookback = max(5, int(fps * 0.4))
                percentile_start = max(0, i - lookback)
                if percentile_start < len(valid_frames):
                    detected_frame = valid_frames[percentile_start]
                    logging.info(f"Percentile-based detection: 75th percentile {activity_75th:.1f}, starting from frame {detected_frame}")
                    return detected_frame
    
    # Fallback: If no clear shot detected, start from first significant activity
    for i, score in enumerate(activity_scores):
        if score > baseline_activity + 5:  # Lower threshold
            if i < len(valid_frames):
                fallback_frame = valid_frames[i]
                logging.info(f"Fallback detection: first activity above baseline at frame {fallback_frame}")
                return fallback_frame
    
    logging.info("No clear shot start detected, beginning analysis from start of video")
    return 0

def process_video_for_analysis(job: VideoAnalysisJob, ideal_shot_data):
    """
    Main function to process a single video analysis job.
    Now includes intelligent shot detection to start analysis when shooting motion begins.
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

        # Detect if video is in portrait mode (appears sideways)
        video_appears_sideways = height > width
        if video_appears_sideways:
            logging.info(f"📱 Portrait video detected ({width}x{height}) - video will appear sideways in results")
        else:
            logging.info(f"📺 Landscape video detected ({width}x{height}) - optimal for viewing")

        logging.info(f"Video properties - FPS: {fps}, Size: {width}x{height}, Frames: {total_frames}")
        
        # Validate video properties
        if fps <= 0 or width <= 0 or height <= 0 or total_frames <= 0:
            logging.error(f"Invalid video properties: FPS={fps}, Input size={width}x{height}, Frames={total_frames}")
            cap.release()
            return {
                'error': 'Invalid video format or corrupted video file'
            }
        
        # 🎯 INTELLIGENT SHOT DETECTION - Find when shooting motion actually begins
        shot_start_frame = detect_shot_start_frame(cap, fps, max_detection_frames=min(total_frames, 300))
        
        # Calculate effective video length from shot start - OPTIMIZED FOR STABILITY
        effective_total_frames = total_frames - shot_start_frame
        max_frames = min(effective_total_frames, 100)  # REDUCED: Process max 100 frames from shot start
        
        if shot_start_frame > 0:
            logging.info(f"🎯 Shot detected! Starting analysis from frame {shot_start_frame} (skipping {shot_start_frame} pre-shot frames)")
            logging.info(f"Will process {max_frames} frames from shot start (total effective: {effective_total_frames})")
            # Set video to start from detected shot start frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, shot_start_frame)
        else:
            logging.info(f"No pre-shot movement detected, processing from beginning")
            max_frames = min(total_frames, 100)
        
        if max_frames < 30:  # Ensure we have enough frames for meaningful analysis
            logging.warning(f"Very short effective video length ({max_frames} frames), results may be limited")

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
    
    # Process frames with timeout protection and memory management
    import time
    start_time = time.time()
    max_processing_time = 90  # Reduce to 90 seconds max processing time to avoid memory issues

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
                # Log progress every 50 frames to reduce logging overhead
                if current_frame_idx % 50 == 0:
                    elapsed = time.time() - start_time
                    logging.info(f"Processing frame {current_frame_idx}/{max_frames} ({elapsed:.1f}s elapsed)")
                    
                # Convert the BGR image to RGB
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                
                # Process with MediaPipe
                results = get_pose_model().process(image)
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
                        
                        # Get additional landmarks for enhanced analysis
                        l_shoulder = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.LEFT_SHOULDER, width, height)
                        l_elbow = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.LEFT_ELBOW, width, height)
                        l_wrist = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.LEFT_WRIST, width, height)
                        l_hip = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.LEFT_HIP, width, height)
                        nose = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.NOSE, width, height)
                        r_index = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_INDEX, width, height)
                        l_index = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.LEFT_INDEX, width, height)
                        r_thumb = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.RIGHT_THUMB, width, height)
                        l_thumb = get_landmark_coords(results.pose_landmarks, mp_pose.PoseLandmark.LEFT_THUMB, width, height)

                        # Calculate basic angles with error handling and validation
                        elbow_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
                        knee_angle = calculate_angle(r_hip, r_knee, r_ankle)
                        wrist_angle = calculate_angle(r_elbow, r_wrist, [r_wrist[0], r_wrist[1] - 50])
                        
                        # Only store metrics if they're within reasonable physiological ranges
                        if 60 <= elbow_angle <= 200:  # Reasonable elbow angle range
                            frame_metrics['elbow_angle'] = elbow_angle
                        if 60 <= knee_angle <= 180:   # Reasonable knee angle range
                            frame_metrics['knee_angle'] = knee_angle
                        if 20 <= wrist_angle <= 160:  # Reasonable wrist angle range
                            frame_metrics['wrist_angle_simplified'] = wrist_angle

                        # Enhanced metrics for guide hand analysis
                        try:
                            # Guide hand thumb angle (detect thumb flick) - with validation
                            if l_thumb and l_index and l_wrist:
                                guide_thumb_angle = calculate_angle(l_wrist, l_thumb, l_index)
                                # Only store if angle is meaningful (avoid noise from poor landmark detection)
                                if 30 <= guide_thumb_angle <= 150:  # Reasonable thumb angle range
                                    frame_metrics['guide_hand_thumb_angle'] = abs(guide_thumb_angle - 90)  # Deviation from neutral
                            
                            # Guide hand position analysis (should be on side of ball)
                            if l_wrist and r_wrist and l_elbow:
                                # Calculate relative position of guide hand (left) to shooting hand (right)
                                guide_dx = l_wrist[0] - r_wrist[0]  # Horizontal difference
                                guide_dy = l_wrist[1] - r_wrist[1]  # Vertical difference (negative = guide hand above)
                                
                                # Only analyze if hands are sufficiently separated
                                hand_distance = (guide_dx**2 + guide_dy**2)**0.5
                                if hand_distance > 30:
                                    # Calculate angle from shooting hand to guide hand
                                    guide_position_angle = np.degrees(np.arctan2(guide_dy, guide_dx))
                                    
                                    # Store both angle and vertical offset for comprehensive analysis
                                    frame_metrics['guide_hand_position_angle'] = guide_position_angle
                                    frame_metrics['guide_hand_vertical_offset'] = guide_dy
                                    frame_metrics['guide_hand_horizontal_offset'] = abs(guide_dx)
                        except:
                            pass
                        
                        # Enhanced elbow flare detection for front view
                        try:
                            if r_elbow and r_shoulder and l_shoulder:
                                # Calculate body centerline from shoulders
                                shoulder_midpoint = [(r_shoulder[0] + l_shoulder[0]) / 2, (r_shoulder[1] + l_shoulder[1]) / 2]
                                
                                # Measure lateral deviation of shooting elbow from body centerline
                                elbow_deviation_x = abs(r_elbow[0] - shoulder_midpoint[0])
                                shoulder_width = abs(r_shoulder[0] - l_shoulder[0])
                                
                                # Normalize elbow deviation as percentage of shoulder width
                                if shoulder_width > 0:
                                    elbow_flare_ratio = (elbow_deviation_x / shoulder_width) * 100
                                    # Store elbow flare ratio for front-view analysis
                                    frame_metrics['elbow_flare_front_view'] = elbow_flare_ratio
                                    # DEBUG: Log elbow flare ratios to understand what values we're getting
                                    if current_frame_idx % 10 == 0:  # Log every 10th frame to avoid spam
                                        logging.debug(f"Frame {current_frame_idx}: elbow_flare_ratio = {elbow_flare_ratio:.1f}%")
                                    
                                    # Also calculate elbow position angle relative to body centerline
                                    elbow_vector = [r_elbow[0] - shoulder_midpoint[0], r_elbow[1] - shoulder_midpoint[1]]
                                    elbow_lateral_angle = abs(np.degrees(np.arctan2(elbow_vector[0], elbow_vector[1])))
                                    frame_metrics['elbow_lateral_angle'] = elbow_lateral_angle
                                    # DEBUG: Log lateral angles too
                                    if current_frame_idx % 10 == 0:
                                        logging.debug(f"Frame {current_frame_idx}: elbow_lateral_angle = {elbow_lateral_angle:.1f}°")
                        except:
                            pass
                        
                        # Enhanced metrics for eye tracking/head stability - with validation
                        try:
                            if nose and r_shoulder and l_shoulder:
                                # Calculate head rotation based on nose position relative to shoulders
                                shoulder_midpoint = [(r_shoulder[0] + l_shoulder[0]) / 2, (r_shoulder[1] + l_shoulder[1]) / 2]
                                head_rotation_vector = [nose[0] - shoulder_midpoint[0], nose[1] - shoulder_midpoint[1]]
                                head_rotation_angle = np.degrees(np.arctan2(head_rotation_vector[1], head_rotation_vector[0]))
                                # Only store reasonable head rotation values
                                if -45 <= head_rotation_angle <= 45:  # Reasonable head rotation range
                                    frame_metrics['head_rotation_angle'] = head_rotation_angle
                        except:
                            pass
                        
                        # Body balance analysis - with validation
                        try:
                            if r_shoulder and l_shoulder and r_hip and l_hip:
                                # Calculate body lean angle
                                shoulder_vector = [r_shoulder[0] - l_shoulder[0], r_shoulder[1] - l_shoulder[1]]
                                hip_vector = [r_hip[0] - l_hip[0], r_hip[1] - l_hip[1]]
                                body_lean = np.degrees(np.arctan2(shoulder_vector[1], shoulder_vector[0]) - np.arctan2(hip_vector[1], hip_vector[0]))
                                # Only store reasonable lean values
                                if -30 <= body_lean <= 30:  # Reasonable body lean range
                                    frame_metrics['body_lean_angle'] = body_lean
                        except:
                            pass
                        
                        # 🎯 NEW FEATURE: Shoulder Alignment Detection (EASILY DISABLED)
                        if ENABLE_SHOULDER_ALIGNMENT_DETECTION:
                            try:
                                if r_shoulder and l_shoulder:
                                    # Calculate shoulder line angle relative to horizontal (camera frame)
                                    shoulder_vector = [l_shoulder[0] - r_shoulder[0], l_shoulder[1] - r_shoulder[1]]
                                    shoulder_line_angle = np.degrees(np.arctan2(shoulder_vector[1], shoulder_vector[0]))
                                    
                                    # Normalize to 0-180° range (absolute deviation from horizontal)
                                    shoulder_line_angle = abs(shoulder_line_angle)
                                    if shoulder_line_angle > 90:
                                        shoulder_line_angle = 180 - shoulder_line_angle
                                    
                                    # Store shoulder alignment metric (0° = perfectly square, higher = more angled)
                                    frame_metrics['shoulder_alignment_angle'] = shoulder_line_angle
                                    
                                    # Also calculate shoulder squaring relative to assumed basket direction
                                    # For front/angled views: basket is typically straight ahead (perpendicular to shoulders)
                                    # Ideal shoulder angle should be close to 0° (horizontal line)
                                    frame_metrics['shoulder_squaring_deviation'] = shoulder_line_angle
                                    
                                    logging.debug(f"Shoulder alignment: {shoulder_line_angle:.1f}° deviation from square")
                            except Exception as e:
                                logging.debug(f"Shoulder alignment calculation failed: {e}")
                                pass
                        
                        # Release point tracking for consistency analysis
                        try:
                            if r_wrist and r_elbow:
                                # Use wrist position as proxy for release point
                                frame_metrics['release_point_x'] = r_wrist[0]
                                frame_metrics['release_point_y'] = r_wrist[1]
                        except:
                            pass

                        # Calculate velocities and motion smoothness with bounds checking
                        if current_frame_idx > 0 and len(processed_frames_data) > 0:
                            prev_frame = processed_frames_data[-1]
                            if prev_frame.landmarks_raw and prev_frame.landmarks_raw.pose_landmarks:
                                prev_r_wrist_y = get_landmark_coords(prev_frame.landmarks_raw.pose_landmarks, mp_pose.PoseLandmark.RIGHT_WRIST, width, height)[1]
                                wrist_vertical_velocity = (prev_r_wrist_y - r_wrist[1]) * fps
                                frame_metrics['wrist_vertical_velocity'] = wrist_vertical_velocity
                                
                                # Calculate motion smoothness (velocity variance indicates jerkiness) - with validation
                                if 'wrist_vertical_velocity' in prev_frame.metrics:
                                    velocity_change = abs(wrist_vertical_velocity - prev_frame.metrics['wrist_vertical_velocity'])
                                    smoothness_value = velocity_change / (fps + 1)  # Normalize by framerate
                                    # Only store if the value is reasonable (prevent extreme outliers)
                                    if smoothness_value <= 5.0:  # Cap smoothness to prevent false positives
                                        frame_metrics['motion_smoothness'] = smoothness_value
                            else:
                                frame_metrics['wrist_vertical_velocity'] = 0
                                frame_metrics['motion_smoothness'] = 0
                        else:
                            frame_metrics['wrist_vertical_velocity'] = 0
                            frame_metrics['motion_smoothness'] = 0

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
            
            # Garbage collection every 20 frames for memory management (reduced frequency)
            if frames_processed % 20 == 0:
                gc.collect()

    except Exception as e:
        logging.error(f"Critical error during frame processing: {e}")
        return {
            'error': f'Critical error during video processing: {str(e)}'
        }
    finally:
        if cap:
            cap.release()
        # Force garbage collection after processing
        gc.collect()

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

        # Create phases with improved timing for complete shot analysis
        if max_knee_bend_frame != -1:
            # 🎯 IMPROVED: Load/Dip phase now starts much earlier to capture full setup
            # Load/Dip should capture the entire loading motion, not just the end
            load_start_frames = int(fps * 1.0) if fps > 0 else 30  # 1.0 second of load phase (was 15 frames)
            load_start = max(0, max_knee_bend_frame - load_start_frames)
            
            # Ensure minimum Load/Dip duration for meaningful analysis
            min_load_duration = int(fps * 0.5) if fps > 0 else 15  # Minimum 0.5 seconds
            if (max_knee_bend_frame - load_start) < min_load_duration:
                load_start = max(0, max_knee_bend_frame - min_load_duration)
            
            shot_phases.append(ShotPhase('Load/Dip', load_start, max_knee_bend_frame, max_knee_bend_frame))
            logging.info(f"Load/Dip phase: frames {load_start}-{max_knee_bend_frame} ({(max_knee_bend_frame-load_start)/fps:.2f}s duration)")
            
        if max_wrist_vel_frame != -1:
            # 🎯 IMPROVED: Shortened Release phase to focus on actual ball release period
            # Release phase should end shortly after peak wrist velocity, not extend into follow-through
            release_end = min(frames_processed - 1, max_wrist_vel_frame + 8)  # Reduced from 15 to 8 frames after release
            min_release_duration = int(fps * 0.3) if fps > 0 else 9  # Minimum 0.3 seconds
            release_start = max(max_wrist_vel_frame - 5, max_wrist_vel_frame - min_release_duration//2)
            
            shot_phases.append(ShotPhase('Release', release_start, release_end, max_wrist_vel_frame))
            logging.info(f"Release phase: frames {release_start}-{release_end} ({(release_end-release_start)/fps:.2f}s duration) - focuses on ball release period")
            
            # Create Follow-Through phase to capture wrist snap during and immediately after ball release
            # Follow-through should start during release (overlap) to capture the actual wrist snap motion
            follow_through_start = max_wrist_vel_frame - 2  # Start 2 frames before peak wrist velocity
            follow_through_end = min(frames_processed - 1, max_wrist_vel_frame + 12)  # Extended for complete follow-through
            if follow_through_start >= 0 and follow_through_start < frames_processed:
                shot_phases.append(ShotPhase('Follow-Through', follow_through_start, follow_through_end, max_wrist_vel_frame))
                logging.info(f"Follow-Through phase: frames {follow_through_start}-{follow_through_end} ({(follow_through_end-follow_through_start)/fps:.2f}s duration)")

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

        # Calculate advanced metrics for enhanced flaw detection
        logging.info("Calculating advanced shooting metrics...")
        calculate_release_point_consistency(processed_frames_data, shot_phases)
        timing_metrics = calculate_shot_timing_metrics(processed_frames_data, shot_phases, fps)
        logging.info(f"Calculated timing metrics: {timing_metrics}")

        # Enhanced flaw detection with new capabilities
        detailed_flaws = analyze_detailed_flaws(processed_frames_data, ideal_shot_data, shot_phases, fps, shot_start_frame)
        
        # Convert detailed flaws to feedback points for user-facing display
        logging.info(f"Converting {len(detailed_flaws)} detailed flaws to feedback points...")
        for flaw in detailed_flaws:
            # Create a comprehensive feedback point from each detailed flaw
            flaw_feedback = FeedbackPoint(
                frame_number=flaw['frame_number'],
                discrepancy=f"{flaw['flaw_type'].replace('_', ' ').title()}: {flaw['description']}",
                ideal_range=f"Severity: {flaw['severity']:.1f}/100",
                user_value=flaw['plain_language'],
                remedy_tips=flaw.get('coaching_tip', 'Work on this aspect of your shot mechanics.'),
                critical_landmarks=[]
            )
            # Add severity as an attribute for prioritization
            flaw_feedback.severity = flaw['severity']
            feedback_points.append(flaw_feedback)
            
        # Sort feedback points by severity (most severe first)
        feedback_points.sort(key=lambda x: getattr(x, 'severity', 0), reverse=True)
        logging.info(f"Total feedback points after adding detailed flaws: {len(feedback_points)}")
        
        # Add advanced fluidity analysis to enhance shot_lacks_fluidity detection
        logging.info("Performing advanced shot fluidity analysis...")
        fluidity_analysis = analyze_advanced_shot_fluidity(processed_frames_data, fps)
        logging.info(f"Fluidity analysis complete. Overall score: {fluidity_analysis['overall_fluidity_score']:.1f}")
        
        # ENHANCED: Always include detailed fluidity analysis in results for permanent visibility
        detailed_fluidity_analysis = {
            'overall_fluidity_score': fluidity_analysis['overall_fluidity_score'],
            'analysis_summary': f"Motion fluidity analysis complete. Overall score: {fluidity_analysis['overall_fluidity_score']:.1f}/100",
            'acceleration_spikes': [],
            'rhythm_breaks': [],
            'velocity_anomalies': [],
            'motion_quality_details': {}
        }
        
        # Extract detailed acceleration spikes for permanent display
        acceleration_spikes = fluidity_analysis['motion_flow_analysis'].get('acceleration_analysis', {}).get('acceleration_spikes', [])
        for spike in acceleration_spikes:
            detailed_fluidity_analysis['acceleration_spikes'].append({
                'frame': spike['frame'],
                'joint': spike['joint'],
                'severity': round(spike['severity'], 1),
                'description': f"Jerky movement detected in {spike['joint']} at frame {spike['frame']} (severity: {spike['severity']:.1f})"
            })
        
        # Extract detailed rhythm breaks for permanent display  
        rhythm_breaks = fluidity_analysis['motion_flow_analysis'].get('rhythm_analysis', {}).get('rhythm_breaks', [])
        for break_point in rhythm_breaks:
            detailed_fluidity_analysis['rhythm_breaks'].append({
                'frame': break_point['frame'],
                'type': break_point['type'],
                'severity': round(break_point['severity'], 1),
                'velocity_change': round(break_point['velocity_change'], 1),
                'description': f"Rhythm break: {break_point['type']} at frame {break_point['frame']} (severity: {break_point['severity']:.1f})"
            })
        
        # Extract velocity anomalies for permanent display
        velocity_analysis = fluidity_analysis['motion_flow_analysis'].get('velocity_analysis', {})
        abrupt_speed_changes = velocity_analysis.get('abrupt_speed_changes', [])
        for change in abrupt_speed_changes:
            detailed_fluidity_analysis['velocity_anomalies'].append({
                'frame': change['frame'],
                'joint': change['joint'],
                'severity': round(change['severity'], 1),
                'velocity_change': round(change['velocity_change'], 1),
                'description': f"Abrupt speed change in {change['joint']} at frame {change['frame']} (severity: {change['severity']:.1f})"
            })
        
        # Add motion quality summary
        detailed_fluidity_analysis['motion_quality_details'] = {
            'velocity_smoothness_score': velocity_analysis.get('velocity_smoothness_score', 100),
            'acceleration_smoothness_score': fluidity_analysis['motion_flow_analysis'].get('acceleration_analysis', {}).get('acceleration_smoothness_score', 100),
            'rhythm_consistency_score': fluidity_analysis['motion_flow_analysis'].get('rhythm_analysis', {}).get('rhythm_consistency_score', 100),
            'total_anomalies_detected': len(acceleration_spikes) + len(rhythm_breaks) + len(abrupt_speed_changes)
        }
        
        logging.info(f"Detailed fluidity analysis prepared: {len(acceleration_spikes)} acceleration spikes, {len(rhythm_breaks)} rhythm breaks, {len(abrupt_speed_changes)} velocity anomalies")
        
        # Enhance detailed_flaws with fluidity insights if fluidity issues detected
        if fluidity_analysis['overall_fluidity_score'] < 70:  # Threshold for concerning fluidity
            # Check if shot_lacks_fluidity was already detected
            fluidity_flaw_exists = any(flaw['flaw_type'] == 'shot_lacks_fluidity' for flaw in detailed_flaws)
            
            if not fluidity_flaw_exists:
                # Find the frame with the worst fluidity issue
                worst_fluidity_frame = None
                worst_severity = 0
                
                # Check for acceleration spikes
                for spike in acceleration_spikes:
                    if spike['severity'] > worst_severity:
                        worst_severity = spike['severity']
                        worst_fluidity_frame = spike['frame']
                
                # Check for rhythm breaks
                for break_point in rhythm_breaks:
                    if break_point['severity'] > worst_severity:
                        worst_severity = break_point['severity']
                        worst_fluidity_frame = break_point['frame']
                
                # If we found significant fluidity issues, add a flaw
                if worst_fluidity_frame is not None and worst_severity > 20:
                    fluidity_flaw = {
                        'flaw_type': 'shot_lacks_fluidity',
                        'description': 'Advanced analysis detected jerky or rushed shooting motion lacking smooth rhythm',
                        'frame_number': min(worst_fluidity_frame, len(processed_frames_data) - 1),
                        'severity': min(worst_severity, 100),
                        'remedy_tip': 'Focus on smooth, rhythmic motion from start to finish. Practice shooting in slow motion to develop muscle memory.',
                        'exercise_tip': 'Practice the complete shooting motion without a ball, focusing on fluid movement.',
                        'plain_language': f'Your shot motion shows jerky movement (fluidity score: {fluidity_analysis["overall_fluidity_score"]:.1f}/100). Work on smoother, more rhythmic motion from start to finish.',
                        'fluidity_details': {
                            'overall_score': fluidity_analysis['overall_fluidity_score'],
                            'acceleration_spikes': len(acceleration_spikes),
                            'rhythm_breaks': len(rhythm_breaks)
                        }
                    }
                    detailed_flaws.append(fluidity_flaw)
                    logging.info(f"Added enhanced fluidity flaw based on advanced analysis (score: {fluidity_analysis['overall_fluidity_score']:.1f})")

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

        # 🎯 IMPORTANT: Set video to start from the detected shot start frame for output generation
        if shot_start_frame > 0:
            cap_reprocess.set(cv2.CAP_PROP_POS_FRAMES, shot_start_frame)
            logging.info(f"🎯 Video output positioned to start from shot frame {shot_start_frame}")

        # --- Stage 1: Attempt to write video with cv2.VideoWriter (simplified for memory efficiency) ---
        # Optimize FPS for production deployment
        reduced_fps = max(fps / 10, 2)  # Further reduce FPS for production efficiency
        
        logging.info(f"Starting video processing with {len(detailed_flaws)} detected flaws")
        for i, flaw in enumerate(detailed_flaws[:5]):
            logging.info(f"Flaw {i+1}: {flaw['flaw_type']} at frame {flaw['frame_number']}")
        
        # Force use of ffmpeg for better video compatibility
        # OpenCV's H.264 encoder often creates incompatible videos
        logging.info("Using ffmpeg pipeline for maximum video compatibility")
        out = None  # Skip cv2.VideoWriter entirely
        
        frame_buffer = [] # To hold frames for ffmpeg fallback
        frame_for_still_capture = {}
        flaw_stills_captured = []
        current_frame_idx_output = 0
        original_frame_index = 0  # Track the frame index within the trimmed shot analysis
        
        # Pre-calculate flaw frame numbers for efficient lookup
        # Create mapping of absolute frame numbers to flaw data for efficient lookup during capture
        # EXCLUDE motion/timing-based flaws that represent the entire shot process, not specific moments
        motion_timing_flaws = {
            'shot_lacks_fluidity',
            'shot_timing_inefficient', 
            'follow_through_timing',
            'balance_issues'  # Balance issues are often about overall stability, not a specific moment
        }
        
        flaw_frames = {}
        for flaw in detailed_flaws[:5]:  # Capture up to 5 flaws instead of 3
            # Skip flaws that are about overall motion/timing rather than specific positions
            if flaw['flaw_type'] not in motion_timing_flaws:
                absolute_frame = flaw['frame_number']  # Now correctly contains absolute frame number
                flaw_frames[absolute_frame] = flaw
                logging.info(f"Will capture still for flaw: {flaw['flaw_type']} at frame {absolute_frame}")
            else:
                logging.info(f"Skipping still capture for motion/timing flaw: {flaw['flaw_type']} (applies to entire shot)")
        
        logging.info(f"Pre-calculated flaw frames for capture: {list(flaw_frames.keys())}")
        logging.info(f"Shot starts at frame: {shot_start_frame}")
        for flaw in detailed_flaws[:5]:
            relative_frame = flaw['frame_number'] - shot_start_frame
            if flaw['flaw_type'] not in motion_timing_flaws:
                logging.info(f"Flaw '{flaw['flaw_type']}': absolute_frame={flaw['frame_number']}, relative_frame={relative_frame}")
            else:
                logging.info(f"Motion/timing flaw '{flaw['flaw_type']}': documented in report only (no still needed)")
        
        # Process every 3rd frame in production to improve performance
        frame_skip = 3  # Increased from 2 to 3 for better performance

        while cap_reprocess.isOpened() and current_frame_idx_output < len(processed_frames_data):
            ret, frame = cap_reprocess.read()
            if not ret:
                break

            # Check for flaw stills efficiently (only if frame has a flaw)
            # FIXED: Use the actual flaw frame number from detection, not relative index
            actual_flaw_frame = shot_start_frame + original_frame_index
            if actual_flaw_frame in flaw_frames:
                try:
                    if original_frame_index < len(processed_frames_data) and processed_frames_data[original_frame_index].landmarks_raw:
                        results_to_draw = processed_frames_data[original_frame_index].landmarks_raw
                        flaw = flaw_frames[actual_flaw_frame]
                        
                        logging.info(f"FLAW STILL CAPTURE: {flaw['flaw_type']} at analysis_frame={original_frame_index}, video_frame={actual_flaw_frame}")
                        flaw_overlay_frame = create_flaw_overlay(frame.copy(), flaw, results_to_draw, width, height)
                        
                        # Apply orientation correction before saving the still
                        flaw_overlay_frame = detect_and_correct_orientation(flaw_overlay_frame)
                        
                        flaw_still_name = f"temp_{job.job_id}_flaw_{flaw['flaw_type']}_frame_{flaw['frame_number']}.png"
                        cv2.imwrite(flaw_still_name, flaw_overlay_frame)
                        flaw_stills_captured.append({
                            'file_path': flaw_still_name,
                            'flaw_data': flaw,
                            'frame_number': flaw['frame_number']
                        })
                        logging.info(f"Successfully saved flaw still: {flaw_still_name}")
                except Exception as e:
                    logging.warning(f"Error capturing flaw still at frame {original_frame_index}: {e}")

            # Skip frames to reduce processing load for video output
            if current_frame_idx_output % frame_skip != 0:
                current_frame_idx_output += 1
                original_frame_index += 1
                continue

            # --- Apply overlays to the frame ---
            try:
                if current_frame_idx_output < len(processed_frames_data) and processed_frames_data[current_frame_idx_output].landmarks_raw:
                    results_to_draw = processed_frames_data[current_frame_idx_output].landmarks_raw
                    mp_drawing.draw_landmarks(frame, results_to_draw.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                             mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                                             mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2))
                    
                    # Add phase overlay
                    for phase in shot_phases:
                        if current_frame_idx_output <= original_frame_index <= phase.end_frame and phase.start_frame <= original_frame_index:
                            cv2.putText(frame, f"Phase: {phase.name}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                            break
            except Exception as e:
                logging.warning(f"Error applying overlay to frame {current_frame_idx_output}: {e}")

            # --- Write frame or buffer it ---
            if out:
                # Apply orientation correction before writing to video
                corrected_frame = detect_and_correct_orientation(frame)
                out.write(corrected_frame)
            else:
                # Apply orientation correction before buffering
                corrected_frame = detect_and_correct_orientation(frame)
                frame_buffer.append(corrected_frame)
            
            current_frame_idx_output += 1
            original_frame_index += 1

        cap_reprocess.release()
        if out:
            out.release()
            video_generated = True
            logging.info(f"Successfully generated video with cv2.VideoWriter.")

        # --- Stage 2: Fallback to ffmpeg if cv2.VideoWriter failed ---
        if not video_generated and FFMPEG_AVAILABLE:
            logging.info("cv2.VideoWriter failed. Attempting to build video with ffmpeg.")
            frame_dir = save_frames_for_ffmpeg(frame_buffer, job.job_id)
            if create_video_from_frames_ffmpeg(frame_dir, output_video_path, reduced_fps):
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

    # --- Stage 3: Skip web format conversion to avoid memory issues ---
    # The ffmpeg web conversion is causing memory issues on Railway, so we'll skip it
    # The video should still be playable in most browsers
    if video_generated:
        logging.info("Skipping web format conversion to avoid memory issues on Railway platform.")
    else:
        logging.warning("No video was generated to convert.")
        output_video_path = None # Ensure no broken video path is returned

    # Generate PDF with enhanced error handling
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
        
        logging.info(f"Starting PDF generation for job {job.job_id}")
        logging.info(f"PDF data contains {len(detailed_flaws)} flaws, {len(shot_phases)} phases, {len(feedback_points)} feedback points")
        
        # Only generate PDF if we have meaningful analysis data
        if detailed_flaws or feedback_points or shot_phases:
            improvement_plan_pdf = generate_improvement_plan_pdf(pdf_results, job.job_id)
            
            if improvement_plan_pdf:
                logging.info(f"Successfully generated PDF: {improvement_plan_pdf}")
            else:
                logging.error(f"PDF generation failed for job {job.job_id} - returned None")
        else:
            logging.warning(f"Skipping PDF generation for job {job.job_id} - no meaningful analysis data available")
            
    except Exception as e:
        logging.error(f"PDF generation failed for job {job.job_id}: {e}")
        import traceback
        logging.error(f"PDF generation traceback: {traceback.format_exc()}")

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
    
    # Ensure detailed_fluidity_analysis exists (fallback if fluidity analysis failed)
    if 'detailed_fluidity_analysis' not in locals():
        detailed_fluidity_analysis = {
            'overall_fluidity_score': 85.0,
            'analysis_summary': "Fluidity analysis not available for this video",
            'acceleration_spikes': [],
            'rhythm_breaks': [],
            'velocity_anomalies': [],
            'motion_quality_details': {
                'velocity_smoothness_score': 85,
                'acceleration_smoothness_score': 85,
                'rhythm_consistency_score': 85,
                'total_anomalies_detected': 0
            }
        }
    
    # Return comprehensive results
    return {
        'analysis_report': None,  # Simplified for deployment
        'output_video_path': output_video_path,
        'feedback_stills': frame_for_still_capture,
        'flaw_stills': flaw_stills_captured,
        'detailed_flaws': detailed_flaws,
        'shot_phases': shot_phases,
        'feedback_points': feedback_points,
        'improvement_plan_pdf': improvement_plan_pdf,
        'video_appears_sideways': video_appears_sideways,
        'detailed_fluidity_analysis': detailed_fluidity_analysis  # ENHANCED: Permanent fluidity details
    }


def analyze_basketball_shot(video_path, job_id=None):
    """
    Main entry point for basketball shot analysis
    
    Args:
        video_path (str): Path to the video file to analyze
        job_id (str): Optional job ID for tracking
        
    Returns:
        dict: Complete analysis results
    """
    if job_id is None:
        job_id = f"analysis_{int(time.time())}"
    
    # Create a VideoAnalysisJob object
    job = VideoAnalysisJob(
        job_id=job_id,
        user_id="default_user",
        video_url=video_path,
        status="PROCESSING"
    )
    
    # Load ideal shot data
    ideal_shot_data = load_ideal_shot_data("ideal_shot_guide.json")
    
    # Process the video
    try:
        results = process_video_for_analysis(job, ideal_shot_data)
        job.status = "COMPLETED"
        logging.info(f"Analysis completed successfully for job {job_id}")
        return results
    except Exception as e:
        job.status = "FAILED"
        logging.error(f"Analysis failed for job {job_id}: {e}")
        return {
            'error': str(e),
            'job_id': job_id,
            'status': 'FAILED'
        }


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('basketball_analysis.log')
        ]
    )
    
    # Example usage
    import sys
    if len(sys.argv) > 1:
        video_file = sys.argv[1]
        if os.path.exists(video_file):
            logging.info(f"Starting analysis of: {video_file}")
            results = analyze_basketball_shot(video_file)
            
            if 'error' not in results:
                print(f"✅ Analysis completed successfully!")
                print(f"📊 Found {len(results.get('detailed_flaws', []))} shooting flaws")
                print(f"🎯 Identified {len(results.get('shot_phases', []))} shot phases")
                if results.get('output_video_path'):
                    print(f"🎬 Analysis video saved to: {results['output_video_path']}")
                if results.get('improvement_plan_pdf'):
                    print(f"📄 Improvement plan saved to: {results['improvement_plan_pdf']}")
            else:
                print(f"❌ Analysis failed: {results['error']}")
        else:
            print(f"❌ Video file not found: {video_file}")
    else:
        print("🏀 Basketball Shot Analysis Service")
        print("Usage: python basketball_analysis_service.py <video_file>")
