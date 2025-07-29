# 🚀 Basketball Analysis Service - Production Deployment Guide

## ✅ **Optimizations Applied**

Your web deployment now includes all the performance optimizations that work perfectly on localhost:

### 🔧 **Key Performance Improvements**
- **Reduced Processing**: 100 max frames (vs 150 previously)
- **Extended Timeout**: 90 seconds (vs 60 seconds)
- **Memory Management**: Garbage collection every 10 frames
- **MediaPipe Optimization**: Model complexity = 0, GPU disabled
- **TensorFlow Optimization**: Minimal logging, CPU-only processing

### 🌐 **Environment Configuration**
- **Development**: `FLASK_DEBUG=true, host=127.0.0.1` (localhost only)
- **Production**: `FLASK_DEBUG=false, host=0.0.0.0` (web accessible)

## 🚀 **Deployment Options**

### **Option 1: Direct Python Production Server**
```bash
# Set environment for production
export FLASK_ENV=production
export FLASK_DEBUG=false
export FLASK_HOST=0.0.0.0
export PORT=5000

# Run optimized production server
python deploy_production.py
```

### **Option 2: Docker Container**
```bash
# Build with optimizations
docker build -t basketball-analysis .

# Run with performance environment variables
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -e FLASK_DEBUG=false \
  -e TF_CPP_MIN_LOG_LEVEL=2 \
  -e MEDIAPIPE_DISABLE_GPU=1 \
  basketball-analysis
```

### **Option 3: Docker Compose (Local Testing)**
```bash
# Test production-like environment locally
docker-compose up --build
```

### **Option 4: Kubernetes Deployment**
```bash
# Deploy to production cluster
kubectl apply -f k8s/production-deployment.yaml
```

## 🔍 **Verification Steps**

After deployment, verify the optimizations are working:

1. **Check Environment Variables**: Look for these in logs:
   ```
   Set TF_CPP_MIN_LOG_LEVEL=2
   Set MEDIAPIPE_DISABLE_GPU=1
   Starting production server on 0.0.0.0:5000
   ```

2. **Test Video Processing**: 
   - Upload a basketball shot video
   - Should complete processing without hanging
   - Processing time should be similar to localhost

3. **Monitor Resource Usage**:
   - Memory usage should stay under 2GB
   - CPU usage should be optimized
   - No GPU usage (MediaPipe CPU-only)

## 🎯 **Expected Performance**

With these optimizations, your web version should perform **identically** to localhost:
- ✅ **No hanging** during video processing
- ✅ **Consistent processing times** (~30-60 seconds for typical videos)
- ✅ **Lower memory usage** due to garbage collection
- ✅ **Reliable completion** with 90-second timeout

## 📊 **Monitoring**

Watch for these success indicators in your production logs:
```
🏀 Basketball Analysis Web Service Starting...
🔧 Optimized for performance with reduced resource usage
🌐 Starting production server on 0.0.0.0:5000
INFO: Created TensorFlow Lite XNNPACK delegate for CPU.
```

## 🛠️ **Troubleshooting**

If web version still has issues:

1. **Check Resource Limits**: Ensure container has at least 2GB RAM
2. **Verify Environment Variables**: All optimization vars should be set
3. **Compare Logs**: Web logs should match localhost startup sequence
4. **Network Timeouts**: May need to increase client-side upload timeouts

Your web deployment is now optimized to match your perfectly working localhost setup! 🎉
