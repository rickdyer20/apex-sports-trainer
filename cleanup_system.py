#!/usr/bin/env python3
"""Clean up stuck processes and temporary files to fix video processing"""

import os
import sys
import psutil
import time
import shutil
from datetime import datetime, timedelta

print("=== Basketball Analysis System Cleanup ===")
print(f"Timestamp: {datetime.now()}")

# Kill old Python processes (older than 30 minutes)
print("\n--- Cleaning Up Old Processes ---")
current_pid = os.getpid()
killed_processes = 0

try:
    for proc in psutil.process_iter(['pid', 'name', 'create_time', 'cmdline']):
        if proc.info['pid'] == current_pid:
            continue  # Don't kill ourselves
            
        if 'python' in proc.info['name'].lower():
            process_age = time.time() - proc.info['create_time']
            age_minutes = process_age / 60
            
            # Check if it's related to basketball analysis
            cmdline = proc.info.get('cmdline', [])
            is_analysis_process = any('basketball' in str(arg).lower() or 'web_app' in str(arg).lower() 
                                    for arg in cmdline if arg)
            
            if age_minutes > 30 and is_analysis_process:
                try:
                    print(f"Killing stuck process PID {proc.info['pid']} (age: {age_minutes:.1f} min)")
                    proc_obj = psutil.Process(proc.info['pid'])
                    proc_obj.terminate()
                    proc_obj.wait(timeout=5)
                    killed_processes += 1
                except psutil.NoSuchProcess:
                    pass  # Process already ended
                except psutil.TimeoutExpired:
                    # Force kill if terminate didn't work
                    try:
                        proc_obj.kill()
                        killed_processes += 1
                    except:
                        pass
                except Exception as e:
                    print(f"Failed to kill process {proc.info['pid']}: {e}")
            elif age_minutes > 5:
                print(f"Found old process PID {proc.info['pid']} (age: {age_minutes:.1f} min) - keeping it")

    print(f"✅ Killed {killed_processes} stuck processes")
    
except Exception as e:
    print(f"❌ Process cleanup failed: {e}")

# Clean up temporary files and directories
print("\n--- Cleaning Up Temporary Files ---")
cleaned_files = 0
cleaned_dirs = 0
freed_space_mb = 0

try:
    for item in os.listdir('.'):
        if item.startswith('temp_'):
            item_path = os.path.join('.', item)
            
            try:
                # Get size before deletion
                if os.path.isfile(item_path):
                    size_mb = os.path.getsize(item_path) / (1024**2)
                    os.remove(item_path)
                    freed_space_mb += size_mb
                    cleaned_files += 1
                    print(f"Removed file: {item} ({size_mb:.1f} MB)")
                    
                elif os.path.isdir(item_path):
                    # Calculate directory size
                    dir_size = 0
                    for dirpath, dirnames, filenames in os.walk(item_path):
                        for filename in filenames:
                            filepath = os.path.join(dirpath, filename)
                            try:
                                dir_size += os.path.getsize(filepath)
                            except:
                                pass
                    
                    size_mb = dir_size / (1024**2)
                    shutil.rmtree(item_path)
                    freed_space_mb += size_mb
                    cleaned_dirs += 1
                    print(f"Removed directory: {item} ({size_mb:.1f} MB)")
                    
            except Exception as e:
                print(f"Failed to remove {item}: {e}")

    print(f"✅ Cleaned {cleaned_files} files and {cleaned_dirs} directories")
    print(f"✅ Freed {freed_space_mb:.1f} MB of disk space")
    
except Exception as e:
    print(f"❌ File cleanup failed: {e}")

# Clean up results folder of old files (keep only recent ones)
print("\n--- Cleaning Up Old Results ---")
results_cleaned = 0

try:
    if os.path.exists('results'):
        cutoff_time = datetime.now() - timedelta(hours=24)  # Keep files from last 24 hours
        
        for item in os.listdir('results'):
            item_path = os.path.join('results', item)
            
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(item_path))
                if file_time < cutoff_time:
                    if os.path.isfile(item_path):
                        size_mb = os.path.getsize(item_path) / (1024**2)
                        os.remove(item_path)
                        freed_space_mb += size_mb
                        results_cleaned += 1
                        print(f"Removed old result: {item} ({size_mb:.1f} MB)")
                        
            except Exception as e:
                print(f"Failed to clean result {item}: {e}")
                
        print(f"✅ Cleaned {results_cleaned} old result files")
        
except Exception as e:
    print(f"❌ Results cleanup failed: {e}")

# Optimize memory settings for future processing
print("\n--- Applying Memory Optimizations ---")

optimization_script = """
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
"""

try:
    with open('memory_optimization.py', 'w') as f:
        f.write(optimization_script)
    print("✅ Created memory optimization script")
except Exception as e:
    print(f"❌ Failed to create optimization script: {e}")

print("\n=== System Cleanup Complete ===")
print(f"Total space freed: {freed_space_mb:.1f} MB")
print("\nRecommendations:")
print("1. Restart the Flask web application to clear memory")
print("2. Test with a short video (< 10 seconds) first")
print("3. Monitor memory usage during processing")
print("4. Consider reducing frame processing limits if issues persist")

# Final system status
try:
    memory = psutil.virtual_memory()
    print(f"\nCurrent memory usage: {memory.percent:.1f}% ({memory.used / (1024**3):.1f} GB used)")
except:
    pass
