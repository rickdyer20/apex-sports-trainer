# Namecheap DNS Configuration - Step by Step
## Setting up apexsports-llc.com for Google Cloud App Engine

### 🎯 OBJECTIVE
Configure your Namecheap DNS settings to point `apexsports-llc.com` to your Google Cloud App Engine basketball analysis service.

---

## 📋 DETAILED NAMECHEAP INSTRUCTIONS

### Step 1: Login to Namecheap Dashboard
1. **Go to**: https://www.namecheap.com
2. **Click**: "Sign In" (top right corner)
3. **Enter**: Your Namecheap username and password
4. **Click**: "Sign In"

### Step 2: Access Domain Management
1. **On Dashboard**: You'll see your domain list
2. **Find**: `apexsports-llc.com` in your domain list
3. **Click**: "Manage" button next to your domain
   - Alternative: Click on the domain name itself

### Step 3: Navigate to Advanced DNS
1. **On Domain Details page**: Look for tabs at the top
2. **Click**: "Advanced DNS" tab
   - **NOT** "Basic DNS" - make sure it's "Advanced DNS"
3. **Wait**: For the page to load (may take 5-10 seconds)

### Step 4: Review Current DNS Records
You'll see a section called **"Host Records"** with existing records like:
```
Type    Host    Value                           TTL
A       @       Parked page IP                  Automatic
CNAME   www     Namecheap parking page          Automatic
```

### Step 5: Delete Existing Records (Important!)
**⚠️ CRITICAL: Remove conflicting records first**

1. **Find**: Any existing A record with Host "@" 
2. **Click**: The trash can icon (🗑️) next to it
3. **Confirm**: Delete when prompted
4. **Find**: Any existing CNAME record with Host "www"
5. **Click**: The trash can icon (🗑️) next to it
6. **Confirm**: Delete when prompted

### Step 6: Add New A Record (Main Domain)
1. **Click**: "Add New Record" button
2. **Select**: "A Record" from dropdown
3. **Fill in exactly**:
   ```
   Type: A Record
   Host: @
   Value: 216.239.32.21
   TTL: Automatic (or select 30 min)
   ```
4. **Click**: ✅ checkmark or "Save" button

### Step 7: Add New CNAME Record (WWW Subdomain)
1. **Click**: "Add New Record" button again
2. **Select**: "CNAME Record" from dropdown
3. **Fill in exactly**:
   ```
   Type: CNAME Record
   Host: www
   Value: ghs.googlehosted.com
   TTL: Automatic (or select 30 min)
   ```
4. **Click**: ✅ checkmark or "Save" button

### Step 8: Optional - Add App Subdomain
1. **Click**: "Add New Record" button again
2. **Select**: "CNAME Record" from dropdown
3. **Fill in exactly**:
   ```
   Type: CNAME Record
   Host: app
   Value: ghs.googlehosted.com
   TTL: Automatic (or select 30 min)
   ```
4. **Click**: ✅ checkmark or "Save" button

---

## 🔍 VERIFICATION - What Your DNS Should Look Like

After completing the steps, your **Host Records** section should show:

```
Type    Host    Value                   TTL
A       @       216.239.32.21          30 min
CNAME   www     ghs.googlehosted.com   30 min
CNAME   app     ghs.googlehosted.com   30 min (optional)
```

---

## ⚠️ COMMON NAMECHEAP ISSUES & SOLUTIONS

### Issue 1: "Host @ already exists"
**Problem**: Namecheap won't let you add @ record
**Solution**: 
1. Delete the existing @ record first
2. Wait 2-3 minutes
3. Try adding the new A record again

### Issue 2: "Invalid Value Format"
**Problem**: Namecheap rejects the value
**Solution**:
- For A record: Use exactly `216.239.32.21` (no spaces)
- For CNAME: Use exactly `ghs.googlehosted.com` (no trailing dot)

### Issue 3: TTL Options Confusion
**Namecheap TTL Options**:
- **Automatic** = Recommended (uses Namecheap default)
- **1 min** = Fastest propagation (for testing)
- **30 min** = Good balance
- **1 hour** = Standard
- **24 hours** = Slowest changes

**Recommendation**: Use "Automatic" or "30 min"

### Issue 4: Records Not Saving
**Solution**:
1. Make sure you click the ✅ checkmark after each record
2. Look for green "Success" message
3. Refresh the page to verify records appear

---

## 🕐 NAMECHEAP PROPAGATION TIMELINE

| Action | Expected Time |
|--------|---------------|
| Record changes save | Immediate |
| Namecheap DNS update | 5-10 minutes |
| Global propagation start | 15-30 minutes |
| Full propagation | 1-24 hours |

---

## 🔧 TESTING YOUR NAMECHEAP DNS

### Immediate Test (5-10 minutes after changes)
```bash
# Test if Namecheap accepted your changes
nslookup apexsports-llc.com 8.8.8.8

# Should eventually return: 216.239.32.21
```

### Online DNS Checker
1. **Go to**: https://www.whatsmydns.net
2. **Enter**: `apexsports-llc.com`
3. **Select**: "A" record type
4. **Click**: "Search"
5. **Look for**: Green checkmarks showing `216.239.32.21`

### Namecheap DNS Checker
1. **Go to**: https://www.namecheap.com/support/knowledgebase/article.aspx/9837/46/dns-checker
2. **Enter**: `apexsports-llc.com`
3. **Check**: Results

---

## 📱 NAMECHEAP MOBILE APP
If you prefer using the mobile app:

1. **Download**: Namecheap app (iOS/Android)
2. **Login**: With your credentials
3. **Navigate**: Domains → Your Domain → DNS
4. **Follow**: Same steps as above

---

## 🆘 NAMECHEAP SUPPORT CONTACTS

### If You Need Help:
- **Live Chat**: Available 24/7 on Namecheap.com
- **Support Ticket**: Submit through your account dashboard
- **Phone**: 1-866-340-9004 (US/Canada)
- **Knowledge Base**: https://www.namecheap.com/support/

---

## 🎯 NEXT STEPS AFTER DNS IS SET

### 1. Google Cloud Domain Mapping (Do this while DNS propagates)
```bash
# Run these commands in your terminal
gcloud auth login
gcloud config set project apex-sports-trainer
gcloud app domain-mappings create apexsports-llc.com
gcloud app domain-mappings create www.apexsports-llc.com
```

### 2. Domain Verification
Google will provide a TXT record. Add it in Namecheap:
1. **Click**: "Add New Record"
2. **Select**: "TXT Record"
3. **Host**: @
4. **Value**: `google-site-verification=XXXXXXXX` (from Google)

### 3. Email Setup (After domain works)
For professional email (support@apexsports-llc.com):
1. **Sign up**: Google Workspace
2. **Add MX records**: In Namecheap Advanced DNS
3. **Verify**: Domain ownership

---

## ✅ SUCCESS CHECKLIST

- [ ] **Logged into Namecheap** successfully
- [ ] **Found domain** apexsports-llc.com in dashboard
- [ ] **Accessed** "Advanced DNS" tab
- [ ] **Deleted** existing conflicting records
- [ ] **Added A record**: @ → 216.239.32.21
- [ ] **Added CNAME**: www → ghs.googlehosted.com
- [ ] **Verified** records appear in Host Records list
- [ ] **Tested** with nslookup or DNS checker
- [ ] **Created** Google Cloud domain mappings

---

## 🚨 EMERGENCY ROLLBACK

If something goes wrong:
1. **Delete** the new records you added
2. **Re-add** Namecheap's default parking records:
   ```
   A Record: @ → [Namecheap parking IP]
   CNAME: www → [Namecheap parking]
   ```
3. **Contact** Namecheap support for help

**Your domain will return to the parking page until fixed.**

---

**🎉 Once DNS propagates (1-24 hours), your basketball analysis service will be live at https://apexsports-llc.com!**
