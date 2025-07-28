#!/usr/bin/env python3
"""Debug script to check actual analysis results structure"""

import os
import sys
import json
import glob
from datetime import datetime

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_recent_job_results():
    """Check recent job results to see what data structure is being generated"""
    
    print("=== Debugging Recent Job Results ===\n")
    
    # Check for recent job files in jobs directory
    job_files = glob.glob("jobs/*.json")
    # Filter out result files (they have _results in the name)
    job_files = [f for f in job_files if '_results' not in f]
    result_files = glob.glob("jobs/*_results.json")
    
    print(f"Found {len(job_files)} job files and {len(result_files)} result files")
    
    if not job_files and not result_files:
        print("No recent job or result files found.")
        print("Run an analysis first to generate debug data.")
        return
    
    # Check the most recent files
    all_files = [(f, os.path.getmtime(f)) for f in job_files + result_files]
    all_files.sort(key=lambda x: x[1], reverse=True)  # Sort by modification time, newest first
    
    print(f"\nRecent files (newest first):")
    for filename, mtime in all_files[:5]:  # Show top 5 most recent
        time_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"  {filename} - {time_str}")
    
    # Analyze the most recent result file
    recent_result_files = [f for f in all_files if f[0].startswith('result_')]
    
    if recent_result_files:
        recent_result_file = recent_result_files[0][0]
        print(f"\n=== Analyzing Most Recent Result File: {recent_result_file} ===")
        
        try:
            with open(recent_result_file, 'r') as f:
                result_data = json.load(f)
            
            print(f"Result data keys: {list(result_data.keys())}")
            
            # Check key fields
            print(f"\nKey Analysis Data:")
            print(f"  • analysis_complete: {result_data.get('analysis_complete', 'Not found')}")
            print(f"  • detailed_flaws: {len(result_data.get('detailed_flaws', []))} items")
            print(f"  • shot_phases: {len(result_data.get('shot_phases', []))} items") 
            print(f"  • feedback_points: {len(result_data.get('feedback_points', []))} items")
            print(f"  • improvement_plan_pdf: {result_data.get('improvement_plan_pdf', 'Not found')}")
            
            # Show detailed flaws if any
            detailed_flaws = result_data.get('detailed_flaws', [])
            if detailed_flaws:
                print(f"\nDetailed Flaws Found:")
                for i, flaw in enumerate(detailed_flaws, 1):
                    print(f"  {i}. {flaw.get('flaw_type', 'Unknown')} - Severity: {flaw.get('severity', 'N/A')}")
                    print(f"     Phase: {flaw.get('phase', 'N/A')}, Frame: {flaw.get('frame_number', 'N/A')}")
            else:
                print(f"\n❌ No detailed flaws found - this explains why PDF might not be generated!")
                print(f"   PDF is only generated when there are detailed_flaws, shot_phases, or feedback_points")
            
            # Show shot phases if any
            shot_phases = result_data.get('shot_phases', [])
            if shot_phases:
                print(f"\nShot Phases Found:")
                for i, phase in enumerate(shot_phases, 1):
                    print(f"  {i}. {phase.get('name', 'Unknown')} - Frames: {phase.get('start_frame', 'N/A')}-{phase.get('end_frame', 'N/A')}")
            else:
                print(f"\n❌ No shot phases found")
            
            # Show feedback points if any
            feedback_points = result_data.get('feedback_points', [])
            if feedback_points:
                print(f"\nFeedback Points Found:")
                for i, feedback in enumerate(feedback_points, 1):
                    print(f"  {i}. Frame {feedback.get('frame_number', 'N/A')}: {feedback.get('feedback_text', 'No text')}")
            else:
                print(f"\n❌ No feedback points found")
                
            # Check PDF status
            pdf_info = result_data.get('improvement_plan_pdf')
            if pdf_info:
                if isinstance(pdf_info, dict):
                    pdf_path = pdf_info.get('file_path')
                    if pdf_path and os.path.exists(pdf_path):
                        size = os.path.getsize(pdf_path)
                        print(f"\n✅ PDF found and exists: {pdf_path} ({size:,} bytes)")
                    else:
                        print(f"\n❌ PDF path in results but file missing: {pdf_path}")
                else:
                    print(f"\n❓ PDF info is not a dict: {pdf_info}")
            else:
                print(f"\n❌ No PDF info in results")
                
        except Exception as e:
            print(f"Error reading result file: {e}")
            import traceback
            traceback.print_exc()
    
    # Also check corresponding job file
    if recent_result_files:
        result_filename = recent_result_files[0][0]
        job_id = result_filename.replace('result_', '').replace('.json', '')
        job_filename = f"job_{job_id}.json"
        
        if os.path.exists(job_filename):
            print(f"\n=== Analyzing Corresponding Job File: {job_filename} ===")
            
            try:
                with open(job_filename, 'r') as f:
                    job_data = json.load(f)
                
                print(f"Job data keys: {list(job_data.keys())}")
                print(f"  • job_id: {job_data.get('job_id', 'Not found')}")
                print(f"  • status: {job_data.get('status', 'Not found')}")
                print(f"  • filename: {job_data.get('filename', 'Not found')}")
                
                # Check timestamps
                created_at = job_data.get('created_at')
                updated_at = job_data.get('updated_at')
                if created_at:
                    print(f"  • created_at: {created_at}")
                if updated_at:
                    print(f"  • updated_at: {updated_at}")
                    
            except Exception as e:
                print(f"Error reading job file: {e}")

def check_pdf_files():
    """Check for PDF files in results directory"""
    
    print(f"\n=== Checking PDF Files ===")
    
    results_dir = "results"
    if not os.path.exists(results_dir):
        print(f"Results directory does not exist: {results_dir}")
        return
    
    pdf_files = glob.glob(os.path.join(results_dir, "*.pdf"))
    
    if pdf_files:
        print(f"Found {len(pdf_files)} PDF files in results directory:")
        for pdf_file in pdf_files:
            size = os.path.getsize(pdf_file)
            mtime = datetime.fromtimestamp(os.path.getmtime(pdf_file)).strftime('%Y-%m-%d %H:%M:%S')
            print(f"  • {os.path.basename(pdf_file)} - {size:,} bytes - {mtime}")
    else:
        print(f"❌ No PDF files found in results directory")

if __name__ == "__main__":
    check_recent_job_results()
    check_pdf_files()
    
    print(f"\n=== Summary ===")
    print(f"If no flaws are being detected, the PDF won't be generated.")
    print(f"This could be due to:")
    print(f"  1. Video quality issues (pose detection failing)")
    print(f"  2. Threshold settings too strict")
    print(f"  3. Analysis logic not detecting expected flaws")
    print(f"  4. Camera angle or visibility issues")
    print(f"\nTo fix:")
    print(f"  1. Try with a clearer video with good lighting")
    print(f"  2. Ensure shooter is clearly visible in frame")  
    print(f"  3. Check if analysis is detecting any flaws at all")
