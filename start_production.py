#!/usr/bin/env python3
"""
Production Startup Script
Basketball Analysis Service

This script handles the complete startup process for production deployment.
"""

import os
import sys
import time
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionStartup:
    """Manages production startup and health checks"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.required_dirs = ['temp_videos', 'output_videos', 'logs']
        self.required_env_vars = [
            'DATABASE_URL', 'REDIS_URL', 'SECRET_KEY'
        ]
    
    def check_environment(self):
        """Check that all required environment variables are set"""
        logger.info("🔍 Checking environment configuration...")
        
        missing_vars = []
        for var in self.required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            logger.error("Please check your .env.production file")
            return False
        
        logger.info("✅ Environment configuration valid")
        return True
    
    def create_directories(self):
        """Create required directories"""
        logger.info("📁 Creating required directories...")
        
        for directory in self.required_dirs:
            dir_path = self.project_root / directory
            dir_path.mkdir(exist_ok=True)
            logger.info(f"✅ Directory created/verified: {directory}")
    
    def check_dependencies(self):
        """Check that all required dependencies are installed"""
        logger.info("📦 Checking dependencies...")
        
        try:
            import flask
            import cv2
            import mediapipe as mp
            import numpy as np
            import redis
            logger.info("✅ Core dependencies available")
            return True
        except ImportError as e:
            logger.error(f"❌ Missing dependency: {e}")
            logger.error("Run: pip install -r requirements.txt")
            return False
    
    def test_database_connection(self):
        """Test database connectivity"""
        logger.info("🗄️ Testing database connection...")
        
        try:
            from sqlalchemy import create_engine, text
            db_url = os.getenv('DATABASE_URL')
            engine = create_engine(db_url)
            
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
            
            logger.info("✅ Database connection successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def test_redis_connection(self):
        """Test Redis connectivity"""
        logger.info("🔴 Testing Redis connection...")
        
        try:
            import redis
            redis_url = os.getenv('REDIS_URL')
            client = redis.Redis.from_url(redis_url)
            client.ping()
            
            logger.info("✅ Redis connection successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            return False
    
    def run_database_migrations(self):
        """Run database setup if needed"""
        logger.info("🔄 Running database setup...")
        
        try:
            # Check if tables exist
            from sqlalchemy import create_engine, text
            db_url = os.getenv('DATABASE_URL')
            engine = create_engine(db_url)
            
            with engine.connect() as connection:
                result = connection.execute(text("SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = 'users')"))
                tables_exist = result.fetchone()[0]
            
            if not tables_exist:
                logger.info("📋 Setting up database tables...")
                subprocess.run([sys.executable, 'setup_database.py'], check=True)
                logger.info("✅ Database setup completed")
            else:
                logger.info("✅ Database tables already exist")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            return False
    
    def start_background_services(self):
        """Start background services (Celery workers)"""
        logger.info("⚙️ Starting background services...")
        
        try:
            # Start Celery worker in background
            worker_cmd = [
                sys.executable, '-m', 'celery', 
                '-A', 'worker.celery_app', 'worker',
                '--loglevel=info',
                '--concurrency=4'
            ]
            
            # Start worker process
            worker_process = subprocess.Popen(
                worker_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Give worker time to start
            time.sleep(3)
            
            if worker_process.poll() is None:
                logger.info("✅ Celery worker started successfully")
                return worker_process
            else:
                logger.error("❌ Failed to start Celery worker")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to start background services: {e}")
            return None
    
    def start_web_application(self):
        """Start the web application"""
        logger.info("🌐 Starting web application...")
        
        try:
            # Production WSGI server configuration
            if os.getenv('USE_GUNICORN', 'false').lower() == 'true':
                # Use Gunicorn for production
                workers = os.getenv('WORKERS_PER_CORE', 2)
                max_workers = os.getenv('MAX_WORKERS', 8)
                timeout = os.getenv('GUNICORN_TIMEOUT', 60)
                port = os.getenv('PORT', 5000)
                
                gunicorn_cmd = [
                    'gunicorn',
                    '--workers', str(workers),
                    '--max-requests', '1000',
                    '--max-requests-jitter', '100',
                    '--timeout', str(timeout),
                    '--bind', f'0.0.0.0:{port}',
                    '--worker-class', 'gthread',
                    '--threads', '2',
                    '--worker-tmp-dir', '/dev/shm',
                    'web_app:app'
                ]
                
                logger.info(f"🚀 Starting Gunicorn with {workers} workers on port {port}")
                subprocess.run(gunicorn_cmd, check=True)
                
            else:
                # Development mode with Flask dev server
                logger.info("🚀 Starting Flask development server")
                from web_app import app
                app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
                
        except Exception as e:
            logger.error(f"❌ Failed to start web application: {e}")
            raise
    
    def health_check(self):
        """Perform application health check"""
        logger.info("🏥 Running health checks...")
        
        import requests
        import time
        
        port = os.getenv('PORT', 5000)
        health_url = f"http://localhost:{port}/health"
        
        # Wait for application to start
        for attempt in range(10):
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Application health check passed")
                    return True
            except requests.exceptions.RequestException:
                time.sleep(2)
                continue
        
        logger.error("❌ Application health check failed")
        return False
    
    def run_startup_sequence(self):
        """Execute complete startup sequence"""
        logger.info("🚀 Starting Basketball Analysis Service Production Deployment")
        logger.info("=" * 60)
        
        startup_steps = [
            ("Environment Check", self.check_environment),
            ("Directory Creation", self.create_directories),
            ("Dependency Check", self.check_dependencies),
            ("Database Connection", self.test_database_connection),
            ("Redis Connection", self.test_redis_connection),
            ("Database Setup", self.run_database_migrations),
        ]
        
        # Run preliminary checks
        for step_name, step_func in startup_steps:
            logger.info(f"📋 Step: {step_name}")
            if not step_func():
                logger.error(f"❌ Startup failed at step: {step_name}")
                sys.exit(1)
            logger.info(f"✅ Step completed: {step_name}")
            logger.info("-" * 40)
        
        # Start background services
        worker_process = self.start_background_services()
        
        try:
            # Start web application (this blocks)
            self.start_web_application()
            
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown signal received")
            
        finally:
            # Cleanup background services
            if worker_process:
                logger.info("🧹 Stopping background services...")
                worker_process.terminate()
                worker_process.wait()
            
            logger.info("👋 Basketball Analysis Service stopped")

def main():
    """Main entry point"""
    # Load environment configuration
    env_file = '.env.production' if os.path.exists('.env.production') else '.env'
    
    if os.path.exists(env_file):
        from dotenv import load_dotenv
        load_dotenv(env_file)
        logger.info(f"📄 Loaded environment from: {env_file}")
    else:
        logger.warning("⚠️ No environment file found, using system environment variables")
    
    # Initialize and run startup
    startup = ProductionStartup()
    startup.run_startup_sequence()

if __name__ == "__main__":
    main()
