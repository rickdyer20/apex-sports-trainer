#!/usr/bin/env python3
"""
Quick Deployment Checklist
Run this script to verify deployment readiness
"""

import os
import subprocess
import json

def check_file_exists(filename, description):
    exists = os.path.exists(filename)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filename}")
    return exists

def check_git_status():
    try:
        # Check if git repo is initialized
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository initialized")
            
            # Check for uncommitted changes
            if "nothing to commit" in result.stdout:
                print("✅ All changes committed")
                return True
            else:
                print("⚠️  Uncommitted changes detected")
                print("   Run: git add . && git commit -m 'Deploy ready'")
                return False
        else:
            print("❌ Git repository not initialized")
            return False
    except FileNotFoundError:
        print("❌ Git not installed or not in PATH")
        return False

def main():
    print("🚀 RENDER DEPLOYMENT READINESS CHECK")
    print("=" * 50)
    
    # Check essential files
    print("\n📁 ESSENTIAL FILES:")
    files_ok = 0
    files_ok += check_file_exists("basketball_analysis_service.py", "Main service")
    files_ok += check_file_exists("web_app.py", "Flask app")
    files_ok += check_file_exists("wsgi.py", "WSGI entry point")
    files_ok += check_file_exists("requirements.txt", "Dependencies")
    files_ok += check_file_exists("Procfile", "Process config")
    
    # Check Procfile content
    print("\n⚙️  CONFIGURATION:")
    try:
        with open("Procfile", "r") as f:
            procfile_content = f.read().strip()
            if "gunicorn" in procfile_content and "--workers 2" in procfile_content:
                print("✅ Procfile optimized for Starter Plan")
            else:
                print("⚠️  Procfile may need optimization")
                print(f"   Current: {procfile_content}")
    except FileNotFoundError:
        print("❌ Procfile missing")
    
    # Check requirements.txt
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read()
            if "opencv-python-headless" in requirements:
                print("✅ OpenCV headless version configured")
            elif "opencv-python" in requirements:
                print("⚠️  Consider using opencv-python-headless for Render")
            
            if "gunicorn" in requirements:
                print("✅ Gunicorn included in requirements")
            else:
                print("❌ Gunicorn missing from requirements.txt")
    except FileNotFoundError:
        print("❌ requirements.txt missing")
    
    # Check Git status
    print("\n📋 GIT STATUS:")
    git_ok = check_git_status()
    
    # Overall readiness
    print("\n🎯 DEPLOYMENT READINESS:")
    total_score = (files_ok / 5) * 50 + (git_ok * 50)
    
    if total_score >= 90:
        print(f"✅ READY TO DEPLOY! Score: {total_score}%")
        print("\n🚀 NEXT STEPS:")
        print("   1. Go to render.com and create account")
        print("   2. Create new Web Service")
        print("   3. Connect your GitHub repository")
        print("   4. Select Starter Plan ($7/month)")
        print("   5. Set environment variables as shown in .env.starter")
        print("   6. Deploy and monitor /health endpoint")
    elif total_score >= 70:
        print(f"⚠️  MOSTLY READY Score: {total_score}%")
        print("   Fix the issues above before deploying")
    else:
        print(f"❌ NOT READY Score: {total_score}%")
        print("   Address critical issues before proceeding")
    
    print("\n" + "=" * 50)
    print("📖 See DEPLOYMENT_GUIDE.md for complete instructions")

if __name__ == "__main__":
    main()
