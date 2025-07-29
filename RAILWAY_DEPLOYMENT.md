# Railway Deployment Guide
## Basketball Analysis Service

This guide will help you deploy your optimized Basketball Analysis Service to Railway with all the performance optimizations that made localhost work perfectly.

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended)

Run the Python deployment script:
```bash
python deploy_railway.py
```

### Option 2: Manual Railway CLI

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize and Deploy**:
   ```bash
   railway up
   ```

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Railway CLI**: Install using npm
3. **Required Files**: All files in this directory are needed

## 🔧 Configuration

### Environment Variables (Set Automatically)
- `TF_CPP_MIN_LOG_LEVEL=2` - Reduce TensorFlow logging
- `CUDA_VISIBLE_DEVICES=""` - Force CPU-only processing  
- `MEDIAPIPE_DISABLE_GPU=1` - Disable GPU for MediaPipe
- `FLASK_ENV=production` - Production Flask mode
- `FLASK_DEBUG=false` - Disable debug mode
- `PYTHONUNBUFFERED=1` - Better logging in containers

### Container Configuration
- **Runtime**: Python 3.11
- **Framework**: Flask + Gunicorn
- **Workers**: 2 workers with thread pooling
- **Timeout**: 90 seconds (optimized for video processing)
- **Health Check**: `/health` endpoint
- **Auto-restart**: On failure (max 10 retries)

## 🎯 Performance Optimizations Applied

✅ **CPU-Only Processing**: No GPU dependencies, works on any Railway instance
✅ **Optimized MediaPipe**: Model complexity 0 for faster processing  
✅ **Reduced Timeouts**: 90s timeout prevents hanging
✅ **Memory Management**: Garbage collection every 10 frames
✅ **Frame Limiting**: Max 100 frames per video for consistent performance
✅ **Production Logging**: Structured logging for monitoring

## 📊 Deployment Process

1. **Validation**: Checks all required files exist
2. **Environment Setup**: Configures performance variables
3. **Container Build**: Creates optimized Docker image
4. **Health Checks**: Ensures service is responding
5. **URL Assignment**: Provides public URL for access

## 🌐 Access Your Service

After deployment, your service will be available at:
- **Main Interface**: `https://your-app.railway.app/`
- **Health Check**: `https://your-app.railway.app/health`
- **API Status**: `https://your-app.railway.app/api/health`

## 📋 Post-Deployment Commands

```bash
# View deployment logs
railway logs

# Check service status
railway status

# Open service in browser
railway open

# View performance metrics
railway metrics

# Scale service resources
railway scale

# Manage environment variables
railway variables

# Add custom domain
railway domain add your-domain.com
```

## 🛠️ Troubleshooting

### Common Issues

1. **Build Fails**:
   - Check that all files are present
   - Verify Docker syntax in Dockerfile
   - Check requirements.txt dependencies

2. **Service Won't Start**:
   - Check logs: `railway logs`
   - Verify environment variables: `railway variables`
   - Ensure health check endpoint is working

3. **Slow Performance**:
   - Monitor metrics: `railway metrics`
   - Check if CPU limits are hit
   - Consider upgrading Railway plan

4. **Memory Issues**:
   - Video processing is memory-intensive
   - Monitor usage in Railway dashboard
   - Consider increasing memory limits

### Environment Variables Check

```bash
# List all environment variables
railway variables

# Add missing variable
railway variables set VARIABLE_NAME=value

# Remove variable
railway variables delete VARIABLE_NAME
```

## 📈 Monitoring

Railway provides built-in monitoring:
- **CPU Usage**: Monitor processing load
- **Memory Usage**: Track video processing memory
- **Request Metrics**: Monitor upload frequency
- **Error Rates**: Track failed analyses
- **Response Times**: Monitor analysis speed

## 🔄 Updates and Redeployment

To update your service:

1. **Make changes** to your code
2. **Commit changes** (if using Git integration)
3. **Redeploy**: 
   ```bash
   railway up
   ```

Railway supports:
- **Auto-deployment** from Git repositories
- **Manual deployment** via CLI
- **Environment-specific** deployments

## 💰 Cost Optimization

Railway pricing tips:
- **Starter Plan**: Good for development and testing
- **Pro Plan**: Recommended for production use
- **Usage-based billing**: Only pay for resources used
- **Sleep mode**: Reduces costs for low-traffic periods

## 🔐 Security

Best practices applied:
- **Non-root user** in container
- **Environment variables** for sensitive config
- **Health checks** for service monitoring
- **Auto-restart** for failure recovery
- **Secure file handling** for uploads

## 📞 Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: Community support
- **Railway Status**: [status.railway.app](https://status.railway.app)

## 🎉 Success Indicators

After deployment, you should see:
- ✅ Service status: "Active"
- ✅ Health check: Returns 200 OK
- ✅ Logs show: "TensorFlow Lite XNNPACK delegate for CPU"
- ✅ Video uploads work without hanging
- ✅ Analysis completes in under 2 minutes

Your Basketball Analysis Service is now running on Railway with all the performance optimizations that made localhost work perfectly!
