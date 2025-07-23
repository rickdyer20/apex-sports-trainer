# Basketball Analysis Service - Docker Build & Test
# PowerShell script for containerized deployment

Write-Host "🐳 Basketball Analysis Service - Docker Deployment" -ForegroundColor Cyan

# Check if Docker is running
try {
    docker --version
    Write-Host "✅ Docker is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Step 1: Build Docker image
Write-Host "`n🔨 Step 1: Building Docker Image" -ForegroundColor Yellow
docker build -t basketball-analysis:latest .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker image built successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}

# Step 2: Run tests in container
Write-Host "`n🧪 Step 2: Running Tests in Container" -ForegroundColor Yellow
docker run --rm basketball-analysis:latest python -m pytest test_basketball_analysis.py -v --tb=short

# Step 3: Start container with Docker Compose
Write-Host "`n🚀 Step 3: Starting Full Stack with Docker Compose" -ForegroundColor Yellow
Write-Host "Starting services: web app, database, Redis, monitoring..."
Write-Host "Web application will be available at http://localhost:5000"
Write-Host "Prometheus monitoring at http://localhost:9090"
Write-Host "Grafana dashboard at http://localhost:3000"
Write-Host ""
Write-Host "Press Ctrl+C to stop all services"
Write-Host ""

# Start Docker Compose stack
docker-compose up
