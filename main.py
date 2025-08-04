# Google App Engine main entry point
# Basketball Analysis Service - GCP Production

import os
import logging
from web_app import app

# Configure logging for GCP
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# GCP App Engine entry point
if __name__ == '__main__':
    # For local development
    app.run(host='127.0.0.1', port=8080, debug=False)
else:
    # For App Engine deployment
    # The 'app' object is used by App Engine
    pass
