# Custom Domain Setup for www.apexsports-llc.com

## Overview
Deploy the basketball analysis service to your custom domain `www.apexsports-llc.com` using DigitalOcean App Platform.

## Prerequisites
- DigitalOcean account with App Platform access
- Domain `apexsports-llc.com` registered and DNS control
- GitHub repository: `rickdyer20/apex-sports-trainer`

## Step 1: DNS Configuration
Configure these DNS records with your domain provider:

### A Record
```
Type: A
Host: @
Value: [DigitalOcean App Platform IP]
TTL: 3600
```

### CNAME Record  
```
Type: CNAME
Host: www
Value: apexsports-llc.com
TTL: 3600
```

## Step 2: DigitalOcean App Setup

### Create App from GitHub
1. Go to DigitalOcean App Platform
2. Create App → GitHub → `rickdyer20/apex-sports-trainer`
3. Branch: `master`
4. Use the configuration from `.do/app.yaml`

### Add Custom Domain
1. In App Settings → Domains
2. Add Domain: `www.apexsports-llc.com`
3. Set as Primary Domain
4. DigitalOcean will auto-provision SSL certificate

## Step 3: Verify Configuration

### App Configuration (`.do/app.yaml`)
```yaml
name: apex-sports-trainer
services:
- name: web
  source_dir: /
  github:
    repo: rickdyer20/apex-sports-trainer
    branch: master
  run_command: python wsgi.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: FLASK_ENV
    value: "production"
  health_check:
    http_path: /health
domains:
- domain: www.apexsports-llc.com
  type: PRIMARY
  wildcard: false
  zone: apexsports-llc.com
```

## Step 4: Deploy
1. Push updated `.do/app.yaml` to GitHub master branch
2. DigitalOcean will automatically deploy
3. Domain will be available at `https://www.apexsports-llc.com`

## Expected Result
- ✅ Basketball Analysis Service deployed
- ✅ Custom domain: `https://www.apexsports-llc.com`
- ✅ SSL certificate auto-provisioned
- ✅ HTTP → HTTPS redirect enabled

## Troubleshooting
- DNS propagation can take 24-48 hours
- Verify DNS records with `nslookup www.apexsports-llc.com`
- Check DigitalOcean App logs for deployment issues
