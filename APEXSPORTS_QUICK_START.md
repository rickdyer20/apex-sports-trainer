# 🏀 APEX Sports LLC - Quick Deployment Checklist

## ✅ **Ready to Deploy to apexsports-llc.com**

Your enhanced basketball analysis service with all new features is ready for production deployment!

### 🎯 **What's Included in This Deployment**

- ✅ **Shoulder Alignment Detection** - NEW biomechanical analysis feature
- ✅ **Enhanced Frame Selection** - Better coaching value for elbow flare/guide hand
- ✅ **Stricter Knee Bend Detection** - 130° threshold for improved accuracy  
- ✅ **Advanced Wrist Snap Analysis** - Conservative detection with detailed methodology
- ✅ **Complete Stripe Payment System** - Full subscription management (Free/Pro/Enterprise)
- ✅ **Robust PDF Generation** - 60-day improvement plans with error handling
- ✅ **Feature Flag System** - Easy enable/disable for new features

### 🚀 **Quick Start - 3 Simple Steps**

#### **Step 1: Configure Production Environment**
```bash
python setup_stripe.py
# Select LIVE mode and enter your production Stripe keys
# Set FRONTEND_URL to: https://apexsports-llc.com
```

#### **Step 2: Deploy to Your Hosting Platform**
```bash
python deploy_to_apexsports.py
# Choose your preferred deployment method:
# 1. Railway (easiest)
# 2. DigitalOcean (professional)  
# 3. Docker (custom VPS)
```

#### **Step 3: Configure Domain**
- Update DNS records to point to your hosting platform
- Set up SSL certificate (usually automatic)
- Configure Stripe webhook: `https://apexsports-llc.com/webhook/stripe`

### 🎛️ **Platform-Specific Quick Deploy**

#### **Railway (Recommended)**
```bash
# Install CLI
npm install -g @railway/cli

# Deploy
railway login
python deploy_to_apexsports.py
# Choose option 1

# Add domain in Railway dashboard
# Settings → Domains → Add Domain → apexsports-llc.com
```

#### **DigitalOcean App Platform**
```bash
# Create app from GitHub repo
# Connect your apex-sports-trainer repository
# Set environment variables in dashboard
# Add domain: apexsports-llc.com
```

#### **Docker + VPS**
```bash
# Build and deploy
docker build -t apex-basketball-service .
docker run -d -p 80:8080 \
  -e STRIPE_PUBLISHABLE_KEY=pk_live_... \
  -e STRIPE_SECRET_KEY=sk_live_... \
  -e FLASK_ENV=production \
  -e FRONTEND_URL=https://apexsports-llc.com \
  apex-basketball-service
```

### 🔐 **Production Security Checklist**

- [ ] Live Stripe keys configured (not test keys)
- [ ] Strong SECRET_KEY generated and set
- [ ] HTTPS enabled and redirects configured
- [ ] Stripe webhook endpoint configured: `/webhook/stripe`
- [ ] Environment variables secured (not in code)
- [ ] DNS configured for apexsports-llc.com

### 🧪 **Post-Deployment Testing**

Test these features after deployment:

- [ ] **Video Upload & Analysis** - Upload basketball shot video
- [ ] **Shoulder Alignment Detection** - Test with angled shooting stance
- [ ] **Payment System** - Test subscription flows (use Stripe test mode first)
- [ ] **PDF Generation** - Generate improvement plan PDF
- [ ] **Frame Selection** - Verify coaching-valuable frames captured
- [ ] **Mobile Responsiveness** - Test on mobile devices

### 🌐 **Your Production URLs**

After deployment:
- **Main Site**: https://apexsports-llc.com
- **Upload Portal**: https://apexsports-llc.com/upload  
- **Pricing Page**: https://apexsports-llc.com/pricing
- **Payment Webhook**: https://apexsports-llc.com/webhook/stripe

### 🆘 **Emergency Controls**

If issues arise with new features:

#### **Disable Shoulder Alignment Detection**
```bash
# Set environment variable
ENABLE_SHOULDER_ALIGNMENT_DETECTION=False

# Or use control script
python shoulder_alignment_feature_control.py
```

#### **Quick Rollback**
```bash
# Revert to previous stable version
git checkout previous-stable-tag
# Redeploy using same process
```

### 📞 **Support Resources**

- **Deployment Guide**: `DEPLOY_TO_APEXSPORTS.md`
- **Feature Documentation**: `SHOULDER_ALIGNMENT_FEATURE.md`  
- **Payment Setup**: `setup_stripe.py`
- **Feature Control**: `shoulder_alignment_feature_control.py`

---

## 🎯 **READY TO GO LIVE!**

Your enhanced basketball analysis service is production-ready with:
- Professional payment processing
- Advanced biomechanical analysis
- Robust error handling
- Easy feature management
- Complete deployment automation

**Run `python deploy_to_apexsports.py` to start deployment to apexsports-llc.com!** 🚀
