#!/usr/bin/env python3
"""
GCP Deployment Validation Script
Basketball Analysis Service - Pre-deployment checks
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_status(message, status="info"):
    """Print colored status messages"""
    colors = {
        "success": "\033[92m✅",
        "error": "\033[91m❌", 
        "warning": "\033[93m⚠️",
        "info": "\033[94mℹ️"
    }
    reset = "\033[0m"
    print(f"{colors.get(status, colors['info'])} {message}{reset}")

def check_prerequisites():
    """Check if required tools are installed"""
    print_status("Checking prerequisites...", "info")
    
    # Check gcloud
    try:
        result = subprocess.run(['gcloud', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_status("Google Cloud SDK installed", "success")
        else:
            print_status("Google Cloud SDK not found", "error")
            return False
    except FileNotFoundError:
        print_status("Google Cloud SDK not installed", "error")
        return False
    
    # Check Docker
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_status("Docker installed", "success")
        else:
            print_status("Docker not found (Cloud Run deployment will be limited)", "warning")
    except FileNotFoundError:
        print_status("Docker not installed (Cloud Run deployment will be limited)", "warning")
    
    # Check authentication
    try:
        result = subprocess.run(['gcloud', 'auth', 'list', '--filter=status:ACTIVE', '--format=value(account)'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            print_status(f"Authenticated as: {result.stdout.strip()}", "success")
        else:
            print_status("Not authenticated with Google Cloud", "error")
            print("Run: gcloud auth login")
            return False
    except:
        print_status("Could not check authentication status", "error")
        return False
    
    return True

def check_required_files():
    """Check if all required deployment files exist"""
    print_status("Checking required files...", "info")
    
    required_files = [
        'app.yaml',
        'cloudbuild.yaml', 
        'main.py',
        'requirements_gcp.txt',
        'cloud-run-service.yaml',
        'basketball_analysis_service.py',
        'web_app.py',
        'ideal_shot_guide.json'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print_status(f"{file} exists", "success")
        else:
            print_status(f"{file} missing", "error")
            missing_files.append(file)
    
    if missing_files:
        print_status(f"Missing files: {', '.join(missing_files)}", "error")
        return False
    
    return True

def validate_app_yaml():
    """Validate app.yaml configuration"""
    print_status("Validating app.yaml...", "info")
    
    try:
        with open('app.yaml', 'r') as f:
            content = f.read()
            
        # Check runtime
        if 'runtime: python311' in content:
            print_status("Python 3.11 runtime configured", "success")
        else:
            print_status("Python 3.11 runtime not configured", "warning")
            
        # Check required environment variables
        required_envs = [
            'FLASK_ENV: production',
            'TF_CPP_MIN_LOG_LEVEL',
            'MEDIAPIPE_DISABLE_GPU'
        ]
        
        for env in required_envs:
            if env in content:
                print_status(f"Environment variable {env.split(':')[0]} configured", "success")
            else:
                print_status(f"Environment variable {env.split(':')[0]} missing", "warning")
                
        return True
        
    except FileNotFoundError:
        print_status("app.yaml not found", "error")
        return False
    except Exception as e:
        print_status(f"Error reading app.yaml: {e}", "error")
        return False

def test_local_import():
    """Test if the main modules can be imported"""
    print_status("Testing module imports...", "info")
    
    try:
        import basketball_analysis_service
        print_status("basketball_analysis_service imports successfully", "success")
    except ImportError as e:
        print_status(f"basketball_analysis_service import failed: {e}", "error")
        return False
        
    try:
        import web_app
        print_status("web_app imports successfully", "success")
    except ImportError as e:
        print_status(f"web_app import failed: {e}", "error")
        return False
        
    return True

def check_gcp_project():
    """Check current GCP project configuration"""
    print_status("Checking GCP project configuration...", "info")
    
    try:
        # Get current project
        result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            project_id = result.stdout.strip()
            print_status(f"Current project: {project_id}", "success")
            
            # Check if billing is enabled
            billing_result = subprocess.run(['gcloud', 'billing', 'projects', 'describe', project_id],
                                          capture_output=True, text=True)
            if billing_result.returncode == 0:
                print_status("Billing is enabled", "success")
            else:
                print_status("Billing may not be enabled", "warning")
                
            return True
        else:
            print_status("No GCP project configured", "error")
            print("Run: gcloud config set project YOUR_PROJECT_ID")
            return False
    except:
        print_status("Could not check GCP project", "error")
        return False

def check_required_apis():
    """Check if required GCP APIs are enabled"""
    print_status("Checking required APIs...", "info")
    
    required_apis = [
        'appengine.googleapis.com',
        'cloudbuild.googleapis.com',
        'run.googleapis.com'
    ]
    
    try:
        result = subprocess.run(['gcloud', 'services', 'list', '--enabled', '--format=value(name)'],
                              capture_output=True, text=True)
        enabled_apis = result.stdout.strip().split('\n')
        
        for api in required_apis:
            if api in enabled_apis:
                print_status(f"{api} enabled", "success")
            else:
                print_status(f"{api} not enabled", "warning")
                print(f"Enable with: gcloud services enable {api}")
                
    except:
        print_status("Could not check API status", "warning")

def generate_deployment_recommendations():
    """Generate deployment recommendations based on checks"""
    print_status("Generating deployment recommendations...", "info")
    
    print("\n🚀 Deployment Recommendations:")
    print("=" * 50)
    
    print("\n1. For beginners (App Engine):")
    print("   gcloud app deploy app.yaml")
    
    print("\n2. For scalability (Cloud Run):")
    print("   gcloud run deploy --source .")
    
    print("\n3. Automated deployment:")
    print("   ./deploy_gcp.sh")
    
    print("\n4. CI/CD Pipeline:")
    print("   Connect repository to Cloud Build")
    print("   Builds will trigger automatically on git push")
    
    print("\n📝 Next Steps:")
    print("- Review environment variables in app.yaml")
    print("- Test locally before deploying: python main.py")
    print("- Monitor logs after deployment")
    print("- Set up alerts for production monitoring")

def main():
    """Main validation function"""
    print("🏀 Basketball Analysis Service - GCP Deployment Validation")
    print("=" * 60)
    
    checks = [
        ("Prerequisites", check_prerequisites),
        ("Required Files", check_required_files), 
        ("App Engine Config", validate_app_yaml),
        ("Module Imports", test_local_import),
        ("GCP Project", check_gcp_project),
        ("Required APIs", check_required_apis)
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}")
        print("-" * 30)
        if check_func():
            passed_checks += 1
    
    print(f"\n📊 Validation Summary")
    print("=" * 30)
    print(f"Passed: {passed_checks}/{total_checks} checks")
    
    if passed_checks == total_checks:
        print_status("🎉 All checks passed! Ready for deployment.", "success")
    elif passed_checks >= total_checks - 1:
        print_status("⚠️ Minor issues found. Deployment should still work.", "warning")
    else:
        print_status("❌ Critical issues found. Fix before deployment.", "error")
        sys.exit(1)
    
    generate_deployment_recommendations()

if __name__ == "__main__":
    main()
