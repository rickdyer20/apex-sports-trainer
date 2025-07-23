# Production Configuration
# Basketball Analysis Service

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Application Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://basketball_user:password@localhost:5432/basketball_analysis'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20
    }
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Celery Configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True
    
    # Video Processing Settings
    MAX_VIDEO_SIZE_MB = int(os.environ.get('MAX_VIDEO_SIZE_MB', 100))
    PROCESSING_TIMEOUT_SECONDS = int(os.environ.get('PROCESSING_TIMEOUT_SECONDS', 300))
    MAX_CONCURRENT_PROCESSING = int(os.environ.get('MAX_CONCURRENT_PROCESSING', 10))
    VIDEO_RETENTION_DAYS = int(os.environ.get('VIDEO_RETENTION_DAYS', 90))
    
    # Cloud Storage Configuration
    CLOUD_PROVIDER = os.environ.get('CLOUD_PROVIDER', 'aws')
    
    # AWS Settings
    AWS_REGION = os.environ.get('AWS_REGION', 'us-west-2')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'basketball-analysis-videos')
    S3_BUCKET_REGION = os.environ.get('S3_BUCKET_REGION', 'us-west-2')
    
    # Azure Settings (alternative to AWS)
    AZURE_STORAGE_ACCOUNT = os.environ.get('AZURE_STORAGE_ACCOUNT')
    AZURE_STORAGE_KEY = os.environ.get('AZURE_STORAGE_KEY')
    AZURE_CONTAINER_NAME = os.environ.get('AZURE_CONTAINER_NAME', 'basketball-videos')
    
    # Security Settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS Settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # File Upload Settings
    MAX_CONTENT_LENGTH = MAX_VIDEO_SIZE_MB * 1024 * 1024  # Convert MB to bytes
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'temp_videos')
    OUTPUT_FOLDER = os.path.join(os.getcwd(), 'output_videos')
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    
    # Monitoring Settings
    PROMETHEUS_ENABLED = os.environ.get('PROMETHEUS_ENABLED', 'true').lower() == 'true'
    PROMETHEUS_PORT = int(os.environ.get('PROMETHEUS_PORT', 8000))
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.sendgrid.net')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@basketballanalysis.com')
    
    # Payment Processing (Stripe)
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # Analytics
    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID')
    MIXPANEL_TOKEN = os.environ.get('MIXPANEL_TOKEN')
    
    # Performance Settings
    WORKERS_PER_CORE = int(os.environ.get('WORKERS_PER_CORE', 2))
    MAX_WORKERS = int(os.environ.get('MAX_WORKERS', 8))
    WORKER_MEMORY_LIMIT_MB = int(os.environ.get('WORKER_MEMORY_LIMIT_MB', 2048))
    GUNICORN_TIMEOUT = int(os.environ.get('GUNICORN_TIMEOUT', 60))
    
    # Feature Flags
    ENABLE_ANALYTICS = os.environ.get('ENABLE_ANALYTICS', 'true').lower() == 'true'
    ENABLE_ADVANCED_METRICS = os.environ.get('ENABLE_ADVANCED_METRICS', 'true').lower() == 'true'
    ENABLE_TEAM_FEATURES = os.environ.get('ENABLE_TEAM_FEATURES', 'false').lower() == 'true'
    ENABLE_WHITE_LABEL = os.environ.get('ENABLE_WHITE_LABEL', 'false').lower() == 'true'
    
    # API Rate Limiting
    API_RATE_LIMIT = int(os.environ.get('API_RATE_LIMIT', 100))  # requests per minute
    UPLOAD_RATE_LIMIT = int(os.environ.get('UPLOAD_RATE_LIMIT', 10))  # uploads per hour
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'postgresql://basketball_user:password@localhost:5432/basketball_analysis_dev'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'postgresql://basketball_user:password@localhost:5432/basketball_analysis_test'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Database connection pooling for production
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 20,
        'max_overflow': 30
    }
    
    @classmethod
    def init_app(cls, app):
        """Initialize production-specific settings"""
        Config.init_app(app)
        
        # Configure logging for production
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            file_handler = RotatingFileHandler(
                'logs/basketball_analysis.log', 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('Basketball Analysis Service startup')

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
