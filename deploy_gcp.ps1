# Google Cloud Platform Deployment Script (PowerShell)
# Basketball Analysis Service - Automated Deployment for Windows

param(
    [string]$ProjectId = "",
    [string]$Region = "us-central1",
    [string]$ServiceName = "basketball-analysis",
    [string]$AppEngineRegion = "us-central"
)

# Color functions
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Blue }

Write-Host "🏀 Basketball Analysis Service - GCP Deployment" -ForegroundColor Blue
Write-Host "==================================================" -ForegroundColor Blue

# Check prerequisites
function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check if gcloud is installed
    try {
        $null = Get-Command gcloud -ErrorAction Stop
    }
    catch {
        Write-Error "Google Cloud SDK is not installed. Please install it first."
        Write-Host "Visit: https://cloud.google.com/sdk/docs/install"
        exit 1
    }
    
    # Check if Docker is installed
    try {
        $null = Get-Command docker -ErrorAction Stop
    }
    catch {
        Write-Warning "Docker is not installed. Cloud Run deployment will be skipped."
        $script:DockerAvailable = $false
    }
    
    # Check authentication
    $authAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
    if (-not $authAccount) {
        Write-Error "Not authenticated with Google Cloud. Please run: gcloud auth login"
        exit 1
    }
    
    Write-Success "Prerequisites check completed"
}

# Set up project
function Initialize-Project {
    if (-not $ProjectId) {
        $ProjectId = Read-Host "Enter your Google Cloud Project ID"
    }
    
    Write-Info "Setting up project: $ProjectId"
    
    # Set the project
    gcloud config set project $ProjectId
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to set project. Please check project ID."
        exit 1
    }
    
    # Enable required APIs
    Write-Info "Enabling required Google Cloud APIs..."
    $apis = @(
        "appengine.googleapis.com",
        "cloudbuild.googleapis.com", 
        "run.googleapis.com",
        "storage.googleapis.com",
        "logging.googleapis.com",
        "monitoring.googleapis.com"
    )
    
    foreach ($api in $apis) {
        Write-Info "Enabling $api..."
        gcloud services enable $api
    }
    
    Write-Success "Project setup completed"
}

# Deploy to App Engine
function Deploy-AppEngine {
    Write-Info "Deploying to Google App Engine..."
    
    # Check if App Engine app exists
    $appExists = gcloud app describe --format="value(id)" 2>$null
    if (-not $appExists) {
        Write-Info "Creating App Engine application..."
        gcloud app create --region=$AppEngineRegion
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to create App Engine application"
            return
        }
    }
    
    # Deploy using app.yaml
    Write-Info "Deploying application..."
    gcloud app deploy app.yaml --quiet --promote
    if ($LASTEXITCODE -ne 0) {
        Write-Error "App Engine deployment failed"
        return
    }
    
    # Get the deployed URL
    $appUrl = gcloud app browse --no-launch-browser 2>&1 | Select-String "https://" | ForEach-Object { $_.Line.Split()[-1] }
    
    Write-Success "App Engine deployment completed"
    Write-Info "Application URL: $appUrl"
    
    # Test the deployment
    Write-Info "Testing deployment..."
    try {
        $response = Invoke-WebRequest -Uri "$appUrl/health" -TimeoutSec 30 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Success "Health check passed"
        }
        else {
            Write-Warning "Health check returned status: $($response.StatusCode)"
        }
    }
    catch {
        Write-Warning "Health check failed. Check the logs: gcloud app logs tail -s default"
    }
}

# Deploy to Cloud Run
function Deploy-CloudRun {
    if (-not $script:DockerAvailable) {
        Write-Warning "Docker not available. Skipping Cloud Run deployment."
        return
    }
    
    Write-Info "Deploying to Google Cloud Run..."
    
    # Build and push container image
    Write-Info "Building container image..."
    docker build -t "gcr.io/$ProjectId/$ServiceName`:latest" .
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker build failed"
        return
    }
    
    Write-Info "Pushing image to Container Registry..."
    docker push "gcr.io/$ProjectId/$ServiceName`:latest"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker push failed"
        return
    }
    
    # Deploy to Cloud Run
    Write-Info "Deploying to Cloud Run..."
    gcloud run deploy $ServiceName `
        --image "gcr.io/$ProjectId/$ServiceName`:latest" `
        --platform managed `
        --region $Region `
        --allow-unauthenticated `
        --memory 4Gi `
        --cpu 2 `
        --timeout 300 `
        --concurrency 10 `
        --max-instances 100 `
        --set-env-vars="FLASK_ENV=production,TF_CPP_MIN_LOG_LEVEL=2,MEDIAPIPE_DISABLE_GPU=1"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Cloud Run deployment failed"
        return
    }
    
    # Get the deployed URL
    $cloudRunUrl = gcloud run services describe $ServiceName --region=$Region --format="value(status.url)"
    
    Write-Success "Cloud Run deployment completed"
    Write-Info "Service URL: $cloudRunUrl"
    
    # Test the deployment
    Write-Info "Testing Cloud Run deployment..."
    try {
        $response = Invoke-WebRequest -Uri "$cloudRunUrl/health" -TimeoutSec 30 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Success "Health check passed"
        }
        else {
            Write-Warning "Health check returned status: $($response.StatusCode)"
        }
    }
    catch {
        Write-Warning "Health check failed. Check logs: gcloud run logs tail --service=$ServiceName --region=$Region"
    }
}

# Set up monitoring
function Initialize-Monitoring {
    Write-Info "Setting up monitoring and logging..."
    
    # Create log-based metrics
    $logFilter = 'resource.type="gae_app" OR resource.type="cloud_run_revision" severity>=ERROR'
    gcloud logging metrics create basketball_analysis_errors `
        --description="Basketball Analysis Service Errors" `
        --log-filter="$logFilter" `
        --quiet 2>$null
    
    Write-Success "Monitoring setup completed"
}

# Main execution
function Main {
    $script:DockerAvailable = $true
    
    Test-Prerequisites
    Initialize-Project
    
    Write-Host ""
    Write-Host "Choose deployment option:"
    Write-Host "1) App Engine (Recommended for beginners)"
    Write-Host "2) Cloud Run (Recommended for scalability)" 
    Write-Host "3) Both App Engine and Cloud Run"
    Write-Host "4) Exit"
    
    $choice = Read-Host "Enter your choice [1-4]"
    
    switch ($choice) {
        "1" { Deploy-AppEngine }
        "2" { Deploy-CloudRun }
        "3" { 
            Deploy-AppEngine
            Deploy-CloudRun 
        }
        "4" { 
            Write-Info "Deployment cancelled"
            exit 0 
        }
        default { 
            Write-Error "Invalid choice. Please try again."
            exit 1 
        }
    }
    
    Initialize-Monitoring
    
    Write-Host ""
    Write-Success "🎉 Deployment completed successfully!"
    Write-Host ""
    Write-Info "Next steps:"
    Write-Host "- Monitor your application logs"
    Write-Host "- Set up domain mapping if needed"
    Write-Host "- Configure custom environment variables"
    Write-Host "- Set up CI/CD with Cloud Build"
    Write-Host ""
    Write-Info "Useful commands:"
    Write-Host "- View App Engine logs: gcloud app logs tail -s default"
    Write-Host "- View Cloud Run logs: gcloud run logs tail --service=$ServiceName --region=$Region"
    Write-Host "- Scale Cloud Run: gcloud run services update $ServiceName --region=$Region --max-instances=50"
    Write-Host "- Update App Engine: gcloud app deploy"
}

# Execute main function
Main
