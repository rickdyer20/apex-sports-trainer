# 📋 DAILY VERSION CONTROL CHEAT SHEET
## Quick Reference for APEX SPORTS, LLC

---

## 🚀 BEFORE YOU START CODING
```powershell
# Check current status
git status

# Make sure you're on the main branch
git checkout main

# Pull any updates (if working with others)
git pull origin main
```

---

## ✏️ WHILE CODING
```powershell
# Check what you've changed
git status
git diff

# See changes in specific file
git diff basketball_analysis_service.py
```

---

## 💾 SAVE YOUR WORK
```powershell
# Save all changes
git add .
git commit -m "Brief description of what you changed"

# OR save specific files
git add basketball_analysis_service.py
git commit -m "Enhanced elbow flare detection accuracy"
```

---

## ☁️ BACKUP TO GITHUB
```powershell
# Upload to GitHub (daily backup)
git push origin main
```

---

## 🏷️ RELEASE NEW VERSION
```powershell
# When ready to deploy to customers
git tag -a v9.1 -m "Version 9.1: Your description"
git push origin v9.1

# Deploy to Google Cloud
gcloud app deploy --version=v9-1
```

---

## 🔄 VIEW HISTORY
```powershell
# See your commit history
git log --oneline

# See all version tags
git tag -l
```

---

## 🚨 EMERGENCY: GO BACK TO PREVIOUS VERSION
```powershell
# See available versions
git tag -l

# Go back to specific version
git checkout v9.0

# Return to latest
git checkout main
```

---

## 📱 COMMIT MESSAGE EXAMPLES
```
✅ GOOD:
"Fix elbow flare detection edge case for side-view videos"
"Add new shot fluidity analysis feature"
"Update documentation for v9.1 release"

❌ AVOID:
"fix stuff"
"update"
"changes"
```

---

## ⏰ DAILY ROUTINE
1. **Morning**: `git status` (check what's changed)
2. **During work**: `git add .` + `git commit -m "..."` (save progress)
3. **End of day**: `git push origin main` (backup to cloud)
4. **Before big changes**: `git tag -a v9.x -m "..."` (mark versions)

---

## 🆘 HELP COMMANDS
```powershell
# If you mess up, don't panic!
git status                    # See what's happening
git log --oneline            # See recent changes
git checkout main            # Go back to main version
git reset --hard HEAD       # Undo uncommitted changes (CAREFUL!)
```

---

## 📞 EMERGENCY CONTACTS
- **GitHub Help**: https://docs.github.com/
- **Git Documentation**: https://git-scm.com/doc
- **Your VERSION_CONTROL_GUIDE.md**: Complete instructions

---

**Remember: Your code = Your business. Save it like it's worth millions! 💰**
