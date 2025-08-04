# 🏠 LOCAL TESTING GUIDE - Basketball Analysis Service

## 🎯 **OVERVIEW**

Test your complete basketball analysis service locally before deploying to Google Cloud. This ensures:
- ✅ All features work correctly
- ✅ Enhanced thumb flick detection functions 
- ✅ MediaPipe processes videos properly
- ✅ Web interface is responsive
- ✅ No issues before cloud deployment

## 🔧 **QUICK START (5 minutes)**

### **Step 1: Install Dependencies**
```bash
python setup_local.py
```

### **Step 2: Run Initial Tests**  
```bash
python local_test.py
```

### **Step 3: Start Local Server**
```bash
python local_test.py --server
```

### **Step 4: Test in Browser**
1. Open: http://localhost:5000
2. Upload: test_shot.mp4 (auto-created) or your own video
3. Verify: Analysis completes successfully

## 📋 **DETAILED TESTING STEPS**

### **Phase 1: Dependency Check**
```bash
# This will verify all required packages
python local_test.py
```
**Expected Output:**
```
✅ flask
✅ cv2  
✅ mediapipe
✅ numpy
✅ reportlab
✅ psutil
✅ gunicorn
```

### **Phase 2: Import Verification**
The script automatically tests:
- Basketball analysis service imports
- Web application imports  
- MediaPipe pose detection initialization

### **Phase 3: Local Server Test**
```bash
# Start the development server
python local_test.py --server
```

**Server will start on: http://localhost:5000**

### **Phase 4: Functionality Testing**

#### **Test 1: Health Endpoint**
```bash
# In another terminal:
python local_test.py --health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "service": "Basketball Shot Analysis"
}
```

#### **Test 2: Web Interface**
1. Visit: http://localhost:5000
2. Should see: Basketball analysis upload form
3. Upload: A basketball shot video
4. Verify: Analysis starts and completes

#### **Test 3: Enhanced Thumb Flick Detection**
1. Upload a video with guide hand movement
2. Check analysis results for:
   - "Guide hand thumb flick" detection
   - 25° threshold mentioned in logs
   - Camera angle considerations

## 🎥 **TEST VIDEOS**

### **Auto-Generated Test Video**
- **File**: test_shot.mp4 (created automatically)
- **Content**: Simple stick figure animation
- **Purpose**: Basic functionality test

### **Real Video Testing**
Upload your own basketball videos to test:
- Different camera angles
- Various shooting forms
- Guide hand movements (for thumb flick detection)

## 🔍 **TROUBLESHOOTING**

### **Common Issues:**

#### **Import Errors**
```bash
# If you see import errors:
pip install -r requirements_gcloud.txt

# Or install specific packages:
pip install mediapipe opencv-python-headless flask
```

#### **MediaPipe Issues**
```bash
# If MediaPipe fails to initialize:
pip uninstall mediapipe
pip install mediapipe>=0.10.0
```

#### **Port Already in Use**
```bash
# If port 5000 is busy, modify local_test.py:
app.run(host='0.0.0.0', port=5001, debug=True)
```

## ✅ **SUCCESS CRITERIA**

### **Your local test is successful if:**
- ✅ All dependencies install without errors
- ✅ Server starts on http://localhost:5000
- ✅ Health endpoint returns JSON response
- ✅ Web interface loads properly
- ✅ Video upload and analysis works
- ✅ Enhanced thumb flick detection shows in results
- ✅ No critical errors in console

## 🚀 **AFTER LOCAL TESTING**

### **If Local Tests Pass:**
1. **Commit your verified code**
2. **Proceed with Google Cloud deployment**
3. **Use the working local setup as reference**

### **If Local Tests Fail:**
1. **Fix issues locally first**
2. **Re-test until everything works**
3. **Then deploy to cloud**

## 📊 **PERFORMANCE EXPECTATIONS**

### **Local Performance:**
- **Small videos (1-5MB)**: 10-30 seconds
- **Medium videos (5-15MB)**: 30-90 seconds
- **Large videos (15-30MB)**: 1-3 minutes

### **Memory Usage:**
- **Peak usage**: 1-2GB during analysis
- **Idle usage**: ~200MB

---

## 🎯 **READY TO TEST?**

**Run these commands in order:**

```bash
# 1. Setup dependencies
python setup_local.py

# 2. Run tests
python local_test.py

# 3. Start server
python local_test.py --server

# 4. Test in browser: http://localhost:5000
```

**Once local testing passes, you'll be confident your app works perfectly for Google Cloud deployment!** 🏀
