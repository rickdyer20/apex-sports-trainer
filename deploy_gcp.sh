#!/bin/bash

# Google Cloud Platform Deployment Script
# Basketball Analysis Service - Automated Deployment

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=""
REGION="us-central1"
SERVICE_NAME="basketball-analysis"
APP_ENGINE_REGION="us-central"

echo -e "${BLUE}🏀 Basketball Analysis Service - GCP Deployment${NC}"
echo "=================================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud SDK is not installed. Please install it first."
        echo "Visit: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    # Check if Docker is installed (for Cloud Run)
    if ! command -v docker &> /dev/null; then
        print_warning "Docker is not installed. Cloud Run deployment will be skipped."
    fi
    
    # Check if authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Not authenticated with Google Cloud. Please run: gcloud auth login"
        exit 1
    fi
    
    print_status "Prerequisites check completed"
}

# Set up project
setup_project() {
    if [ -z "$PROJECT_ID" ]; then
        echo -n "Enter your Google Cloud Project ID: "
        read PROJECT_ID
    fi
    
    print_info "Setting up project: $PROJECT_ID"
    
    # Set the project
    gcloud config set project $PROJECT_ID
    
    # Enable required APIs
    print_info "Enabling required Google Cloud APIs..."
    gcloud services enable \
        appengine.googleapis.com \
        cloudbuild.googleapis.com \
        run.googleapis.com \
        storage.googleapis.com \
        logging.googleapis.com \
        monitoring.googleapis.com
    
    print_status "Project setup completed"
}

# Deploy to App Engine
deploy_app_engine() {
    print_info "Deploying to Google App Engine..."
    
    # Create App Engine app if it doesn't exist
    if ! gcloud app describe &> /dev/null; then
        print_info "Creating App Engine application..."
        gcloud app create --region=$APP_ENGINE_REGION
    fi
    
    # Deploy using app.yaml
    print_info "Deploying application..."
    gcloud app deploy app.yaml --quiet --promote
    
    # Get the deployed URL
    APP_URL=$(gcloud app browse --no-launch-browser 2>&1 | grep "https://" | awk '{print $NF}')
    
    print_status "App Engine deployment completed"
    print_info "Application URL: $APP_URL"
    
    # Test the deployment
    print_info "Testing deployment..."
    if curl -f -s "$APP_URL/health" > /dev/null; then
        print_status "Health check passed"
    else
        print_warning "Health check failed. Check the logs: gcloud app logs tail -s default"
    fi
}

# Deploy to Cloud Run
deploy_cloud_run() {
    if ! command -v docker &> /dev/null; then
        print_warning "Docker not found. Skipping Cloud Run deployment."
        return
    fi
    
    print_info "Deploying to Google Cloud Run..."
    
    # Build and push container image
    print_info "Building container image..."
    docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .
    
    print_info "Pushing image to Container Registry..."
    docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest
    
    # Deploy to Cloud Run
    print_info "Deploying to Cloud Run..."
    gcloud run deploy $SERVICE_NAME \
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 4Gi \
        --cpu 2 \
        --timeout 300 \
        --concurrency 10 \
        --max-instances 100 \
        --set-env-vars="FLASK_ENV=production,TF_CPP_MIN_LOG_LEVEL=2,MEDIAPIPE_DISABLE_GPU=1"
    
    # Get the deployed URL
    CLOUD_RUN_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    
    print_status "Cloud Run deployment completed"
    print_info "Service URL: $CLOUD_RUN_URL"
    
    # Test the deployment
    print_info "Testing Cloud Run deployment..."
    if curl -f -s "$CLOUD_RUN_URL/health" > /dev/null; then
        print_status "Health check passed"
    else
        print_warning "Health check failed. Check the logs: gcloud run logs tail --service=$SERVICE_NAME --region=$REGION"
    fi
}

# Set up monitoring and logging
setup_monitoring() {
    print_info "Setting up monitoring and logging..."
    
    # Create log-based metrics
    gcloud logging metrics create basketball_analysis_errors \
        --description="Basketball Analysis Service Errors" \
        --log-filter='resource.type="gae_app" OR resource.type="cloud_run_revision"
        severity>=ERROR' \
        --quiet || true
    
    print_status "Monitoring setup completed"
}

# Main deployment menu
main() {
    check_prerequisites
    setup_project
    
    echo ""
    echo "Choose deployment option:"
    echo "1) App Engine (Recommended for beginners)"
    echo "2) Cloud Run (Recommended for scalability)"
    echo "3) Both App Engine and Cloud Run"
    echo "4) Exit"
    echo -n "Enter your choice [1-4]: "
    read choice
    
    case $choice in
        1)
            deploy_app_engine
            ;;
        2)
            deploy_cloud_run
            ;;
        3)
            deploy_app_engine
            deploy_cloud_run
            ;;
        4)
            print_info "Deployment cancelled"
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please try again."
            exit 1
            ;;
    esac
    
    setup_monitoring
    
    echo ""
    print_status "🎉 Deployment completed successfully!"
    echo ""
    print_info "Next steps:"
    echo "- Monitor your application logs"
    echo "- Set up domain mapping if needed"
    echo "- Configure custom environment variables"
    echo "- Set up CI/CD with Cloud Build"
    echo ""
    print_info "Useful commands:"
    echo "- View logs: gcloud app logs tail -s default (App Engine)"
    echo "- View logs: gcloud run logs tail --service=$SERVICE_NAME --region=$REGION (Cloud Run)"
    echo "- Scale service: gcloud run services update $SERVICE_NAME --region=$REGION --max-instances=50"
    echo "- Update app: gcloud app deploy"
}

# Run the main function
main "$@"
