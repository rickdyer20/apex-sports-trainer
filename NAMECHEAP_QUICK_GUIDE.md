# Namecheap DNS - Quick Visual Guide
## apexsports-llc.com Setup

### 🎯 What You're Looking For

**Namecheap Dashboard → Domain → Advanced DNS → Host Records**

### 📍 Step-by-Step Locations

#### 1. Login Screen
- Website: namecheap.com
- Look for: "Sign In" button (top right)
- Enter: Username + Password

#### 2. Domain Dashboard  
- Look for: List of your domains
- Find: "apexsports-llc.com" 
- Click: "Manage" button (blue button next to domain)

#### 3. Domain Details Page
- Look for: Row of tabs across the top
- Tabs will show: "Dashboard", "Advanced DNS", "Email", etc.
- Click: "Advanced DNS" (second or third tab)

#### 4. Advanced DNS Page - Host Records Section
- Look for: Section titled "Host Records"
- You'll see: Table with columns: Type, Host, Value, TTL, Actions
- Look for: "Add New Record" button (usually blue)

### 🗂️ Records to Add

#### Delete First (if they exist):
```
OLD: A record with Host "@" 
OLD: CNAME record with Host "www"
```

#### Add These Exact Records:
```
Record 1:
- Click "Add New Record"
- Type: A Record
- Host: @
- Value: 216.239.32.21
- TTL: Automatic
- Click checkmark ✅

Record 2:  
- Click "Add New Record"
- Type: CNAME Record
- Host: www
- Value: ghs.googlehosted.com
- TTL: Automatic
- Click checkmark ✅
```

### 🎯 Final Result Should Look Like:
```
Type    Host    Value                   TTL        Actions
A       @       216.239.32.21          Automatic   🗑️
CNAME   www     ghs.googlehosted.com   Automatic   🗑️
```

### ⚡ Quick Test Commands
```bash
# Test DNS (wait 10-15 minutes first)
nslookup apexsports-llc.com

# Should return: 216.239.32.21
```

### 🆘 Namecheap Support
- **Live Chat**: Click chat bubble on any Namecheap page
- **Phone**: 1-866-340-9004
- **Help**: "How do I add DNS records?" (search their help)

### ⏰ Timeline
- **Save records**: Immediate
- **DNS propagation**: 15 minutes - 24 hours
- **Website live**: After Google Cloud setup complete

**Next**: Run Google Cloud domain mapping commands while DNS propagates!
