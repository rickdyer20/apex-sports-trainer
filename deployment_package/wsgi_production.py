# WSGI Configuration for ApexSports-LLC.com
# This file should be used with Gunicorn or Apache mod_wsgi

import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Import the Flask application
from complete_web_app import app

# WSGI application object
application = app

if __name__ == "__main__":
    # For direct execution (development only)
    app.run(host='0.0.0.0', port=5000, debug=False)
