# 🔄 UPDATING EXISTING RENDER SERVICE

## If You Already Created `apex-sports-trainer` on Render

### 🔍 **First, Check Your Current Service Status**

1. **Go to Render Dashboard** → Find your `apex-sports-trainer` service
2. **Check the Service Type**:
   - If it says **"Web Service"** ✅ → Good, proceed with Option A
   - If it says **"Docker"** or you see Docker errors → Use Option B

3. **Check Current Status**:
   - **"Deploy succeeded"** → Your service is working, test it
   - **"Deploy failed"** → Follow the update steps below
   - **"Building"** → Wait for it to complete, then assess

---

## 🎯 **Option A: Update Existing Web Service (RECOMMENDED)**

**If your service is a "Web Service" type, you can update it:**

### **Step 1: Update Service Settings**

1. **Go to your service** → Click **"Settings"** tab
2. **Update Build & Start Commands**:
   ```
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --workers 2 --timeout 180 --bind 0.0.0.0:$PORT wsgi:application
   ```
3. **Click "Save Changes"**

### **Step 2: Update Environment Variables**

1. **Go to "Environment"** tab
2. **Add/Update these variables**:
   ```
   FLASK_ENV=production
   FLASK_DEBUG=False
   PORT=8080
   TF_CPP_MIN_LOG_LEVEL=2
   TF_ENABLE_ONEDNN_OPTS=0
   MEDIAPIPE_DISABLE_GPU=1
   CUDA_VISIBLE_DEVICES=""
   ```
3. **Click "Save Changes"**

### **Step 3: Trigger New Deployment**

1. **Go to "Deploys"** tab
2. **Click "Deploy Latest Commit"** OR
3. **Push a small change** to trigger auto-deploy:
   ```bash
   # Make a small change to trigger redeploy
   echo "# Updated for buildpack deployment" >> README.md
   git add README.md
   git commit -m "Trigger buildpack deployment update"
   git push origin master
   ```

---

## 🗑️ **Option B: Delete and Recreate (If Docker/Failed)**

**If your service was created with Docker or keeps failing:**

### **Step 1: Delete Current Service**
1. **Go to your service** → **"Settings"** tab
2. **Scroll down** → **"Delete Service"**
3. **Type service name** to confirm → **Delete**

### **Step 2: Create New Web Service**
1. **Click "New +"** → **"Web Service"**
2. **Connect GitHub** → Select `apex-sports-trainer`
3. **Use buildpack settings** from previous guide:
   ```
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --workers 2 --timeout 180 --bind 0.0.0.0:$PORT wsgi:application
   ```

---

## 🔄 **Option C: Keep Both (Different Names)**

**If you want to keep the old one as backup:**

### **Create a New Service with Different Name**
1. **Click "New +"** → **"Web Service"**
2. **Name it**: `basketball-analysis-v2` or `basketball-prod`
3. **Connect same repository** (`apex-sports-trainer`)
4. **Use buildpack deployment** settings

---

## 🚨 **Common Issues with Existing Services**

### **Issue 1: Service is Docker-Based**
**Symptoms**: Build logs show Docker commands, longer build times
**Solution**: Use Option B (delete and recreate) or Option C (new service)

### **Issue 2: Wrong Build/Start Commands**
**Symptoms**: "Web service failed to bind to $PORT"
**Solution**: Update commands in Settings (Option A, Step 1)

### **Issue 3: Missing Environment Variables**
**Symptoms**: Service starts but health check fails
**Solution**: Add environment variables (Option A, Step 2)

### **Issue 4: Old Requirements Cached**
**Symptoms**: Build succeeds but import errors at runtime
**Solution**: 
1. **Settings** → **"Clear Build Cache"**
2. **Deploy Latest Commit**

---

## ✅ **How to Verify Your Update Worked**

### **Check Build Logs**
Look for these signs of successful buildpack deployment:
```
Building...
-----> Python app detected
-----> Installing Python 3.11
-----> Installing requirements from requirements.txt
-----> Build completed successfully
Starting...
-----> Running: gunicorn --workers 2 --timeout 180 --bind 0.0.0.0:$PORT wsgi:application
Deploy succeeded
```

### **Test Health Endpoint**
```bash
curl https://apex-sports-trainer.onrender.com/health
# OR use your actual service URL
```

### **Check Service Performance**
- **Memory usage**: Should stay under 400MB
- **Response time**: Health check should respond in <2 seconds
- **No Docker overhead**: Faster startup times

---

## 🎯 **My Recommendation**

**Based on your situation:**

1. **If current service is failing** → **Option A** (update existing)
2. **If it's Docker-based** → **Option B** (delete and recreate)
3. **If you want to be safe** → **Option C** (create new one)

**Option A is usually best** because:
- ✅ Keeps your service URL
- ✅ Maintains any custom domain settings  
- ✅ Preserves deployment history
- ✅ No service interruption

---

## 📞 **Next Steps**

1. **Check your current service status** in Render dashboard
2. **Choose the appropriate option** based on what you see
3. **Follow the steps** for your chosen option
4. **Test the deployment** with health endpoint

**🏀 Let me know what you see in your Render dashboard and I'll help you choose the best path forward!**
