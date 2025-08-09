"""
Basketball Analysis Service v9.0 - Clean Deployment Entry Point
NO PAYMENT PROCESSING - Pure basketball analysis functionality
"""

# Import the clean web application
from web_app_v9_clean import app

# Export for Google Cloud App Engine
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
