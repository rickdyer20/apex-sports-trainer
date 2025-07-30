web: gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 180 --max-requests 50 --max-requests-jitter 5 --preload --worker-class sync
