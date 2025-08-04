#!/bin/bash
# Google Cloud Deployment Script for Basketball Analysis Service

echo "🏀 Basketball Analysis - Google Cloud Deployment"
echo "================================================"

# Check if gcloud CLI is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI not found. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with Google Cloud. Please run:"
    echo "   gcloud auth login"
    exit 1
fi

# Set project variables
PROJECT_ID=${1:-"basketball-analysis-app"}
SERVICE_NAME="basketball-analysis"
REGION="us-central1"

echo "📋 Deployment Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   Service: $SERVICE_NAME"
echo "   Region: $REGION"
echo ""

# Create project if it doesn't exist
echo "🔧 Setting up Google Cloud project..."
gcloud projects create $PROJECT_ID --name="Basketball Analysis Service" 2>/dev/null || echo "Project already exists"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔌 Enabling required APIs..."
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com

# Create App Engine app if it doesn't exist
echo "🚀 Setting up App Engine..."
gcloud app create --region=$REGION 2>/dev/null || echo "App Engine already initialized"

# Deploy to App Engine
echo "📦 Deploying Basketball Analysis Service..."
echo "   This may take 5-10 minutes..."

# Use the Google Cloud optimized requirements
cp requirements_gcloud.txt requirements.txt

# Deploy
gcloud app deploy app.yaml --quiet

# Get the service URL
APP_URL=$(gcloud app describe --format="value(defaultHostname)")
echo ""
echo "✅ Deployment Complete!"
echo "🌐 Your Basketball Analysis Service is live at:"
echo "   https://$APP_URL"
echo ""
echo "📊 Service Features:"
echo "   • Video upload and analysis"
echo "   • Real-time progress tracking"
echo "   • Professional PDF reports"
echo "   • Download complete analysis packages"
echo ""
echo "🔧 Management Commands:"
echo "   View logs: gcloud app logs tail -s default"
echo "   Open app:  gcloud app browse"
echo "   Stop app:  gcloud app versions stop [VERSION]"
echo ""

# Test the deployment
echo "🧪 Testing deployment..."
if curl -s "https://$APP_URL/health" | grep -q "healthy"; then
    echo "✅ Health check passed!"
else
    echo "⚠️  Health check failed - check logs for issues"
fi

echo "🎯 Basketball Analysis Service is ready for use!"
