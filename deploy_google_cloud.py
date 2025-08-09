#!/usr/bin/env python3
"""
Google Cloud Platform Deployment Script
Basketball Analysis Service - Production Deployment to GCP
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class GoogleCloudDeployer:
    def __init__(self, project_id=None):
        self.project_id = project_id
        self.service_name = "basketball-analysis"
        self.region = "us-central1"
        self.image_name = f"gcr.io/{project_id}/{self.service_name}" if project_id else None
        
    def check_gcloud_auth(self):
        """Check if user is authenticated with Google Cloud"""
        try:
            result = subprocess.run(['gcloud', 'auth', 'list'], 
                                  capture_output=True, text=True, check=True)
            if "ACTIVE" not in result.stdout:
                print("❌ Not authenticated with Google Cloud")
                print("Run: gcloud auth login")
                return False
            print("✅ Google Cloud authentication verified")
            return True
        except subprocess.CalledProcessError:
            print("❌ gcloud CLI not found. Please install Google Cloud SDK")
            return False
    
    def check_project_setup(self):
        """Verify project configuration"""
        if not self.project_id:
            print("❌ Project ID not set")
            return False
            
        try:
            # Check if project exists and is accessible
            result = subprocess.run(['gcloud', 'projects', 'describe', self.project_id], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Project {self.project_id} verified")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ Cannot access project {self.project_id}")
            return False
    
    def enable_apis(self):
        """Enable required Google Cloud APIs"""
        apis = [
            'cloudbuild.googleapis.com',
            'run.googleapis.com',
            'appengine.googleapis.com',
            'secretmanager.googleapis.com',
            'storage.googleapis.com'
        ]
        
        print("🔧 Enabling required APIs...")
        for api in apis:
            try:
                subprocess.run(['gcloud', 'services', 'enable', api, 
                              '--project', self.project_id], check=True)
                print(f"✅ Enabled {api}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to enable {api}")
                return False
        return True
    
    def create_secrets(self):
        """Create secrets in Secret Manager"""
        print("🔐 Setting up secrets...")
        
        # Get Stripe keys from user
        stripe_secret = input("🔑 Stripe Secret Key (sk_test_... or sk_live_...): ").strip()
        stripe_publishable = input("🔑 Stripe Publishable Key (pk_test_... or pk_live_...): ").strip()
        
        if not stripe_secret or not stripe_publishable:
            print("⚠️  Skipping secret creation - no keys provided")
            return True
        
        try:
            # Create stripe-secret secret
            subprocess.run(['gcloud', 'secrets', 'create', 'stripe-secret', 
                          '--project', self.project_id], check=True)
            
            # Add secret versions
            subprocess.run(['gcloud', 'secrets', 'versions', 'add', 'stripe-secret',
                          '--data-file=-', '--project', self.project_id],
                         input=json.dumps({
                             'secret-key': stripe_secret,
                             'publishable-key': stripe_publishable
                         }), text=True, check=True)
            
            print("✅ Secrets created successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            if "already exists" in str(e):
                print("ℹ️  Secrets already exist - updating...")
                try:
                    subprocess.run(['gcloud', 'secrets', 'versions', 'add', 'stripe-secret',
                                  '--data-file=-', '--project', self.project_id],
                                 input=json.dumps({
                                     'secret-key': stripe_secret,
                                     'publishable-key': stripe_publishable
                                 }), text=True, check=True)
                    print("✅ Secrets updated successfully")
                    return True
                except subprocess.CalledProcessError:
                    print("❌ Failed to update secrets")
                    return False
            else:
                print(f"❌ Failed to create secrets: {e}")
                return False
    
    def build_and_push_image(self):
        """Build and push Docker image to Google Container Registry"""
        print("🏗️  Building Docker image...")
        
        try:
            # Build with Cloud Build for better performance
            subprocess.run(['gcloud', 'builds', 'submit', '--tag', self.image_name,
                          '--project', self.project_id], check=True)
            print(f"✅ Image built and pushed: {self.image_name}")
            return True
            
        except subprocess.CalledProcessError:
            print("❌ Failed to build and push image")
            return False
    
    def deploy_to_cloud_run(self):
        """Deploy to Google Cloud Run"""
        print("🚀 Deploying to Cloud Run...")
        
        try:
            cmd = [
                'gcloud', 'run', 'deploy', self.service_name,
                '--image', self.image_name,
                '--platform', 'managed',
                '--region', self.region,
                '--allow-unauthenticated',
                '--memory', '4Gi',
                '--cpu', '2',
                '--timeout', '900',
                '--max-instances', '10',
                '--project', self.project_id
            ]
            
            subprocess.run(cmd, check=True)
            
            # Get service URL
            result = subprocess.run([
                'gcloud', 'run', 'services', 'describe', self.service_name,
                '--platform', 'managed', '--region', self.region,
                '--format', 'value(status.url)', '--project', self.project_id
            ], capture_output=True, text=True, check=True)
            
            service_url = result.stdout.strip()
            print(f"✅ Deployed to Cloud Run: {service_url}")
            return service_url
            
        except subprocess.CalledProcessError:
            print("❌ Failed to deploy to Cloud Run")
            return None
    
    def deploy_to_app_engine(self):
        """Deploy to Google App Engine"""
        print("🚀 Deploying to App Engine...")
        
        try:
            subprocess.run(['gcloud', 'app', 'deploy', 'app.yaml', '--quiet',
                          '--project', self.project_id], check=True)
            
            # Get service URL
            result = subprocess.run([
                'gcloud', 'app', 'browse', '--no-launch-browser',
                '--project', self.project_id
            ], capture_output=True, text=True, check=True)
            
            print("✅ Deployed to App Engine")
            return True
            
        except subprocess.CalledProcessError:
            print("❌ Failed to deploy to App Engine")
            return False
    
    def setup_custom_domain(self, domain):
        """Setup custom domain mapping"""
        print(f"🌐 Setting up custom domain: {domain}")
        
        try:
            subprocess.run([
                'gcloud', 'run', 'domain-mappings', 'create',
                '--service', self.service_name,
                '--domain', domain,
                '--region', self.region,
                '--project', self.project_id
            ], check=True)
            
            print(f"✅ Domain mapping created for {domain}")
            print("📝 Add these DNS records to your domain:")
            print("   Type: CNAME")
            print("   Name: www")
            print("   Value: ghs.googlehosted.com")
            
            return True
            
        except subprocess.CalledProcessError:
            print(f"❌ Failed to setup domain mapping for {domain}")
            return False

def main():
    print("🏀 Basketball Analysis Service - Google Cloud Deployment")
    print("=" * 60)
    
    # Get project ID
    project_id = input("📋 Google Cloud Project ID: ").strip()
    if not project_id:
        print("❌ Project ID is required")
        return
    
    deployer = GoogleCloudDeployer(project_id)
    
    print("\n🔍 Pre-deployment checks...")
    if not deployer.check_gcloud_auth():
        return
    
    if not deployer.check_project_setup():
        return
    
    print("\n🔧 Setting up Google Cloud services...")
    if not deployer.enable_apis():
        return
    
    if not deployer.create_secrets():
        return
    
    # Choose deployment target
    print("\n🎯 Choose deployment target:")
    print("1. Cloud Run (Recommended)")
    print("2. App Engine")
    print("3. Both")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice in ['1', '3']:
        print("\n🏗️  Preparing Cloud Run deployment...")
        if not deployer.build_and_push_image():
            return
        
        service_url = deployer.deploy_to_cloud_run()
        if service_url:
            print(f"\n✅ Cloud Run deployment successful!")
            print(f"🌐 Service URL: {service_url}")
    
    if choice in ['2', '3']:
        print("\n🏗️  Preparing App Engine deployment...")
        if deployer.deploy_to_app_engine():
            print(f"\n✅ App Engine deployment successful!")
            print(f"🌐 Service URL: https://{project_id}.appspot.com")
    
    # Optional domain setup
    setup_domain = input("\n🌐 Setup custom domain? (y/N): ").strip().lower()
    if setup_domain == 'y':
        domain = input("Domain name (e.g., yourdomain.com): ").strip()
        if domain:
            deployer.setup_custom_domain(domain)
    
    print("\n🎉 Deployment Complete!")
    print("\n📋 Next Steps:")
    print("1. Test your deployed service")
    print("2. Configure your DNS (if using custom domain)")
    print("3. Set up monitoring and logging")
    print("4. Configure Stripe webhooks to point to your new URL")
    print("\n🔧 Useful commands:")
    print(f"  gcloud run services list --project {project_id}")
    print(f"  gcloud logs tail --service {deployer.service_name} --project {project_id}")

if __name__ == "__main__":
    main()
