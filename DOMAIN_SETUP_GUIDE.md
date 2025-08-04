# APEX SPORTS, LLC - Domain Setup Guide
## apexsports-llc.com Configuration

### 🎉 Domain Purchased Successfully!
**Domain**: apexsports-llc.com  
**Status**: Ready for configuration  
**Next Steps**: DNS setup and email configuration

---

## 📋 IMMEDIATE SETUP TASKS

### 1. DNS Configuration
**Goal**: Point domain to Google Cloud App Engine

#### DNS Records to Configure:
```dns
# Main domain
Type: A
Name: @
Value: 216.239.32.21
TTL: 3600

# WWW subdomain  
Type: CNAME
Name: www
Value: ghs.googlehosted.com
TTL: 3600

# App Engine custom domain
Type: CNAME
Name: app
Value: ghs.googlehosted.com
TTL: 3600
```

#### Google Cloud App Engine Custom Domain Setup:
1. **In Google Cloud Console**:
   ```bash
   gcloud app domain-mappings create apexsports-llc.com
   gcloud app domain-mappings create www.apexsports-llc.com
   ```

2. **Verify Domain Ownership**:
   - Add TXT record provided by Google
   - Wait for verification (can take 24-48 hours)

### 2. SSL Certificate
- **Automatic**: Google Cloud will provision SSL certificate
- **Timeline**: 15 minutes after DNS propagation
- **Verify**: https://apexsports-llc.com should show green lock

### 3. Professional Email Setup

#### Option A: Google Workspace (Recommended)
**Cost**: $6/user/month  
**Features**: Professional email, calendar, drive integration

**Setup Steps**:
1. Sign up at: https://workspace.google.com
2. Verify domain ownership
3. Create email accounts:
   - `support@apexsports-llc.com` (primary)
   - `admin@apexsports-llc.com`
   - `billing@apexsports-llc.com`
   - `hello@apexsports-llc.com`

#### Option B: Microsoft 365 Business
**Cost**: $5/user/month  
**Features**: Professional email, Office apps

#### Option C: Email Hosting via Domain Provider
**Cost**: $1-3/month  
**Features**: Basic professional email

### 4. Website Hosting Setup

#### Current: Google Cloud App Engine
- **URL**: https://apex-sports-trainer.uw.r.appspot.com
- **Target**: https://apexsports-llc.com
- **Custom domain mapping required**

#### Professional Website Structure:
```
https://apexsports-llc.com/
├── / (landing page)
├── /analysis (basketball analysis app)
├── /pricing (subscription plans)
├── /about (company info)
├── /contact (support)
├── /privacy (privacy policy)
└── /terms (terms of service)
```

---

## 🔧 TECHNICAL IMPLEMENTATION

### App Engine Configuration Update

#### app.yaml modifications needed:
```yaml
runtime: python311

handlers:
- url: /.*
  script: auto

env_variables:
  DOMAIN_NAME: "apexsports-llc.com"
  COMPANY_EMAIL: "support@apexsports-llc.com"
  
automatic_scaling:
  min_instances: 1
  max_instances: 10
```

### Update Service Configuration
The `COMPANY_INFO` in `basketball_analysis_service.py` has been updated with:
- Domain: `apexsports-llc.com`
- Support Email: `support@apexsports-llc.com`

### Email Templates Update Required
All email templates need domain updates:
- Welcome emails
- Analysis completion notifications
- Payment confirmations
- Support responses

---

## 🎯 PRIORITY TIMELINE

### Week 1 (This Week)
- [ ] **DNS Configuration** (Day 1-2)
- [ ] **Google Cloud Domain Mapping** (Day 2-3)
- [ ] **SSL Certificate Verification** (Day 3-4)
- [ ] **Email Account Setup** (Day 4-5)
- [ ] **Test Domain Resolution** (Day 5-7)

### Week 2
- [ ] **Website Content Updates**
- [ ] **Email Template Updates**
- [ ] **SEO Setup** (Google Search Console)
- [ ] **Analytics Setup** (Google Analytics)

---

## 📊 BUSINESS IMPACT

### Professional Benefits
✅ **Credibility**: Professional domain enhances trust  
✅ **Branding**: Consistent with LLC name  
✅ **Email**: Professional communication  
✅ **Marketing**: Easy to remember and share  

### SEO & Marketing
- **Primary Domain**: apexsports-llc.com
- **Keywords**: basketball, analysis, training, sports
- **Target Audience**: Basketball players, coaches, trainers

### Cost Analysis
- **Domain**: ~$12-15/year
- **Email**: $6/month (Google Workspace)
- **SSL**: Free (Google Cloud)
- **Total Monthly**: ~$6-8

---

## 🔍 VERIFICATION CHECKLIST

### DNS Propagation Check
```bash
# Check DNS resolution
nslookup apexsports-llc.com
dig apexsports-llc.com

# Check website accessibility
curl -I https://apexsports-llc.com
```

### Email Verification
- [ ] Send test email from support@apexsports-llc.com
- [ ] Receive email at professional address
- [ ] Verify SPF/DKIM records for deliverability

### Website Verification
- [ ] https://apexsports-llc.com loads correctly
- [ ] SSL certificate is valid
- [ ] All pages accessible
- [ ] Mobile-responsive design

---

## 🚀 NEXT STEPS AFTER DOMAIN SETUP

1. **Business Bank Account**: Use professional domain for business banking
2. **Marketing Materials**: Update all materials with new domain
3. **Google Business Profile**: Claim business listing
4. **Social Media**: Update all social profiles
5. **Legal Documents**: Update terms/privacy with new domain

**Estimated Total Setup Time**: 3-5 business days
**Key Milestone**: Professional online presence established
