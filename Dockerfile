# Simple redirect to render.yaml configuration
# This file exists only to prevent Docker build errors
# The actual deployment should use render.yaml settings

FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app files
COPY wsgi.py .

# Use the same command as render.yaml
EXPOSE $PORT
CMD gunicorn wsgi:application --bind 0.0.0.0:$PORT
