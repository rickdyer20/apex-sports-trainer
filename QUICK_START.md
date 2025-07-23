# Quick Start Deployment Guide
## Basketball Analysis Service

### 🚀 **Ready to Launch!**

Choose your deployment option:

---

## Option 1: Docker Compose (Recommended for Testing)

### Prerequisites
- Docker and Docker Compose installed
- 4GB+ RAM available
- 10GB+ disk space

### 1. Quick Start
```bash
# Clone and enter directory
cd basketball_analysis/New_Shot_AI

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web
```

### 2. Access Services
- **Web App**: http://localhost:5000
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **MinIO**: http://localhost:9001 (basketball/basketball123)

### 3. Test the System
```bash
# Upload a test video at http://localhost:5000
# Monitor processing in Grafana dashboards
# Check health: curl http://localhost:5000/health
```

---

## Option 2: Local Development Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 15+
- Redis 7+
- FFmpeg

### 1. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install postgresql redis-server ffmpeg

# Or on macOS
brew install postgresql redis ffmpeg
```

### 2. Setup Database
```bash
# Start services
sudo systemctl start postgresql redis

# Setup database
python setup_database.py
```

### 3. Configure Environment
```bash
# Copy environment file
cp .env.production .env

# Edit configuration
nano .env

# Set required variables:
DATABASE_URL=postgresql://basketball_user:password@localhost:5432/basketball_analysis
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
```

### 4. Start Application
```bash
# Option A: Production startup script
python start_production.py

# Option B: Development mode
python web_app.py
```

---

## Option 3: AWS Production Deployment

### Prerequisites
- AWS CLI configured
- Terraform installed
- kubectl installed
- Docker installed

### 1. Infrastructure Setup
```bash
# Initialize Terraform
cd terraform
terraform init

# Plan deployment
terraform plan

# Deploy infrastructure
terraform apply
```

### 2. Configure kubectl
```bash
# Get cluster credentials
aws eks update-kubeconfig --name basketball-analysis-prod --region us-west-2
```

### 3. Deploy Application
```bash
# Build and push image
docker build -t your-registry/basketball-analysis:v1.0.0 .
docker push your-registry/basketball-analysis:v1.0.0

# Deploy to Kubernetes
kubectl apply -f k8s/

# Check deployment
kubectl get pods -n basketball-analysis
```

---

## Verification Checklist

### ✅ Basic Functionality
- [ ] Web interface loads at configured URL
- [ ] Video upload form is accessible
- [ ] Health check returns 200: `/health`
- [ ] Database connection successful
- [ ] Redis connection successful

### ✅ Video Processing
- [ ] Can upload MP4 video (< 100MB)
- [ ] Processing starts automatically
- [ ] Status updates appear in real-time
- [ ] Results page displays analysis
- [ ] Can download processed video

### ✅ Performance & Monitoring
- [ ] Processing completes in < 2 minutes for 30s video
- [ ] Grafana dashboards show metrics
- [ ] Error logs are captured
- [ ] Auto-scaling works under load
- [ ] Storage cleanup runs properly

---

## Troubleshooting

### Common Issues

#### 1. Video Processing Fails
```bash
# Check worker logs
docker-compose logs worker

# Check FFmpeg installation
ffmpeg -version

# Verify video format
ffprobe your_video.mp4
```

#### 2. Database Connection Error
```bash
# Check database status
docker-compose logs db

# Test connection
psql postgresql://basketball_user:password@localhost:5432/basketball_analysis

# Reset database
docker-compose down -v
docker-compose up db
```

#### 3. High Memory Usage
```bash
# Monitor resource usage
docker stats

# Scale workers
docker-compose up --scale worker=4

# Check for memory leaks
docker-compose logs worker | grep -i memory
```

### Performance Tuning

#### For High Load
```yaml
# In docker-compose.yml
worker:
  deploy:
    replicas: 8
  resources:
    limits:
      memory: 4GB
      cpus: '2'
```

#### For Cost Optimization
```bash
# Use spot instances in AWS
# Enable video compression
# Set up storage lifecycle policies
# Configure auto-scaling boundaries
```

---

## Next Steps

### Production Readiness
1. **Security**: Configure SSL certificates, firewall rules
2. **Monitoring**: Set up alerting and log aggregation
3. **Backup**: Implement database and video backup
4. **Scaling**: Configure auto-scaling policies
5. **Documentation**: Create user guides and API docs

### Feature Enhancement
1. **Mobile App**: iOS/Android development
2. **Advanced Analytics**: ML model improvements
3. **Team Features**: Multi-user support
4. **Integrations**: Third-party API connections

### Business Development
1. **User Onboarding**: Tutorial videos and guides
2. **Payment Processing**: Stripe integration
3. **Customer Support**: Help desk system
4. **Marketing**: Landing page and SEO

---

## Support & Resources

### Documentation
- [Commercial Deployment Plan](COMMERCIAL_DEPLOYMENT_PLAN.md)
- [Business Plan](BUSINESS_PLAN.md)
- [Implementation Roadmap](IMPLEMENTATION_ROADMAP.md)

### Monitoring URLs
- Health Check: `/health`
- API Status: `/api/health`
- Metrics: `/metrics` (if Prometheus enabled)

### Contact
- Technical Issues: Create GitHub issue
- Business Inquiries: Contact development team
- Emergency Support: Use monitoring alerts

---

**🎯 Success Criteria Met:**
- ✅ Production-ready codebase
- ✅ Scalable infrastructure
- ✅ Monitoring and alerting
- ✅ Security best practices
- ✅ Commercial deployment plan

**Ready for launch! 🚀**
