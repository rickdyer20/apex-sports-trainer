#!/usr/bin/env python3
"""
Local Development Setup for Basketball Analysis Service
Install dependencies and prepare for local testing
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies for local development"""
    print("📦 INSTALLING DEPENDENCIES FOR LOCAL TESTING...")
    
    # Use the cloud requirements as they have all features
    requirements_file = "requirements_gcloud.txt"
    
    if not os.path.exists(requirements_file):
        print(f"❌ {requirements_file} not found")
        return False
    
    try:
        print(f"Installing from {requirements_file}...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def verify_installation():
    """Verify that key packages are installed"""
    print("\n🔍 VERIFYING INSTALLATION...")
    
    packages_to_check = [
        ("flask", "Flask"),
        ("cv2", "OpenCV"),
        ("mediapipe", "MediaPipe"), 
        ("numpy", "NumPy"),
        ("reportlab", "ReportLab"),
        ("psutil", "psutil")
    ]
    
    all_good = True
    for package, name in packages_to_check:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - Failed to import")
            all_good = False
    
    return all_good

def main():
    """Main setup function"""
    print("🏀 BASKETBALL ANALYSIS SERVICE - LOCAL SETUP")
    print("=" * 50)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        return False
    
    # Verify installation
    if not verify_installation():
        print("❌ Setup failed during verification")
        return False
    
    print("\n🎉 LOCAL SETUP COMPLETE!")
    print("\n📋 NEXT STEPS:")
    print("1. Run local test: python local_test.py")
    print("2. Start server: python local_test.py --server")
    print("3. Test health: python local_test.py --health")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
