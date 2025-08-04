# 🏀 LOCAL HOST SETUP GUIDE

## 🚀 START YOUR BASKETBALL ANALYSIS SERVICE LOCALLY

You have several options to run your basketball analysis service on localhost:

### ⚡ QUICK START (Choose One)

#### Option 1: Direct Python Command
```bash
python web_app.py
```

#### Option 2: Flask Command
```bash
python -m flask --app web_app run --host=127.0.0.1 --port=5000 --debug
```

#### Option 3: Custom Starter Script
```bash
python run_local_server.py
```

#### Option 4: Windows Batch File (Double-click)
```
start_local_server.bat
```

## 🌐 ACCESS YOUR APP

Once started, open your web browser and go to:
**http://127.0.0.1:5000**

You'll see your basketball analysis interface where you can:
- Upload basketball shot videos (MP4, AVI, MOV, MKV)
- Get real-time analysis with 12+ flaw detection types
- Download PDF reports with detailed feedback
- See enhanced thumb flick detection in action

## 🎯 TEST YOUR ENHANCED FEATURES

### Upload a Basketball Video
1. Click "Choose File" or drag & drop a video
2. Click "Analyze Shot"
3. Watch the real-time progress
4. Download your analysis results

### Verify Thumb Flick Detection
- Upload a video with obvious thumb flick motion
- Check that it's detected with the new 25° threshold
- Confirm it works from multiple camera angles

## 📊 EXPECTED LOCAL PERFORMANCE

- **Video Upload**: Instant (up to 100MB files)
- **Analysis Time**: 30-60 seconds for typical videos
- **Memory Usage**: 2-4GB during processing
- **CPU Usage**: Moderate (MediaPipe optimized)

## 🔧 TROUBLESHOOTING

### If Server Won't Start:
```bash
# Check dependencies
python -c "import flask, cv2, mediapipe; print('Dependencies OK')"

# Check if port is available
netstat -an | findstr :5000
```

### If Page Doesn't Load:
- Make sure you're going to http://127.0.0.1:5000 (not localhost:5000)
- Check that the server started without errors
- Try a different port: `python -m flask --app web_app run --port=8000`

### If Analysis Fails:
- Ensure video file is under 100MB
- Use supported formats: MP4, AVI, MOV, MKV
- Check that MediaPipe is properly installed

## 🏀 YOUR LOCAL SERVICE FEATURES

✅ **Enhanced Thumb Flick Detection** (25° threshold)
✅ **12+ Flaw Types**: Elbow flare, knee bend, follow-through, etc.
✅ **Multiple Camera Angles**: Front, side, angled views supported
✅ **Real-time Progress**: See analysis status live
✅ **Professional Reports**: Downloadable PDF with detailed feedback
✅ **Video Analysis**: Slow-motion overlays with coaching tips

## 🎉 READY TO ANALYZE!

Your basketball analysis service is ready to help players improve their shooting form with professional-grade biomechanical analysis!

To stop the server: Press **Ctrl+C** in the terminal
