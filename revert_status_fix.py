#!/usr/bin/env python3
"""
EASY REVERT - Status Completion Fix

Quick script to revert the status completion fix if needed.
"""

import os
import shutil
from datetime import datetime

def revert_status_fix():
    """Revert the status completion fix in web_app.py"""
    web_app_file = "web_app.py"
    
    # Create backup
    backup_file = f"web_app.py.backup_revert_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(web_app_file, backup_file)
    print(f"✅ Created backup: {backup_file}")
    
    # Read file
    with open(web_app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace enhanced status check with original simple version
    enhanced_block = """        # EASILY REVERSIBLE FIX: Verify all reports are ready before marking COMPLETED
        reports_ready = True
        report_status = []
        
        # Check if video file exists
        if job_results[job_id].get('video_path'):
            if os.path.exists(job_results[job_id]['video_path']):
                report_status.append("✅ Video file ready")
            else:
                reports_ready = False
                report_status.append("❌ Video file missing")
        
        # Check if PDF exists
        pdf_info = job_results[job_id].get('improvement_plan_pdf')
        if pdf_info and isinstance(pdf_info, dict) and 'file_path' in pdf_info:
            if os.path.exists(pdf_info['file_path']):
                report_status.append("✅ PDF report ready")
            else:
                reports_ready = False
                report_status.append("❌ PDF report missing")
        
        # Check if flaw stills exist
        flaw_stills = job_results[job_id].get('flaw_stills', [])
        if flaw_stills:
            missing_stills = 0
            for still in flaw_stills:
                if not os.path.exists(still.get('file_path', '')):
                    missing_stills += 1
            if missing_stills == 0:
                report_status.append(f"✅ All {len(flaw_stills)} flaw stills ready")
            else:
                reports_ready = False
                report_status.append(f"❌ {missing_stills} flaw stills missing")
        
        logging.info(f"Report readiness check for job {job_id}: {', '.join(report_status)}")
        
        # Only set COMPLETED if all reports are actually ready
        if reports_ready:
            analysis_jobs[job_id]['status'] = 'COMPLETED'
            logging.info(f"Job {job_id} marked as COMPLETED - all reports verified ready")
        else:
            analysis_jobs[job_id]['status'] = 'FINALIZING'
            logging.warning(f"Job {job_id} kept in FINALIZING - some reports not ready yet")"""
    
    original_block = """        # Update job status to COMPLETED only after all file operations are complete
        analysis_jobs[job_id]['status'] = 'COMPLETED'"""
    
    # Replace enhanced with original
    content = content.replace(enhanced_block, original_block)
    
    # Write back
    with open(web_app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ STATUS FIX REVERTED")
    print("✅ Original simple status setting restored")
    print("✅ Status will now show COMPLETED immediately after file operations")

if __name__ == "__main__":
    print("Reverting Status Completion Fix...")
    revert_status_fix()
    print("Done!")
