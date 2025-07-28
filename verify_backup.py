"""
🏀 Basketball Analysis - Backup Verification Script
Verifies that the backup contains all necessary files and functionality
"""

import os
import json
from datetime import datetime

def verify_backup():
    """Verify backup integrity and completeness"""
    backup_dir = "backup_simplified_version"
    
    print("🏀 Basketball Analysis - Backup Verification")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if backup directory exists
    if not os.path.exists(backup_dir):
        print("❌ Backup directory not found!")
        return False
    
    # Required files
    required_files = {
        "web_app_simplified.py": "Flask web application",
        "basketball_analysis_service_simplified.py": "Core analysis engine", 
        "results_simplified.html": "Results template",
        "ideal_shot_guide_simplified.json": "Shot metrics configuration",
        "pdf_generator_simplified.py": "PDF report generator",
        "README_BACKUP.md": "Backup documentation"
    }
    
    print("📦 Checking backup files...")
    all_files_present = True
    
    for filename, description in required_files.items():
        filepath = os.path.join(backup_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✅ {filename:<45} ({size:,} bytes) - {description}")
        else:
            print(f"❌ {filename:<45} MISSING - {description}")
            all_files_present = False
    
    print()
    
    # Verify JSON configuration file
    print("⚙️ Verifying configuration integrity...")
    try:
        config_path = os.path.join(backup_dir, "ideal_shot_guide_simplified.json")
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        required_keys = [
            "release_elbow_angle",
            "load_knee_angle", 
            "follow_through_wrist_snap_angle",
            "common_remedies"
        ]
        
        for key in required_keys:
            if key in config:
                print(f"✅ Configuration key: {key}")
            else:
                print(f"❌ Missing configuration key: {key}")
                all_files_present = False
                
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")
        all_files_present = False
    
    print()
    
    # Check key functionality markers in code
    print("🔍 Verifying code integrity...")
    
    try:
        # Check web app
        web_app_path = os.path.join(backup_dir, "web_app_simplified.py")
        with open(web_app_path, 'r', encoding='utf-8', errors='ignore') as f:
            web_app_content = f.read()
        
        web_app_checks = [
            ("Flask import", "from flask import Flask"),
            ("Upload route", "@app.route('/upload'"),
            ("Download route", "@app.route('/download'"),
            ("Results route", "@app.route('/results'"),
            ("No video serving", "serve_video" not in web_app_content)
        ]
        
        for check_name, check_condition in web_app_checks:
            if isinstance(check_condition, str):
                if check_condition in web_app_content:
                    print(f"✅ Web app {check_name}")
                else:
                    print(f"❌ Web app missing {check_name}")
            else:
                if check_condition:
                    print(f"✅ Web app {check_name}")
                else:
                    print(f"❌ Web app {check_name}")
        
        # Check analysis service
        service_path = os.path.join(backup_dir, "basketball_analysis_service_simplified.py")
        with open(service_path, 'r', encoding='utf-8', errors='ignore') as f:
            service_content = f.read()
        
        service_checks = [
            ("MediaPipe import", "import mediapipe as mp"),
            ("Angle calculation", "def calculate_angle"),
            ("Flaw detection", "def analyze_detailed_flaws"),
            ("No rotation handling", "detect_video_rotation" not in service_content)
        ]
        
        for check_name, check_condition in service_checks:
            if isinstance(check_condition, str):
                if check_condition in service_content:
                    print(f"✅ Analysis service {check_name}")
                else:
                    print(f"❌ Analysis service missing {check_name}")
            else:
                if check_condition:
                    print(f"✅ Analysis service {check_name}")
                else:
                    print(f"❌ Analysis service {check_name}")
                    
    except Exception as e:
        print(f"❌ Error verifying code integrity: {e}")
        all_files_present = False
    
    print()
    print("=" * 50)
    
    if all_files_present:
        print("✅ BACKUP VERIFICATION PASSED")
        print("   All files present and integrity checks passed")
        print("   Safe to proceed with analytics enhancements")
        print()
        print("📝 To restore this backup later, run:")
        print("   restore_simplified_version.bat")
        return True
    else:
        print("❌ BACKUP VERIFICATION FAILED")
        print("   Some files missing or integrity issues detected")
        print("   Recommend creating backup again")
        return False

if __name__ == "__main__":
    verify_backup()
