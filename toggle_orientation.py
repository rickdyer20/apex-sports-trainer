#!/usr/bin/env python3
"""
Easy toggle script for orientation correction feature.
Usage: python toggle_orientation.py [on|off|status]

Version 2.0 - Enhanced orientation detection with multiple heuristics
"""

import sys
import re

def toggle_orientation_correction(enable=True):
    """Toggle the orientation correction feature on or off"""
    file_path = "basketball_analysis_service.py"
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find and replace the ENABLE_ORIENTATION_CORRECTION flag
        pattern = r'ENABLE_ORIENTATION_CORRECTION = (True|False)'
        new_value = 'True' if enable else 'False'
        replacement = f'ENABLE_ORIENTATION_CORRECTION = {new_value}'
        
        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content)
            
            with open(file_path, 'w') as f:
                f.write(new_content)
            
            status = "ENABLED" if enable else "DISABLED"
            print(f"✅ Orientation correction {status}")
            return True
        else:
            print("❌ Could not find ENABLE_ORIENTATION_CORRECTION flag in file")
            return False
            
    except FileNotFoundError:
        print(f"❌ File {file_path} not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_current_status():
    """Check current orientation correction status"""
    try:
        with open("basketball_analysis_service.py", 'r') as f:
            content = f.read()
        
        match = re.search(r'ENABLE_ORIENTATION_CORRECTION = (True|False)', content)
        if match:
            current_status = match.group(1)
            status_text = "ENABLED" if current_status == 'True' else "DISABLED"
            print(f"📊 Current status: Orientation correction is {status_text}")
            
            # Show enhanced detection info
            if current_status == 'True':
                print("🔍 Enhanced detection features active:")
                print("   • Aspect ratio analysis (more sensitive)")
                print("   • Phone recording detection (1080x1920, 720x1280)")
                print("   • Content-based gradient analysis")
                print("   • Automatic verification of corrections")
            
            return current_status == 'True'
        else:
            print("❓ Could not determine current status")
            return None
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return None
            )
            print("✅ Orientation correction ENABLED")
        else:
            # Disable the feature
            content = re.sub(
                r'ENABLE_ORIENTATION_CORRECTION = True',
                'ENABLE_ORIENTATION_CORRECTION = False',
                content
            )
            print("❌ Orientation correction DISABLED")
        
        with open(file_path, 'w') as f:
            f.write(content)
            
        print(f"Updated {file_path}")
        
    except Exception as e:
        print(f"Error updating orientation correction setting: {e}")

if __name__ == "__main__":
    import sys
    
    print("Basketball Analysis - Orientation Correction Toggle")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1].lower() in ['off', 'disable', 'false', '0']:
            toggle_orientation_correction(False)
        elif sys.argv[1].lower() in ['on', 'enable', 'true', '1']:
            toggle_orientation_correction(True)
        else:
            print("Usage: python toggle_orientation.py [on|off]")
    else:
        print("Current setting: Checking...")
        with open("basketball_analysis_service.py", 'r') as f:
            content = f.read()
            if 'ENABLE_ORIENTATION_CORRECTION = True' in content:
                print("Current setting: ENABLED")
                print("\nTo disable: python toggle_orientation.py off")
            elif 'ENABLE_ORIENTATION_CORRECTION = False' in content:
                print("Current setting: DISABLED") 
                print("\nTo enable: python toggle_orientation.py on")
            else:
                print("Could not determine current setting")
