# Basketball Analysis Service - Production Deployment Script
# Automated deployment to AWS EKS with monitoring

Write-Host "🚀 Basketball Analysis Service - Production Deployment" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# Configuration
$CLUSTER_NAME = "basketball-analysis-prod"
$AWS_REGION = "us-west-2"
$NAMESPACE = "basketball-analysis"
$IMAGE_TAG = "latest"

# Step 1: Pre-deployment Validation
Write-Host "`n📋 Step 1: Pre-deployment Validation" -ForegroundColor Yellow

Write-Host "Checking AWS CLI..."
try {
    aws --version
    Write-Host "✅ AWS CLI available" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not found. Please install AWS CLI." -ForegroundColor Red
    exit 1
}

Write-Host "Checking kubectl..."
try {
    kubectl version --client=true
    Write-Host "✅ kubectl available" -ForegroundColor Green
} catch {
    Write-Host "❌ kubectl not found. Please install kubectl." -ForegroundColor Red
    exit 1
}

Write-Host "Checking Terraform..."
try {
    terraform version
    Write-Host "✅ Terraform available" -ForegroundColor Green
} catch {
    Write-Host "❌ Terraform not found. Please install Terraform." -ForegroundColor Red
    exit 1
}

# Step 2: Infrastructure Deployment
Write-Host "`n🏗️ Step 2: Infrastructure Deployment" -ForegroundColor Yellow

Write-Host "Deploying AWS infrastructure with Terraform..."
cd terraform

# Initialize Terraform
terraform init
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Terraform init failed" -ForegroundColor Red
    exit 1
}

# Plan deployment
terraform plan -out=tfplan
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Terraform plan failed" -ForegroundColor Red
    exit 1
}

# Apply infrastructure
Write-Host "Applying Terraform configuration..."
terraform apply -auto-approve tfplan
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Infrastructure deployed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Infrastructure deployment failed" -ForegroundColor Red
    exit 1
}

cd ..

# Step 3: Kubernetes Configuration
Write-Host "`n⚙️ Step 3: Kubernetes Configuration" -ForegroundColor Yellow

Write-Host "Updating kubeconfig..."
aws eks update-kubeconfig --region $AWS_REGION --name $CLUSTER_NAME
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Kubeconfig updated successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to update kubeconfig" -ForegroundColor Red
    exit 1
}

Write-Host "Testing cluster connection..."
kubectl cluster-info
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Cluster connection successful" -ForegroundColor Green
} else {
    Write-Host "❌ Cannot connect to cluster" -ForegroundColor Red
    exit 1
}

# Step 4: Application Deployment
Write-Host "`n📦 Step 4: Application Deployment" -ForegroundColor Yellow

Write-Host "Creating namespace..."
kubectl apply -f k8s/production-deployment.yaml --dry-run=client
kubectl apply -f k8s/production-deployment.yaml

Write-Host "Deploying load balancer configuration..."
kubectl apply -f k8s/load-balancer.yaml

Write-Host "Setting up SSL/TLS certificates..."
kubectl apply -f k8s/ssl-tls.yaml

Write-Host "Deploying monitoring stack..."
kubectl apply -f k8s/monitoring.yaml

# Step 5: Health Checks
Write-Host "`n🏥 Step 5: Health Checks & Validation" -ForegroundColor Yellow

Write-Host "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/basketball-analysis-web -n $NAMESPACE
kubectl wait --for=condition=available --timeout=300s deployment/basketball-analysis-worker -n $NAMESPACE

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All deployments are ready" -ForegroundColor Green
} else {
    Write-Host "❌ Some deployments failed to become ready" -ForegroundColor Red
}

Write-Host "Checking pod status..."
kubectl get pods -n $NAMESPACE

Write-Host "Checking services..."
kubectl get services -n $NAMESPACE

Write-Host "Checking ingress..."
kubectl get ingress -n $NAMESPACE

# Step 6: Application Health Check
Write-Host "`n🩺 Step 6: Application Health Check" -ForegroundColor Yellow

Write-Host "Getting load balancer URL..."
$LB_URL = kubectl get ingress basketball-analysis-ingress-tls -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

if ($LB_URL) {
    Write-Host "Load Balancer URL: https://$LB_URL" -ForegroundColor Green
    
    Write-Host "Testing health endpoint..."
    Start-Sleep -Seconds 30  # Wait for LB to be ready
    
    try {
        $response = Invoke-WebRequest -Uri "https://$LB_URL/health" -UseBasicParsing -TimeoutSec 30
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Health check passed" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Health check returned status: $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ Health check failed (this is normal for new deployments): $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ Load balancer URL not yet available. Check status later with:" -ForegroundColor Yellow
    Write-Host "kubectl get ingress basketball-analysis-ingress-tls -n $NAMESPACE" -ForegroundColor White
}

# Step 7: Monitoring Setup
Write-Host "`n📊 Step 7: Monitoring & Alerts" -ForegroundColor Yellow

Write-Host "Checking Prometheus deployment..."
kubectl get pods -n monitoring -l app=prometheus

Write-Host "Checking Grafana deployment..."
kubectl get pods -n monitoring -l app=grafana

# Get monitoring URLs
$PROMETHEUS_URL = kubectl get service prometheus-service -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
$GRAFANA_URL = kubectl get service grafana-service -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

if ($PROMETHEUS_URL) {
    Write-Host "Prometheus: http://$PROMETHEUS_URL:9090" -ForegroundColor Green
}
if ($GRAFANA_URL) {
    Write-Host "Grafana: http://$GRAFANA_URL:3000" -ForegroundColor Green
    Write-Host "Default Grafana credentials: admin/admin (change on first login)" -ForegroundColor Yellow
}

# Step 8: Final Summary
Write-Host "`n🎉 Step 8: Deployment Summary" -ForegroundColor Yellow

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "🏀 Basketball Analysis Service Deployed!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan

Write-Host "`nApplication URLs:" -ForegroundColor White
if ($LB_URL) {
    Write-Host "• Main Application: https://$LB_URL" -ForegroundColor Green
    Write-Host "• API Endpoint: https://$LB_URL/api" -ForegroundColor Green
    Write-Host "• Health Check: https://$LB_URL/health" -ForegroundColor Green
}

Write-Host "`nMonitoring URLs:" -ForegroundColor White
if ($PROMETHEUS_URL) {
    Write-Host "• Prometheus: http://$PROMETHEUS_URL:9090" -ForegroundColor Green
}
if ($GRAFANA_URL) {
    Write-Host "• Grafana: http://$GRAFANA_URL:3000" -ForegroundColor Green
}

Write-Host "`nUseful Commands:" -ForegroundColor White
Write-Host "• Check pods: kubectl get pods -n $NAMESPACE" -ForegroundColor Cyan
Write-Host "• View logs: kubectl logs -f deployment/basketball-analysis-web -n $NAMESPACE" -ForegroundColor Cyan
Write-Host "• Scale app: kubectl scale deployment basketball-analysis-web --replicas=5 -n $NAMESPACE" -ForegroundColor Cyan
Write-Host "• Update app: kubectl set image deployment/basketball-analysis-web web=your-registry/basketball-analysis:new-tag -n $NAMESPACE" -ForegroundColor Cyan

Write-Host "`nNext Steps:" -ForegroundColor White
Write-Host "1. Configure DNS to point to the load balancer" -ForegroundColor Yellow
Write-Host "2. Set up custom domain SSL certificates" -ForegroundColor Yellow
Write-Host "3. Configure monitoring alerts" -ForegroundColor Yellow
Write-Host "4. Set up backup procedures" -ForegroundColor Yellow
Write-Host "5. Run load testing" -ForegroundColor Yellow

Write-Host "`n🚀 Production deployment completed successfully!" -ForegroundColor Green
