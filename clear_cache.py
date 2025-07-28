#!/usr/bin/env python3
"""
Basketball Analysis Cache Cleaner
Clears all cached results and temporary files to force fresh analysis
"""

import os
import glob
import json
import shutil
from datetime import datetime

def clear_all_caches():
    """Clear all types of caches in the basketball analysis system"""
    
    print("🧹 Basketball Analysis Cache Cleaner")
    print("=" * 50)
    
    cleared_items = []
    
    # 1. Clear JSON result cache files
    print("\n📁 Clearing JSON result cache files...")
    jobs_dir = 'jobs'
    if os.path.exists(jobs_dir):
        for file_pattern in ['*_results.json', '*results*.json']:
            cache_files = glob.glob(os.path.join(jobs_dir, file_pattern))
            for cache_file in cache_files:
                try:
                    os.remove(cache_file)
                    cleared_items.append(f"JSON Cache: {cache_file}")
                    print(f"  ✅ Removed: {cache_file}")
                except Exception as e:
                    print(f"  ❌ Failed to remove {cache_file}: {e}")
    
    # 2. Clear temporary video files
    print("\n🎬 Clearing temporary video files...")
    temp_patterns = [
        'temp_*.mp4',
        'temp_*_raw.mp4', 
        'temp_*_analyzed.mp4',
        'temp_*_web_analyzed.mp4'
    ]
    
    for pattern in temp_patterns:
        temp_files = glob.glob(pattern)
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
                cleared_items.append(f"Temp Video: {temp_file}")
                print(f"  ✅ Removed: {temp_file}")
            except Exception as e:
                print(f"  ❌ Failed to remove {temp_file}: {e}")
    
    # 3. Clear temporary image files (flaw stills)
    print("\n🖼️ Clearing temporary image files...")
    image_patterns = [
        'temp_*.png',
        'temp_*_flaw_*.png',
        'temp_*_still_*.png'
    ]
    
    for pattern in image_patterns:
        image_files = glob.glob(pattern)
        for image_file in image_files:
            try:
                os.remove(image_file)
                cleared_items.append(f"Temp Image: {image_file}")
                print(f"  ✅ Removed: {image_file}")
            except Exception as e:
                print(f"  ❌ Failed to remove {image_file}: {e}")
    
    # 4. Clear temporary frame directories
    print("\n📂 Clearing temporary frame directories...")
    frame_dirs = glob.glob('temp_*_frames')
    for frame_dir in frame_dirs:
        try:
            shutil.rmtree(frame_dir)
            cleared_items.append(f"Frame Dir: {frame_dir}")
            print(f"  ✅ Removed directory: {frame_dir}")
        except Exception as e:
            print(f"  ❌ Failed to remove {frame_dir}: {e}")
    
    # 5. Clear Python cache
    print("\n🐍 Clearing Python cache...")
    pycache_dirs = []
    for root, dirs, files in os.walk('.'):
        for d in dirs:
            if d == '__pycache__':
                pycache_dirs.append(os.path.join(root, d))
    
    for pycache_dir in pycache_dirs:
        try:
            shutil.rmtree(pycache_dir)
            cleared_items.append(f"Python Cache: {pycache_dir}")
            print(f"  ✅ Removed: {pycache_dir}")
        except Exception as e:
            print(f"  ❌ Failed to remove {pycache_dir}: {e}")
    
    # 6. Clear any uploaded videos (optional - be careful!)
    print("\n📤 Checking for uploaded videos to clear...")
    uploads_dir = 'uploads'
    if os.path.exists(uploads_dir):
        upload_files = glob.glob(os.path.join(uploads_dir, '*'))
        if upload_files:
            print(f"  ⚠️  Found {len(upload_files)} uploaded files")
            response = input("  🤔 Clear uploaded videos too? (y/N): ").strip().lower()
            if response == 'y':
                for upload_file in upload_files:
                    try:
                        os.remove(upload_file)
                        cleared_items.append(f"Upload: {upload_file}")
                        print(f"  ✅ Removed: {upload_file}")
                    except Exception as e:
                        print(f"  ❌ Failed to remove {upload_file}: {e}")
            else:
                print("  ⏭️  Skipping uploaded files")
    
    # Summary
    print(f"\n🎯 Cache clearing complete!")
    print(f"📊 Total items cleared: {len(cleared_items)}")
    
    if cleared_items:
        print("\n📋 Items cleared:")
        for item in cleared_items[-10:]:  # Show last 10 items
            print(f"  • {item}")
        if len(cleared_items) > 10:
            print(f"  ... and {len(cleared_items) - 10} more items")
    
    print(f"\n✨ All caches cleared! Your next video analysis will be completely fresh.")
    print(f"🔄 Remember to restart your web server if it's currently running.")
    
    return len(cleared_items)

if __name__ == "__main__":
    try:
        cleared_count = clear_all_caches()
        print(f"\n🏁 Finished! Cleared {cleared_count} cached items.")
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Cache clearing interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during cache clearing: {e}")
