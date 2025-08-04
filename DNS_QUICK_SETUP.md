# Quick DNS Setup Checklist
## apexsports-llc.com → Google Cloud App Engine

### 🎯 DNS Records to Add (Copy & Paste)

```
Record 1:
Type: A
Name: @ (or blank)
Value: 216.239.32.21
TTL: 3600

Record 2:
Type: CNAME
Name: www
Value: ghs.googlehosted.com
TTL: 3600
```

### 🔧 Google Cloud Commands

```bash
# Login and set project
gcloud auth login
gcloud config set project apex-sports-trainer

# Create domain mappings
gcloud app domain-mappings create apexsports-llc.com
gcloud app domain-mappings create www.apexsports-llc.com
```

### ✅ Verification Commands

```bash
# Test DNS
nslookup apexsports-llc.com
# Should return: 216.239.32.21

# Test website
curl -I https://apexsports-llc.com
# Should return: HTTP 200
```

### 📞 Quick Help
- **DNS Propagation Check**: whatsmydns.net
- **Google Cloud Console**: console.cloud.google.com
- **Domain Verification**: Add TXT record from Google Cloud

### ⏰ Timeline
- DNS Records: 5 minutes
- Propagation: 15 minutes - 24 hours  
- SSL Certificate: Automatic after verification
