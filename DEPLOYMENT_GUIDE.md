# 🚀 Complete Render Deployment Guide
## Basketball Analysis Service - Step-by-Step Instructions

### Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [GitHub Repository Setup](#github-repository-setup)
3. [Render Account & Service Creation](#render-account--service-creation)
4. [Environment Configuration](#environment-configuration)
5. [Deployment & Testing](#deployment--testing)
6. [Post-Deployment Monitoring](#post-deployment-monitoring)
7. [Troubleshooting Guide](#troubleshooting-guide)
8. [Scaling & Optimization](#scaling--optimization)

---

## Pre-Deployment Checklist

### ✅ Required Files Verification
Before deploying, ensure these files exist in your repository:

```bash
# Essential deployment files
├── basketball_analysis_service.py    # Main analysis service
├── web_app.py                       # Flask web application
├── wsgi.py                          # WSGI entry point
├── requirements.txt                 # Python dependencies
├── Procfile                         # Process configuration
├── .env.starter                     # Environment variables template
└── templates/                       # HTML templates (if using web interface)
    └── index.html
```

### ✅ File Content Verification
Run this command to verify your files are properly configured:

```bash
# Check Procfile
cat Procfile
# Should show: web: gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 180 --max-requests 50 --max-requests-jitter 5 --preload --worker-class sync

# Check requirements.txt for key dependencies
grep -E "(gunicorn|flask|opencv|mediapipe)" requirements.txt
```

---

## GitHub Repository Setup

### Step 1: Initialize Git Repository (if not already done)
```bash
# Navigate to your project directory
cd c:\basketball_analysis\New_Shot_AI

# Initialize git (if not already initialized)
git init

# Add GitHub remote (replace with your repository URL)
git remote add origin https://github.com/rickdyer20/apex-sports-trainer.git
```

### Step 2: Commit All Changes
```bash
# Add all files to staging
git add .

# Commit with descriptive message
git commit -m "Complete basketball analysis service ready for Render deployment

- Optimized Procfile for Starter Plan (2 workers, 180s timeout)
- Updated requirements.txt with headless OpenCV
- Added health check endpoint at /health
- Memory optimizations and error handling
- Starter Plan environment configuration"

# Push to GitHub
git push origin master
```

### Step 3: Verify Repository Structure
Go to your GitHub repository and confirm all files are present:
- ✅ All Python files uploaded
- ✅ requirements.txt contains correct dependencies
- ✅ Procfile shows optimized configuration
- ✅ No sensitive information (API keys, passwords) in code

---

## Render Account & Service Creation

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Click **"Get Started"**
3. Sign up with GitHub account (recommended for easy repository access)
4. Verify your email address

### Step 2: Connect GitHub Repository
1. In Render Dashboard, click **"New +"** 
2. Select **"Web Service"**
3. Click **"Connect to GitHub"**
4. Authorize Render to access your repositories
5. Select your repository: `apex-sports-trainer`
6. Click **"Connect"**

### Step 3: Configure Basic Settings
Fill in the service configuration:

```yaml
Name: basketball-analysis-service
Region: Oregon (US West) # Choose closest to your users
Branch: master
Root Directory: . # Leave blank if repository root
Runtime: Docker # Render will auto-detect Python
```

### Step 4: Build Configuration
```yaml
Build Command: pip install -r requirements.txt
Start Command: gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 180
```

### Step 5: Select Starter Plan
- **Plan**: Select **"Starter - $7/month"**
- **Auto-Deploy**: ✅ Enable (deploys automatically on git push)

---

## Environment Configuration

### Step 1: Set Environment Variables
In Render Dashboard, go to **"Environment"** tab and add these variables:

#### Core Configuration
```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-basketball-key-change-this-to-something-random
```

#### Processing Optimization (Starter Plan)
```bash
MAX_PROCESSING_TIME=180
FRAME_SKIP=2
GARBAGE_COLLECTION_INTERVAL=15
MAX_CONCURRENT_JOBS=3
```

#### Memory & Performance
```bash
TF_ENABLE_ONEDNN_OPTS=0
TF_CPP_MIN_LOG_LEVEL=2
OPENCV_DISABLE_CUDA_CACHE=1
```

#### File Upload Settings
```bash
MAX_FILE_SIZE=30
UPLOAD_FOLDER=uploads
RESULTS_FOLDER=results
```

#### Optional Settings
```bash
ENABLE_ORIENTATION_CORRECTION=false
LOG_LEVEL=INFO
```

### Step 2: Generate Secure Secret Key
Use this Python command to generate a secure secret key:
```python
import secrets
print(secrets.token_urlsafe(32))
# Copy the output and use it as your SECRET_KEY
```

---

## Deployment & Testing

### Step 1: Deploy Service
1. Click **"Create Web Service"** 
2. Render will automatically:
   - Clone your repository
   - Install dependencies from requirements.txt
   - Start the service using your Procfile

### Step 2: Monitor Build Process
Watch the build logs for:
- ✅ Dependencies installing successfully
- ✅ No import errors
- ✅ Service starting without crashes
- ❌ Common issues: Missing dependencies, import errors

### Step 3: Verify Deployment
Once deployment completes:

#### Check Service Status
```bash
# Your service URL will be: https://basketball-analysis-service.onrender.com
# Or custom domain if configured

# Test health endpoint
curl https://your-service-url.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-30T...",
  "memory_usage": "25%",
  "available_memory_gb": 0.38,
  "active_jobs": 0,
  "total_jobs": 0
}
```

#### Test Main Application
1. Visit your service URL in browser
2. You should see the basketball analysis upload page
3. Try uploading a small test video (1-5MB)

---

## Post-Deployment Monitoring

### Step 1: Set Up Monitoring Dashboard
Bookmark these Render dashboard pages:
- **Service Overview**: Monitor uptime and requests
- **Metrics**: CPU, memory, and response time graphs  
- **Logs**: Real-time application logs
- **Environment**: Manage environment variables

### Step 2: Health Check Monitoring
Set up regular health checks:

```bash
# Create a simple monitoring script
#!/bin/bash
HEALTH_URL="https://your-service-url.onrender.com/health"
RESPONSE=$(curl -s $HEALTH_URL)
echo "$(date): $RESPONSE"

# Run every 5 minutes via cron or task scheduler
```

### Step 3: Performance Baselines
Establish performance baselines:

| Video Size | Expected Processing Time | Memory Usage |
|------------|-------------------------|--------------|
| 1-5MB      | 15-30 seconds          | 30-50%       |
| 5-15MB     | 30-90 seconds          | 50-70%       |
| 15-30MB    | 90-180 seconds         | 70-85%       |

---

## Troubleshooting Guide

### Common Deployment Issues

#### 1. Build Failures
**Symptom**: Deployment fails during build
```bash
# Check logs for:
- "No module named 'opencv'" → requirements.txt issue
- "Permission denied" → Render filesystem issue  
- "Memory error" → Dependencies too large
```

**Solutions**:
- Verify requirements.txt has all dependencies
- Use `opencv-python-headless` instead of `opencv-python`
- Remove unused dependencies to reduce memory

#### 2. Service Crashes on Startup
**Symptom**: Build succeeds but service won't start
```bash
# Common causes:
- Import errors in Python code
- Missing environment variables
- Port binding issues
```

**Solutions**:
- Check logs for specific error messages
- Verify all environment variables are set
- Ensure wsgi.py correctly imports your Flask app

#### 3. Memory Issues During Processing
**Symptom**: Service crashes when processing videos
```bash
# Monitor /health endpoint for memory usage
# If consistently >85%, try:
```

**Solutions**:
- Reduce MAX_CONCURRENT_JOBS to 2 or 1
- Increase FRAME_SKIP to 3 or 4
- Test with smaller video files
- Consider upgrading to higher plan

#### 4. Timeout Issues
**Symptom**: Videos fail with timeout errors
```bash
# Processing takes longer than 180 seconds
```

**Solutions**:
- Reduce video file size (<15MB recommended)
- Increase timeout in Procfile (max 300s)
- Optimize processing parameters

### Debug Commands
```bash
# View recent logs
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.render.com/v1/services/YOUR_SERVICE_ID/logs

# Check service status
curl https://your-service-url.onrender.com/health

# Test video processing endpoint
curl -X POST -F "video=@test_video.mp4" \
  https://your-service-url.onrender.com/upload
```

---

## Scaling & Optimization

### Immediate Optimizations
1. **Custom Domain**: Add professional domain in Render dashboard
2. **SSL Certificate**: Automatic with custom domains
3. **Error Tracking**: Implement error reporting service
4. **Analytics**: Add usage tracking for optimization insights

### Performance Monitoring
```python
# Add to your Flask app for detailed monitoring
import time
import psutil
from flask import request

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request  
def after_request(response):
    duration = time.time() - g.start_time
    memory = psutil.virtual_memory().percent
    
    logging.info(f"Request: {request.path} | "
                f"Duration: {duration:.2f}s | "
                f"Memory: {memory}%")
    return response
```

### Future Enhancements
When ready to scale beyond Starter Plan:

1. **External Storage**: S3/GCS for persistent file storage
2. **Database**: PostgreSQL for job persistence
3. **Background Jobs**: Redis/Celery for async processing
4. **CDN**: CloudFlare for faster video delivery
5. **API Authentication**: User accounts and API keys
6. **Rate Limiting**: Prevent abuse and manage resources

### Plan Upgrade Considerations
**Consider upgrading to Standard Plan ($25/month) when**:
- Processing >100 videos per day
- Consistent memory usage >70%
- Need for larger video file support (>30MB)
- Multiple concurrent users

---

## Success Metrics

### Deployment Success Indicators
- ✅ Service deploys without errors
- ✅ Health endpoint returns 200 OK
- ✅ Can upload and process test videos
- ✅ Memory usage stays below 80%
- ✅ Processing times meet expectations

### Production Readiness Checklist
- ✅ Custom domain configured
- ✅ Environment variables properly set
- ✅ Monitoring and alerting setup
- ✅ Error handling tested
- ✅ Performance baselines established
- ✅ Backup/recovery plan documented

---

## Support & Resources

### Render Documentation
- [Render Docs](https://render.com/docs)
- [Python Deployment Guide](https://render.com/docs/deploy-flask)
- [Environment Variables](https://render.com/docs/environment-variables)

### Basketball Analysis Service Support
- Health Check: `https://your-service-url.onrender.com/health`
- Service Logs: Available in Render dashboard
- Repository Issues: Create issues on GitHub for bugs/features

### Emergency Contacts
- Render Support: Available via dashboard for Starter plan users
- Repository Owner: GitHub @rickdyer20

---

**🎉 Congratulations! Your basketball analysis service is now live on Render!**

Your service should now be accessible at: `https://basketball-analysis-service.onrender.com`

Start with small test videos and monitor performance through the `/health` endpoint and Render dashboard metrics.
