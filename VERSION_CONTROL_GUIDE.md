# 🔄 APEX SPORTS, LLC - VERSION CONTROL & BACKUP GUIDE

## Complete Guide to Saving, Managing, and Recalling Script Versions

---

## 🎯 OVERVIEW: Why Version Control Matters for Your Business

Your basketball analysis service is now a **commercial product**. Proper version control ensures:
- **Business Continuity**: Never lose working code
- **Safe Updates**: Test changes without breaking production
- **Rollback Capability**: Quickly revert if issues arise
- **Professional Development**: Industry-standard practices
- **Team Collaboration**: Easy for others to contribute later

---

## 📋 RECOMMENDED VERSION CONTROL STRATEGY

### Method 1: Git + GitHub (PROFESSIONAL - RECOMMENDED)

#### **Why Git + GitHub?**
- ✅ Industry standard for software businesses
- ✅ Free for your use case
- ✅ Automatic cloud backup
- ✅ Professional collaboration features
- ✅ Integration with deployment tools
- ✅ Version history and comparison tools

#### **Setup Instructions:**

1. **Install Git (if not already installed)**
   ```powershell
   # Check if Git is installed
   git --version
   
   # If not installed, download from: https://git-scm.com/download/win
   ```

2. **Initialize Your Repository**
   ```powershell
   # Navigate to your project folder
   cd c:\basketball_analysis\New_Shot_AI
   
   # Initialize Git repository
   git init
   
   # Configure Git with your information
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

3. **Create .gitignore File** (Exclude sensitive/temporary files)
   ```powershell
   # Create .gitignore file
   New-Item -Path ".gitignore" -ItemType File
   ```

4. **Add Initial Files**
   ```powershell
   # Add all files to Git tracking
   git add .
   
   # Create initial commit
   git commit -m "Initial commit: APEX SPORTS LLC Basketball Analysis Service v9.0"
   ```

5. **Connect to GitHub**
   ```powershell
   # Create repository on GitHub (go to github.com and create new repo)
   # Then connect your local repo:
   git remote add origin https://github.com/yourusername/apex-sports-basketball-analysis.git
   git branch -M main
   git push -u origin main
   ```

---

## 🔄 DAILY VERSION CONTROL WORKFLOW

### **Before Making Changes:**
```powershell
# 1. Check current status
git status

# 2. Pull latest changes (if working with others)
git pull origin main

# 3. Create a new branch for your changes
git checkout -b feature/new-enhancement-name
```

### **After Making Changes:**
```powershell
# 1. Review what changed
git status
git diff

# 2. Add changes to staging
git add basketball_analysis_service.py  # Add specific files
# OR
git add .  # Add all changes

# 3. Commit with descriptive message
git commit -m "Enhanced elbow flare detection accuracy - v9.1"

# 4. Push to GitHub
git push origin feature/new-enhancement-name
```

### **Deploying to Production:**
```powershell
# 1. Switch to main branch
git checkout main

# 2. Merge your feature branch
git merge feature/new-enhancement-name

# 3. Tag the version
git tag -a v9.1 -m "Version 9.1: Enhanced elbow detection"

# 4. Push to GitHub
git push origin main
git push origin v9.1

# 5. Deploy to Google Cloud
gcloud app deploy
```

---

## 📂 BACKUP STRATEGY (MULTI-LAYERED PROTECTION)

### **Level 1: Local Git Repository**
- **Location**: Your computer's `.git` folder
- **Purpose**: Track all changes locally
- **Frequency**: Every commit

### **Level 2: GitHub Cloud Backup**
- **Location**: GitHub.com cloud servers
- **Purpose**: Remote backup and collaboration
- **Frequency**: Every push

### **Level 3: File System Backup**
```powershell
# Create timestamped backup
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupPath = "C:\APEX_SPORTS_BACKUPS\backup_$timestamp"
Copy-Item -Path "c:\basketball_analysis\New_Shot_AI" -Destination $backupPath -Recurse
```

### **Level 4: Google Cloud Source Repositories** (Optional)
```powershell
# Mirror to Google Cloud for extra redundancy
gcloud source repos create apex-sports-basketball-analysis
git remote add google https://source.developers.google.com/p/[PROJECT-ID]/r/apex-sports-basketball-analysis
git push google main
```

---

## 🏷️ VERSION NAMING CONVENTION

### **Semantic Versioning (MAJOR.MINOR.PATCH)**

```
v9.0.0 - Current production version
v9.1.0 - New feature addition
v9.0.1 - Bug fix or small improvement
v10.0.0 - Major overhaul or breaking changes
```

### **Git Commit Message Standards:**
```
feat: Add new shot fluidity analysis
fix: Resolve elbow flare detection edge case
docs: Update API documentation
refactor: Optimize pose estimation performance
style: Improve code formatting
test: Add unit tests for angle calculations
```

---

## 🔍 RECALLING SPECIFIC VERSIONS

### **View Version History:**
```powershell
# See all commits
git log --oneline

# See specific file history
git log --oneline basketball_analysis_service.py

# See tags (version releases)
git tag -l
```

### **Restore Specific Version:**
```powershell
# Restore to a specific commit
git checkout [commit-hash]

# Restore to a specific tag
git checkout v9.0

# Create new branch from old version
git checkout -b fix/revert-to-v9.0 v9.0
```

### **Compare Versions:**
```powershell
# Compare current with previous version
git diff v9.0 v9.1

# Compare specific files
git diff v9.0:basketball_analysis_service.py v9.1:basketball_analysis_service.py
```

---

## 📊 PRODUCTION DEPLOYMENT VERSIONING

### **Google App Engine Version Management:**

1. **Deploy New Version Without Promoting:**
   ```powershell
   gcloud app deploy --no-promote --version=v9-1
   ```

2. **Test New Version:**
   ```
   https://v9-1-dot-apex-sports-trainer.uw.r.appspot.com
   ```

3. **Promote When Ready:**
   ```powershell
   gcloud app services set-traffic default --splits=v9-1=1.00
   ```

4. **Rollback If Needed:**
   ```powershell
   gcloud app services set-traffic default --splits=v9=1.00
   ```

---

## 🛠️ RECOMMENDED TOOLS

### **IDE Integration:**
- **VS Code**: Built-in Git support
- **Extensions**: 
  - GitLens (enhanced Git features)
  - GitHub Pull Requests
  - Git Graph (visual history)

### **GUI Tools (Alternative to Command Line):**
- **GitHub Desktop**: User-friendly Git interface
- **Sourcetree**: Advanced Git GUI
- **VS Code Source Control**: Built into your editor

---

## 🚨 EMERGENCY RECOVERY PROCEDURES

### **If Local Files Are Lost:**
```powershell
# Clone from GitHub
git clone https://github.com/yourusername/apex-sports-basketball-analysis.git
cd apex-sports-basketball-analysis
```

### **If GitHub Is Unavailable:**
```powershell
# Restore from local backup
Copy-Item -Path "C:\APEX_SPORTS_BACKUPS\backup_[timestamp]" -Destination "C:\basketball_analysis\Recovery" -Recurse
```

### **If Need to Revert Production:**
```powershell
# Quick rollback to previous App Engine version
gcloud app services set-traffic default --splits=v9=1.00
```

---

## 📅 MAINTENANCE SCHEDULE

### **Daily:**
- Commit changes with descriptive messages
- Push to GitHub at end of work day

### **Weekly:**
- Create version tags for significant updates
- Review and clean up old branches
- Test deployment process

### **Monthly:**
- Create full system backup
- Review version history and cleanup
- Update documentation

---

## 🎯 QUICK REFERENCE COMMANDS

```powershell
# SAVE CURRENT WORK
git add .
git commit -m "Description of changes"
git push origin main

# RECALL SPECIFIC VERSION
git log --oneline                    # See available versions
git checkout v9.1                   # Switch to version 9.1
git checkout main                   # Return to latest

# EMERGENCY ROLLBACK
gcloud app services set-traffic default --splits=v9=1.00

# CREATE NEW VERSION
git tag -a v9.2 -m "Version 9.2"
git push origin v9.2
gcloud app deploy --version=v9-2
```

---

## 💡 BEST PRACTICES FOR APEX SPORTS, LLC

1. **Never edit directly in production** - Always test locally first
2. **Use descriptive commit messages** - Future you will thank you
3. **Tag all production releases** - Easy to track customer-facing versions
4. **Keep main branch stable** - Always deployable
5. **Regular backups** - Multiple layers of protection
6. **Document breaking changes** - Important for business continuity

---

## 🎮 GETTING STARTED CHECKLIST

- [ ] Install Git if not already installed
- [ ] Initialize repository in your project folder
- [ ] Create GitHub account and repository
- [ ] Make initial commit and push to GitHub
- [ ] Create .gitignore file for sensitive data
- [ ] Tag current version as v9.0
- [ ] Set up automated backup schedule
- [ ] Test the recall process with a small change
- [ ] Document your specific workflow

**Your code is your business asset - protect it like the valuable commercial product it is!** 🚀
