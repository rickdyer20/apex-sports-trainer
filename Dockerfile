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

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for processing
RUN mkdir -p /app/temp_videos /app/output_videos /app/logs

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Health check endpoint  
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port (Railway will set PORT env var)
EXPOSE 8080

# Use gunicorn for production deployment
CMD gunicorn --workers 2 --timeout 60 --bind 0.0.0.0:$PORT --worker-class gthread --threads 2 wsgi:application
