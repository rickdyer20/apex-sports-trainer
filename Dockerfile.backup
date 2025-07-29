# Basketball Analysis Service - Dockerfile
# Production-ready container for cloud deployment

FROM python:3.11-slim

# Install curl for health checks
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Set environment variables for optimized performance
ENV TF_CPP_MIN_LOG_LEVEL=2
ENV CUDA_VISIBLE_DEVICES=""
ENV TF_ENABLE_ONEDNN_OPTS=0
ENV MEDIAPIPE_DISABLE_GPU=1
ENV FLASK_ENV=production
ENV FLASK_DEBUG=false
ENV FLASK_HOST=0.0.0.0

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download MediaPipe models to avoid runtime permission issues
RUN python -c "import mediapipe as mp; import os; os.makedirs('/tmp/mediapipe', exist_ok=True); pose = mp.solutions.pose.Pose(model_complexity=0); pose.close(); print('MediaPipe models downloaded')"

# Copy application code
COPY . .

# Create directories for processing
RUN mkdir -p /app/temp_videos /app/output_videos /app/logs

# Create MediaPipe cache directory with write permissions for model downloads
RUN mkdir -p /tmp/mediapipe && \
    chmod 777 /tmp/mediapipe

# Set MediaPipe to use temp directory for model cache
ENV MEDIAPIPE_MODEL_PATH=/tmp/mediapipe
ENV XDG_CACHE_HOME=/tmp

# Create non-root user for security but allow MediaPipe access
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app && \
    chown -R app:app /tmp/mediapipe
USER app

# Health check endpoint  
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Expose port (Railway will set PORT env var)
EXPOSE ${PORT:-8080}

# Use gunicorn for production deployment
CMD gunicorn --workers 2 --timeout 90 --bind 0.0.0.0:${PORT:-8080} --worker-class gthread --threads 2 wsgi:application
