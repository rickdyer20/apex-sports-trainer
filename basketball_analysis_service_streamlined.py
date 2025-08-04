#!/usr/bin/env python3
"""
Basketball Shot Analysis Service - Clean & Streamlined Version
Professional basketball shot form analysis using MediaPipe pose estimation
"""
import os
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

# Performance optimizations for TensorFlow
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

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

# --- Global Configuration ---
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
FFMPEG_AVAILABLE = shutil.which('ffmpeg') is not None

# Lazy initialization for pose model
pose_model = None

def get_pose_model():
    """Lazy initialization of MediaPipe pose model"""
    global pose_model
    if pose_model is None:
        pose_model = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,  # Faster model for production
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            enable_segmentation=False
        )
    return pose_model

# --- Data Classes ---
class VideoAnalysisJob:
    """Represents a video analysis request"""
    def __init__(self, job_id, user_id, video_url, status="PENDING"):
        self.job_id = job_id
        self.user_id = user_id
        self.video_url = video_url
        self.status = status
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.results_url = None

class FrameData:
    """Stores pose landmarks and metrics for a frame"""
    def __init__(self, frame_number, landmarks_raw, metrics):
        self.frame_number = frame_number
        self.landmarks_raw = landmarks_raw
        self.metrics = metrics

class ShotPhase:
    """Defines a shot phase with timing"""
    def __init__(self, name, start_frame, end_frame, key_moment_frame=None):
        self.name = name
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.key_moment_frame = key_moment_frame

class FeedbackPoint:
    """Details a specific form issue and remedy"""
    def __init__(self, frame_number, discrepancy, ideal_range, user_value, remedy_tips, critical_landmarks=None):
        self.frame_number = frame_number
        self.discrepancy = discrepancy
        self.ideal_range = ideal_range
        self.user_value = user_value
        self.remedy_tips = remedy_tips
        self.critical_landmarks = critical_landmarks

class AnalysisReport:
    """Complete analysis results"""
    def __init__(self, job_id, user_id, video_url, phases, feedback_points, overall_score=None):
        self.job_id = job_id
        self.user_id = user_id
        self.video_url = video_url
        self.phases = phases
        self.feedback_points = feedback_points
        self.overall_score = overall_score
        self.created_at = datetime.now()

# --- Utility Functions ---
def calculate_angle(p1, p2, p3):
    """Calculate angle between three 2D points (p2 is vertex)"""
    p1, p2, p3 = np.array(p1), np.array(p2), np.array(p3)
    
    v1, v2 = p1 - p2, p3 - p2
    dot_product = np.dot(v1, v2)
    magnitude_v1, magnitude_v2 = np.linalg.norm(v1), np.linalg.norm(v2)
    
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return 0
        
    angle_rad = np.arccos(np.clip(dot_product / (magnitude_v1 * magnitude_v2), -1.0, 1.0))
    return np.degrees(angle_rad)

def get_landmark_coords(landmarks, landmark_enum, width, height):
    """Extract pixel coordinates for a landmark"""
    lm = landmarks.landmark[landmark_enum.value]
    return [int(lm.x * width), int(lm.y * height)]

def load_ideal_shot_data(ideal_guide_path):
    """Load ideal shot metrics from JSON file"""
    logging.info(f"Loading ideal shot data from {ideal_guide_path}")
    
    try:
        with open(ideal_guide_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Ideal shot guide not found at {ideal_guide_path}. Using defaults.")
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

# --- Video Processing Functions ---
def save_frames_for_ffmpeg(frames, job_id):
    """Save frames to temporary directory for ffmpeg processing"""
    frame_dir = f"temp_{job_id}_frames"
    os.makedirs(frame_dir, exist_ok=True)
    for i, frame in enumerate(frames):
        cv2.imwrite(os.path.join(frame_dir, f"frame_{i:04d}.png"), frame)
    return frame_dir

def create_video_from_frames_ffmpeg(frame_dir, output_path, fps):
    """Create video from frames using ffmpeg with fallback options"""
    if not FFMPEG_AVAILABLE:
        logging.error("ffmpeg not found, cannot create video from frames.")
        return False
    
    # Multiple encoding options for compatibility
    ffmpeg_options = [
        # H.264 high compatibility
        ['ffmpeg', '-y', '-framerate', str(fps), '-i', os.path.join(frame_dir, 'frame_%04d.png'),
         '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-profile:v', 'baseline', 
         '-level', '3.0', '-preset', 'ultrafast', output_path],
        # Standard H.264
        ['ffmpeg', '-y', '-framerate', str(fps), '-i', os.path.join(frame_dir, 'frame_%04d.png'),
         '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'ultrafast', output_path],
        # MPEG-4 fallback
        ['ffmpeg', '-y', '-framerate', str(fps), '-i', os.path.join(frame_dir, 'frame_%04d.png'),
         '-c:v', 'mpeg4', '-pix_fmt', 'yuv420p', '-preset', 'ultrafast', output_path]
    ]
    
    for i, ffmpeg_cmd in enumerate(ffmpeg_options):
        try:
            logging.info(f"Attempting ffmpeg encoding option {i+1}")
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                logging.info(f"Successfully created video with option {i+1}: {output_path}")
                return True
            else:
                logging.warning(f"ffmpeg option {i+1} failed: {result.stderr}")
        except Exception as e:
            logging.warning(f"ffmpeg option {i+1} exception: {e}")
            continue
    
    logging.error("All ffmpeg encoding options failed")
    return False

def cleanup_temp_directory(frame_dir):
    """Clean up temporary frame directory"""
    try:
        shutil.rmtree(frame_dir)
        logging.debug(f"Cleaned up temporary directory: {frame_dir}")
    except Exception as e:
        logging.warning(f"Failed to remove temp directory {frame_dir}: {e}")

# --- Analysis Functions ---
def detect_camera_angle_and_visibility(processed_frames_data):
    """Analyze camera angle and determine visible body parts"""
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
    
    # Sample middle frames for stability
    sample_frames = good_frames[len(good_frames)//4:3*len(good_frames)//4] or good_frames
    
    left_visible_count = right_visible_count = face_profile_count = 0
    
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
            
        # Check face profile visibility
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
        # Left side view (showing right side)
        visibility_analysis['camera_angle'] = 'left_side_view'
        visibility_analysis['visible_features']['shooting_hand'] = True
        visibility_analysis['visible_features']['guide_hand'] = left_ratio > 0.2
        visibility_analysis['visible_features']['full_body_side'] = True
        visibility_analysis['confidence'] = right_ratio
    elif left_ratio > 0.7 and right_ratio < 0.3:
        # Right side view (showing left side)
        visibility_analysis['camera_angle'] = 'right_side_view'
        visibility_analysis['visible_features']['shooting_hand'] = right_ratio > 0.2
        visibility_analysis['visible_features']['guide_hand'] = True
        visibility_analysis['visible_features']['full_body_side'] = True
        visibility_analysis['confidence'] = left_ratio
    elif left_ratio > 0.5 and right_ratio > 0.5:
        # Front/back view
        visibility_analysis['camera_angle'] = 'front_view'
        visibility_analysis['visible_features']['shooting_hand'] = True
        visibility_analysis['visible_features']['guide_hand'] = True
        visibility_analysis['visible_features']['front_view'] = True
        visibility_analysis['confidence'] = min(left_ratio, right_ratio)
    else:
        # Angled view
        visibility_analysis['camera_angle'] = 'angled_view'
        visibility_analysis['visible_features']['shooting_hand'] = right_ratio > 0.4
        visibility_analysis['visible_features']['guide_hand'] = left_ratio > 0.4
        visibility_analysis['confidence'] = max(left_ratio, right_ratio)
    
    visibility_analysis['visible_features']['face_profile'] = face_ratio > 0.5
    
    return visibility_analysis

# This is a placeholder - the full file will continue with all analysis functions
# For now, I'll save this clean structure and continue building the rest

if __name__ == "__main__":
    # Main execution would go here
    logging.basicConfig(level=logging.INFO)
    logging.info("Basketball Analysis Service - Clean Version Ready")
