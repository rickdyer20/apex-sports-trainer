# 🚀 BUILDPACK DEPLOYMENT GUIDE

## ✅ **Why Buildpack Deployment?**

**Buildpack deployment** is the **recommended method** for your basketball analysis service because:
- ✅ **Faster builds**: 5-10 minutes vs 15-20 for Docker
- ✅ **Less memory usage**: Better for Starter Plan's 512MB RAM
- ✅ **Automatic Python setup**: Render handles Python environment
- ✅ **Uses your optimized Procfile**: Already configured for 2 workers, 180s timeout
- ✅ **Easier troubleshooting**: Simpler build process

---

## 🎯 **Step-by-Step Buildpack Deployment**

### **Step 1: Prepare Your Repository**

✅ Your repository is already ready! You have:
- ✅ `Procfile` (optimized for Starter Plan)
- ✅ `requirements.txt` (cleaned with headless OpenCV)
- ✅ `wsgi.py` (production WSGI entry point)
- ✅ `.env.starter` (environment template)

### **Step 2: Deploy to Render**

#### 2.1 Go to Render Dashboard
1. Visit [render.com](https://render.com)
2. Sign up/Login with your GitHub account
3. Click **"New +"** → **"Web Service"**

#### 2.2 Connect Your Repository
1. **Connect GitHub** (authorize if needed)
2. **Select Repository**: `apex-sports-trainer`
3. **Branch**: `master`
4. **Root Directory**: Leave blank (use root)

#### 2.3 Configure Service Settings

**CRITICAL: Choose these exact settings for buildpack deployment:**

```
Service Name: basketball-analysis-service
Environment: Web Service
Region: Oregon (US West) or Ohio (US East)
Branch: master
Build Command: pip install -r requirements.txt
Start Command: gunicorn --workers 2 --timeout 180 --bind 0.0.0.0:$PORT wsgi:application
```

#### 2.4 Choose Starter Plan
- **Plan**: Starter ($7/month)
- **Auto-Deploy**: Yes (recommended)

#### 2.5 Environment Variables

**Copy these exactly from your `.env.starter` file:**

```bash
FLASK_ENV=production
FLASK_DEBUG=False
PORT=8080
TF_CPP_MIN_LOG_LEVEL=2
TF_ENABLE_ONEDNN_OPTS=0
MEDIAPIPE_DISABLE_GPU=1
CUDA_VISIBLE_DEVICES=""
```

**Important**: 
- Don't use quotes around values in Render dashboard
- Each variable goes in a separate field
- PORT will be automatically set by Render, but include it anyway

### **Step 3: Deploy & Monitor**

1. **Click "Create Web Service"**
2. **Watch the build logs** (5-10 minutes)
3. **Wait for "Deploy succeeded"** message

Expected build process:
```
Building...
--> Python buildpack detected
--> Installing Python 3.11
--> Installing requirements from requirements.txt
--> Build completed successfully
Starting...
--> Running: gunicorn --workers 2 --timeout 180 --bind 0.0.0.0:$PORT wsgi:application
Deploy succeeded
```

---

## 🔍 **Verification Steps**

### **Test 1: Health Check**
```bash
# Replace YOUR_APP_NAME with your actual service name
curl https://YOUR_APP_NAME.onrender.com/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-01-30T12:00:00Z",
  "service": "Basketball Analysis Service"
}
```

### **Test 2: Web Interface**
1. Visit `https://YOUR_APP_NAME.onrender.com`
2. You should see the basketball analysis upload page
3. Try uploading a small test video (under 5MB)

### **Test 3: Check Logs**
In Render dashboard:
1. Go to your service
2. Click **"Logs"** tab
3. Look for successful startup messages

---

## ⚠️ **Important Buildpack vs Docker Differences**

| Aspect | Buildpack (Recommended) | Docker |
|--------|------------------------|--------|
| **Build Time** | 5-10 minutes | 15-20 minutes |
| **Setup** | Automatic Python | Manual system deps |
| **Memory Usage** | Lower during build | Higher during build |
| **Troubleshooting** | Easier | More complex |
| **Your Service** | ✅ Optimized for this | Works but overkill |

---

## 🚨 **Common Buildpack Issues & Solutions**

### **Issue 1: Build Fails on Requirements**
```
Error: Could not install packages due to an EnvironmentError
```
**Solution**: Your `requirements.txt` is already optimized, but if this happens:
1. Check build logs for specific package failures
2. May need to temporarily remove problematic packages

### **Issue 2: Service Won't Start**
```
Error: Web service failed to bind to $PORT
```
**Solution**: 
- Verify your `wsgi.py` file exists
- Check start command exactly matches: 
  `gunicorn --workers 2 --timeout 180 --bind 0.0.0.0:$PORT wsgi:application`

### **Issue 3: Memory Issues**
```
Error: Process killed (out of memory)
```
**Solution**: Your service is already optimized, but:
- Monitor memory usage in Render dashboard
- May need to reduce concurrent video processing

---

## 🎯 **Why This Works Better Than Docker**

Your basketball analysis service is **perfectly suited** for buildpack deployment because:

1. **Python-native**: Your service is pure Python with standard dependencies
2. **Already optimized**: Your Procfile and requirements.txt are tuned for Render
3. **Resource efficient**: Buildpack uses less memory during build
4. **Faster iterations**: Quick rebuilds when you push updates

---

## 📞 **Next Steps After Deployment**

1. **Monitor performance**: Check Render dashboard metrics
2. **Test with real videos**: Upload basketball shot videos
3. **Check health endpoint**: Set up monitoring alerts
4. **Scale if needed**: Upgrade to Standard plan for more resources

**🏀 Your basketball analysis service will be live and helping players improve their shots!**

---

## 🔗 **Quick Reference**

**Build Command**: `pip install -r requirements.txt`
**Start Command**: `gunicorn --workers 2 --timeout 180 --bind 0.0.0.0:$PORT wsgi:application`
**Plan**: Starter ($7/month)
**Environment**: Use values from `.env.starter`
