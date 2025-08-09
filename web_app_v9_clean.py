"""
Basketball Shot Analysis Service v9.0 - Restored Clean Version
Professional basketball shot analysis using MediaPipe pose estimation
NO PAYMENT PROCESSING - Pure basketball analysis functionality
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, Response
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import threading
import time

# Import our basketball analysis service
from basketball_analysis_service import (
    VideoAnalysisJob, 
    process_video_for_analysis, 
    load_ideal_shot_data
)

app = Flask(__name__)
app.secret_key = 'basketball_analysis_secret_key_2025'

# Configuration
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs('jobs', exist_ok=True)

# In-memory storage for demo
analysis_jobs = {}
job_results = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_job_to_file(job_id, job_data):
    """Save job data to file for persistence"""
    try:
        job_file = os.path.join('jobs', f"{job_id}.json")
        serializable_data = job_data.copy()
        
        # Convert datetime objects to ISO strings
        if 'created_at' in serializable_data:
            serializable_data['created_at'] = serializable_data['created_at'].isoformat()
        if 'updated_at' in serializable_data:
            serializable_data['updated_at'] = serializable_data['updated_at'].isoformat()
        if 'processed_at' in serializable_data:
            serializable_data['processed_at'] = serializable_data['processed_at'].isoformat()
        
        with open(job_file, 'w') as f:
            json.dump(serializable_data, f, indent=2)
    except Exception as e:
        print(f"Error saving job {job_id}: {e}")

def load_job_from_file(job_id):
    """Load job data from file"""
    try:
        job_file = os.path.join('jobs', f"{job_id}.json")
        if os.path.exists(job_file):
            with open(job_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading job {job_id}: {e}")
    return None

def load_all_jobs():
    """Load all jobs from files on startup"""
    global analysis_jobs
    try:
        for filename in os.listdir('jobs'):
            if filename.endswith('.json'):
                job_id = filename[:-5]  # Remove .json
                job_data = load_job_from_file(job_id)
                if job_data:
                    analysis_jobs[job_id] = job_data
        print(f"Loaded {len(analysis_jobs)} jobs from files")
    except Exception as e:
        print(f"Error loading jobs: {e}")

def process_video_async(job_id):
    """Process video analysis in background thread"""
    try:
        job_data = analysis_jobs[job_id]
        job_data['status'] = 'PROCESSING'
        job_data['updated_at'] = datetime.now()
        save_job_to_file(job_id, job_data)
        
        video_path = job_data['video_path']
        
        # Process the video
        results = process_video_for_analysis(
            video_path, 
            job_id=job_id,
            output_dir=RESULTS_FOLDER
        )
        
        if results and 'error' not in results:
            job_data['status'] = 'COMPLETED'
            job_data['processed_at'] = datetime.now()
            job_data['results'] = results
            
            # Store in job_results for quick access
            job_results[job_id] = results
            
            flash(f'Analysis completed for job {job_id}!', 'success')
        else:
            job_data['status'] = 'FAILED'
            job_data['error'] = results.get('error', 'Unknown error') if results else 'Processing failed'
            flash(f'Analysis failed for job {job_id}', 'error')
        
        job_data['updated_at'] = datetime.now()
        save_job_to_file(job_id, job_data)
        
    except Exception as e:
        print(f"Error processing video {job_id}: {e}")
        if job_id in analysis_jobs:
            analysis_jobs[job_id]['status'] = 'FAILED'
            analysis_jobs[job_id]['error'] = str(e)
            analysis_jobs[job_id]['updated_at'] = datetime.now()
            save_job_to_file(job_id, analysis_jobs[job_id])

@app.route('/')
def index():
    """Home page with upload form"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Basketball Shot Analysis v9.0</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                margin-bottom: 30px;
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 30px;
                font-size: 1.2em;
            }
            .upload-section {
                border: 2px dashed #007bff;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                margin-bottom: 30px;
                background: #f8f9ff;
            }
            .upload-button {
                background: #007bff;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 1.1em;
                cursor: pointer;
                transition: background 0.3s;
            }
            .upload-button:hover {
                background: #0056b3;
            }
            .file-input {
                margin: 20px 0;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                width: 100%;
                max-width: 400px;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .feature {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }
            .feature h3 {
                color: #007bff;
                margin-bottom: 10px;
            }
            .footer {
                text-align: center;
                color: #666;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #eee;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏀 Basketball Shot Analysis</h1>
            <p class="subtitle">Professional shot analysis using AI-powered pose estimation</p>
            
            <div class="upload-section">
                <h3>Upload Your Basketball Shot Video</h3>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="video" accept="video/*" class="file-input" required>
                    <br><br>
                    <button type="submit" class="upload-button">🎯 Analyze My Shot</button>
                </form>
                <p style="margin-top: 15px; color: #666;">
                    Supported formats: MP4, AVI, MOV, MKV (Max 100MB)
                </p>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>📊 Detailed Analysis</h3>
                    <p>Get comprehensive feedback on your shooting form, including joint angles and movement patterns</p>
                </div>
                <div class="feature">
                    <h3>🎥 Visual Feedback</h3>
                    <p>Receive annotated video with overlays showing your form and areas for improvement</p>
                </div>
                <div class="feature">
                    <h3>📈 Performance Metrics</h3>
                    <p>Track key metrics like release consistency, balance, and follow-through</p>
                </div>
                <div class="feature">
                    <h3>💡 Coaching Tips</h3>
                    <p>Get specific, actionable advice to improve your shooting technique</p>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="/jobs" style="color: #007bff; text-decoration: none; font-weight: bold;">
                    📋 View All Analysis Jobs
                </a>
            </div>
        </div>
        
        <div class="footer">
            <p>Basketball Shot Analysis v9.0 - Professional AI-Powered Shot Analysis</p>
        </div>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_video():
    """Handle video upload and start analysis"""
    if 'video' not in request.files:
        flash('No video file provided!', 'error')
        return redirect(url_for('index'))
    
    file = request.files['video']
    if file.filename == '':
        flash('No file selected!', 'error')
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        flash('Invalid file type! Please upload MP4, AVI, MOV, or MKV files only.', 'error')
        return redirect(url_for('index'))
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    video_path = os.path.join(UPLOAD_FOLDER, f"{job_id}_{filename}")
    file.save(video_path)
    
    # Create job record
    job_data = {
        'job_id': job_id,
        'original_filename': filename,
        'video_path': video_path,
        'status': 'PENDING',
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    analysis_jobs[job_id] = job_data
    save_job_to_file(job_id, job_data)
    
    # Start processing in background
    thread = threading.Thread(target=process_video_async, args=(job_id,))
    thread.daemon = True
    thread.start()
    
    flash(f'Video uploaded successfully! Job ID: {job_id}', 'success')
    return redirect(url_for('job_status', job_id=job_id))

@app.route('/jobs')
def list_jobs():
    """Display all analysis jobs"""
    # Sort jobs by creation time (newest first)
    sorted_jobs = sorted(analysis_jobs.items(), 
                        key=lambda x: x[1].get('created_at', datetime.min), 
                        reverse=True)
    
    jobs_html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Analysis Jobs - Basketball Shot Analysis</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .job-card {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                transition: transform 0.2s;
            }
            .job-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            .status-pending { border-left: 5px solid #ffc107; }
            .status-processing { border-left: 5px solid #17a2b8; }
            .status-completed { border-left: 5px solid #28a745; }
            .status-failed { border-left: 5px solid #dc3545; }
            .job-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .job-id {
                font-family: monospace;
                background: #e9ecef;
                padding: 4px 8px;
                border-radius: 4px;
            }
            .status-badge {
                padding: 4px 12px;
                border-radius: 20px;
                color: white;
                font-weight: bold;
                text-transform: uppercase;
                font-size: 0.8em;
            }
            .status-pending .status-badge { background: #ffc107; color: #212529; }
            .status-processing .status-badge { background: #17a2b8; }
            .status-completed .status-badge { background: #28a745; }
            .status-failed .status-badge { background: #dc3545; }
            .action-links {
                margin-top: 15px;
            }
            .action-links a {
                color: #007bff;
                text-decoration: none;
                margin-right: 15px;
                font-weight: bold;
            }
            .action-links a:hover {
                text-decoration: underline;
            }
            .back-link {
                display: inline-block;
                margin-bottom: 20px;
                color: #007bff;
                text-decoration: none;
                font-weight: bold;
            }
            .back-link:hover {
                text-decoration: underline;
            }
            .empty-state {
                text-align: center;
                color: #666;
                font-style: italic;
                padding: 40px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Home</a>
            <h1>📋 Analysis Jobs</h1>
    '''
    
    if not sorted_jobs:
        jobs_html += '''
            <div class="empty-state">
                <p>No analysis jobs found. <a href="/">Upload a video</a> to get started!</p>
            </div>
        '''
    else:
        for job_id, job_data in sorted_jobs:
            status = job_data.get('status', 'UNKNOWN')
            status_class = f"status-{status.lower()}"
            
            created_at = job_data.get('created_at', 'Unknown')
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            elif hasattr(created_at, 'strftime'):
                created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')
            
            jobs_html += f'''
            <div class="job-card {status_class}">
                <div class="job-header">
                    <div>
                        <strong>{job_data.get('original_filename', 'Unknown file')}</strong>
                        <div class="job-id">ID: {job_id}</div>
                    </div>
                    <span class="status-badge">{status}</span>
                </div>
                <p><strong>Created:</strong> {created_at}</p>
            '''
            
            if 'error' in job_data:
                jobs_html += f'<p style="color: #dc3545;"><strong>Error:</strong> {job_data["error"]}</p>'
            
            jobs_html += '<div class="action-links">'
            jobs_html += f'<a href="/job/{job_id}">View Details</a>'
            
            if status == 'COMPLETED':
                jobs_html += f'<a href="/results/{job_id}">View Results</a>'
                jobs_html += f'<a href="/download/{job_id}">Download Video</a>'
            
            jobs_html += '</div></div>'
    
    jobs_html += '''
        </div>
    </body>
    </html>
    '''
    
    return jobs_html

@app.route('/job/<job_id>')
def job_status(job_id):
    """Display detailed job status"""
    if job_id not in analysis_jobs:
        flash(f'Job {job_id} not found!', 'error')
        return redirect(url_for('list_jobs'))
    
    job_data = analysis_jobs[job_id]
    status = job_data.get('status', 'UNKNOWN')
    
    # Auto-refresh for pending/processing jobs
    refresh_meta = ''
    if status in ['PENDING', 'PROCESSING']:
        refresh_meta = '<meta http-equiv="refresh" content="5">'
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Job {job_id} - Basketball Shot Analysis</title>
        {refresh_meta}
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .container {{
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            .status-indicator {{
                text-align: center;
                padding: 30px;
                margin: 20px 0;
                border-radius: 10px;
                font-size: 1.2em;
                font-weight: bold;
            }}
            .status-pending {{
                background: #fff3cd;
                color: #856404;
                border: 1px solid #ffeaa7;
            }}
            .status-processing {{
                background: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
            }}
            .status-completed {{
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }}
            .status-failed {{
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }}
            .job-details {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .job-details h3 {{
                margin-top: 0;
                color: #333;
            }}
            .job-details p {{
                margin: 10px 0;
            }}
            .action-buttons {{
                text-align: center;
                margin: 30px 0;
            }}
            .btn {{
                display: inline-block;
                padding: 12px 24px;
                margin: 0 10px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: bold;
                transition: background 0.3s;
            }}
            .btn-primary {{
                background: #007bff;
                color: white;
            }}
            .btn-primary:hover {{
                background: #0056b3;
            }}
            .btn-secondary {{
                background: #6c757d;
                color: white;
            }}
            .btn-secondary:hover {{
                background: #545b62;
            }}
            .loading-spinner {{
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3498db;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 2s linear infinite;
                margin: 20px auto;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏀 Job Status</h1>
            
            <div class="status-indicator status-{status.lower()}">
                {get_status_display(status)}
            </div>
            
            {get_loading_spinner(status)}
            
            <div class="job-details">
                <h3>Job Details</h3>
                <p><strong>Job ID:</strong> {job_id}</p>
                <p><strong>File:</strong> {job_data.get('original_filename', 'Unknown')}</p>
                <p><strong>Status:</strong> {status}</p>
                <p><strong>Created:</strong> {format_datetime(job_data.get('created_at'))}</p>
                <p><strong>Updated:</strong> {format_datetime(job_data.get('updated_at'))}</p>
                {get_error_display(job_data)}
                {get_processing_time(job_data)}
            </div>
            
            <div class="action-buttons">
                <a href="/jobs" class="btn btn-secondary">← All Jobs</a>
                {get_action_buttons(job_id, status)}
            </div>
        </div>
    </body>
    </html>
    '''

def get_status_display(status):
    """Get user-friendly status display"""
    status_messages = {
        'PENDING': '⏳ Analysis queued and waiting to start...',
        'PROCESSING': '🔄 Analyzing your basketball shot...',
        'COMPLETED': '✅ Analysis completed successfully!',
        'FAILED': '❌ Analysis failed. Please try again.'
    }
    return status_messages.get(status, f'Status: {status}')

def get_loading_spinner(status):
    """Show loading spinner for active jobs"""
    if status in ['PENDING', 'PROCESSING']:
        return '<div class="loading-spinner"></div>'
    return ''

def get_error_display(job_data):
    """Display error message if job failed"""
    if 'error' in job_data:
        return f'<p style="color: #dc3545;"><strong>Error:</strong> {job_data["error"]}</p>'
    return ''

def get_processing_time(job_data):
    """Calculate and display processing time"""
    if 'processed_at' in job_data and 'created_at' in job_data:
        try:
            processed_at = job_data['processed_at']
            created_at = job_data['created_at']
            
            if isinstance(processed_at, str):
                processed_at = datetime.fromisoformat(processed_at)
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
            
            duration = processed_at - created_at
            return f'<p><strong>Processing Time:</strong> {duration.total_seconds():.1f} seconds</p>'
        except:
            pass
    return ''

def get_action_buttons(job_id, status):
    """Get appropriate action buttons based on job status"""
    if status == 'COMPLETED':
        return f'''
            <a href="/results/{job_id}" class="btn btn-primary">📊 View Results</a>
            <a href="/download/{job_id}" class="btn btn-primary">📥 Download Video</a>
        '''
    elif status in ['PENDING', 'PROCESSING']:
        return '<p style="color: #666; font-style: italic;">Results will be available when analysis completes</p>'
    else:
        return '<a href="/" class="btn btn-primary">🏠 Upload New Video</a>'

def format_datetime(dt):
    """Format datetime for display"""
    if dt is None:
        return 'Unknown'
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except:
            return dt
    if hasattr(dt, 'strftime'):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    return str(dt)

@app.route('/results/<job_id>')
def view_results(job_id):
    """Display analysis results"""
    if job_id not in analysis_jobs:
        flash(f'Job {job_id} not found!', 'error')
        return redirect(url_for('list_jobs'))
    
    job_data = analysis_jobs[job_id]
    if job_data.get('status') != 'COMPLETED':
        flash(f'Job {job_id} is not completed yet!', 'warning')
        return redirect(url_for('job_status', job_id=job_id))
    
    results = job_data.get('results', {})
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Analysis Results - {job_id}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .container {{
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            .results-header {{
                text-align: center;
                margin-bottom: 40px;
            }}
            .score-display {{
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: white;
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                margin: 30px 0;
            }}
            .score-number {{
                font-size: 3em;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .results-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            .result-card {{
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                border-left: 4px solid #007bff;
            }}
            .result-card h3 {{
                color: #007bff;
                margin-top: 0;
            }}
            .feedback-section {{
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
            }}
            .feedback-section h3 {{
                color: #856404;
                margin-top: 0;
            }}
            .action-buttons {{
                text-align: center;
                margin: 40px 0;
            }}
            .btn {{
                display: inline-block;
                padding: 12px 24px;
                margin: 0 10px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: bold;
                transition: background 0.3s;
            }}
            .btn-primary {{
                background: #007bff;
                color: white;
            }}
            .btn-primary:hover {{
                background: #0056b3;
            }}
            .btn-secondary {{
                background: #6c757d;
                color: white;
            }}
            .btn-secondary:hover {{
                background: #545b62;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="results-header">
                <h1>🏀 Shot Analysis Results</h1>
                <p>Job ID: {job_id}</p>
            </div>
            
            {format_results_display(results)}
            
            <div class="action-buttons">
                <a href="/job/{job_id}" class="btn btn-secondary">← Job Details</a>
                <a href="/download/{job_id}" class="btn btn-primary">📥 Download Analysis Video</a>
                <a href="/jobs" class="btn btn-secondary">📋 All Jobs</a>
                <a href="/" class="btn btn-primary">🏠 Analyze Another Shot</a>
            </div>
        </div>
    </body>
    </html>
    '''

def format_results_display(results):
    """Format analysis results for display"""
    if not results:
        return '<p>No results available</p>'
    
    html = ''
    
    # Overall score
    overall_score = results.get('overall_score', 0)
    html += f'''
    <div class="score-display">
        <div class="score-number">{overall_score}/100</div>
        <div>Overall Shot Quality Score</div>
    </div>
    '''
    
    # Key metrics
    if 'key_metrics' in results:
        html += '<div class="results-grid">'
        for metric_name, metric_value in results['key_metrics'].items():
            html += f'''
            <div class="result-card">
                <h3>{metric_name.replace('_', ' ').title()}</h3>
                <p>{format_metric_value(metric_value)}</p>
            </div>
            '''
        html += '</div>'
    
    # Feedback points
    if 'feedback_points' in results and results['feedback_points']:
        html += '''
        <div class="feedback-section">
            <h3>💡 Areas for Improvement</h3>
        '''
        for feedback in results['feedback_points'][:5]:  # Show top 5 feedback points
            html += f'<p>• {feedback.get("remedy_tips", "No specific tips available")}</p>'
        html += '</div>'
    
    # Analysis summary
    if 'analysis_summary' in results:
        html += f'''
        <div class="feedback-section">
            <h3>📊 Analysis Summary</h3>
            <p>{results["analysis_summary"]}</p>
        </div>
        '''
    
    return html

def format_metric_value(value):
    """Format metric values for display"""
    if isinstance(value, (int, float)):
        return f"{value:.1f}"
    return str(value)

@app.route('/download/<job_id>')
def download_result(job_id):
    """Download analysis result video"""
    if job_id not in analysis_jobs:
        flash(f'Job {job_id} not found!', 'error')
        return redirect(url_for('list_jobs'))
    
    job_data = analysis_jobs[job_id]
    if job_data.get('status') != 'COMPLETED':
        flash(f'Job {job_id} is not completed yet!', 'warning')
        return redirect(url_for('job_status', job_id=job_id))
    
    # Look for the analysis video file
    output_video = os.path.join(RESULTS_FOLDER, f"{job_id}_analysis.mp4")
    if os.path.exists(output_video):
        return send_file(output_video, as_attachment=True, 
                        download_name=f"basketball_analysis_{job_id}.mp4")
    else:
        flash('Analysis video not found!', 'error')
        return redirect(url_for('job_status', job_id=job_id))

# API endpoints for status checking
@app.route('/api/job/<job_id>')
def api_job_status(job_id):
    """API endpoint for job status"""
    if job_id not in analysis_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job_data = analysis_jobs[job_id].copy()
    
    # Convert datetime objects to ISO strings for JSON serialization
    for field in ['created_at', 'updated_at', 'processed_at']:
        if field in job_data and hasattr(job_data[field], 'isoformat'):
            job_data[field] = job_data[field].isoformat()
    
    return jsonify(job_data)

@app.route('/api/jobs')
def api_list_jobs():
    """API endpoint for listing all jobs"""
    jobs_list = []
    for job_id, job_data in analysis_jobs.items():
        job_copy = job_data.copy()
        job_copy['job_id'] = job_id
        
        # Convert datetime objects to ISO strings
        for field in ['created_at', 'updated_at', 'processed_at']:
            if field in job_copy and hasattr(job_copy[field], 'isoformat'):
                job_copy[field] = job_copy[field].isoformat()
        
        jobs_list.append(job_copy)
    
    # Sort by creation time (newest first)
    jobs_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return jsonify({'jobs': jobs_list, 'total': len(jobs_list)})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Basketball Analysis v9.0',
        'active_jobs': len([j for j in analysis_jobs.values() if j.get('status') in ['PENDING', 'PROCESSING']]),
        'total_jobs': len(analysis_jobs)
    })

# Initialize on startup
load_all_jobs()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
