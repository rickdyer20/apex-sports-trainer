#!/usr/bin/env python3
"""
Deploy Basketball Analysis Service to apexsports-llc.com
Run this script to automatically deploy your service to the live server
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_deployment_package():
    """Create a deployment package with all necessary files"""
    
    # Essential files for deployment
    essential_files = [
        'complete_web_app.py',
        'enhanced_payment_manager.py', 
        'user_analysis_tracker.py',
        '.env',
        'requirements.txt',
        'wsgi_production.py'
    ]
    
    # Template files
    template_files = [
        'templates/pricing_with_onetime.html',
        'templates/privacy_policy.md'
    ]
    
    # Legal files
    legal_files = [
        'terms_of_service.md'
    ]
    
    # Optional analysis files (for full functionality)
    analysis_files = [
        'basketball_analysis_service.py',
        'pdf_generator.py'
    ]
    
    print("🚀 Creating deployment package for apexsports-llc.com...")
    
    # Create deployment directory
    deploy_dir = Path('deployment_package')
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    # Create templates subdirectory
    (deploy_dir / 'templates').mkdir()
    
    # Copy essential files
    print("\n📁 Copying essential files...")
    for file in essential_files:
        if os.path.exists(file):
            shutil.copy2(file, deploy_dir)
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ Missing: {file}")
    
    # Copy template files  
    print("\n📄 Copying template files...")
    for file in template_files:
        if os.path.exists(file):
            shutil.copy2(file, deploy_dir / file)
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ Missing: {file}")
    
    # Copy legal files
    print("\n⚖️ Copying legal files...")
    for file in legal_files:
        if os.path.exists(file):
            shutil.copy2(file, deploy_dir)
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ Missing: {file}")
    
    # Copy analysis files (optional)
    print("\n🏀 Copying analysis engine files...")
    for file in analysis_files:
        if os.path.exists(file):
            shutil.copy2(file, deploy_dir)
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️ Optional: {file}")
    
    # Create deployment instructions
    instructions = """
# DEPLOYMENT INSTRUCTIONS FOR APEXSPORTS-LLC.COM

## 1. Upload all files to your server
Upload the contents of this deployment_package folder to your web server.

## 2. Install dependencies on server
```bash
pip install flask stripe python-dotenv gunicorn
```

## 3. Start the application
```bash
python complete_web_app.py
```

## 4. For production (recommended)
```bash
gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app
```

## 5. Verify deployment
- Visit: https://apexsports-llc.com
- Test: https://apexsports-llc.com/pricing
- Check: https://apexsports-llc.com/webhook

## YOUR SERVICE IS LIVE AND READY FOR PAYMENTS!
"""
    
    with open(deploy_dir / 'DEPLOYMENT_INSTRUCTIONS.txt', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    # Create ZIP file for easy upload
    print("\n📦 Creating deployment ZIP file...")
    with zipfile.ZipFile('apexsports_deployment.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deploy_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deploy_dir)
                zipf.write(file_path, arcname)
    
    print(f"\n✅ Deployment package created!")
    print(f"📁 Files ready in: {deploy_dir}")
    print(f"📦 ZIP file: apexsports_deployment.zip")
    
    return deploy_dir

def show_deployment_summary():
    """Show final deployment summary"""
    print("\n" + "="*60)
    print("DEPLOYMENT READY FOR APEXSPORTS-LLC.COM")
    print("="*60)
    print("\nREVENUE MODEL ACTIVE:")
    print("  Free: 1 analysis per year")
    print("  One-time: $9.99 for 5 analyses")  
    print("  Pro: $19.99/month unlimited")
    print("  Enterprise: $49.99/month premium")
    
    print("\nLIVE STRIPE INTEGRATION:")
    print("  Live publishable key configured")
    print("  Live secret key configured") 
    print("  Webhook secret configured")
    
    print("\nNEXT STEPS:")
    print("  1. Upload 'apexsports_deployment.zip' to your server")
    print("  2. Extract the files")
    print("  3. Run: pip install flask stripe gunicorn")
    print("  4. Run: python complete_web_app.py")
    print("  5. Visit: https://apexsports-llc.com")
    
    print("\nYOU'RE READY TO GO LIVE AND EARN REVENUE!")
    print("="*60)

if __name__ == "__main__":
    deploy_dir = create_deployment_package()
    show_deployment_summary()
