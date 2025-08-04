# DNS Configuration Guide for apexsports-llc.com
## Google Cloud App Engine Custom Domain Setup

### 🎯 OBJECTIVE
Configure DNS settings to point `apexsports-llc.com` to your Google Cloud App Engine basketball analysis service.

---

## 📋 STEP-BY-STEP DNS CONFIGURATION

### Step 1: Access Your Domain Registrar's DNS Management
**Where you purchased apexsports-llc.com** (GoDaddy, Namecheap, Google Domains, etc.)

1. **Log into your domain registrar account**
2. **Find DNS Management section** (usually called "DNS", "DNS Management", or "Nameservers")
3. **Look for "DNS Records" or "Advanced DNS"**

### Step 2: Configure DNS Records
**Add these EXACT DNS records:**

```dns
# Record 1: Main domain (apex root)
Type: A
Name: @ (or leave blank for root domain)
Value: 216.239.32.21
TTL: 3600 (or 1 hour)

# Record 2: WWW subdomain
Type: CNAME
Name: www
Value: ghs.googlehosted.com
TTL: 3600 (or 1 hour)

# Record 3: App subdomain (optional but recommended)
Type: CNAME  
Name: app
Value: ghs.googlehosted.com
TTL: 3600 (or 1 hour)
```

### Step 3: Google Cloud App Engine Domain Mapping
**Run these commands in Google Cloud Shell or your terminal:**

#### 3a. Authenticate with Google Cloud
```bash
gcloud auth login
gcloud config set project apex-sports-trainer
```

#### 3b. Create Domain Mappings
```bash
# Map main domain
gcloud app domain-mappings create apexsports-llc.com

# Map www subdomain
gcloud app domain-mappings create www.apexsports-llc.com
```

#### 3c. Verify Domain Ownership
```bash
# Google will provide a TXT record for verification
# Add this TXT record to your DNS:
# Type: TXT
# Name: @ (or root)
# Value: google-site-verification=XXXXXXXXXXXXXXXX
```

---

## 🔧 DOMAIN REGISTRAR SPECIFIC INSTRUCTIONS

### If using **GoDaddy**:
1. Go to "My Products" → "Domains" → "DNS"
2. Click "Add" for each record
3. Select record type (A or CNAME)
4. Enter Name and Value as shown above

### If using **Namecheap**:
1. Go to "Domain List" → "Manage" → "Advanced DNS"
2. Click "Add New Record"
3. Select record type and enter details

### If using **Google Domains**:
1. Go to "My Domains" → "DNS"
2. Click "Manage custom records"
3. Add each record as specified

### If using **Cloudflare**:
1. Go to "DNS" tab
2. Click "Add record"
3. **IMPORTANT**: Set proxy status to "DNS only" (gray cloud, not orange)

---

## ⚠️ CRITICAL VERIFICATION STEPS

### 1. Check DNS Propagation (15 minutes - 24 hours)
```bash
# Test if DNS is working
nslookup apexsports-llc.com
nslookup www.apexsports-llc.com

# Should return: 216.239.32.21
```

### 2. Online DNS Checker Tools
- **whatsmydns.net** - Check global DNS propagation
- **dnschecker.org** - Verify DNS records worldwide
- **mxtoolbox.com** - Professional DNS lookup

### 3. Google Cloud Verification
```bash
# Check domain mapping status
gcloud app domain-mappings list

# Should show your domains with status
```

---

## 🔒 SSL CERTIFICATE SETUP

### Automatic SSL (Recommended)
Google Cloud automatically provisions SSL certificates for verified domains.

**Timeline**: 15-60 minutes after DNS propagation

**Verification**:
```bash
# Test SSL certificate
curl -I https://apexsports-llc.com

# Should return HTTP 200 with valid SSL
```

---

## 🚨 TROUBLESHOOTING COMMON ISSUES

### Issue 1: "Domain verification failed"
**Solution**:
```bash
# Get verification record
gcloud app domain-mappings describe apexsports-llc.com

# Add the TXT record to your DNS
# Wait 15-30 minutes and try again
```

### Issue 2: "SSL certificate pending"
**Solution**:
- Wait 24-48 hours for full propagation
- Ensure DNS records are correct
- Check with: `gcloud app ssl-certificates list`

### Issue 3: "403 Forbidden" or "404 Not Found"
**Solution**:
```bash
# Verify app.yaml routing
# Check that your App Engine service is running
gcloud app browse
```

### Issue 4: DNS not propagating
**Solution**:
- Check TTL values (lower = faster propagation)
- Clear DNS cache: `ipconfig /flushdns` (Windows)
- Wait longer (can take up to 48 hours)

---

## 📱 EMAIL SETUP (Next Step)

### Google Workspace Setup
After DNS is working, set up professional email:

```dns
# MX Records for Google Workspace
Type: MX
Name: @ (or blank)
Priority: 1
Value: smtp.google.com

# Additional MX records (add all 5)
Priority: 5, Value: gmail-smtp-in.l.google.com
Priority: 10, Value: alt1.gmail-smtp-in.l.google.com  
Priority: 20, Value: alt2.gmail-smtp-in.l.google.com
Priority: 30, Value: alt3.gmail-smtp-in.l.google.com
Priority: 40, Value: alt4.gmail-smtp-in.l.google.com
```

---

## ✅ SUCCESS CHECKLIST

- [ ] **A record** added: apexsports-llc.com → 216.239.32.21
- [ ] **CNAME record** added: www → ghs.googlehosted.com
- [ ] **Domain mapping** created in Google Cloud
- [ ] **Domain verification** completed (TXT record)
- [ ] **DNS propagation** confirmed (nslookup works)
- [ ] **SSL certificate** active (https:// works)
- [ ] **Website loading** at https://apexsports-llc.com

---

## 🎯 EXPECTED TIMELINE

| Step | Time Required |
|------|---------------|
| DNS record addition | 5-10 minutes |
| DNS propagation | 15 minutes - 24 hours |
| Domain verification | 15-30 minutes |
| SSL certificate | 15 minutes - 2 hours |
| **Total completion** | **1-48 hours** |

---

## 📞 SUPPORT CONTACTS

### Domain Registrar Support
- **GoDaddy**: 1-480-505-8877
- **Namecheap**: Live chat support
- **Google Domains**: support.google.com

### Google Cloud Support
- **Console**: console.cloud.google.com/support
- **Documentation**: cloud.google.com/appengine/docs/custom-domains

---

## 🚀 WHAT HAPPENS NEXT

Once DNS is configured successfully:

1. **Professional Email Setup** (support@apexsports-llc.com)
2. **Website Content Updates** (remove .uw.r.appspot.com references)
3. **SEO Setup** (Google Search Console)
4. **Marketing Launch** (professional domain ready!)

**Let me know when you've added the DNS records and I'll help verify the setup!**
