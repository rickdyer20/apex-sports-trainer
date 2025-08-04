#!/usr/bin/env python3
"""
Render Deployment Checklist and Status
"""

import os
import json

def check_file_exists(filepath, description):
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {'Found' if exists else 'Missing'}")
    return exists

def check_file_content(filepath, required_content, description):
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
                has_content = required_content in content
                status = "✅" if has_content else "⚠️"
                print(f"{status} {description}: {'Present' if has_content else 'Missing'}")
                return has_content
        else:
            print(f"❌ {description}: File not found")
            return False
    except Exception as e:
        print(f"❌ {description}: Error reading file - {e}")
        return False

print("🚀 RENDER DEPLOYMENT READINESS CHECK")
print("=" * 50)

print("\n📋 REQUIRED FILES:")
files_ok = 0
files_ok += check_file_exists("requirements.txt", "Dependencies file")
files_ok += check_file_exists("Procfile", "Process file") 
files_ok += check_file_exists("wsgi.py", "WSGI entry point")
files_ok += check_file_exists("web_app.py", "Flask application")
files_ok += check_file_exists("basketball_analysis_service.py", "Analysis service")

print(f"\n📁 FILES STATUS: {files_ok}/5 required files present")

print("\n🔧 CONFIGURATION CHECKS:")
config_ok = 0
config_ok += check_file_content("requirements.txt", "gunicorn", "Gunicorn server")
config_ok += check_file_content("requirements.txt", "opencv-python-headless", "Headless OpenCV (Render-optimized)")
config_ok += check_file_content("web_app.py", "/health", "Health check endpoint")
config_ok += check_file_content("Procfile", "--timeout 120", "Extended timeout")
config_ok += check_file_content("basketball_analysis_service.py", "TF_ENABLE_ONEDNN_OPTS", "TensorFlow optimizations")

print(f"\n⚙️  CONFIGURATION STATUS: {config_ok}/5 optimizations applied")

print("\n⚠️  RENDER-SPECIFIC CONCERNS:")
concerns = [
    "• Ephemeral storage - uploaded files will be lost on restart",
    "• Memory limits - OpenCV/MediaPipe are memory-intensive", 
    "• Cold starts - MediaPipe initialization can be slow",
    "• Request timeouts - video processing may exceed limits",
    "• No persistent database - using in-memory storage"
]

for concern in concerns:
    print(f"   {concern}")

print("\n💡 DEPLOYMENT RECOMMENDATIONS:")
recs = [
    "1. Test with small video files first (<10MB)",
    "2. Monitor memory usage via /health endpoint",
    "3. Consider upgrading to paid plan for more resources",
    "4. Implement external storage (S3/GCS) for file persistence",
    "5. Add async job processing for longer videos",
    "6. Set up database for job persistence",
    "7. Configure CDN for static assets"
]

for rec in recs:
    print(f"   {rec}")

total_readiness = ((files_ok/5) + (config_ok/5)) * 50
print(f"\n🎯 RENDER READINESS SCORE: {total_readiness:.0f}%")

if total_readiness >= 80:
    print("✅ READY FOR DEPLOYMENT - Good to go!")
elif total_readiness >= 60:
    print("⚠️  MOSTLY READY - Minor issues to address")
else:
    print("❌ NOT READY - Critical issues need fixing")

print("\n🚀 NEXT STEPS:")
if total_readiness >= 70:
    print("   1. Connect GitHub repo to Render")
    print("   2. Set environment variables in Render dashboard")
    print("   3. Deploy and monitor /health endpoint")
    print("   4. Test with sample video files")
else:
    print("   1. Fix missing files and configurations above")
    print("   2. Re-run this readiness check")
    print("   3. Then proceed with deployment")

print("\n" + "=" * 50)
