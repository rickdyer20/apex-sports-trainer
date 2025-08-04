#!/usr/bin/env python3
"""
Local Basketball Analysis Service Launcher
=========================================

This script launches the full basketball analysis service locally
with all computer vision capabilities.
"""

import subprocess
import sys
import os

def start_basketball_service():
    """Start the basketball analysis service locally"""
    
    print("🏀 Starting Basketball Analysis Service Locally")
    print("=" * 50)
    print()
    
    # Set environment variables for optimal performance
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = 'true'
    os.environ['MEDIAPIPE_DISABLE_GPU'] = '0'  # Enable GPU for local use
    
    print("🔧 Environment configured for local development")
    print("🖥️ Opening browser at: http://localhost:5000")
    print("⏹️ Press Ctrl+C to stop the service")
    print()
    
    try:
        # Run the basketball analysis service
        cmd = [
            "C:/Users/rickd/miniconda3/Scripts/conda.exe",
            "run", "-p", "c:\\Users\\rickd\\basketball_analyzer\\.conda",
            "--no-capture-output", "python", "basketball_analysis_service.py"
        ]
        
        print("🚀 Starting service...")
        result = subprocess.run(cmd, cwd=os.getcwd())
        
    except KeyboardInterrupt:
        print("\n\n👋 Basketball Analysis Service stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting service: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Check if conda environment exists")
        print("2. Verify basketball_analysis_service.py file exists")
        print("3. Check if all dependencies are installed")

if __name__ == "__main__":
    start_basketball_service()
