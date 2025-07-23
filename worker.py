# Basketball Analysis Service Worker
# Async video processing with Celery

import os
import logging
from celery import Celery
from basketball_analysis_service import BasketballAnalysisService
from data_models import VideoAnalysisJob
import redis
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery('basketball_worker')
celery_app.conf.update(
    broker_url=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    result_backend=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'process_video': {'queue': 'video_processing'},
        'cleanup_temp_files': {'queue': 'maintenance'},
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=10,
)

# Initialize services
redis_client = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
analysis_service = BasketballAnalysisService()

@celery_app.task(bind=True, max_retries=3)
def process_video(self, job_data):
    """Process basketball video analysis job"""
    try:
        logger.info(f"Starting video processing for job: {job_data['job_id']}")
        
        # Create job object
        job = VideoAnalysisJob(**job_data)
        
        # Update job status
        job.status = "processing"
        redis_client.set(f"job:{job.job_id}", json.dumps(job.to_dict()))
        
        # Process the video
        result = analysis_service.analyze_video(
            video_path=job.video_path,
            output_path=job.output_path
        )
        
        # Update job with results
        job.status = "completed"
        job.analysis_report = result
        job.output_video_path = result.output_video_path
        
        redis_client.set(f"job:{job.job_id}", json.dumps(job.to_dict()))
        
        logger.info(f"Video processing completed for job: {job.job_id}")
        return {"status": "success", "job_id": job.job_id}
        
    except Exception as exc:
        logger.error(f"Video processing failed for job {job_data['job_id']}: {str(exc)}")
        
        # Update job status to failed
        job = VideoAnalysisJob(**job_data)
        job.status = "failed"
        job.error_message = str(exc)
        redis_client.set(f"job:{job.job_id}", json.dumps(job.to_dict()))
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying job {job.job_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        raise exc

@celery_app.task
def cleanup_temp_files():
    """Clean up temporary files older than 24 hours"""
    import glob
    import time
    
    temp_dir = "/tmp/basketball_processing"
    cutoff_time = time.time() - (24 * 60 * 60)  # 24 hours ago
    
    for file_path in glob.glob(f"{temp_dir}/*"):
        try:
            if os.path.getmtime(file_path) < cutoff_time:
                os.remove(file_path)
                logger.info(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up {file_path}: {str(e)}")

@celery_app.task
def health_check():
    """Health check task for monitoring"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "worker_id": os.environ.get('HOSTNAME', 'unknown')
    }

# Periodic tasks
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'cleanup-temp-files': {
        'task': 'cleanup_temp_files',
        'schedule': crontab(minute=0, hour=2),  # Run at 2 AM daily
    },
}

if __name__ == '__main__':
    celery_app.start()
