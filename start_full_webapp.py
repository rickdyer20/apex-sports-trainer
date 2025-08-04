#!/usr/bin/env python3
"""
🏀 Basketball Analysis Service - Full Version Localhost
Complete web application with all features
"""

import os
import sys

def start_full_basketball_service():
    """Start the complete basketball analysis web application"""
    print("🏀 BASKETBALL ANALYSIS SERVICE - FULL VERSION")
    print("=" * 65)
    
    # Set environment variables for local development
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = 'True'
    os.environ['FLASK_HOST'] = '127.0.0.1'
    os.environ['PORT'] = '5000'
    
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    os.makedirs('jobs', exist_ok=True)
    
    print("📁 Directories verified")
    print("🔧 Environment configured for development")
    print("🎯 All enhanced features active:")
    print("   • Enhanced thumb flick detection (25° threshold)")
    print("   • 12+ comprehensive flaw detection types")
    print("   • Multiple camera angle support")
    print("   • Real-time progress tracking")
    print("   • Professional PDF report generation")
    print("   • Complete analysis history")
    print()
    print("🌐 Starting full web application...")
    print("📊 Host: http://127.0.0.1:5000")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 65)
    
    try:
        # Import and run the complete web application
        from web_app import app
        
        print("✅ Full Basketball Analysis Service loaded")
        print("📈 All analysis features ready")
        print("🎮 Web interface starting...")
        
        # Run the complete application
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            threaded=True,
            use_reloader=False
        )
        
    except Exception as e:
        print(f"❌ Error starting full service: {e}")
        print("🔧 Troubleshooting suggestions:")
        print("   • Check if port 5000 is available")
        print("   • Verify all dependencies are installed")
        print("   • Try: pip install -r requirements.txt")
        
        # Show available startup options
        print(f"\n📋 Alternative startup methods:")
        print(f"   • python web_app.py")
        print(f"   • python basketball_analysis_service.py")
        print(f"   • python start_fixed_service.py")

if __name__ == "__main__":
    start_full_basketball_service()
