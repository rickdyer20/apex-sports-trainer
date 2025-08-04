# 🚀 AWS DEPLOYMENT GUIDE - Full Basketball Analysis Service

## 🎯 **Why AWS for Full App**
- ✅ **No dependency restrictions** like Render
- ✅ **More memory/CPU** for MediaPipe processing
- ✅ **Custom Docker containers** supported
- ✅ **Auto-scaling** for video processing
- ✅ **Professional production environment**

## 📋 **AWS Deployment Options**

### **Option 1: AWS App Runner (RECOMMENDED - Easiest)**
```bash
# Similar to Render but more powerful
- Direct GitHub integration
- Automatic scaling
- 2GB RAM / 1 vCPU (vs Render's 512MB)
- Full Docker support
- ~$25-50/month for production usage
```

### **Option 2: AWS Elastic Beanstalk**
```bash
# Platform-as-a-service with full control
- Python 3.12 support
- Custom requirements.txt
- Environment variables
- Load balancing
- ~$20-40/month
```

### **Option 3: AWS ECS + Fargate (Most Professional)**
```bash
# Containerized deployment
- Full Docker control
- Microservices architecture
- Auto-scaling based on load
- ~$30-60/month
```

## 🔧 **DEPLOYMENT PLAN**

### **Step 1: Prepare Full Requirements**
```txt
# Full-featured requirements.txt for AWS
Flask==3.0.0
gunicorn==21.2.0
opencv-python-headless>=4.8.0,<5.0.0
mediapipe>=0.10.0,<0.11.0
numpy>=1.24.0,<2.0.0
reportlab>=4.0.0,<5.0.0
psutil>=5.9.0,<6.0.0
cryptography>=41.0.0
python-dotenv>=1.0.0
Werkzeug==3.0.1
itsdangerous>=2.1.0
Jinja2>=3.1.0
MarkupSafe>=2.1.0
click>=8.1.0
```

### **Step 2: AWS App Runner Deployment**
```yaml
# apprunner.yaml
version: 1.0
runtime: python312
build:
  commands:
    build:
      - pip install -r requirements.txt
run:
  runtime-version: 3.12
  command: gunicorn --workers 2 --timeout 180 --bind 0.0.0.0:8000 wsgi:application
  network:
    port: 8000
    env: PORT
  env:
    - name: FLASK_ENV
      value: production
    - name: PYTHONPATH
      value: /app
```

### **Step 3: Create Dockerfile (for ECS option)**
```dockerfile
FROM python:3.12-slim

# Install system dependencies for MediaPipe
RUN apt-get update && apt-get install -y \\
    libglib2.0-0 \\
    libsm6 \\
    libxext6 \\
    libxrender-dev \\
    libgomp1 \\
    libglib2.0-0 \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["gunicorn", "--workers", "2", "--timeout", "180", "--bind", "0.0.0.0:8000", "wsgi:application"]
```

## 📊 **Cost Comparison**

| Platform | Memory | Processing | Cost/Month | MediaPipe |
|----------|--------|------------|------------|-----------|
| Render Starter | 512MB | Limited | $7 | ❌ Fails |
| AWS App Runner | 2GB | Good | $25-40 | ✅ Works |
| AWS Beanstalk | 2GB+ | Good | $20-35 | ✅ Works |
| AWS ECS | 4GB+ | Excellent | $30-50 | ✅ Works |

## 🚀 **IMMEDIATE NEXT STEPS**

### **Quick Start with App Runner:**
1. **Create AWS account** (free tier available)
2. **Go to App Runner console**
3. **Connect your GitHub repo** (`apex-sports-trainer`)
4. **Use full requirements.txt**
5. **Deploy with 2GB memory allocation**

### **Expected Results:**
- ✅ **Full MediaPipe support**
- ✅ **Complete basketball analysis**
- ✅ **PDF report generation**
- ✅ **Professional deployment**
- ✅ **Auto-scaling capabilities**

---
**Want me to help you set up AWS App Runner step-by-step?**
