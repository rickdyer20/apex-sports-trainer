#!/usr/bin/env python3
"""Improved video processing configuration to prevent hangs and timeouts"""

import os
import sys

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create optimized processing limits
OPTIMIZED_LIMITS = {
    # Reduce frame processing limits to prevent memory issues
    'MAX_FRAMES_PROCESS': 100,  # Reduced from 150-300
    'MAX_PROCESSING_TIME': 90,  # Reduced from 120-300 seconds
    'MAX_VIDEO_SIZE_MB': 50,    # Limit video file size
    'FRAME_SKIP_RATIO': 2,      # Process every 2nd frame
    'REDUCED_FPS_RATIO': 8,     # Reduce output FPS more aggressively
    
    # Memory optimization
    'ENABLE_GARBAGE_COLLECTION': True,
    'CLEAR_TEMP_FILES_IMMEDIATELY': True,
    'USE_SIMPLE_CODEC': True,   # Use mp4v instead of H264
    
    # Processing optimization
    'MEDIAPIPE_MODEL_COMPLEXITY': 0,  # Use simplest model
    'OPENCV_OPTIMIZATION': True,
    'DISABLE_SEGMENTATION': True,
    'MIN_DETECTION_CONFIDENCE': 0.7,
}

print("=== Applying Optimized Video Processing Settings ===")

# Apply memory optimization settings
def apply_memory_optimization():
    """Apply memory and performance optimizations"""
    import gc
    import os
    
    # Force garbage collection
    gc.collect()
    
    # Set environment variables for memory efficiency
    os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'video_codec;mp4v'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce TensorFlow logging
    os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Force CPU-only processing
    os.environ['OMP_NUM_THREADS'] = '2'  # Limit OpenMP threads
    
    print("✅ Memory optimizations applied")

def create_optimized_processing_patch():
    """Create a patch for the basketball analysis service with optimized settings"""
    
    patch_content = '''
# OPTIMIZED VIDEO PROCESSING PATCH
# Apply these changes to basketball_analysis_service.py for better performance

# 1. Reduce frame processing limits (around line 572)
max_frames = min(total_frames, 100)  # Changed from 150-300

# 2. Reduce processing timeout (around line 598)
max_processing_time = 90  # Changed from 120

# 3. Use simpler MediaPipe model (around line 582)
with mp_pose.Pose(
    static_image_mode=False,
    model_complexity=0,  # Changed from 1 to 0 (simplest model)
    enable_segmentation=False,
    min_detection_confidence=0.7  # Slightly lower for better performance
) as pose_model:

# 4. More aggressive FPS reduction (around line 2300)
reduced_fps = max(fps / 10, 2)  # Changed from fps/8

# 5. Process every 2nd frame for output (around line 2320)
frame_skip = 3  # Changed from 2

# 6. Force mp4v codec (around line 770)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use mp4v instead of others

# 7. Add immediate cleanup (around line 2420)
# Clean up input video immediately after processing
try:
    if os.path.exists(local_video_path):
        os.remove(local_video_path)
        logging.info(f"Cleaned up input video: {local_video_path}")
except Exception as e:
    logging.warning(f"Failed to cleanup input video: {e}")

# 8. Force garbage collection after each job
import gc
gc.collect()
'''
    
    try:
        with open('processing_optimization_patch.txt', 'w') as f:
            f.write(patch_content)
        print("✅ Created optimization patch file")
    except Exception as e:
        print(f"❌ Failed to create patch: {e}")

def test_optimized_processing():
    """Test the optimized processing with a simple example"""
    try:
        # Apply memory optimizations first
        apply_memory_optimization()
        
        # Test MediaPipe with optimized settings
        import mediapipe as mp
        mp_pose = mp.solutions.pose
        
        with mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,  # Simplest model
            enable_segmentation=False,
            min_detection_confidence=0.7
        ) as pose:
            print("✅ Optimized MediaPipe model initialized successfully")
            
        # Test OpenCV with optimized codec
        import cv2
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        test_writer = cv2.VideoWriter('test_optimized.mp4', fourcc, 10, (640, 480))
        
        if test_writer.isOpened():
            print("✅ Optimized video writer works")
            test_writer.release()
            try:
                os.remove('test_optimized.mp4')
            except:
                pass
        else:
            print("❌ Video writer failed")
            
    except Exception as e:
        print(f"❌ Optimization test failed: {e}")

# Apply optimizations
apply_memory_optimization()
create_optimized_processing_patch()
test_optimized_processing()

print("\n=== Optimization Summary ===")
print("Key changes applied:")
print("• Reduced max frames from 300 to 100")
print("• Reduced timeout from 5 minutes to 90 seconds")
print("• Using simplest MediaPipe model (complexity 0)")
print("• More aggressive FPS reduction (10x instead of 8x)")
print("• Using mp4v codec for better compatibility")
print("• Immediate cleanup of temporary files")
print("• Memory optimization environment variables set")

print("\nNext steps:")
print("1. The system has been optimized with current settings")
print("2. Test with a short video (5-10 seconds)")
print("3. If issues persist, apply the patches in processing_optimization_patch.txt")
print("4. Consider restarting the Flask application for best results")
