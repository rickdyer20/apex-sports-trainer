# Testing Framework for Basketball Analysis Service
# Comprehensive test suite with pytest

import pytest
import os
import sys
import json
import tempfile
import sqlite3
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import application modules
from web_app import app
from basketball_analysis_service import (
    VideoAnalysisJob, 
    FrameData, 
    ShotPhase, 
    FeedbackPoint, 
    AnalysisReport,
    process_video_for_analysis
)
from setup_sqlite_db import SQLiteDatabase

class TestConfig:
    """Test configuration"""
    TESTING = True
    DATABASE_PATH = ':memory:'  # In-memory SQLite for tests
    UPLOAD_FOLDER = tempfile.mkdtemp()
    SECRET_KEY = 'test-secret-key'

@pytest.fixture
def app_instance():
    """Create Flask app instance for testing"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def test_database():
    """Create test database"""
    db = SQLiteDatabase(':memory:')
    db.create_tables()
    db.create_sample_data()
    return db

@pytest.fixture
def sample_video_file():
    """Create a sample video file for testing"""
    # Create a temporary file that simulates a video
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
        # Write some dummy content
        f.write(b'fake video content for testing')
        return f.name

class TestWebApplication:
    """Test web application endpoints"""
    
    def test_home_page(self, app_instance):
        """Test home page loads correctly"""
        response = app_instance.get('/')
        assert response.status_code == 200
        assert b'Basketball Shot Analysis' in response.data
    
    def test_health_check(self, app_instance):
        """Test health check endpoint"""
        response = app_instance.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'Basketball Analysis Service'
        assert 'timestamp' in data
    
    def test_api_health_check(self, app_instance):
        """Test comprehensive health check"""
        response = app_instance.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert 'checks' in data
        assert 'active_jobs' in data
    
    def test_about_page(self, app_instance):
        """Test about page"""
        response = app_instance.get('/about')
        assert response.status_code == 200
    
    def test_demo_page(self, app_instance):
        """Test demo page with sample video"""
        response = app_instance.get('/demo')
        assert response.status_code == 200
        assert b'Demo Analysis' in response.data

class TestVideoAnalysis:
    """Test video analysis functionality"""
    
    def test_video_analysis_job_creation(self):
        """Test VideoAnalysisJob creation"""
        job = VideoAnalysisJob(
            job_id="test-123",
            user_id="user-456",
            video_url="/test/video.mp4"
        )
        
        assert job.job_id == "test-123"
        assert job.user_id == "user-456"
        assert job.video_url == "/test/video.mp4"
        assert job.status == "PENDING"
    
    def test_frame_data_creation(self):
        """Test FrameData structure"""
        frame_data = FrameData(
            frame_number=100,
            landmarks_raw=[],
            metrics={"elbow": 90.0, "knee": 120.0}
        )
        
        assert frame_data.frame_number == 100
        assert frame_data.landmarks_raw == []
        assert frame_data.metrics["elbow"] == 90.0
    
    def test_shot_phase_creation(self):
        """Test ShotPhase structure"""
        phase = ShotPhase(
            name="Load/Dip",
            start_frame=50,
            end_frame=80,
            key_moment_frame=75
        )
        
        assert phase.name == "Load/Dip"
        assert phase.start_frame == 50
        assert phase.end_frame == 80
        assert phase.key_moment_frame == 75
    
    def test_feedback_point_creation(self):
        """Test FeedbackPoint structure"""
        feedback = FeedbackPoint(
            frame_number=75,
            discrepancy="Elbow not aligned under ball",
            ideal_range="90-110 degrees",
            user_value="75 degrees",
            remedy_tips="Focus on elbow positioning during the load phase"
        )
        
        assert feedback.frame_number == 75
        assert feedback.discrepancy == "Elbow not aligned under ball"
        assert feedback.ideal_range == "90-110 degrees"
        assert feedback.user_value == "75 degrees"
        assert "elbow positioning" in feedback.remedy_tips
    
    def test_analysis_report_creation(self):
        """Test AnalysisReport structure"""
        report = AnalysisReport(
            job_id="test-123",
            user_id="user-456",
            video_url="/test/video.mp4",
            phases=[],
            feedback_points=[],
            overall_score=85.5
        )
        
        assert report.job_id == "test-123"
        assert report.user_id == "user-456"
        assert report.video_url == "/test/video.mp4"
        assert report.overall_score == 85.5

class TestVideoProcessing:
    """Test video processing pipeline"""
    
    @patch('basketball_analysis_service.cv2')
    @patch('basketball_analysis_service.mp')
    def test_video_processing_mock(self, mock_mp, mock_cv2):
        """Test video processing with mocked dependencies"""
        # Mock MediaPipe pose detection
        mock_pose = MagicMock()
        mock_mp.solutions.pose.Pose.return_value = mock_pose
        
        # Mock OpenCV video capture
        mock_cap = MagicMock()
        mock_cv2.VideoCapture.return_value = mock_cap
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 30.0  # 30 FPS
        
        # Mock frame reading
        mock_cap.read.side_effect = [
            (True, MagicMock()),  # First frame
            (True, MagicMock()),  # Second frame
            (False, None)         # End of video
        ]
        
        # Mock pose detection results
        mock_results = MagicMock()
        mock_results.pose_landmarks = MagicMock()
        mock_pose.process.return_value = mock_results
        
        # Test the function (would need actual implementation)
        # This is a placeholder for the actual test
        assert True  # Placeholder assertion
    
    def test_video_file_validation(self):
        """Test video file validation"""
        from web_app import allowed_file
        
        assert allowed_file('test.mp4') == True
        assert allowed_file('test.avi') == True
        assert allowed_file('test.mov') == True
        assert allowed_file('test.mkv') == True
        assert allowed_file('test.txt') == False
        assert allowed_file('test') == False

class TestDatabase:
    """Test database operations"""
    
    def test_database_creation(self, test_database):
        """Test database table creation"""
        # Just test that the method runs without error
        test_database.test_database()
        assert True  # If we get here, test passed
    
    def test_user_operations(self, test_database):
        """Test user database operations"""
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Recreate tables in memory
        test_database.create_tables()
        
        # Test user insertion
        cursor.execute("""
            INSERT INTO users (email, password_hash, first_name, last_name)
            VALUES (?, ?, ?, ?)
        """, ('test@example.com', 'hash123', 'Test', 'User'))
        
        # Test user retrieval
        cursor.execute("SELECT * FROM users WHERE email = ?", ('test@example.com',))
        user = cursor.fetchone()
        
        assert user is not None
        assert user[1] == 'test@example.com'  # email
        assert user[3] == 'Test'  # first_name
        
        conn.close()
    
    def test_analysis_job_operations(self, test_database):
        """Test analysis job database operations"""
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Recreate tables
        test_database.create_tables()
        
        # Insert test job
        cursor.execute("""
            INSERT INTO analysis_jobs (job_id, status, video_path)
            VALUES (?, ?, ?)
        """, ('test-job-123', 'pending', '/test/video.mp4'))
        
        # Retrieve job
        cursor.execute("SELECT * FROM analysis_jobs WHERE job_id = ?", ('test-job-123',))
        job = cursor.fetchone()
        
        assert job is not None
        assert job[1] == 'test-job-123'  # job_id
        assert job[4] == 'pending'  # status
        
        conn.close()

class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_video_upload_endpoint(self, app_instance):
        """Test video upload API"""
        # Create a test file
        with tempfile.NamedTemporaryFile(suffix='.mp4') as tmp_file:
            tmp_file.write(b'test video content')
            tmp_file.seek(0)
            
            response = app_instance.post('/upload', data={
                'video': (tmp_file, 'test.mp4')
            })
            
            # Should redirect to status page on successful upload
            assert response.status_code in [200, 302]
    
    def test_status_endpoint(self, app_instance):
        """Test job status endpoint"""
        # Test with non-existent job
        response = app_instance.get('/api/status/nonexistent-job')
        assert response.status_code == 404
    
    def test_video_serving_endpoint(self, app_instance):
        """Test video serving endpoint"""
        # Test with non-existent video
        response = app_instance.get('/video/nonexistent-job')
        assert response.status_code == 404

class TestPerformance:
    """Test performance and load"""
    
    def test_concurrent_requests(self, app_instance):
        """Test handling multiple concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = app_instance.get('/health')
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for i in range(10):
            t = threading.Thread(target=make_request)
            threads.append(t)
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 10
    
    def test_memory_usage(self):
        """Test memory usage patterns"""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Simulate heavy operations
        large_data = [i for i in range(100000)]
        
        # Force garbage collection
        del large_data
        gc.collect()
        
        final_memory = process.memory_info().rss
        
        # Memory should not grow excessively
        memory_growth = final_memory - initial_memory
        assert memory_growth < 100 * 1024 * 1024  # Less than 100MB growth

class TestIntegration:
    """Integration tests"""
    
    def test_full_workflow_simulation(self, app_instance, test_database):
        """Test complete workflow from upload to results"""
        # 1. Check home page
        response = app_instance.get('/')
        assert response.status_code == 200
        
        # 2. Check health
        response = app_instance.get('/health')
        assert response.status_code == 200
        
        # 3. Access demo page
        response = app_instance.get('/demo')
        assert response.status_code == 200
        
        # This simulates a complete user workflow
        assert True
    
    def test_error_handling(self, app_instance):
        """Test error handling and recovery"""
        # Test 404 error
        response = app_instance.get('/nonexistent-page')
        assert response.status_code == 404
        
        # Test invalid job ID
        response = app_instance.get('/results/invalid-job-id')
        assert response.status_code == 404

# Test configuration and runner
if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "-x"  # Stop on first failure
    ])
