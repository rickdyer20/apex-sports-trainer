# Basketball Analysis Service - Production Database Setup
# PostgreSQL + Redis deployment configuration

import os
import psycopg2
import redis
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionDatabase:
    """Production PostgreSQL database setup and management"""
    
    def __init__(self):
        # Production database configuration
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'basketball_analysis_prod'),
            'user': os.getenv('DB_USER', 'basketball_user'),
            'password': os.getenv('DB_PASSWORD', 'secure_password_123')
        }
        
        # Redis configuration
        self.redis_config = {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', '6379')),
            'db': int(os.getenv('REDIS_DB', '0')),
            'password': os.getenv('REDIS_PASSWORD', None)
        }
        
        self.connection = None
        self.redis_client = None
    
    def connect_postgresql(self):
        """Connect to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            logger.info("✅ Connected to PostgreSQL database")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
            return False
    
    def connect_redis(self):
        """Connect to Redis cache"""
        try:
            self.redis_client = redis.Redis(**self.redis_config)
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Connected to Redis cache")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            return False
    
    def create_production_tables(self):
        """Create production database schema"""
        if not self.connection:
            logger.error("❌ No database connection")
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Users table with production features
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    subscription_tier VARCHAR(50) DEFAULT 'free',
                    subscription_status VARCHAR(50) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    email_verified BOOLEAN DEFAULT FALSE,
                    stripe_customer_id VARCHAR(255),
                    INDEX(email),
                    INDEX(subscription_tier),
                    INDEX(created_at)
                )
            """)
            
            # Analysis jobs table with production tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_jobs (
                    id SERIAL PRIMARY KEY,
                    job_id VARCHAR(255) UNIQUE NOT NULL,
                    user_id INTEGER REFERENCES users(id),
                    video_url TEXT NOT NULL,
                    status VARCHAR(50) DEFAULT 'PENDING',
                    priority INTEGER DEFAULT 5,
                    processing_started_at TIMESTAMP,
                    processing_completed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    result_video_url TEXT,
                    analysis_data JSONB,
                    feedback_points JSONB,
                    processing_duration_seconds INTEGER,
                    error_message TEXT,
                    INDEX(job_id),
                    INDEX(user_id),
                    INDEX(status),
                    INDEX(created_at),
                    INDEX(priority)
                )
            """)
            
            # Usage tracking for billing
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage_tracking (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    job_id VARCHAR(255) REFERENCES analysis_jobs(job_id),
                    action_type VARCHAR(100) NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processing_seconds INTEGER,
                    video_duration_seconds INTEGER,
                    cost_credits DECIMAL(10,2),
                    INDEX(user_id),
                    INDEX(timestamp),
                    INDEX(action_type)
                )
            """)
            
            # Subscriptions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    stripe_subscription_id VARCHAR(255),
                    plan_name VARCHAR(100) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    current_period_start TIMESTAMP,
                    current_period_end TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    monthly_analysis_limit INTEGER DEFAULT 10,
                    analyses_used_this_month INTEGER DEFAULT 0,
                    INDEX(user_id),
                    INDEX(stripe_subscription_id),
                    INDEX(status)
                )
            """)
            
            # Performance monitoring table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metric_name VARCHAR(100) NOT NULL,
                    metric_value DECIMAL(15,4),
                    job_id VARCHAR(255),
                    user_id INTEGER,
                    additional_data JSONB,
                    INDEX(timestamp),
                    INDEX(metric_name),
                    INDEX(job_id)
                )
            """)
            
            self.connection.commit()
            logger.info("✅ Production database schema created successfully")
            
            # Create initial admin user
            self.create_admin_user()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create production tables: {e}")
            self.connection.rollback()
            return False
    
    def create_admin_user(self):
        """Create initial admin user for production"""
        try:
            cursor = self.connection.cursor()
            
            # Check if admin already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", ('admin@basketballanalysis.com',))
            if cursor.fetchone():
                logger.info("👤 Admin user already exists")
                return
            
            # Create admin user
            import bcrypt
            admin_password = os.getenv('ADMIN_PASSWORD', 'SecureAdmin123!')
            password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO users (email, password_hash, first_name, last_name, subscription_tier, email_verified)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                'admin@basketballanalysis.com',
                password_hash,
                'System',
                'Administrator',
                'enterprise',
                True
            ))
            
            self.connection.commit()
            logger.info("✅ Admin user created: admin@basketballanalysis.com")
            
        except Exception as e:
            logger.error(f"❌ Failed to create admin user: {e}")
    
    def setup_redis_cache(self):
        """Set up Redis cache with production configuration"""
        if not self.redis_client:
            logger.error("❌ No Redis connection")
            return False
        
        try:
            # Set up cache configuration
            cache_config = {
                'default_expiry': 3600,  # 1 hour
                'job_status_expiry': 86400,  # 24 hours
                'user_session_expiry': 1800,  # 30 minutes
                'analysis_cache_expiry': 7200  # 2 hours
            }
            
            # Store configuration in Redis
            for key, value in cache_config.items():
                self.redis_client.hset('cache_config', key, value)
            
            # Set up job queue lists
            self.redis_client.delete('job_queue:high_priority')
            self.redis_client.delete('job_queue:normal_priority')
            self.redis_client.delete('job_queue:low_priority')
            
            logger.info("✅ Redis cache configuration complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup Redis cache: {e}")
            return False
    
    def test_connections(self):
        """Test both PostgreSQL and Redis connections"""
        postgres_ok = self.connect_postgresql()
        redis_ok = self.connect_redis()
        
        if postgres_ok and redis_ok:
            logger.info("🎉 All database connections successful!")
            return True
        else:
            logger.error("❌ Some database connections failed")
            return False
    
    def get_health_status(self):
        """Get database health status for monitoring"""
        status = {
            'postgresql': False,
            'redis': False,
            'timestamp': datetime.now().isoformat()
        }
        
        # Test PostgreSQL
        try:
            if self.connection:
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                status['postgresql'] = True
        except:
            status['postgresql'] = False
        
        # Test Redis
        try:
            if self.redis_client:
                self.redis_client.ping()
                status['redis'] = True
        except:
            status['redis'] = False
        
        return status

def main():
    """Main deployment function"""
    logger.info("🚀 Starting Production Database Deployment")
    
    # Initialize production database
    prod_db = ProductionDatabase()
    
    # Test connections
    if not prod_db.test_connections():
        logger.error("❌ Database deployment failed - connection issues")
        return False
    
    # Create production schema
    if not prod_db.create_production_tables():
        logger.error("❌ Database deployment failed - schema creation issues")
        return False
    
    # Setup Redis cache
    if not prod_db.setup_redis_cache():
        logger.error("❌ Database deployment failed - Redis setup issues")
        return False
    
    # Final health check
    health = prod_db.get_health_status()
    logger.info(f"📊 Database Health Status: {health}")
    
    logger.info("✅ Production database deployment completed successfully!")
    return True

if __name__ == "__main__":
    main()
