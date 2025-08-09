# 🏀 Deploy to apexsports-llc.com - Complete Guide

## 🎯 **Domain Deployment for Enhanced Basketball Analysis Service**

This guide covers deploying your fully enhanced basketball analysis service with all new features (shoulder alignment detection, optimized frame selection, stricter knee bend detection, improved wrist snap analysis, and complete Stripe payment system) to your production domain `apexsports-llc.com`.

## 📊 **Enhanced Features Ready for Production**

### ✅ **New Features Included**
- **Shoulder Alignment Detection** - NEW biomechanical analysis
- **Optimized Frame Selection** - Better coaching value for elbow flare/guide hand
- **Stricter Knee Bend Detection** - 130° threshold for better accuracy
- **Enhanced Wrist Snap Analysis** - Conservative detection with detailed methodology
- **Complete Stripe Payment System** - 523-line payment manager with subscriptions
- **PDF Generation with Error Handling** - Robust 60-day improvement plans
- **Feature Flag System** - Easy enable/disable for new features

## 🚀 **Deployment Options for apexsports-llc.com**

### Option 1: **Railway (Recommended - Easiest)**
```bash
# Quick deploy with automatic domain setup
python deploy_railway.py
```

### Option 2: **DigitalOcean App Platform**
```bash
# Professional hosting with domain integration
python deploy_production.py --platform=digitalocean
```

### Option 3: **Docker + VPS**
```bash
# Maximum control with custom VPS
docker build -t apex-basketball-service .
docker run -d -p 80:8080 apex-basketball-service
```

## 🔧 **Pre-Deployment Setup**

### 1. **Environment Configuration**
Create production `.env` file:
```bash
# Run the interactive setup
python setup_stripe.py

# Or create manually with your production values:
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
FLASK_ENV=production
FLASK_DEBUG=False
FRONTEND_URL=https://apexsports-llc.com
SECRET_KEY=your-super-secure-production-key
ENABLE_SHOULDER_ALIGNMENT_DETECTION=True
```

### 2. **Domain DNS Setup**
Point your domain to the deployment platform:

**For Railway:**
- Add CNAME record: `www.apexsports-llc.com` → `your-app.railway.app`
- Add A record: `apexsports-llc.com` → Railway IP

**For DigitalOcean:**
- Add A record: `apexsports-llc.com` → DigitalOcean IP
- Add CNAME record: `www.apexsports-llc.com` → `apexsports-llc.com`

### 3. **SSL Certificate**
Most platforms auto-provision Let's Encrypt certificates for custom domains.

## 📦 **Deployment Steps**

### **Option 1: Railway Deployment (Recommended)**

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
railway login
```

2. **Deploy Service**
```bash
# Initialize railway project
railway init

# Set environment variables
railway variables set STRIPE_PUBLISHABLE_KEY=pk_live_...
railway variables set STRIPE_SECRET_KEY=sk_live_...
railway variables set FLASK_ENV=production
railway variables set FRONTEND_URL=https://apexsports-llc.com
railway variables set ENABLE_SHOULDER_ALIGNMENT_DETECTION=True

# Deploy
railway up
```

3. **Add Custom Domain**
```bash
# In Railway dashboard:
# Settings → Domains → Add Domain → apexsports-llc.com
```

### **Option 2: DigitalOcean App Platform**

1. **Create App Spec**
```bash
# Use deploy_production.py to generate app spec
python deploy_production.py --platform=digitalocean --domain=apexsports-llc.com
```

2. **Deploy via CLI**
```bash
# Install doctl CLI
doctl apps create --spec app.yaml

# Or deploy via web interface:
# Upload your repository to GitHub
# Connect DigitalOcean to your GitHub repo
# Configure domain in DigitalOcean dashboard
```

### **Option 3: Docker + VPS**

1. **Prepare VPS**
```bash
# On your VPS (Ubuntu/Debian):
sudo apt update
sudo apt install docker.io nginx certbot

# Configure Nginx reverse proxy
sudo nano /etc/nginx/sites-available/apexsports-llc.com
```

2. **Deploy Container**
```bash
# Build and run
docker build -t apex-basketball-service .
docker run -d \
  --name basketball-service \
  -p 127.0.0.1:8080:8080 \
  -e STRIPE_PUBLISHABLE_KEY=pk_live_... \
  -e STRIPE_SECRET_KEY=sk_live_... \
  -e FLASK_ENV=production \
  -e FRONTEND_URL=https://apexsports-llc.com \
  -e ENABLE_SHOULDER_ALIGNMENT_DETECTION=True \
  apex-basketball-service
```

3. **Setup SSL**
```bash
# Get SSL certificate
sudo certbot --nginx -d apexsports-llc.com -d www.apexsports-llc.com
```

## 🔐 **Production Security Setup**

### 1. **Stripe Configuration**
```bash
# In Stripe Dashboard:
# 1. Switch to Live mode
# 2. Add webhook endpoint: https://apexsports-llc.com/webhook/stripe
# 3. Select events: checkout.session.completed, customer.subscription.*
# 4. Copy webhook secret to STRIPE_WEBHOOK_SECRET
```

### 2. **Environment Security**
```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Set in production environment:
SECRET_KEY=your-generated-32-character-hex-key
```

### 3. **Domain Security**
- Enable HTTPS redirect
- Set secure headers
- Configure CORS for your domain only

## 📊 **Feature Validation Checklist**

Before going live, test these enhanced features:

### ✅ **Shoulder Alignment Detection**
- [ ] Upload video with poor shoulder squaring → Should detect and provide coaching
- [ ] Upload video with good alignment → Should not flag false positives
- [ ] Verify feature can be disabled with flag if needed

### ✅ **Enhanced Frame Selection**
- [ ] Elbow flare detection shows frame during Load/Dip phase (instructional value)
- [ ] Guide hand positioning captured during ball control phases
- [ ] Frame stills clearly demonstrate the detected flaws

### ✅ **Stricter Knee Bend Detection**
- [ ] 130° threshold properly flags insufficient knee bend
- [ ] Previously acceptable 131°-135° range now triggers detection
- [ ] Coaching feedback provides clear improvement guidance

### ✅ **Wrist Snap Analysis**
- [ ] Conservative < 50° threshold only flags serious issues
- [ ] Peak Follow-Through timing (±2 frames) working correctly
- [ ] 70°-90° ideal range documented in coaching feedback

### ✅ **Stripe Payment System**
- [ ] Free tier: 3 analyses per month
- [ ] Pro tier: Unlimited analyses + PDF reports
- [ ] Enterprise tier: API access + priority support
- [ ] Subscription management working correctly
- [ ] Webhook processing subscription events

### ✅ **PDF Generation**
- [ ] 60-day improvement plans generating successfully
- [ ] Graceful error handling for missing data
- [ ] Professional formatting with coaching recommendations

## 🚨 **Rollback Plan**

If issues arise with new features:

### **Immediate Disable of New Features**
```bash
# Set environment variable to disable shoulder alignment
ENABLE_SHOULDER_ALIGNMENT_DETECTION=False

# Or use the control script
python shoulder_alignment_feature_control.py
```

### **Quick Rollback to Previous Version**
```bash
# Revert to stable version without enhancements
git checkout stable-version-tag
railway up  # or your deployment command
```

## 📈 **Monitoring & Maintenance**

### **Log Monitoring**
```bash
# Check application logs
railway logs --tail  # Railway
doctl apps logs your-app-id --tail  # DigitalOcean
docker logs basketball-service --tail  # Docker
```

### **Performance Metrics**
- Monitor video processing times
- Track memory usage during analysis
- Watch for MediaPipe initialization issues
- Monitor Stripe webhook delivery

### **Feature Usage Analytics**
- Track shoulder alignment detection rates
- Monitor PDF generation success rates
- Analyze payment conversion rates
- Review customer feedback on new features

## 🎯 **Production URLs**

After deployment, your service will be available at:
- **Main Site**: https://apexsports-llc.com
- **Video Upload**: https://apexsports-llc.com/upload
- **Payment Portal**: https://apexsports-llc.com/pricing
- **API Endpoint**: https://apexsports-llc.com/api/analyze
- **Webhook Endpoint**: https://apexsports-llc.com/webhook/stripe

## 📞 **Support & Documentation**

- **Feature Documentation**: `/SHOULDER_ALIGNMENT_FEATURE.md`
- **Payment Setup**: `/setup_stripe.py`
- **Feature Control**: `/shoulder_alignment_feature_control.py`
- **Deployment Logs**: Check platform-specific logging

---

**🚀 Ready to deploy your enhanced basketball analysis service to apexsports-llc.com!**

Choose your preferred deployment method above and follow the step-by-step instructions. All new features are production-ready with proper fallback mechanisms.
