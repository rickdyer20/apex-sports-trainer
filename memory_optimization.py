
# Memory optimization settings
import gc
import os

# Force garbage collection
gc.collect()

# Set environment variables for memory efficiency
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'video_codec;h264_cuvid'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce TensorFlow logging
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Force CPU-only processing

print("Memory optimizations applied")
