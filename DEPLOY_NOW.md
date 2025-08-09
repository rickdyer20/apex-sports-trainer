# 🚀 DEPLOY NOW - Single Command Deployment

## **INSTANT DEPLOYMENT TO APEXSPORTS-LLC.COM**

Your Basketball Analysis Service is ready to deploy! Here's how to go live in under 2 minutes:

### **STEP 1: SSH to Your Server**
```bash
ssh your_username@apexsports-llc.com
```

### **STEP 2: Run This Single Command**
```bash
curl -sSL https://raw.githubusercontent.com/rickdyer20/apex-sports-trainer/working-full-featured/deploy_from_git.sh | bash
```

**That's it!** This one command will:
- ✅ Clone your repository
- ✅ Extract all deployment files
- ✅ Install dependencies (Flask, Stripe, Gunicorn)
- ✅ Set proper permissions
- ✅ Test the application
- ✅ Prepare for launch

### **STEP 3: Start Your Service**

After the deployment script completes, start your service:

**For Production (Recommended):**
```bash
cd apex-sports-trainer
gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app
```

**For Background (Runs Continuously):**
```bash
cd apex-sports-trainer
nohup gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app > service.log 2>&1 &
```

### **STEP 4: Verify Your Live Service**

Visit these URLs to confirm everything is working:
- 🌐 **Homepage**: https://apexsports-llc.com
- 💰 **Pricing**: https://apexsports-llc.com/pricing
- 🏀 **Analysis**: https://apexsports-llc.com/analyze

---

## **💰 REVENUE READY**

Your Basketball Analysis Service will be live with:
- **Free**: 1 analysis per year (aggressive conversion)
- **One-time**: $9.99 for 5 analyses
- **Pro**: $19.99/month unlimited
- **Enterprise**: $49.99/month premium

## **🔐 LIVE PAYMENTS**

Your Stripe integration is configured with live keys and ready to accept real payments immediately!

---

## **🎯 DEPLOY NOW!**

**Copy and paste these commands on your server:**

```bash
# SSH to your server
ssh your_username@apexsports-llc.com

# Run deployment script
curl -sSL https://raw.githubusercontent.com/rickdyer20/apex-sports-trainer/working-full-featured/deploy_from_git.sh | bash

# Start production service
cd apex-sports-trainer
gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app
```

**You'll be earning revenue in under 5 minutes!** 🚀
