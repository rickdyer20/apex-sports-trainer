# SQLite Database Setup for Development
# Basketball Analysis Service - Local Development Database

import sqlite3
import os
import logging
from datetime import datetime
import json
import bcrypt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLiteDatabase:
    """SQLite database setup for local development and testing"""
    
    def __init__(self, db_path="basketball_analysis.db"):
        self.db_path = db_path
        
    def create_tables(self):
        """Create all required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    subscription_type TEXT DEFAULT 'free',
                    subscription_status TEXT DEFAULT 'active',
                    api_key TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Analysis jobs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE NOT NULL,
                    user_id INTEGER,
                    video_path TEXT,
                    output_video_path TEXT,
                    status TEXT DEFAULT 'pending',
                    processing_time_seconds INTEGER,
                    file_size_bytes INTEGER,
                    video_duration_seconds REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Analysis results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    shot_accuracy_score REAL,
                    elbow_angle_avg REAL,
                    knee_bend_angle REAL,
                    release_angle REAL,
                    follow_through_score REAL,
                    overall_score REAL,
                    feedback_points TEXT, -- JSON as TEXT
                    biomechanical_data TEXT, -- JSON as TEXT
                    pose_landmarks TEXT, -- JSON as TEXT
                    shot_phases TEXT, -- JSON as TEXT
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES analysis_jobs (job_id)
                )
            """)
            
            # Subscriptions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    stripe_subscription_id TEXT,
                    plan_name TEXT,
                    status TEXT,
                    monthly_analysis_limit INTEGER,
                    current_period_start TIMESTAMP,
                    current_period_end TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Usage tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action_type TEXT,
                    resource_used TEXT,
                    quantity INTEGER DEFAULT 1,
                    metadata TEXT, -- JSON as TEXT
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # API keys table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    key_name TEXT,
                    api_key TEXT UNIQUE NOT NULL,
                    permissions TEXT, -- JSON as TEXT
                    is_active BOOLEAN DEFAULT 1,
                    last_used_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_jobs_user_id ON analysis_jobs(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_jobs_status ON analysis_jobs(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_jobs_created_at ON analysis_jobs(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_results_job_id ON analysis_results(job_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_id ON usage_tracking(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id)")
            
            conn.commit()
            conn.close()
            
            logger.info("✅ SQLite database tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            return False
    
    def create_sample_data(self):
        """Create sample users and data for testing"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create admin user
            admin_password = "AdminPass123!"
            admin_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT OR IGNORE INTO users (email, password_hash, first_name, last_name, subscription_type)
                VALUES (?, ?, ?, ?, ?)
            """, ('admin@basketballanalysis.com', admin_hash, 'Admin', 'User', 'enterprise'))
            
            # Create demo user
            demo_password = "DemoPass123!"
            demo_hash = bcrypt.hashpw(demo_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT OR IGNORE INTO users (email, password_hash, first_name, last_name, subscription_type)
                VALUES (?, ?, ?, ?, ?)
            """, ('demo@basketballanalysis.com', demo_hash, 'Demo', 'User', 'pro'))
            
            # Create test user
            test_password = "TestPass123!"
            test_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT OR IGNORE INTO users (email, password_hash, first_name, last_name, subscription_type)
                VALUES (?, ?, ?, ?, ?)
            """, ('test@basketballanalysis.com', test_hash, 'Test', 'User', 'free'))
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Sample users created successfully")
            logger.info("📧 Admin: admin@basketballanalysis.com / AdminPass123!")
            logger.info("📧 Demo: demo@basketballanalysis.com / DemoPass123!")
            logger.info("📧 Test: test@basketballanalysis.com / TestPass123!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create sample data: {e}")
            return False
    
    def test_database(self):
        """Test database operations"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM analysis_jobs")
            job_count = cursor.fetchone()[0]
            
            conn.close()
            
            logger.info(f"✅ Database test successful: {user_count} users, {job_count} jobs")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database test failed: {e}")
            return False
    
    def setup_development_database(self):
        """Complete database setup for development"""
        logger.info("🔄 Setting up SQLite development database...")
        
        # Remove existing database if it exists (for clean setup)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            logger.info("🗑️ Removed existing database")
        
        success = True
        success &= self.create_tables()
        success &= self.create_sample_data()
        success &= self.test_database()
        
        if success:
            logger.info("✅ Development database setup completed!")
            logger.info(f"📁 Database file: {os.path.abspath(self.db_path)}")
        else:
            logger.error("❌ Database setup failed!")
        
        return success

if __name__ == "__main__":
    db = SQLiteDatabase()
    db.setup_development_database()
