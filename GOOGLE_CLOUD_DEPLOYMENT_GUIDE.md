# 🌟 GOOGLE CLOUD DEPLOYMENT GUIDE - Full Basketball Analysis Service

## 🎯 **Why Google Cloud for Full App**
- ✅ **Native MediaPipe support** (Google-created library)
- ✅ **Cloud Run**: Serverless container deployment
- ✅ **4GB+ memory allocation** available
- ✅ **Auto-scaling** based on demand
- ✅ **Pay-per-use** pricing model
- ✅ **Excellent for ML workloads**

## 📋 **Google Cloud Deployment Options**

### **Option 1: Cloud Run (HIGHLY RECOMMENDED)**
```bash
# Serverless container platform
- Direct Docker deployment
- Auto-scaling 0-1000 instances
- Up to 8GB RAM per instance
- MediaPipe optimized infrastructure
- Pay only when processing videos
- ~$10-30/month for typical usage
```

### **Option 2: App Engine Flexible**
```bash
# Platform-as-a-service
- Custom Docker runtime
- Always-on instances
- 4GB+ memory available
- ~$50-100/month
```

### **Option 3: Google Kubernetes Engine (GKE)**
```bash
# Full container orchestration
- Professional microservices
- Horizontal pod autoscaling
- ~$70-150/month
```

## 🚀 **CLOUD RUN DEPLOYMENT (RECOMMENDED)**

### **Step 1: Create Full Dockerfile**
```dockerfile
# Dockerfile optimized for Google Cloud Run
FROM python:3.12-slim

# Install system dependencies for MediaPipe and OpenCV
RUN apt-get update && apt-get install -y \\
    libglib2.0-0 \\
    libsm6 \\
    libxext6 \\
    libxrender-dev \\
    libgomp1 \\
    libgl1-mesa-glx \\
    libglib2.0-0 \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements_full_cloud.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Cloud Run uses PORT environment variable)
EXPOSE 8080

# Use environment PORT or default to 8080
ENV PORT=8080

# Start gunicorn with Cloud Run optimizations
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 wsgi:application
```

### **Step 2: Full Cloud Requirements**
```txt
# requirements_full_cloud.txt - Optimized for Google Cloud
Flask==3.0.0
gunicorn==21.2.0

# Computer Vision (Google Cloud optimized)
opencv-python-headless>=4.8.0,<5.0.0
mediapipe>=0.10.0,<0.11.0
numpy>=1.24.0,<2.0.0

# Analysis and Reports
reportlab>=4.0.0,<5.0.0
psutil>=5.9.0,<6.0.0

# Security and Flask ecosystem
cryptography>=41.0.0
python-dotenv>=1.0.0
Werkzeug==3.0.1
itsdangerous>=2.1.0
Jinja2>=3.1.0
MarkupSafe>=2.1.0
click>=8.1.0

# Google Cloud specific optimizations
google-cloud-storage>=2.10.0  # For video storage
google-cloud-logging>=3.8.0   # For centralized logging
```

### **Step 3: Cloud Run Deployment Commands**
```bash
# 1. Install Google Cloud CLI
# Download from: https://cloud.google.com/sdk/docs/install

# 2. Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 3. Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# 4. Deploy directly from GitHub
gcloud run deploy basketball-analysis \\
  --source https://github.com/rickdyer20/apex-sports-trainer \\
  --platform managed \\
  --region us-central1 \\
  --memory 4Gi \\
  --cpu 2 \\
  --timeout 900 \\
  --concurrency 10 \\
  --max-instances 5 \\
  --allow-unauthenticated

# 5. Get your service URL
gcloud run services describe basketball-analysis --region us-central1
```

## 📊 **Cost Comparison - Google Cloud vs Others**

| Platform | Memory | CPU | Timeout | Cost/Month | MediaPipe |
|----------|--------|-----|---------|------------|-----------|
| Render | 512MB | 0.5 | 180s | $7 | ❌ |
| AWS App Runner | 2GB | 1 | 300s | $25-40 | ✅ |
| **Google Cloud Run** | **4GB** | **2** | **900s** | **$10-30** | **✅✅** |

### **Google Cloud Run Advantages:**
- ✅ **Pay per request** (not per hour)
- ✅ **Native MediaPipe optimization**
- ✅ **Auto-scale to zero** (no idle costs)
- ✅ **Massive processing capacity**
- ✅ **15-minute video processing timeout**

## 🔧 **IMPLEMENTATION STEPS**

### **Phase 1: Quick Deploy (5 minutes)**
```bash
# Create requirements_full_cloud.txt with all dependencies
# Use Cloud Run's source deployment feature
# Deploy directly from your GitHub repo
```

### **Phase 2: Optimize (Optional)**
```bash
# Add Cloud Storage for large video files
# Enable Cloud Logging for monitoring
# Set up Cloud Scheduler for batch processing
```

### **Phase 3: Scale (If needed)**
```bash
# Configure auto-scaling rules
# Add Cloud CDN for global distribution
# Set up Cloud Load Balancing
```

## 🎯 **IMMEDIATE ACTION PLAN**

### **Option A: Google Cloud Run (RECOMMENDED)**
- **Best for**: Full MediaPipe support, cost-effective scaling
- **Setup time**: 15 minutes
- **Monthly cost**: $10-30
- **Supports**: All your basketball analysis features

### **Option B: AWS App Runner**
- **Best for**: Familiar GitHub integration
- **Setup time**: 20 minutes  
- **Monthly cost**: $25-40
- **Supports**: All features with more memory

---

**Which platform would you like to try first? I can walk you through the exact deployment steps for either Google Cloud Run or AWS App Runner!**
