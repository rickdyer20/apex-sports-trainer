#!/usr/bin/env python3
"""
Minimal Test Server - Basketball Analysis
Simple test to verify Flask works on your system
"""

from flask import Flask, render_template_string

# Create minimal Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🏀 Basketball Analysis - Test Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f8ff; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #ff6600; text-align: center; }
            .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .button { background: #ff6600; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏀 Basketball Analysis Service</h1>
            <div class="status">
                <h3>✅ Test Server Running Successfully!</h3>
                <p>Your Flask server is working on localhost.</p>
            </div>
            
            <h3>🔧 Next Steps:</h3>
            <ol>
                <li>This confirms Flask works on your system</li>
                <li>Stop this test server (Ctrl+C)</li>
                <li>Start the full basketball analysis service</li>
            </ol>
            
            <h3>🚀 Start Full Service:</h3>
            <p>In your terminal, run one of these commands:</p>
            <code style="background: #f5f5f5; padding: 10px; display: block; margin: 10px 0;">
                python web_app.py
            </code>
            <code style="background: #f5f5f5; padding: 10px; display: block; margin: 10px 0;">
                python -m flask --app web_app run
            </code>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="/health" class="button">Test Health Check</a>
                <a href="/status" class="button">Check Status</a>
            </div>
        </div>
    </body>
    </html>
    """)

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "message": "Test server running",
        "service": "basketball-analysis-test"
    }

@app.route('/status')
def status():
    return render_template_string("""
    <h1>🏀 System Status</h1>
    <p><strong>✅ Flask:</strong> Working</p>
    <p><strong>✅ Port 5000:</strong> Available</p>
    <p><strong>✅ Server:</strong> Running</p>
    <p><a href="/">← Back to Home</a></p>
    """)

if __name__ == '__main__':
    print("🏀 BASKETBALL ANALYSIS - TEST SERVER")
    print("=" * 45)
    print("📍 Starting test server at: http://127.0.0.1:5000")
    print("🌐 Open this URL in your browser to test")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 45)
    
    try:
        app.run(host='127.0.0.1', port=5000, debug=True)
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        print("\n💡 Try a different port:")
        print("   python minimal_test_server.py")
        print("   Then try: http://127.0.0.1:8000")
