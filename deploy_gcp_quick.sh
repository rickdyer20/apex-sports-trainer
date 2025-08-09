#!/bin/bash
# Google Cloud Deployment Script - Basketball Analysis Service
# Quick deployment commands for GCP

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="basketball-analysis"
REGION="us-central1"

echo -e "${BLUE}🏀 Basketball Analysis Service - Google Cloud Deployment${NC}"
echo "============================================================"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Please install Google Cloud SDK${NC}"
    exit 1
fi

# Get project ID
if [ -z "$PROJECT_ID" ]; then
    read -p "📋 Google Cloud Project ID: " PROJECT_ID
fi

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Project ID is required${NC}"
    exit 1
fi

IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo -e "${YELLOW}🔍 Setting up project: $PROJECT_ID${NC}"

# Set project
gcloud config set project $PROJECT_ID

# Enable APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    secretmanager.googleapis.com \
    storage.googleapis.com

# Build and deploy
echo -e "${YELLOW}🏗️  Building and deploying to Cloud Run...${NC}"

# Build with Cloud Build
gcloud builds submit --tag $IMAGE_NAME

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --timeout 900 \
    --max-instances 10 \
    --set-env-vars="FLASK_ENV=production,FLASK_DEBUG=False,TF_CPP_MIN_LOG_LEVEL=2,ENABLE_SHOULDER_ALIGNMENT_DETECTION=True"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --format 'value(status.url)')

echo -e "${GREEN}✅ Deployment successful!${NC}"
echo -e "${GREEN}🌐 Service URL: $SERVICE_URL${NC}"

# Test the deployment
echo -e "${YELLOW}🧪 Testing deployment...${NC}"
if curl -f "$SERVICE_URL/health" &> /dev/null; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
fi

echo -e "${BLUE}📋 Post-deployment tasks:${NC}"
echo "1. Configure Stripe webhooks to: $SERVICE_URL/webhook/stripe"
echo "2. Set up monitoring: gcloud logging metrics create"
echo "3. Configure domain mapping if needed"
echo ""
echo -e "${BLUE}🔧 Useful commands:${NC}"
echo "  View logs: gcloud logs tail --service $SERVICE_NAME"
echo "  Update service: gcloud run services update $SERVICE_NAME --region $REGION"
echo "  Delete service: gcloud run services delete $SERVICE_NAME --region $REGION"
