# 📖 SIMPLE VERSION CONTROL GUIDE FOR APEX SPORTS, LLC
## Step-by-Step Text Instructions (No Scripts Required)

---

## 🎯 WHY YOU NEED VERSION CONTROL

Your basketball analysis service is now a **commercial business asset**. Version control protects you from:
- ❌ Accidentally deleting working code
- ❌ Breaking your live service with bad changes
- ❌ Losing weeks of work to computer crashes
- ❌ Not being able to undo problematic updates

Think of it as **"Save Game" for your business code**.

---

## 📋 STEP 1: INSTALL GIT (One-Time Setup)

### Check if Git is Already Installed:
1. Open Command Prompt or PowerShell
2. Type: `git --version`
3. If you see a version number → Skip to Step 2
4. If you get an error → Continue below

### Install Git:
1. Go to: https://git-scm.com/download/win
2. Download the Windows installer
3. Run installer with default settings
4. Restart your command prompt
5. Test: `git --version`

---

## 📋 STEP 2: SETUP YOUR PROJECT (One-Time)

### Navigate to Your Project:
```
cd c:\basketball_analysis\New_Shot_AI
```

### Initialize Git Repository:
```
git init
```
*This creates a hidden `.git` folder to track changes*

### Configure Your Identity:
```
git config user.name "Your Name"
git config user.email "your.email@example.com"
```
*Replace with your actual name and email*

### Create .gitignore File:
1. Create a new file called `.gitignore` (note the dot at the start)
2. Add this content to ignore temporary/sensitive files:
```
__pycache__/
*.pyc
*.log
temp/
*.tmp
debug_frame_*.jpg
config.ini
secrets/
```

### Add All Your Files:
```
git add .
```
*The dot means "add everything"*

### Create Your First Save Point:
```
git commit -m "Initial commit: APEX SPORTS LLC Basketball Analysis Service v9.0"
```

### Tag This as Version 9.0:
```
git tag -a v9.0 -m "Version 9.0: Initial production release"
```

**✅ Congratulations! Your code is now tracked locally.**

---

## 📋 STEP 3: SETUP CLOUD BACKUP (One-Time)

### Create GitHub Account:
1. Go to: https://github.com
2. Create free account
3. Verify email address

### Create Repository:
1. Click "New repository" (green button)
2. Repository name: `apex-sports-basketball-analysis`
3. Make it **Private** (your business code)
4. Don't initialize with README (you already have files)
5. Click "Create repository"

### Connect Your Local Code to GitHub:
```
git remote add origin https://github.com/YOURUSERNAME/apex-sports-basketball-analysis.git
git branch -M main
git push -u origin main
git push origin v9.0
```
*Replace YOURUSERNAME with your actual GitHub username*

**✅ Your code is now backed up to the cloud!**

---

## 📋 DAILY WORKFLOW: SAVING YOUR WORK

### Every Time You Make Changes:

#### 1. Check What Changed:
```
git status
```
*Shows which files you modified*

#### 2. See Specific Changes:
```
git diff
```
*Shows exactly what code changed*

#### 3. Save Your Changes:
```
git add .
git commit -m "Brief description of what you changed"
```

**Example commit messages:**
- `"Fix elbow flare detection for side camera angles"`
- `"Add new shot fluidity analysis feature"`
- `"Improve pose estimation accuracy"`

#### 4. Backup to Cloud (End of Day):
```
git push origin main
```

---

## 📋 CREATING NEW VERSIONS

### When You Have Major Updates:

#### 1. Tag a New Version:
```
git tag -a v9.1 -m "Version 9.1: Enhanced elbow detection"
git push origin v9.1
```

#### 2. Deploy to Google Cloud:
```
gcloud app deploy --version=v9-1
```

#### 3. If Everything Works, Make It Live:
```
gcloud app services set-traffic default --splits=v9-1=1.00
```

---

## 📋 EMERGENCY: GOING BACK TO PREVIOUS VERSION

### If You Break Something:

#### 1. See Available Versions:
```
git tag -l
```

#### 2. Go Back to Working Version:
```
git checkout v9.0
```

#### 3. Create New Branch from Old Version:
```
git checkout -b fix-attempt v9.0
```

#### 4. Return to Latest When Ready:
```
git checkout main
```

### Rollback Production Service:
```
gcloud app services set-traffic default --splits=v9=1.00
```

---

## 📋 VIEWING YOUR HISTORY

### See All Your Saves:
```
git log --oneline
```

### See All Tagged Versions:
```
git tag -l
```

### Compare Two Versions:
```
git diff v9.0 v9.1
```

---

## 📋 SIMPLE DAILY ROUTINE

### Morning (Start of Work):
```
git status
```
*Check if anything changed overnight*

### During Work (Save Progress):
```
git add .
git commit -m "What I just did"
```
*Do this every hour or after completing a feature*

### Evening (Cloud Backup):
```
git push origin main
```
*Upload the day's work to GitHub*

### Weekly (Version Release):
```
git tag -a v9.x -m "Version description"
git push origin v9.x
gcloud app deploy
```

---

## 📋 IMPORTANT REMINDERS

### ✅ DO:
- Commit changes frequently (every hour)
- Use descriptive commit messages
- Push to GitHub daily
- Tag important versions
- Test before deploying to production

### ❌ DON'T:
- Edit files directly on the production server
- Make commits with messages like "fix stuff" or "update"
- Forget to push to GitHub for days
- Delete the `.git` folder
- Ignore error messages

---

## 📋 FILE ORGANIZATION

### Your project should have:
```
c:\basketball_analysis\New_Shot_AI\
├── .git/                          (Git tracking - don't touch)
├── .gitignore                     (Files to ignore)
├── basketball_analysis_service.py (Your main code)
├── VERSION_CONTROL_GUIDE.md       (This guide)
├── LAUNCH_SUCCESS_REPORT.md       (Your achievements)
└── ... (other files)
```

---

## 📋 TROUBLESHOOTING

### If Something Goes Wrong:

#### "I accidentally deleted important code":
```
git checkout HEAD -- filename.py
```
*Restores file to last committed version*

#### "I want to undo my last commit":
```
git reset --soft HEAD~1
```
*Undoes commit but keeps your changes*

#### "I'm totally confused":
```
git status
git log --oneline
```
*Shows current state and recent history*

#### "Emergency: Go back to last working version":
```
git checkout main
git reset --hard HEAD
```
*⚠️ WARNING: This deletes all uncommitted changes*

---

## 📞 HELP RESOURCES

- **Git Basics**: https://git-scm.com/docs
- **GitHub Help**: https://docs.github.com/
- **Visual Guide**: https://learngitbranching.js.org/

---

## 🎯 SUMMARY FOR APEX SPORTS, LLC

**Your business code is now protected with:**
- ✅ Local version tracking (Git)
- ✅ Cloud backup (GitHub) 
- ✅ Version tagging system
- ✅ Rollback capabilities
- ✅ Professional development workflow

**Remember: Your code = Your business. Protect it like it's worth millions!** 💰

---

*This guide covers everything you need to safely manage your basketball analysis service code. Start with the one-time setup, then follow the daily workflow to keep your business protected.*
