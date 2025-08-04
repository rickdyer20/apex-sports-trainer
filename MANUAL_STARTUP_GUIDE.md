# 🚨 MANUAL STARTUP GUIDE - PAGE WON'T OPEN

## 🔍 **Current Status**
- ✅ Requirements.txt restored with MediaPipe
- ✅ Web app imports successfully  
- ✅ All dependencies available
- ❌ Server still won't start through VS Code terminal

## 🚀 **MANUAL STARTUP METHODS**

### Method 1: Windows Command Prompt (RECOMMENDED)
1. Open **Windows Command Prompt** (not VS Code terminal)
2. Navigate to your project:
   ```cmd
   cd c:\basketball_analysis\New_Shot_AI
   ```
3. Start the server:
   ```cmd
   python web_app.py
   ```

### Method 2: PowerShell (Outside VS Code)
1. Open **Windows PowerShell** (not VS Code terminal)
2. Navigate to project:
   ```powershell
   cd "c:\basketball_analysis\New_Shot_AI"
   ```
3. Start server:
   ```powershell
   python web_app.py
   ```

### Method 3: Direct Python Script
1. Run the direct start script:
   ```cmd
   python direct_start.py
   ```

### Method 4: Flask Command Line
1. Set environment variable:
   ```cmd
   set FLASK_APP=web_app.py
   ```
2. Start Flask:
   ```cmd
   python -m flask run --host=127.0.0.1 --port=5000
   ```

## 🌐 **Expected Output**

When working, you should see:
```
🏀 Basketball Analysis Service Starting...
📍 Server starting at: http://127.0.0.1:5000
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

Then open your browser to: **http://127.0.0.1:5000**

## 🔧 **If Still Not Working**

### Check 1: Verify Dependencies
```cmd
python -c "import flask, cv2, mediapipe, numpy; print('All OK')"
```

### Check 2: Test Different Port
```cmd
python -c "from web_app import app; app.run(host='127.0.0.1', port=8000)"
```
Then try: http://127.0.0.1:8000

### Check 3: Emergency Server
```cmd
python emergency_server.py
```
This will start a diagnostic server and show exact errors.

## 🎯 **Why VS Code Terminal May Be Failing**

VS Code's integrated terminal sometimes has issues with:
- Background process management
- Port binding conflicts
- Output buffering
- Flask's development server startup

Using an external command prompt often resolves these issues.

## 📋 **Step-by-Step Troubleshooting**

1. **Close VS Code completely**
2. **Open Windows Command Prompt**
3. **Navigate to your project folder**
4. **Run: python web_app.py**
5. **Open browser to http://127.0.0.1:5000**

## 🚨 **Emergency Fallback**

If nothing works, create this minimal test file:

**test_flask.py:**
```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Basketball Analysis Test</h1><p>Flask is working!</p>'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
```

Run with: `python test_flask.py`

This will confirm Flask can start a server on your system.

## 📞 **What You Should See**

Once working:
- Basketball analysis interface loads
- Video upload form appears
- Enhanced thumb flick detection ready
- All 12+ flaw detection types active

Try the external command prompt method - this often resolves VS Code terminal issues!
