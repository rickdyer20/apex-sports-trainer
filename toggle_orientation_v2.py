#!/usr/bin/env python3
"""
Enhanced toggle script for orientation correction feature.
Usage: python toggle_orientation_v2.py [on|off|status]

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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("📱 Enhanced Orientation Correction Toggle v2.0")
        print("==============================================")
        print("Usage: python toggle_orientation_v2.py [on|off|status]")
        print("  on     - Enable enhanced orientation correction")
        print("  off    - Disable orientation correction") 
        print("  status - Check current status")
        print("\n🔧 Enhanced v2.0 features:")
        print("  • More sensitive aspect ratio detection")
        print("  • Phone recording format detection")
        print("  • Content-based analysis for edge cases")
        print("  • Automatic correction verification")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "status":
        check_current_status()
    elif command == "on":
        if toggle_orientation_correction(True):
            print("🔄 Enhanced orientation correction is now active")
            print("💡 Will detect and fix sideways videos using multiple methods:")
            print("   • Aspect ratio analysis")
            print("   • Common phone recording formats") 
            print("   • Content gradient analysis")
    elif command == "off":
        if toggle_orientation_correction(False):
            print("⏸️  Orientation correction is now disabled")
            print("💡 Videos and stills will be saved in their original orientation")
    else:
        print("❌ Invalid command. Use 'on', 'off', or 'status'")
        sys.exit(1)
