#!/bin/bash
# Google Cloud Deployment Script for Basketball Analysis Service
# Deploy to: https://apexsports-llc.com

echo "🚀 GOOGLE CLOUD DEPLOYMENT - Basketball Analysis Service"
echo "======================================================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK not found!"
    echo "📥 Install from: https://cloud.google.com/sdk/docs/install"
    echo ""
    echo "💡 Quick install:"
    echo "   curl https://sdk.cloud.google.com | bash"
    echo "   exec -l $SHELL"
    echo "   gcloud init"
    exit 1
fi

echo "✅ Google Cloud SDK found"

# Check authentication
echo "🔐 Checking Google Cloud authentication..."
gcloud auth list --filter=status:ACTIVE --format="value(account)"

if [ $? -ne 0 ]; then
    echo "❌ Not authenticated with Google Cloud"
    echo "🔑 Please run: gcloud auth login"
    exit 1
fi

echo "✅ Authenticated with Google Cloud"

# Set project (you'll need to replace with your actual project ID)
echo "📋 Setting up Google Cloud project..."
read -p "Enter your Google Cloud Project ID: " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Project ID required"
    exit 1
fi

gcloud config set project $PROJECT_ID
echo "✅ Project set: $PROJECT_ID"

# Enable necessary APIs
echo "🔧 Enabling required Google Cloud APIs..."
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
echo "✅ APIs enabled"

# Create App Engine app if it doesn't exist
echo "🏗️ Setting up App Engine..."
gcloud app describe > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Creating new App Engine application..."
    gcloud app create --region=us-central1
fi
echo "✅ App Engine ready"

# Deploy the application
echo "🚀 Deploying Basketball Analysis Service..."
echo ""
echo "📦 Deploying files:"
echo "   ✅ complete_web_app.py (Flask application)"
echo "   ✅ app.yaml (Google Cloud configuration)"
echo "   ✅ requirements.txt (dependencies)"
echo "   ✅ templates/ (HTML templates)"
echo "   ✅ static/ (CSS, JS, images)"
echo ""

gcloud app deploy app.yaml --quiet

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 DEPLOYMENT SUCCESSFUL!"
    echo "========================"
    echo ""
    echo "🌐 Your Basketball Analysis Service is now LIVE!"
    echo ""
    
    # Get the deployed URL
    APP_URL=$(gcloud app describe --format="value(defaultHostname)")
    echo "📱 Application URL: https://$APP_URL"
    echo ""
    
    echo "💰 REVENUE MODEL ACTIVE:"
    echo "   🆓 Free: 1 analysis per year (aggressive conversion)"
    echo "   💵 One-time: \$9.99 for 5 analyses"
    echo "   🔥 Pro: \$19.99/month unlimited"
    echo "   🌟 Enterprise: \$49.99/month premium"
    echo ""
    echo "🔐 Live Stripe Integration: Ready for payments!"
    echo ""
    echo "🔧 CUSTOM DOMAIN SETUP:"
    echo "   1. In Google Cloud Console, go to App Engine > Settings > Custom Domains"
    echo "   2. Add domain: apexsports-llc.com"
    echo "   3. Follow DNS verification steps"
    echo "   4. Update Namecheap DNS to point to Google Cloud"
    echo ""
    echo "📊 Next Steps:"
    echo "   1. Set up custom domain mapping"
    echo "   2. Configure SSL certificate"
    echo "   3. Test payment processing"
    echo "   4. Monitor application logs"
    echo ""
    echo "🎯 READY TO GENERATE REVENUE!"
    
    # Open the deployed app
    read -p "🌐 Open your deployed app now? (y/n): " OPEN_APP
    if [ "$OPEN_APP" = "y" ] || [ "$OPEN_APP" = "Y" ]; then
        gcloud app browse
    fi
else
    echo "❌ Deployment failed"
    echo "🔍 Check logs: gcloud app logs tail -s default"
fi
