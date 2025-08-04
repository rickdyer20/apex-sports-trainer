# Basketball Analysis Service - Google Cloud Deployment Guide

## Current Deployment Readiness: ✅ READY with minor modifications

### What's Already Good:
- ✅ Flask app with proper environment variable handling
- ✅ Production-ready dependencies (gunicorn, opencv-headless)
- ✅ Health endpoints for monitoring
- ✅ WSGI entry point exists
- ✅ Error handling and logging
- ✅ File upload handling

### Google Cloud Specific Files Added:
- ✅ `app.yaml` - App Engine configuration
- ✅ `requirements_gcloud.txt` - Cloud-optimized dependencies  
- ✅ `deploy_gcloud.sh` - Automated deployment script

### Quick Deployment Steps:

1. **Install Google Cloud CLI:**
   ```bash
   # Download from: https://cloud.google.com/sdk/docs/install
   gcloud auth login
   ```

2. **Deploy to Google Cloud:**
   ```bash
   chmod +x deploy_gcloud.sh
   ./deploy_gcloud.sh your-project-id
   ```

3. **Alternative Manual Deployment:**
   ```bash
   gcloud config set project your-project-id
   gcloud app deploy app.yaml
   ```

### Estimated Deployment Time: 5-10 minutes

### ⚠️ Current Limitations for Cloud:

1. **File Storage**: Uses local filesystem - files lost on restart
   - **Impact**: Uploaded videos and results won't persist
   - **Solution**: Add Google Cloud Storage integration

2. **Database**: Uses in-memory + local JSON files
   - **Impact**: Job history lost on restart  
   - **Solution**: Add Cloud SQL or Firestore

3. **Processing Time**: No timeout handling for long videos
   - **Impact**: May hit Google Cloud request timeouts
   - **Solution**: Add Cloud Tasks for background processing

### For Production Use:
The app **WILL WORK** on Google Cloud but should add:
- Google Cloud Storage for file persistence
- Cloud SQL/Firestore for job persistence  
- Cloud Tasks for background video processing
- Cloud CDN for video delivery

### Cost Estimate:
- **App Engine Standard**: ~$20-50/month for moderate usage
- **Cloud Storage**: ~$5-15/month for video files
- **Total**: ~$25-65/month for a production basketball analysis service

The current script is **deployment-ready** for testing and initial use!
