#!/usr/bin/env python3
"""Debug script to identify video processing issues"""

import os
import sys
import psutil
import subprocess
import time
from datetime import datetime

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=== Video Processing Diagnostics ===")
print(f"Timestamp: {datetime.now()}")

# Check system resources
print("\n--- System Resources ---")
try:
    memory = psutil.virtual_memory()
    print(f"Memory - Total: {memory.total / (1024**3):.2f} GB")
    print(f"Memory - Available: {memory.available / (1024**3):.2f} GB")
    print(f"Memory - Used: {memory.used / (1024**3):.2f} GB ({memory.percent:.1f}%)")
    
    disk = psutil.disk_usage('.')
    print(f"Disk - Total: {disk.total / (1024**3):.2f} GB")
    print(f"Disk - Free: {disk.free / (1024**3):.2f} GB")
    print(f"Disk - Used: {disk.used / (1024**3):.2f} GB")
    
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"CPU Usage: {cpu_percent:.1f}%")
    
except Exception as e:
    print(f"Resource check failed: {e}")

# Check Python processes
print("\n--- Python Processes ---")
try:
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'create_time']):
        if 'python' in proc.info['name'].lower():
            memory_mb = proc.info['memory_info'].rss / (1024**2)
            uptime = time.time() - proc.info['create_time']
            print(f"PID {proc.info['pid']}: {memory_mb:.1f} MB, uptime: {uptime/60:.1f} min")
except Exception as e:
    print(f"Process check failed: {e}")

# Check ffmpeg availability
print("\n--- FFmpeg Check ---")
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        print("✅ FFmpeg is available")
        # Get first line which contains version info
        first_line = result.stdout.split('\n')[0]
        print(f"   Version: {first_line}")
    else:
        print("❌ FFmpeg failed to run")
        print(f"   Error: {result.stderr}")
except subprocess.TimeoutExpired:
    print("❌ FFmpeg timeout")
except FileNotFoundError:
    print("❌ FFmpeg not found")
except Exception as e:
    print(f"❌ FFmpeg check failed: {e}")

# Check MediaPipe
print("\n--- MediaPipe Check ---")
try:
    import mediapipe as mp
    print("✅ MediaPipe imported successfully")
    
    # Test pose model initialization
    mp_pose = mp.solutions.pose
    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=0,  # Use simplest model
        enable_segmentation=False,
        min_detection_confidence=0.7
    ) as pose:
        print("✅ MediaPipe Pose model initialized")
        
except Exception as e:
    print(f"❌ MediaPipe failed: {e}")

# Check OpenCV
print("\n--- OpenCV Check ---")
try:
    import cv2
    print(f"✅ OpenCV version: {cv2.__version__}")
    
    # Test video codec availability
    fourcc_codes = ['mp4v', 'XVID', 'H264', 'X264']
    available_codecs = []
    
    for codec in fourcc_codes:
        try:
            fourcc = cv2.VideoWriter_fourcc(*codec)
            # Test by trying to create a VideoWriter (don't actually write)
            test_writer = cv2.VideoWriter('test.mp4', fourcc, 30, (640, 480))
            if test_writer.isOpened():
                available_codecs.append(codec)
                test_writer.release()
                # Clean up test file if created
                try:
                    os.remove('test.mp4')
                except:
                    pass
        except:
            pass
    
    if available_codecs:
        print(f"✅ Available codecs: {', '.join(available_codecs)}")
    else:
        print("❌ No video codecs available")
        
except Exception as e:
    print(f"❌ OpenCV failed: {e}")

# Check temporary files
print("\n--- Temporary Files ---")
try:
    temp_files = [f for f in os.listdir('.') if f.startswith('temp_')]
    if temp_files:
        print(f"Found {len(temp_files)} temporary files:")
        for f in temp_files[:10]:  # Show first 10
            try:
                stat = os.stat(f)
                size_mb = stat.st_size / (1024**2)
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                print(f"   {f}: {size_mb:.1f} MB, modified: {mod_time}")
            except:
                print(f"   {f}: (stat failed)")
        if len(temp_files) > 10:
            print(f"   ... and {len(temp_files) - 10} more")
    else:
        print("No temporary files found")
except Exception as e:
    print(f"Temp files check failed: {e}")

# Check import of basketball service
print("\n--- Basketball Analysis Service ---")
try:
    from basketball_analysis_service import process_video_for_analysis
    print("✅ Basketball analysis service imported")
    
    # Check if we can import data models
    from basketball_analysis_service import VideoAnalysisJob, FrameData, ShotPhase
    print("✅ Data models imported")
    
except Exception as e:
    print(f"❌ Basketball service import failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Diagnostics Complete ===")
print("Common issues and solutions:")
print("1. High memory usage: Reduce video resolution or frame count limits")
print("2. Missing FFmpeg: Install FFmpeg for video processing")
print("3. Codec issues: Use mp4v codec instead of H264")
print("4. Timeout issues: Increase timeout limits or reduce processing complexity")
print("5. Stuck processes: Kill old Python processes and restart")
