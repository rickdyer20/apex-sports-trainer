#!/usr/bin/env python3
"""
Emergency Basketball Analysis Server
Direct server start with error capture
"""

print("🏀 EMERGENCY SERVER START")
print("=" * 40)

try:
    print("Step 1: Testing Flask import...")
    from flask import Flask
    print("✅ Flask imported")
    
    print("Step 2: Testing MediaPipe import...")
    import mediapipe as mp
    print("✅ MediaPipe imported")
    
    print("Step 3: Testing OpenCV import...")
    import cv2
    print("✅ OpenCV imported")
    
    print("Step 4: Testing web_app import...")
    from web_app import app
    print("✅ Web app imported successfully!")
    
    print("\nStep 5: Starting server...")
    print("📍 Server will start at: http://127.0.0.1:5000")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 40)
    
    # Start the server
    app.run(host='127.0.0.1', port=5000, debug=True)
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\n🔧 Try installing missing package:")
    print(f"pip install {str(e).split()[-1].replace("'", "")}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e).__name__}")
    
    # Try creating a minimal Flask app instead
    print("\n🚨 Creating emergency minimal server...")
    
    emergency_app = Flask(__name__)
    
    @emergency_app.route('/')
    def emergency():
        return """
        <h1>🏀 Basketball Analysis - Emergency Mode</h1>
        <p>Main app failed to start. Emergency server running.</p>
        <p><strong>Error:</strong> """ + str(e) + """</p>
        <p><a href="/test">Test Page</a></p>
        """
    
    @emergency_app.route('/test')
    def test():
        return "<h1>✅ Emergency server working!</h1><p><a href='/'>Back</a></p>"
    
    print("📍 Emergency server at: http://127.0.0.1:5001")
    emergency_app.run(host='127.0.0.1', port=5001, debug=True)
