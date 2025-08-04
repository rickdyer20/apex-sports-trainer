# 🚨 LOCALHOST NOT OPENING - TROUBLESHOOTING GUIDE

## 🔍 Step-by-Step Diagnosis

### Step 1: Test Basic Flask (Run This First)
Open PowerShell in your basketball analysis folder and run:

```powershell
python minimal_test_server.py
```

If this works, you'll see:
- Server starting message
- URL: http://127.0.0.1:5000
- Open that URL in your browser

### Step 2: Check Dependencies
```powershell
python -c "import flask; print('Flask OK'); import cv2; print('OpenCV OK'); import mediapipe; print('MediaPipe OK')"
```

### Step 3: Test Web App Import
```powershell
python -c "from web_app import app; print('Web app imported successfully')"
```

### Step 4: Check Port Availability
```powershell
netstat -an | findstr :5000
```
(Should show nothing if port is free)

## 🚀 Alternative Startup Methods

### Method 1: Direct Python
```powershell
python web_app.py
```

### Method 2: Flask Command
```powershell
$env:FLASK_APP="web_app.py"
python -m flask run --host=127.0.0.1 --port=5000
```

### Method 3: Different Port
```powershell
python -c "from web_app import app; app.run(host='127.0.0.1', port=8000)"
```

### Method 4: Batch File
Double-click: `start_local_server.bat`

## 🔧 Common Issues & Solutions

### Issue 1: "Module not found" errors
**Solution:** Install missing dependencies
```powershell
pip install flask opencv-python-headless mediapipe numpy reportlab pillow
```

### Issue 2: Port already in use
**Solution:** Try different port
```powershell
python -c "from web_app import app; app.run(host='127.0.0.1', port=8000)"
```
Then open: http://127.0.0.1:8000

### Issue 3: Import errors in web_app.py
**Solution:** Run diagnostic
```powershell
python debug_localhost.py
```

### Issue 4: Windows Firewall blocking
**Solution:** 
1. Windows Security → Firewall & network protection
2. Allow an app through firewall
3. Add Python.exe

### Issue 5: Browser cache issues
**Solution:**
1. Try incognito/private browsing
2. Clear browser cache
3. Try different browser

## 📋 Manual Verification Steps

### 1. Verify Current Directory
```powershell
pwd
dir web_app.py
```
Should show you're in the basketball analysis folder with web_app.py present.

### 2. Test Minimal Server
```powershell
python minimal_test_server.py
```
This should definitely work and open at http://127.0.0.1:5000

### 3. Check Basketball Service
```powershell
python -c "from basketball_analysis_service import BasketballAnalysisService; print('Service OK')"
```

## 🎯 Expected Behavior

When working correctly, you should see:
```
🏀 Basketball Analysis Service Starting...
📍 Server starting at: http://127.0.0.1:5000
📝 Upload basketball shot videos for analysis
🎯 Enhanced thumb flick detection active (25° threshold)
⚡ Starting Flask server...
 * Running on http://127.0.0.1:5000
```

Then opening http://127.0.0.1:5000 shows the basketball analysis interface.

## 📞 If Nothing Works

Try this emergency fallback:
```powershell
python -c "
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Basketball Analysis Test</h1><p>Basic Flask working!</p>'

app.run(host='127.0.0.1', port=5000)
"
```

This will at least confirm Flask can start a server on your system.

## 🔄 Next Steps After Testing

1. **If minimal test works:** Your system is fine, issue is with main app
2. **If minimal test fails:** System/dependency issue, check Python installation  
3. **If port issues:** Try different ports (8000, 3000, 5001)
4. **If still stuck:** Run `python debug_localhost.py` for detailed diagnosis

Let me know which step fails and I can provide more specific help!
