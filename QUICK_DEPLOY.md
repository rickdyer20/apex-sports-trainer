# 🚀 Quick Deployment Reference Card

## Essential Pre-Deployment Commands

```bash
# 1. Verify deployment readiness
python deployment_checklist.py

# 2. Commit all changes to Git
git add .
git commit -m "Ready for Render deployment - Starter Plan optimized"
git push origin master

# 3. Verify key files exist
ls -la Procfile requirements.txt wsgi.py web_app.py basketball_analysis_service.py
```

## Render Dashboard Setup (5 minutes)

1. **Create Account**: [render.com](https://render.com) → Sign up with GitHub
2. **New Service**: Dashboard → "New +" → "Web Service"  
3. **Connect Repo**: Select `apex-sports-trainer` repository
4. **Plan Selection**: Choose **Starter ($7/month)**
5. **Auto-Deploy**: ✅ Enable

## Essential Environment Variables

Copy these to Render Dashboard → Environment tab:

```bash
# Required
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-here

# Starter Plan Optimized  
MAX_PROCESSING_TIME=180
FRAME_SKIP=2
MAX_CONCURRENT_JOBS=3

# Performance
TF_ENABLE_ONEDNN_OPTS=0
TF_CPP_MIN_LOG_LEVEL=2
```

## Build Configuration

```yaml
Build Command: pip install -r requirements.txt
Start Command: gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 180
```

## Post-Deployment Verification

```bash
# 1. Check health endpoint
curl https://your-app-name.onrender.com/health

# 2. Expected response
{
  "status": "healthy",
  "memory_usage": "25%",
  "active_jobs": 0
}

# 3. Test file upload with small video (<5MB)
```

## Troubleshooting Quick Fixes

**Build Fails?**
- Check requirements.txt for typos
- Ensure opencv-python-headless (not opencv-python)

**Service Crashes?**  
- Check Render logs for import errors
- Verify all environment variables set
- Try smaller test video first

**Memory Issues?**
- Reduce MAX_CONCURRENT_JOBS to 2 or 1
- Increase FRAME_SKIP to 3
- Monitor /health endpoint

## Success Indicators

✅ Health endpoint returns 200 OK  
✅ Can upload and process 5MB video  
✅ Memory usage stays below 80%  
✅ Processing completes within timeout  

## Support Resources

- **Full Guide**: See `DEPLOYMENT_GUIDE.md` 
- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Health Check**: `https://your-app.onrender.com/health`

---

**🎯 Deployment Time: ~10 minutes for experienced users, ~30 minutes first time**
