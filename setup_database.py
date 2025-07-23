# Database Management Script
# Basketball Analysis Service - Production Setup

import os
import sys
import logging
from datetime import datetime
from typing import Optional

# Database imports (these would need to be installed in production)
try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    import redis
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
except ImportError as e:
    print(f"Missing required dependencies: {e}")
    print("Install with: pip install psycopg2-binary redis sqlalchemy")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database setup and maintenance for production deployment"""
    
    def __init__(self, db_url: str, redis_url: str):
        self.db_url = db_url
        self.redis_url = redis_url
        self.engine = None
        self.redis_client = None
    
    def create_database(self, db_name: str = "basketball_analysis"):
        """Create the main database if it doesn't exist"""
        try:
            # Connect to default postgres database
            base_url = self.db_url.rsplit('/', 1)[0] + '/postgres'
            conn = psycopg2.connect(base_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f'CREATE DATABASE "{db_name}"')
                logger.info(f"Database '{db_name}' created successfully")
            else:
                logger.info(f"Database '{db_name}' already exists")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            raise
    
    def create_tables(self):
        """Create application tables"""
        try:
            self.engine = create_engine(self.db_url)
            
            # SQL for creating tables
            create_tables_sql = """
            -- Users table
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                subscription_type VARCHAR(50) DEFAULT 'free',
                subscription_status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Video analysis jobs table
            CREATE TABLE IF NOT EXISTS analysis_jobs (
                id SERIAL PRIMARY KEY,
                job_id VARCHAR(50) UNIQUE NOT NULL,
                user_id INTEGER REFERENCES users(id),
                video_path VARCHAR(500),
                output_video_path VARCHAR(500),
                status VARCHAR(50) DEFAULT 'pending',
                processing_time_seconds INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT
            );
            
            -- Analysis results table
            CREATE TABLE IF NOT EXISTS analysis_results (
                id SERIAL PRIMARY KEY,
                job_id VARCHAR(50) REFERENCES analysis_jobs(job_id),
                shot_accuracy_score DECIMAL(5,2),
                elbow_angle_avg DECIMAL(5,2),
                knee_bend_angle DECIMAL(5,2),
                release_angle DECIMAL(5,2),
                follow_through_score DECIMAL(5,2),
                overall_score DECIMAL(5,2),
                feedback_points JSON,
                biomechanical_data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- User subscriptions table
            CREATE TABLE IF NOT EXISTS subscriptions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                stripe_subscription_id VARCHAR(100),
                plan_name VARCHAR(50),
                status VARCHAR(50),
                current_period_start TIMESTAMP,
                current_period_end TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Usage tracking table
            CREATE TABLE IF NOT EXISTS usage_tracking (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                action_type VARCHAR(50),
                resource_used VARCHAR(100),
                quantity INTEGER DEFAULT 1,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            with self.engine.connect() as connection:
                connection.execute(text(create_tables_sql))
                connection.commit()
            
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def create_indexes(self):
        """Create database indexes for performance"""
        try:
            indexes_sql = """
            -- Performance indexes
            CREATE INDEX IF NOT EXISTS idx_analysis_jobs_user_id ON analysis_jobs(user_id);
            CREATE INDEX IF NOT EXISTS idx_analysis_jobs_status ON analysis_jobs(status);
            CREATE INDEX IF NOT EXISTS idx_analysis_jobs_created_at ON analysis_jobs(created_at);
            CREATE INDEX IF NOT EXISTS idx_analysis_results_job_id ON analysis_results(job_id);
            CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
            CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_id ON usage_tracking(user_id);
            CREATE INDEX IF NOT EXISTS idx_usage_tracking_timestamp ON usage_tracking(timestamp);
            """
            
            with self.engine.connect() as connection:
                connection.execute(text(indexes_sql))
                connection.commit()
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise
    
    def create_admin_user(self, email: str, password: str):
        """Create initial admin user"""
        try:
            import bcrypt
            
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            insert_admin_sql = """
            INSERT INTO users (email, password_hash, first_name, last_name, subscription_type)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING;
            """
            
            with self.engine.connect() as connection:
                connection.execute(
                    text(insert_admin_sql),
                    (email, password_hash, 'Admin', 'User', 'enterprise')
                )
                connection.commit()
            
            logger.info(f"Admin user created: {email}")
            
        except Exception as e:
            logger.error(f"Failed to create admin user: {e}")
            raise
    
    def test_redis_connection(self):
        """Test Redis connection"""
        try:
            self.redis_client = redis.Redis.from_url(self.redis_url)
            self.redis_client.ping()
            logger.info("Redis connection successful")
            
            # Set test key
            self.redis_client.set('basketball_analysis:test', 'connection_ok', ex=60)
            
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    def setup_production_database(self, admin_email: str = "admin@basketballanalysis.com", 
                                admin_password: str = "AdminPass123!"):
        """Complete database setup for production"""
        logger.info("Starting production database setup...")
        
        try:
            # 1. Create database
            self.create_database()
            
            # 2. Create tables
            self.create_tables()
            
            # 3. Create indexes
            self.create_indexes()
            
            # 4. Create admin user
            self.create_admin_user(admin_email, admin_password)
            
            # 5. Test Redis
            self.test_redis_connection()
            
            logger.info("✅ Production database setup completed successfully!")
            logger.info(f"Admin user created: {admin_email}")
            logger.info("Next steps:")
            logger.info("1. Update .env.production with correct database URLs")
            logger.info("2. Run application with: python web_app.py")
            logger.info("3. Test video upload and analysis")
            
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            raise

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv('.env.production')
    
    db_url = os.getenv('DATABASE_URL', 'postgresql://basketball_user:password@localhost:5432/basketball_analysis')
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Initialize database manager
    db_manager = DatabaseManager(db_url, redis_url)
    
    # Run setup
    db_manager.setup_production_database()
