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
os.makedirs('jobs', exist_ok=True)  # Directory for job persistence

# In-memory storage for demo (in production, use a database)
analysis_jobs = {}
job_results = {}

# Job persistence functions
def save_job_to_file(job_id, job_data):
    """Save job data to file for persistence across sessions"""
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
        print(f"DEBUG: Saved job {job_id} to file")
    except Exception as e:
        print(f"DEBUG: Failed to save job {job_id}: {e}")

def load_job_from_file(job_id):
    """Load job data from file"""
    try:
        job_file = os.path.join('jobs', f"{job_id}.json")
        if os.path.exists(job_file):
            with open(job_file, 'r') as f:
                job_data = json.load(f)
            
            # Convert ISO strings back to datetime objects
            if 'created_at' in job_data:
                job_data['created_at'] = datetime.fromisoformat(job_data['created_at'])
            if 'updated_at' in job_data:
                job_data['updated_at'] = datetime.fromisoformat(job_data['updated_at'])
            if 'processed_at' in job_data:
                job_data['processed_at'] = datetime.fromisoformat(job_data['processed_at'])
            
            print(f"DEBUG: Loaded job {job_id} from file")
            return job_data
    except Exception as e:
        print(f"DEBUG: Failed to load job {job_id}: {e}")
    return None

def save_results_to_file(job_id, results_data):
    """Save results data to file for persistence"""
    try:
        # Ensure jobs directory exists
        jobs_dir = 'jobs'
        if not os.path.exists(jobs_dir):
            os.makedirs(jobs_dir)
            print(f"DEBUG: Created jobs directory: {jobs_dir}")
        
        results_file = os.path.join(jobs_dir, f"{job_id}_results.json")
        print(f"DEBUG: Attempting to save results to: {results_file}")
        
        serializable_data = results_data.copy()
        
        # Convert datetime objects to ISO strings
        if 'processed_at' in serializable_data:
            serializable_data['processed_at'] = serializable_data['processed_at'].isoformat()
        
        # Convert complex objects to serializable format
        def make_serializable(obj, depth=0, max_depth=5):
            # Prevent infinite recursion
            if depth > max_depth:
                return str(obj)
            
            # Handle basic types first
            if obj is None or isinstance(obj, (str, int, float, bool)):
                return obj
            elif isinstance(obj, list):
                return [make_serializable(item, depth + 1, max_depth) for item in obj]
            elif isinstance(obj, dict):
                return {k: make_serializable(v, depth + 1, max_depth) for k, v in obj.items()}
            elif hasattr(obj, '__dict__'):
                # Skip MediaPipe and OpenCV objects - just convert to string representation
                if any(x in str(type(obj)) for x in ['mediapipe', 'cv2', 'numpy.ndarray']):
                    return str(obj)
                # Convert other objects with attributes to dictionaries
                try:
                    return {k: make_serializable(v, depth + 1, max_depth) for k, v in obj.__dict__.items()}
                except:
                    return str(obj)
            else:
                return str(obj)
        
        # Apply serialization to complex fields
        for key in ['shot_phases', 'detailed_flaws', 'feedback_points']:
            if key in serializable_data:
                serializable_data[key] = make_serializable(serializable_data[key])
        
        with open(results_file, 'w') as f:
            json.dump(serializable_data, f, indent=2)
        
        print(f"DEBUG: Successfully saved results {job_id} to file")
        print(f"DEBUG: File size: {os.path.getsize(results_file)} bytes")
        
        # Verify the file was written correctly
        if os.path.exists(results_file):
            try:
                with open(results_file, 'r') as f:
                    test_load = json.load(f)
                print(f"DEBUG: Results file verification successful")
            except Exception as e:
                print(f"DEBUG: Results file verification failed: {e}")
        
    except Exception as e:
        print(f"DEBUG: Failed to save results {job_id}: {e}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")

def load_results_from_file(job_id):
    """Load results data from file"""
    try:
        results_file = os.path.join('jobs', f"{job_id}_results.json")
        print(f"DEBUG: Attempting to load results from: {results_file}")
        print(f"DEBUG: Results file exists: {os.path.exists(results_file)}")
        
        if os.path.exists(results_file):
            print(f"DEBUG: File size: {os.path.getsize(results_file)} bytes")
            
            with open(results_file, 'r') as f:
                content = f.read()
                print(f"DEBUG: File content length: {len(content)}")
                
            # Reset file pointer and load JSON
            with open(results_file, 'r') as f:
                results_data = json.load(f)
            
            # Convert ISO strings back to datetime objects
            if 'processed_at' in results_data:
                results_data['processed_at'] = datetime.fromisoformat(results_data['processed_at'])
            
            print(f"DEBUG: Successfully loaded results {job_id} from file")
            print(f"DEBUG: Results keys: {list(results_data.keys())}")
            return results_data
        else:
            print(f"DEBUG: Results file does not exist: {results_file}")
            # List files in jobs directory to see what's there
            jobs_dir = 'jobs'
            if os.path.exists(jobs_dir):
                files_in_jobs = os.listdir(jobs_dir)
                print(f"DEBUG: Files in jobs directory: {files_in_jobs}")
            else:
                print(f"DEBUG: Jobs directory does not exist: {jobs_dir}")
                
    except Exception as e:
        print(f"DEBUG: Failed to load results {job_id}: {e}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
    return None

def load_all_jobs():
    """Load all jobs from files on startup"""
    try:
        job_files = [f for f in os.listdir('jobs') if f.endswith('.json') and not f.endswith('_results.json')]
        for job_file in job_files:
            job_id = job_file.replace('.json', '')
            job_data = load_job_from_file(job_id)
            if job_data:
                analysis_jobs[job_id] = job_data
                
                # Also load results if available
                results_data = load_results_from_file(job_id)
                if results_data:
                    job_results[job_id] = results_data
        
        print(f"DEBUG: Loaded {len(analysis_jobs)} jobs from files")
    except Exception as e:
        print(f"DEBUG: Failed to load jobs from files: {e}")

# Load existing jobs on startup
load_all_jobs()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_web_compatible_video(video_path):
    """Ensure video is web-compatible, convert if needed, and fix orientation"""
    if not os.path.exists(video_path):
        return video_path
    
    # Check if video needs conversion or orientation fix
    try:
        import subprocess
        
        # Get video codec info and rotation metadata
        probe_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', video_path]
        result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            import json
            probe_data = json.loads(result.stdout)
            
            needs_conversion = False
            rotation = 0
            
            # Check if video stream uses web-compatible codec and check rotation
            for stream in probe_data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    codec = stream.get('codec_name', '')
                    
                    # If not H.264, needs conversion
                    if codec != 'h264':
                        needs_conversion = True
                    
                    # Check for rotation metadata
                    side_data = stream.get('side_data_list', [])
                    for data in side_data:
                        if data.get('side_data_type') == 'Display Matrix':
                            rotation_str = data.get('rotation', '0')
                            try:
                                rotation = int(float(rotation_str))
                            except (ValueError, TypeError):
                                rotation = 0
                    
                    # Also check tags for rotation
                    tags = stream.get('tags', {})
                    if 'rotate' in tags:
                        try:
                            rotation = int(tags['rotate'])
                        except (ValueError, TypeError):
                            rotation = 0
                    break
            
            # Convert to web-compatible format and fix orientation if needed
            if needs_conversion or (rotation != 0 and rotation % 90 == 0):
                web_path = video_path.replace('.mp4', '_web.mp4')
                
                # Build FFmpeg command
                convert_cmd = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-c:v', 'libx264',
                    '-profile:v', 'baseline',
                    '-level', '3.0',
                    '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart',
                    '-preset', 'fast',
                    '-crf', '23'
                ]
                
                # Add rotation fix if needed
                if rotation != 0 and rotation % 90 == 0:
                    if rotation == 90:
                        convert_cmd.extend(['-vf', 'transpose=1'])  # 90° clockwise
                    elif rotation == 180:
                        convert_cmd.extend(['-vf', 'transpose=2,transpose=2'])  # 180°
                    elif rotation == 270:
                        convert_cmd.extend(['-vf', 'transpose=2'])  # 90° counter-clockwise
                    
                    # Remove rotation metadata
                    convert_cmd.extend(['-metadata:s:v:0', 'rotate=0'])
                
                convert_cmd.append(web_path)
                
                convert_result = subprocess.run(convert_cmd, capture_output=True, text=True, timeout=120)
                
                if convert_result.returncode == 0 and os.path.exists(web_path):
                    # Replace original with converted version
                    os.remove(video_path)
                    os.rename(web_path, video_path)
                    print(f"Converted video to web format and fixed orientation: {video_path}")
                    return video_path
                else:
                    print(f"Video conversion failed: {convert_result.stderr}")
                    
    except Exception as e:
        print(f"Video compatibility check/fix failed: {e}")
    
    return video_path

def process_video_async(job_id, video_path, ideal_data):
    """Process video analysis in background thread"""
    import signal
    import threading
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Analysis timeout - processing took too long")
    
    try:
        # Set timeout for analysis (10 minutes for deployment)
        timeout_seconds = 600  # 10 minutes
        
        # Update job status
        analysis_jobs[job_id]['status'] = 'PROCESSING'
        analysis_jobs[job_id]['updated_at'] = datetime.now()
        save_job_to_file(job_id, analysis_jobs[job_id])
        
        # Create job object
        job = VideoAnalysisJob(
            job_id=job_id,
            user_id="web_user",
            video_url=video_path
        )
        
        # Process the video with timeout protection
        print(f"DEBUG: Starting analysis for job {job_id} with {timeout_seconds}s timeout")
        
        # Use threading timer as fallback timeout mechanism for deployment
        def analysis_with_timeout():
            try:
                return process_video_for_analysis(job, ideal_data)
            except Exception as e:
                print(f"DEBUG: Analysis exception: {e}")
                return {'error': str(e)}
        
        # Run analysis in separate thread with monitoring
        analysis_result = [None]
        analysis_exception = [None]
        
        def run_analysis():
            try:
                analysis_result[0] = process_video_for_analysis(job, ideal_data)
            except Exception as e:
                analysis_exception[0] = e
        
        analysis_thread = threading.Thread(target=run_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
        analysis_thread.join(timeout=timeout_seconds)
        
        if analysis_thread.is_alive():
            print(f"DEBUG: Analysis timeout for job {job_id}")
            analysis_results = {'error': 'Analysis timeout - video processing took too long. Please try with a shorter video.'}
        elif analysis_exception[0]:
            print(f"DEBUG: Analysis exception for job {job_id}: {analysis_exception[0]}")
            analysis_results = {'error': str(analysis_exception[0])}
        else:
            analysis_results = analysis_result[0]
        
        print(f"DEBUG: Analysis completed for job {job_id}. Results: {type(analysis_results)}")
        
        if analysis_results:
            print(f"DEBUG: Analysis results keys: {analysis_results.keys()}")
        else:
            print(f"DEBUG: Analysis results is None or empty")
        
        # Check if analysis encountered errors
        if analysis_results and 'error' in analysis_results:
            print(f"DEBUG: Analysis had errors: {analysis_results['error']}")
            # Store error results
            job_results[job_id] = {
                'video_path': None,
                'analysis_complete': False,
                'processed_at': datetime.now(),
                'flaw_stills': [],
                'feedback_stills': [],
                'detailed_flaws': [],
                'shot_phases': [],
                'feedback_points': [],
                'improvement_plan_pdf': None,
                'error': analysis_results['error']
            }
            save_results_to_file(job_id, job_results[job_id])
            analysis_jobs[job_id]['status'] = 'FAILED'
            analysis_jobs[job_id]['error'] = analysis_results['error']
            analysis_jobs[job_id]['updated_at'] = datetime.now()
            save_job_to_file(job_id, analysis_jobs[job_id])
            return
        
        # Store results - get video path from analysis results
        result_video_path = None
        if analysis_results and 'output_video_path' in analysis_results:
            result_video_path = analysis_results['output_video_path']
            print(f"DEBUG: Analysis returned video path: {result_video_path}")
            print(f"DEBUG: Video path exists: {result_video_path and os.path.exists(result_video_path)}")
        
        if result_video_path and os.path.exists(result_video_path):
            
            # Move flaw stills to results folder
            flaw_stills_results = []
            if analysis_results and 'flaw_stills' in analysis_results:
                for flaw_still in analysis_results['flaw_stills']:
                    original_path = flaw_still['file_path']
                    if os.path.exists(original_path):
                        # Create a more user-friendly filename
                        flaw_type = flaw_still['flaw_data']['flaw_type']
                        frame_num = flaw_still['frame_number']
                        new_filename = f"{job_id}_flaw_{flaw_type}_frame_{frame_num}.png"
                        new_path = os.path.join(RESULTS_FOLDER, new_filename)
                        os.rename(original_path, new_path)
                        
                        flaw_stills_results.append({
                            'file_path': new_path,
                            'filename': new_filename,
                            'flaw_data': flaw_still['flaw_data'],
                            'frame_number': flaw_still['frame_number']
                        })
            
            # Move feedback stills to results folder  
            feedback_stills_results = []
            if analysis_results and 'feedback_stills' in analysis_results:
                for frame_num, still_path in analysis_results['feedback_stills'].items():
                    if os.path.exists(still_path):
                        new_filename = f"{job_id}_feedback_frame_{frame_num}.png"
                        new_path = os.path.join(RESULTS_FOLDER, new_filename)
                        os.rename(still_path, new_path)
                        
                        feedback_stills_results.append({
                            'file_path': new_path,
                            'filename': new_filename,
                            'frame_number': frame_num
                        })
            
            # Move improvement plan PDF to results folder
            improvement_plan_pdf = None
            if analysis_results and 'improvement_plan_pdf' in analysis_results:
                original_pdf_path = analysis_results['improvement_plan_pdf']
                if original_pdf_path and os.path.exists(original_pdf_path):
                    new_pdf_filename = f"{job_id}_60_Day_Improvement_Plan.pdf"
                    new_pdf_path = os.path.join(RESULTS_FOLDER, new_pdf_filename)
                    os.rename(original_pdf_path, new_pdf_path)
                    improvement_plan_pdf = {
                        'file_path': new_pdf_path,
                        'filename': new_pdf_filename
                    }
            
            job_results[job_id] = {
                'video_path': result_video_path,
                'analysis_complete': True,
                'processed_at': datetime.now(),
                'flaw_stills': flaw_stills_results,
                'feedback_stills': feedback_stills_results,
                'detailed_flaws': analysis_results.get('detailed_flaws', []) if analysis_results else [],
                'shot_phases': analysis_results.get('shot_phases', []) if analysis_results else [],
                'feedback_points': analysis_results.get('feedback_points', []) if analysis_results else [],
                'improvement_plan_pdf': improvement_plan_pdf
            }
        else:
            # No output video was generated, but analysis completed 
            # This can happen when MediaPipe fails to detect poses in most frames
            print(f"DEBUG: No output video generated for job {job_id}, storing results without video")
            job_results[job_id] = {
                'video_path': None,
                'analysis_complete': True,
                'processed_at': datetime.now(),
                'flaw_stills': [],
                'feedback_stills': [],
                'detailed_flaws': analysis_results.get('detailed_flaws', []) if analysis_results else [],
                'shot_phases': analysis_results.get('shot_phases', []) if analysis_results else [],
                'feedback_points': analysis_results.get('feedback_points', []) if analysis_results else [],
                'improvement_plan_pdf': None,
                'warning': 'Analysis completed but pose detection failed in most frames. Please try with better lighting or a clearer view of the player.'
            }
        
        # Save results to file
        print(f"DEBUG: Saving results for job {job_id}")
        print(f"DEBUG: Results keys: {list(job_results[job_id].keys())}")
        print(f"DEBUG: Analysis complete: {job_results[job_id].get('analysis_complete', False)}")
        print(f"DEBUG: Video path exists: {job_results[job_id].get('video_path') and os.path.exists(job_results[job_id]['video_path'])}")
        
        save_results_to_file(job_id, job_results[job_id])
        
        # Update job status
        analysis_jobs[job_id]['status'] = 'COMPLETED'
        analysis_jobs[job_id]['updated_at'] = datetime.now()
        save_job_to_file(job_id, analysis_jobs[job_id])
        
    except Exception as e:
        print(f"Error processing job {job_id}: {e}")
        analysis_jobs[job_id]['status'] = 'FAILED'
        analysis_jobs[job_id]['error'] = str(e)
        analysis_jobs[job_id]['updated_at'] = datetime.now()
        save_job_to_file(job_id, analysis_jobs[job_id])

@app.route('/')
def index():
    """Main upload page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    """Handle video upload and start analysis"""
    print("Upload route called")
    print("request.files:", request.files)
    print("request.form:", request.form)
    
    if 'video' not in request.files:
        print("No 'video' key in request.files")
        flash('No video file selected')
        return redirect(url_for('index'))
    
    file = request.files['video']
    print("File object:", file)
    print("File filename:", file.filename)
    
    if file.filename == '':
        print("Empty filename")
        flash('No video file selected')
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        print("File type not allowed:", file.filename)
        flash('Invalid file type. Please upload MP4, AVI, MOV, or MKV files.')
        return redirect(url_for('index'))
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        flash('File too large. Maximum size is 100MB.')
        return redirect(url_for('index'))
    
    # Save the uploaded file
    job_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    file_extension = filename.rsplit('.', 1)[1].lower()
    saved_filename = f"{job_id}.{file_extension}"
    filepath = os.path.join(UPLOAD_FOLDER, saved_filename)
    file.save(filepath)
    
    # Create job record
    analysis_jobs[job_id] = {
        'job_id': job_id,
        'filename': filename,
        'filepath': filepath,
        'status': 'PENDING',
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    # Save job to file for persistence
    save_job_to_file(job_id, analysis_jobs[job_id])
    
    # Load ideal shot data
    ideal_data = load_ideal_shot_data('ideal_shot_guide.json')
    
    # Start background processing
    thread = threading.Thread(
        target=process_video_async, 
        args=(job_id, filepath, ideal_data)
    )
    thread.daemon = True
    thread.start()
    
    flash(f'Video uploaded successfully! Analysis started for job: {job_id}')
    return redirect(url_for('analysis_status', job_id=job_id))

@app.route('/status/<job_id>')
def analysis_status(job_id):
    """Show analysis status page"""
    if job_id not in analysis_jobs:
        # Try to load from file
        job_data = load_job_from_file(job_id)
        if job_data:
            analysis_jobs[job_id] = job_data
            # Also try to load results
            results_data = load_results_from_file(job_id)
            if results_data:
                job_results[job_id] = results_data
        else:
            flash('Job not found')
            return redirect(url_for('index'))
    
    job = analysis_jobs[job_id]
    return render_template('status.html', job=job, job_id=job_id)

@app.route('/api/status/<job_id>')
def api_status(job_id):
    """API endpoint for checking job status"""
    if job_id not in analysis_jobs:
        # Try to load from file
        job_data = load_job_from_file(job_id)
        if job_data:
            analysis_jobs[job_id] = job_data
            # Also try to load results
            results_data = load_results_from_file(job_id)
            if results_data:
                job_results[job_id] = results_data
        else:
            return jsonify({'error': 'Job not found'}), 404
    
    job = analysis_jobs[job_id]
    response = {
        'job_id': job_id,
        'status': job['status'],
        'created_at': job['created_at'].isoformat(),
        'updated_at': job['updated_at'].isoformat()
    }
    
    if job['status'] == 'COMPLETED' and job_id in job_results:
        response['results_available'] = True
        response['download_url'] = url_for('download_result', job_id=job_id)
    elif job['status'] == 'FAILED':
        response['error'] = job.get('error', 'Unknown error')
    
    return jsonify(response)

@app.route('/demo')
def demo_results():
    """Demo route to test video display with existing results"""
    import glob
    
    # Find an existing analyzed video
    video_files = glob.glob(os.path.join(RESULTS_FOLDER, "*_analyzed.mp4"))
    if not video_files:
        flash('No demo videos available')
        return redirect(url_for('index'))
    
    # Use the first available video
    demo_video = video_files[0]
    demo_job_id = os.path.basename(demo_video).replace('_analyzed.mp4', '')
    
    # Create demo job and results
    analysis_jobs[demo_job_id] = {
        'job_id': demo_job_id,
        'filename': 'demo_basketball_shot.mp4',
        'filepath': demo_video,
        'status': 'COMPLETED',
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    # Find related files
    flaw_stills = []
    feedback_stills = []
    improvement_plan_pdf = None
    
    # Look for flaw stills
    flaw_files = glob.glob(os.path.join(RESULTS_FOLDER, f"{demo_job_id}_flaw_*.png"))
    for i, flaw_file in enumerate(flaw_files):
        filename = os.path.basename(flaw_file)
        flaw_type = filename.split('_flaw_')[1].split('_frame_')[0]
        frame_num = filename.split('_frame_')[1].split('.')[0]
        flaw_stills.append({
            'file_path': flaw_file,
            'filename': filename,
            'flaw_data': {
                'flaw_type': flaw_type,
                'phase': 'Release',
                'severity': 25.0 + i * 10,
                'plain_language': f'Demo {flaw_type.replace("_", " ").title()} detected in your shooting form.',
                'coaching_tip': f'Focus on correcting your {flaw_type.replace("_", " ")} for better accuracy.',
                'drill_suggestion': f'Practice {flaw_type.replace("_", " ")} correction drills daily.'
            },
            'frame_number': int(frame_num) if frame_num.isdigit() else 0
        })
    
    # Look for feedback stills
    feedback_files = glob.glob(os.path.join(RESULTS_FOLDER, f"{demo_job_id}_feedback_*.png"))
    for feedback_file in feedback_files:
        filename = os.path.basename(feedback_file)
        frame_num = filename.split('_frame_')[1].split('.')[0]
        feedback_stills.append({
            'file_path': feedback_file,
            'filename': filename,
            'frame_number': int(frame_num) if frame_num.isdigit() else 0
        })
    
    # Look for PDF
    pdf_files = glob.glob(os.path.join(RESULTS_FOLDER, f"{demo_job_id}_60_Day_*.pdf"))
    if not pdf_files:
        pdf_files = glob.glob(os.path.join(RESULTS_FOLDER, f"60_Day_*{demo_job_id}*.pdf"))
    
    if pdf_files:
        pdf_file = pdf_files[0]
        improvement_plan_pdf = {
            'file_path': pdf_file,
            'filename': os.path.basename(pdf_file)
        }
    
    job_results[demo_job_id] = {
        'video_path': demo_video,
        'analysis_complete': True,
        'processed_at': datetime.now(),
        'flaw_stills': flaw_stills,
        'feedback_stills': feedback_stills,
        'detailed_flaws': [still['flaw_data'] for still in flaw_stills],
        'shot_phases': [
            {'name': 'Load/Dip', 'start_frame': 0, 'end_frame': 15},
            {'name': 'Release', 'start_frame': 16, 'end_frame': 25},
            {'name': 'Follow-Through', 'start_frame': 26, 'end_frame': 40}
        ],
        'feedback_points': [
            {
                'frame_number': 20,
                'discrepancy': 'Demo feedback point for testing',
                'remedy_tips': 'Practice proper shooting form'
            }
        ],
        'improvement_plan_pdf': improvement_plan_pdf
    }
    
    flash(f'Demo results loaded for job: {demo_job_id}')
    return redirect(url_for('view_results', job_id=demo_job_id))

@app.route('/results/<job_id>')
def view_results(job_id):
    """View analysis results"""
    if job_id not in analysis_jobs:
        # Try to load from file
        job_data = load_job_from_file(job_id)
        if job_data:
            analysis_jobs[job_id] = job_data
            # Also try to load results
            results_data = load_results_from_file(job_id)
            if results_data:
                job_results[job_id] = results_data
        else:
            flash('Job not found')
            return redirect(url_for('index'))
    
    job_status = analysis_jobs[job_id]['status']
    
    if job_status == 'PROCESSING':
        flash('Analysis is still in progress. Please wait...')
        return redirect(url_for('index'))
    elif job_status == 'FAILED':
        if job_id in job_results and 'error' in job_results[job_id]:
            flash(f'Analysis failed: {job_results[job_id]["error"]}')
        else:
            flash('Analysis failed due to an error')
        return redirect(url_for('index'))
    elif job_status != 'COMPLETED':
        flash('Analysis not completed or job not found')
        return redirect(url_for('index'))
    
    if job_id not in job_results:
        # Try to load results from file
        results_data = load_results_from_file(job_id)
        if results_data:
            job_results[job_id] = results_data
        else:
            # Enhanced debugging for missing results
            print(f"DEBUG: Results not found for job {job_id}")
            print(f"DEBUG: Analysis jobs keys: {list(analysis_jobs.keys())}")
            print(f"DEBUG: Job results keys: {list(job_results.keys())}")
            print(f"DEBUG: Job status: {analysis_jobs[job_id]['status']}")
            
            # Check if results file exists
            results_file = os.path.join('jobs', f'{job_id}_results.json')
            print(f"DEBUG: Results file {results_file} exists: {os.path.exists(results_file)}")
            
            if os.path.exists(results_file):
                try:
                    with open(results_file, 'r') as f:
                        content = f.read()
                        print(f"DEBUG: Results file content length: {len(content)}")
                        print(f"DEBUG: Results file first 200 chars: {content[:200]}")
                except Exception as e:
                    print(f"DEBUG: Error reading results file: {e}")
            
            flash('Results not available - analysis may have failed or results were not saved properly. Please try uploading the video again.')
            return redirect(url_for('index'))
    
    job = analysis_jobs[job_id]
    results = job_results[job_id]
    
    # Show warning if analysis completed but with issues
    if 'warning' in results:
        flash(results['warning'], 'warning')
    
    return render_template('results.html', job=job, results=results, job_id=job_id)

@app.route('/download/<job_id>')
def download_result(job_id):
    """Download analyzed video"""
    if job_id not in job_results:
        # Try to load results from file
        results_data = load_results_from_file(job_id)
        if results_data:
            job_results[job_id] = results_data
        else:
            # Enhanced debugging for missing results in download
            print(f"DEBUG DOWNLOAD: Results not found for job {job_id}")
            print(f"DEBUG DOWNLOAD: Analysis jobs keys: {list(analysis_jobs.keys())}")
            print(f"DEBUG DOWNLOAD: Job results keys: {list(job_results.keys())}")
            
            # Check if job exists
            if job_id in analysis_jobs:
                print(f"DEBUG DOWNLOAD: Job status: {analysis_jobs[job_id]['status']}")
            else:
                print(f"DEBUG DOWNLOAD: Job {job_id} not found in analysis_jobs")
            
            # Check if results file exists
            results_file = os.path.join('jobs', f'{job_id}_results.json')
            print(f"DEBUG DOWNLOAD: Results file {results_file} exists: {os.path.exists(results_file)}")
            
            if os.path.exists(results_file):
                try:
                    with open(results_file, 'r') as f:
                        content = f.read()
                        print(f"DEBUG DOWNLOAD: Results file content length: {len(content)}")
                        print(f"DEBUG DOWNLOAD: Results file first 200 chars: {content[:200]}")
                except Exception as e:
                    print(f"DEBUG DOWNLOAD: Error reading results file: {e}")
            
            flash('Results not available - analysis may have failed or results were not saved properly. Please try uploading the video again.')
            return redirect(url_for('index'))
    
    video_path = job_results[job_id]['video_path']
    print(f"DEBUG DOWNLOAD: Video path for job {job_id}: {video_path}")
    print(f"DEBUG DOWNLOAD: Video path exists: {video_path and os.path.exists(video_path)}")
    
    if not video_path or not os.path.exists(video_path):
        print(f"DEBUG DOWNLOAD: Video file not found - {video_path}")
        flash('Result video not found - analysis may have failed to generate an output video')
        return redirect(url_for('index'))
    
    print(f"DEBUG DOWNLOAD: Sending video file: {video_path}")
    return send_file(
        video_path,
        as_attachment=True,
        download_name=f"analyzed_shot_{job_id}.mp4",
        mimetype='video/mp4'
    )

@app.route('/video/<job_id>')
def serve_video(job_id):
    """Serve analyzed video for web playback with proper headers"""
    if job_id not in job_results:
        # Try to load results from file
        results_data = load_results_from_file(job_id)
        if results_data:
            job_results[job_id] = results_data
        else:
            print(f"DEBUG VIDEO: Results not found for job {job_id}")
            print(f"DEBUG VIDEO: Job results keys: {list(job_results.keys())}")
            flash('Results not available')
            return redirect(url_for('index'))
    
    video_path = job_results[job_id]['video_path']
    print(f"DEBUG VIDEO: Video path for job {job_id}: {video_path}")
    print(f"DEBUG VIDEO: Video path exists: {video_path and os.path.exists(video_path)}")
    
    if not video_path or not os.path.exists(video_path):
        print(f"DEBUG VIDEO: Video file not found - {video_path}")
        flash('Result video not found - analysis may have failed to generate an output video')
        return redirect(url_for('index'))
    
    # Ensure video is web-compatible
    video_path = ensure_web_compatible_video(video_path)
    
    def generate():
        with open(video_path, 'rb') as f:
            data = f.read(1024)
            while data:
                yield data
                data = f.read(1024)
    
    response = Response(generate(), mimetype="video/mp4")
    response.headers.add('Accept-Ranges', 'bytes')
    response.headers.add('Cache-Control', 'no-cache')
    response.headers.add('Access-Control-Allow-Origin', '*')
    
    return response

@app.route('/download_flaw_still/<job_id>/<int:still_index>')
def download_flaw_still(job_id, still_index):
    """Download specific flaw analysis still"""
    if job_id not in job_results:
        flash('Results not available')
        return redirect(url_for('index'))
    
    flaw_stills = job_results[job_id].get('flaw_stills', [])
    if still_index >= len(flaw_stills):
        flash('Still frame not found')
        return redirect(url_for('view_results', job_id=job_id))
    
    still_info = flaw_stills[still_index]
    still_path = still_info['file_path']
    
    if not os.path.exists(still_path):
        flash('Still frame file not found')
        return redirect(url_for('view_results', job_id=job_id))
    
    return send_file(
        still_path,
        as_attachment=True,
        download_name=still_info['filename'],
        mimetype='image/png'
    )

@app.route('/download_improvement_plan/<job_id>')
def download_improvement_plan(job_id):
    """Download 60-day improvement plan PDF"""
    if job_id not in job_results:
        flash('Results not available')
        return redirect(url_for('index'))
    
    improvement_plan = job_results[job_id].get('improvement_plan_pdf')
    if not improvement_plan or not os.path.exists(improvement_plan['file_path']):
        flash('Improvement plan PDF not available')
        return redirect(url_for('view_results', job_id=job_id))
    
    return send_file(
        improvement_plan['file_path'],
        as_attachment=True,
        download_name=improvement_plan['filename'],
        mimetype='application/pdf'
    )

@app.route('/download_complete_package/<job_id>')
def download_complete_package(job_id):
    """Download complete analysis package including video, stills, and PDF"""
    if job_id not in job_results:
        flash('Results not available')
        return redirect(url_for('index'))
    
    import zipfile
    import io
    
    results = job_results[job_id]
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add analyzed video
        video_path = results.get('video_path')
        if video_path and os.path.exists(video_path):
            zip_file.write(video_path, f"analyzed_video_{job_id}.mp4")
        
        # Add improvement plan PDF
        improvement_plan = results.get('improvement_plan_pdf')
        if improvement_plan and os.path.exists(improvement_plan['file_path']):
            zip_file.write(improvement_plan['file_path'], improvement_plan['filename'])
        
        # Add flaw analysis stills
        flaw_stills = results.get('flaw_stills', [])
        if flaw_stills:
            for still in flaw_stills:
                if os.path.exists(still['file_path']):
                    zip_file.write(still['file_path'], f"flaw_analysis/{still['filename']}")
        
        # Add feedback stills
        feedback_stills = results.get('feedback_stills', [])
        if feedback_stills:
            for still in feedback_stills:
                if os.path.exists(still['file_path']):
                    zip_file.write(still['file_path'], f"feedback_frames/{still['filename']}")
        
        # Add summary text file
        summary_content = f"""BASKETBALL SHOT ANALYSIS SUMMARY
Analysis ID: {job_id}
Analysis Date: {results['processed_at'].strftime('%B %d, %Y at %I:%M %p')}

PACKAGE CONTENTS:
- analyzed_video_{job_id}.mp4: Slow-motion video with pose overlays and analysis
- {improvement_plan['filename'] if improvement_plan else 'N/A'}: Comprehensive 60-day improvement plan
- flaw_analysis/: Frame stills showing detected flaws with coaching overlays
- feedback_frames/: Additional feedback frame captures

DETECTED FLAWS: {len(results.get('detailed_flaws', []))}
"""
        
        for i, flaw in enumerate(results.get('detailed_flaws', []), 1):
            summary_content += f"""
{i}. {flaw.get('flaw_type', 'Unknown').replace('_', ' ').title()}
   Severity: {flaw.get('severity', 0):.1f}/100
   Phase: {flaw.get('phase', 'Unknown')}
   Issue: {flaw.get('plain_language', 'No description available')}
"""
        
        summary_content += f"""

NEXT STEPS:
1. Review the 60-day improvement plan PDF for detailed training guidance
2. Study the flaw analysis images to understand specific issues
3. Follow the progressive drill recommendations
4. Re-analyze your shot every 2 weeks using the Basketball Analysis App
5. Track your progress using the provided benchmarks

For questions or support, visit: www.basketballanalysis.ai
"""
        
        zip_file.writestr(f"Analysis_Summary_{job_id}.txt", summary_content)
    
    zip_buffer.seek(0)
    
    return send_file(
        io.BytesIO(zip_buffer.read()),
        as_attachment=True,
        download_name=f"Complete_Basketball_Analysis_{job_id}.zip",
        mimetype='application/zip'
    )

@app.route('/download_all_stills/<job_id>')
def download_all_stills(job_id):
    """Download all flaw analysis stills as a ZIP file"""
    if job_id not in job_results:
        flash('Results not available')
        return redirect(url_for('index'))
    
    import zipfile
    import io
    
    flaw_stills = job_results[job_id].get('flaw_stills', [])
    feedback_stills = job_results[job_id].get('feedback_stills', [])
    
    if not flaw_stills and not feedback_stills:
        flash('No still frames available for download')
        return redirect(url_for('view_results', job_id=job_id))
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add flaw analysis stills
        for still in flaw_stills:
            if os.path.exists(still['file_path']):
                zip_file.write(still['file_path'], still['filename'])
        
        # Add feedback stills
        for still in feedback_stills:
            if os.path.exists(still['file_path']):
                zip_file.write(still['file_path'], still['filename'])
    
    zip_buffer.seek(0)
    
    return send_file(
        io.BytesIO(zip_buffer.read()),
        as_attachment=True,
        download_name=f"shot_analysis_stills_{job_id}.zip",
        mimetype='application/zip'
    )

@app.route('/history')
def view_history():
    """View analysis history"""
    # Sort jobs by creation date (newest first)
    sorted_jobs = sorted(
        analysis_jobs.items(),
        key=lambda x: x[1]['created_at'],
        reverse=True
    )
    return render_template('history.html', jobs=sorted_jobs)

@app.route('/about')
def about():
    """About page explaining the analysis"""
    return render_template('about.html')

@app.route('/health')
def health():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Basketball Analysis Service',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def health_check():
    """Comprehensive health check endpoint"""
    health_status = {
        'status': 'healthy',
        'service': 'Basketball Analysis Service',
        'timestamp': datetime.now().isoformat(),
        'active_jobs': len([j for j in analysis_jobs.values() if j['status'] == 'PROCESSING']),
        'checks': {}
    }
    
    # Check database connection (if configured)
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            from sqlalchemy import create_engine, text
            engine = create_engine(database_url)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            health_status['checks']['database'] = 'healthy'
        else:
            health_status['checks']['database'] = 'not_configured'
    except Exception as e:
        health_status['checks']['database'] = f'error: {str(e)}'
        health_status['status'] = 'degraded'
    
    # Check Redis connection (if configured)
    try:
        redis_url = os.getenv('REDIS_URL')
        if redis_url:
            try:
                import redis
                client = redis.Redis.from_url(redis_url)
                client.ping()
                health_status['checks']['redis'] = 'healthy'
            except ImportError:
                health_status['checks']['redis'] = 'redis_not_installed'
        else:
            health_status['checks']['redis'] = 'not_configured'
    except Exception as e:
        health_status['checks']['redis'] = f'error: {str(e)}'
        health_status['status'] = 'degraded'
    
    # Check disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage('.')
        free_gb = free // (1024**3)
        health_status['checks']['disk_space'] = f'{free_gb}GB free'
        if free_gb < 1:  # Less than 1GB free
            health_status['status'] = 'warning'
    except Exception as e:
        health_status['checks']['disk_space'] = f'error: {str(e)}'
    
    return jsonify(health_status)

if __name__ == '__main__':
    print("🏀 Basketball Analysis Web Service Starting...")
    print("📊 Service Features:")
    print("   • Video upload and analysis")
    print("   • Real-time progress tracking")
    print("   • Biomechanical feedback")
    print("   • Downloadable results")
    print("   • Analysis history")
    print("\n🌐 Starting web server at http://127.0.0.1:5000")
    print("📝 Upload a basketball shot video to begin analysis!")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
