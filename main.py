"""
Minimal main.py for Google Cloud App Engine
Basketball Analysis Service
"""

# Import the Flask application
from complete_web_app import app

# Export the app for gunicorn
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
