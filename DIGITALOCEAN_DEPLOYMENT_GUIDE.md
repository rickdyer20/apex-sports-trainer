# 🌊 DigitalOcean Deployment Guide
## Basketball Shot Analysis Service

### ✅ Pre-Deployment Complete
- [x] Code committed and pushed to GitHub
- [x] App configuration updated for production
- [x] Requirements.txt updated with all dependencies  
- [x] Video orientation solution implemented
- [x] Repository ready: https://github.com/rickdyer20/apex-sports-trainer

---

## 🚀 Deploy to DigitalOcean (Manual Steps)

### Step 1: Access DigitalOcean
1. Go to https://cloud.digitalocean.com/
2. Log in to your DigitalOcean account
3. Navigate to **Apps** in the sidebar

### Step 2: Create New App
1. Click **"Create App"**
2. Choose **"GitHub"** as source
3. Select repository: `rickdyer20/apex-sports-trainer`
4. Branch: `master`
5. Auto-deploy: ✅ **Enabled** (recommended)

### Step 3: Configure App Settings
**DigitalOcean should auto-detect these settings from app.yaml:**

- **Name:** `apex-sports-trainer`
- **Runtime:** Python
- **Build Command:** Auto-detected
- **Run Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 web_app:app`
- **HTTP Port:** `8080`

### Step 4: Environment Variables
The following should be set automatically:
```bash
PORT=8080
FLASK_ENV=production
```

### Step 5: Health Check
- **Path:** `/health`
- **Timeout:** 100 seconds
- **Port:** 8080

### Step 6: Resource Configuration
- **Plan:** Basic ($5/month recommended)
- **Instance Size:** basic-xxs (512MB RAM, 1 vCPU)
- **Scaling:** 1 instance (can increase later)

---

## 🎯 Deployment Process

### During Deployment:
1. **Build Phase:** ~3-5 minutes
   - Downloads dependencies from requirements.txt
   - Installs OpenCV, MediaPipe, and other packages
   - Prepares application environment

2. **Deploy Phase:** ~1-2 minutes
   - Starts gunicorn server
   - Runs health checks
   - Makes app available

### Expected URL Format:
```
https://apex-sports-trainer-[random-hash].ondigitalocean.app
```

---

## 📋 Post-Deployment Checklist

### ✅ Immediate Tests:
1. **Health Check:** Visit `/health` endpoint
2. **Home Page:** Verify main interface loads
3. **Recording Guidance:** Check new video orientation notices
4. **Upload Form:** Ensure file upload works

### 🔍 Monitoring:
- **Build Logs:** Check for any dependency installation issues
- **Runtime Logs:** Monitor for any startup errors
- **Resource Usage:** Watch memory/CPU usage during video processing

---

## 🛠️ Configuration Details

### App.yaml Configuration:
```yaml
name: apex-sports-trainer
services:
- name: web
  source_dir: /
  github:
    repo: rickdyer20/apex-sports-trainer
    branch: master
  run_command: gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 web_app:app
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: PORT
    value: "8080"
  - key: FLASK_ENV
    value: "production"
  health_check:
    http_path: /health
```

### Key Features Deployed:
- ✅ **Full Basketball Analysis Service**
- ✅ **Video Orientation User Education System**
- ✅ **MediaPipe Pose Detection**
- ✅ **Smart Recording Guidance**
- ✅ **Portrait Video Detection**
- ✅ **Comprehensive User Interface**

---

## ⚠️ Troubleshooting

### If Build Fails:
1. Check build logs in DigitalOcean dashboard
2. Verify all dependencies in requirements.txt are compatible
3. Check Python version compatibility (using Python 3.x)

### If App Won't Start:
1. Check runtime logs for specific errors
2. Verify gunicorn command syntax
3. Ensure Flask app imports correctly

### If Health Check Fails:
1. Verify `/health` endpoint exists in web_app.py
2. Check if app is binding to correct port
3. Review timeout settings (currently 100s)

---

## 📞 Support Resources

- **DigitalOcean Docs:** https://docs.digitalocean.com/products/app-platform/
- **GitHub Repository:** https://github.com/rickdyer20/apex-sports-trainer
- **App Platform Troubleshooting:** https://docs.digitalocean.com/products/app-platform/troubleshooting/

---

## 🎉 Success Indicators

When deployment is successful, you should see:
- ✅ **Green "Running" status** in DigitalOcean dashboard
- ✅ **Accessible app URL** with basketball analysis interface
- ✅ **Working health check** at `/health`
- ✅ **Video upload functionality** with new recording guidance
- ✅ **Smart orientation detection** for portrait videos

**Ready to deploy!** 🚀
