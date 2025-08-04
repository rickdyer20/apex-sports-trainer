# 🚀 Google Cloud Platform Deployment Guide
## Basketball Analysis Service - Complete GCP Setup

This guide provides step-by-step instructions for deploying your basketball analysis service to Google Cloud Platform using multiple deployment options.

## 📋 Prerequisites

### Required Tools
- **Google Cloud SDK**: [Download here](https://cloud.google.com/sdk/docs/install)
- **Docker** (for Cloud Run): [Download here](https://docs.docker.com/get-docker/)
- **Git**: For code deployment
- **Python 3.11**: Local development and testing

### GCP Account Setup
1. Create a Google Cloud account at [cloud.google.com](https://cloud.google.com)
2. Create a new project or select existing one
3. Enable billing for your project
4. Install and initialize gcloud CLI:
   ```bash
   gcloud init
   gcloud auth login
   ```

## 🎯 Deployment Options

### Option 1: App Engine (Recommended for Beginners)
**Best for**: Simple deployment, automatic scaling, managed infrastructure

#### Advantages
- ✅ Zero server management
- ✅ Automatic scaling
- ✅ Built-in health checks
- ✅ Easy domain mapping
- ✅ Integrated with other GCP services

#### Quick Deploy
```bash
# 1. Set your project
gcloud config set project YOUR_PROJECT_ID

# 2. Enable App Engine API
gcloud services enable appengine.googleapis.com

# 3. Create App Engine app (one-time)
gcloud app create --region=us-central

# 4. Deploy your service
gcloud app deploy app.yaml

# 5. View your app
gcloud app browse
```

#### Configuration
Your `app.yaml` is already optimized with:
- Python 3.11 runtime
- 4GB memory, 2 CPU cores
- Auto-scaling (1-10 instances)
- Health checks on `/health`
- Production environment variables

### Option 2: Cloud Run (Recommended for Scale)
**Best for**: High scalability, containerized deployment, pay-per-use

#### Advantages
- ✅ Scale to zero (cost-effective)
- ✅ Scale to millions of requests
- ✅ Container-based deployment
- ✅ Advanced traffic management
- ✅ Supports custom domains with SSL

#### Quick Deploy
```bash
# 1. Enable Cloud Run API
gcloud services enable run.googleapis.com

# 2. Build and deploy in one command
gcloud run deploy basketball-analysis \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --timeout 300

# 3. Get your service URL
gcloud run services list
```

#### Manual Container Build
```bash
# Build container
docker build -t gcr.io/YOUR_PROJECT_ID/basketball-analysis:latest .

# Push to Container Registry
docker push gcr.io/YOUR_PROJECT_ID/basketball-analysis:latest

# Deploy to Cloud Run
gcloud run deploy basketball-analysis \
    --image gcr.io/YOUR_PROJECT_ID/basketball-analysis:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

## 🛠️ Automated Deployment

### Using the Deployment Scripts

#### For Linux/macOS:
```bash
chmod +x deploy_gcp.sh
./deploy_gcp.sh
```

#### For Windows (PowerShell):
```powershell
.\deploy_gcp.ps1
```

### Using Cloud Build (CI/CD)
1. Connect your GitHub repository to Cloud Build
2. The `cloudbuild.yaml` will automatically:
   - Run tests
   - Build container images
   - Deploy to App Engine
   - Run health checks

```bash
# Trigger a build manually
gcloud builds submit --config cloudbuild.yaml .
```

## 🔧 Configuration Details

### Environment Variables
Both deployment options use optimized environment variables:

```yaml
FLASK_ENV: production
FLASK_DEBUG: false
TF_CPP_MIN_LOG_LEVEL: '2'          # Reduce TensorFlow logging
MEDIAPIPE_DISABLE_GPU: '1'         # Force CPU processing
OPENCV_DISABLE_CUDA_CACHE: '1'     # Disable CUDA for OpenCV
MAX_PROCESSING_TIME: '300'         # 5-minute timeout
MAX_CONCURRENT_JOBS: '2'           # Limit concurrent processing
FRAME_SKIP: '2'                    # Skip frames for performance
GARBAGE_COLLECTION_INTERVAL: '10'  # Memory optimization
```

### Resource Allocation
- **CPU**: 2 cores (sufficient for video processing)
- **Memory**: 4GB (handles large video files)
- **Timeout**: 300 seconds (5 minutes for complex analysis)
- **Disk**: 10GB temporary storage

### Security Features
- HTTPS enforced by default
- No sensitive data in code
- Environment-based configuration
- Secure file handling

## 📊 Monitoring and Logging

### Built-in Monitoring
Both deployments include:
- Health check endpoints (`/health`)
- Automatic log collection
- Error tracking
- Performance metrics

### View Logs
```bash
# App Engine logs
gcloud app logs tail -s default

# Cloud Run logs  
gcloud run logs tail --service=basketball-analysis --region=us-central1
```

### Set Up Alerts
```bash
# Create log-based metric for errors
gcloud logging metrics create basketball_analysis_errors \
    --description="Basketball Analysis Service Errors" \
    --log-filter='severity>=ERROR'
```

## 🌐 Domain and SSL Setup

### Custom Domain (App Engine)
```bash
# Map custom domain
gcloud app domain-mappings create your-domain.com
```

### Custom Domain (Cloud Run)
```bash
# Create domain mapping
gcloud run domain-mappings create \
    --service basketball-analysis \
    --domain your-domain.com \
    --region us-central1
```

## 💰 Cost Optimization

### App Engine Pricing
- **Free Tier**: 28 instance hours per day
- **Standard**: ~$0.05-0.10 per hour per instance
- **Estimated Monthly**: $15-50 for moderate usage

### Cloud Run Pricing
- **Pay-per-request**: Only pay when processing
- **Free Tier**: 2 million requests per month
- **Estimated Monthly**: $10-30 for moderate usage

### Cost-Saving Tips
1. **Use Cloud Run** for variable traffic
2. **Set max instances** to control costs
3. **Enable auto-scaling** to scale down during low usage
4. **Monitor usage** with Cloud Billing alerts

## 🚀 Performance Optimization

### For High Traffic
```bash
# Increase max instances (Cloud Run)
gcloud run services update basketball-analysis \
    --max-instances 100 \
    --region us-central1

# Scale App Engine
gcloud app deploy --version v2 --no-promote  # Blue-green deployment
```

### For Better Performance
1. **Enable CDN**: Cache static assets
2. **Use Cloud Storage**: For video file storage
3. **Implement caching**: Redis/Memorystore for results
4. **Optimize images**: Use WebP format

## 🔒 Security Best Practices

### Authentication (Optional)
```bash
# Require authentication (Cloud Run)
gcloud run services update basketball-analysis \
    --no-allow-unauthenticated \
    --region us-central1
```

### VPC Configuration
```bash
# Deploy to private VPC (advanced)
gcloud run deploy basketball-analysis \
    --vpc-connector YOUR_CONNECTOR \
    --vpc-egress private-ranges-only
```

## 🛠️ Troubleshooting

### Common Issues

#### Deployment Fails
```bash
# Check build logs
gcloud builds log BUILD_ID

# Check service logs
gcloud app logs tail -s default
gcloud run logs tail --service=basketball-analysis
```

#### Out of Memory
```bash
# Increase memory (Cloud Run)
gcloud run services update basketball-analysis \
    --memory 8Gi \
    --region us-central1
```

#### Timeout Issues
```bash
# Increase timeout (Cloud Run)
gcloud run services update basketball-analysis \
    --timeout 600 \
    --region us-central1
```

#### Cold Starts
```bash
# Set minimum instances (Cloud Run)
gcloud run services update basketball-analysis \
    --min-instances 1 \
    --region us-central1
```

### Debug Commands
```bash
# Check service status
gcloud app describe
gcloud run services describe basketball-analysis --region us-central1

# View recent deployments
gcloud app versions list
gcloud run revisions list --service basketball-analysis --region us-central1

# Test health endpoint
curl https://YOUR_PROJECT_ID.appspot.com/health
curl https://basketball-analysis-HASH-uc.a.run.app/health
```

## 📈 Scaling Strategies

### Horizontal Scaling
- **App Engine**: Automatic based on request volume
- **Cloud Run**: Scale to zero, up to 1000 instances per service

### Vertical Scaling
```bash
# Increase resources (Cloud Run)
gcloud run services update basketball-analysis \
    --cpu 4 \
    --memory 8Gi \
    --region us-central1
```

### Traffic Splitting
```bash
# Blue-green deployment (Cloud Run)
gcloud run services update-traffic basketball-analysis \
    --to-revisions basketball-analysis-v2=50,basketball-analysis-v1=50 \
    --region us-central1
```

## 🎯 Production Checklist

- [ ] Project created and billing enabled
- [ ] APIs enabled (App Engine/Cloud Run)
- [ ] Code deployed successfully
- [ ] Health checks passing
- [ ] Environment variables configured
- [ ] Monitoring and alerting set up
- [ ] Custom domain configured (if needed)
- [ ] SSL certificates validated
- [ ] Load testing completed
- [ ] Backup and disaster recovery planned

## 📞 Support Resources

- **GCP Documentation**: [cloud.google.com/docs](https://cloud.google.com/docs)
- **App Engine Guide**: [cloud.google.com/appengine/docs](https://cloud.google.com/appengine/docs)
- **Cloud Run Guide**: [cloud.google.com/run/docs](https://cloud.google.com/run/docs)
- **GCP Support**: Available with paid support plans
- **Community**: Stack Overflow, Reddit r/googlecloud

## 🎉 Success Indicators

After successful deployment, you should see:
- ✅ Service status: "Serving" (App Engine) or "Ready" (Cloud Run)
- ✅ Health check returns 200 OK
- ✅ Video upload and analysis works
- ✅ Logs show successful MediaPipe initialization
- ✅ Processing completes within timeout limits
- ✅ PDF reports generate successfully

Your Basketball Analysis Service is now running on Google Cloud Platform with enterprise-grade scalability and reliability! 🏀🚀
