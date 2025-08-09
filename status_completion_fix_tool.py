#!/usr/bin/env python3
"""
EASILY REVERSIBLE STATUS FIX - Ensures status shows COMPLETED only after reports are ready

This script creates a backup of the current web_app.py and applies a fix to prevent
users from seeing "View Results" before reports are actually generated.
"""

import os
import shutil
from datetime import datetime

def create_backup():
    """Create a backup of the current web_app.py"""
    web_app_file = "web_app.py"
    backup_file = f"web_app.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if os.path.exists(web_app_file):
        shutil.copy2(web_app_file, backup_file)
        print(f"✅ Created backup: {backup_file}")
        return backup_file
    else:
        print(f"❌ Web app file not found: {web_app_file}")
        return None

def apply_status_fix():
    """Apply the status fix to ensure COMPLETED only shows when reports are ready"""
    web_app_file = "web_app.py"
    
    if not os.path.exists(web_app_file):
        print(f"❌ Web app file not found: {web_app_file}")
        return False
    
    # Create backup first
    backup_file = create_backup()
    if not backup_file:
        return False
    
    try:
        # Read current file
        with open(web_app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the location where status is set to COMPLETED
        status_line = "        # Update job status to COMPLETED only after all file operations are complete"
        completed_line = "        analysis_jobs[job_id]['status'] = 'COMPLETED'"
        
        if status_line in content and completed_line in content:
            # Replace the COMPLETED status setting with verification logic
            old_block = f"""        # Update job status to COMPLETED only after all file operations are complete
        analysis_jobs[job_id]['status'] = 'COMPLETED'"""
            
            new_block = f"""        # EASILY REVERSIBLE FIX: Verify all reports are ready before marking COMPLETED
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
                report_status.append(f"✅ All {{len(flaw_stills)}} flaw stills ready")
            else:
                reports_ready = False
                report_status.append(f"❌ {{missing_stills}} flaw stills missing")
        
        logging.info(f"Report readiness check for job {{job_id}}: {{', '.join(report_status)}}")
        
        # Only set COMPLETED if all reports are actually ready
        if reports_ready:
            analysis_jobs[job_id]['status'] = 'COMPLETED'
            logging.info(f"Job {{job_id}} marked as COMPLETED - all reports verified ready")
        else:
            analysis_jobs[job_id]['status'] = 'FINALIZING'
            logging.warning(f"Job {{job_id}} kept in FINALIZING - some reports not ready yet")"""
            
            content = content.replace(old_block, new_block)
            
            # Write the updated content
            with open(web_app_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ STATUS FIX APPLIED SUCCESSFULLY")
            print("✅ Status will only show COMPLETED when all reports are actually ready")
            print(f"✅ Backup saved as: {backup_file}")
            print("\nApplied changes:")
            print("- Added report readiness verification before marking COMPLETED")
            print("- Status stays as FINALIZING if any reports are missing")
            print("- Added detailed logging of report status")
            print("- View Results button only appears when everything is ready")
            
            return True
        else:
            print("❌ Could not find the status setting code to modify")
            print("⚠️  Manual inspection may be required")
            return False
            
    except Exception as e:
        print(f"❌ Error applying status fix: {e}")
        print(f"⚠️  You can manually restore from backup: {backup_file}")
        return False

def revert_status_fix():
    """Revert the status fix"""
    web_app_file = "web_app.py"
    
    if not os.path.exists(web_app_file):
        print(f"❌ Web app file not found: {web_app_file}")
        return False
    
    # Create backup first
    backup_file = create_backup()
    if not backup_file:
        return False
    
    try:
        # Read current file
        with open(web_app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the enhanced status block and replace with original
        enhanced_start = "        # EASILY REVERSIBLE FIX: Verify all reports are ready before marking COMPLETED"
        enhanced_end = '            logging.warning(f"Job {job_id} kept in FINALIZING - some reports not ready yet")'
        
        start_pos = content.find(enhanced_start)
        end_pos = content.find(enhanced_end)
        
        if start_pos != -1 and end_pos != -1:
            # Replace enhanced block with original simple version
            end_pos += len(enhanced_end)
            
            original_block = """        # Update job status to COMPLETED only after all file operations are complete
        analysis_jobs[job_id]['status'] = 'COMPLETED'"""
            
            content = content[:start_pos] + original_block + content[end_pos:]
            
            # Write the reverted content
            with open(web_app_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ STATUS FIX REVERTED SUCCESSFULLY")
            print("✅ Original behavior restored")
            print(f"✅ Backup saved as: {backup_file}")
            print("\nReverted changes:")
            print("- Removed report readiness verification")
            print("- Status set to COMPLETED immediately after file operations")
            print("- Removed detailed report status logging")
            
            return True
        else:
            print("❌ Could not find the enhanced status code to revert")
            print("⚠️  Manual inspection may be required")
            return False
            
    except Exception as e:
        print(f"❌ Error reverting status fix: {e}")
        print(f"⚠️  You can manually restore from backup: {backup_file}")
        return False

def main():
    print("Status Fix Tool - Prevent Early 'View Results' Button")
    print("=" * 55)
    print("1. Apply fix (verify reports before showing COMPLETED)")
    print("2. Revert fix (restore original behavior)")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            print("\n🔧 APPLYING status completion fix...")
            if apply_status_fix():
                print("\n✅ Fix applied successfully!")
                print("Users will now only see 'View Results' when all reports are ready.")
            break
        elif choice == '2':
            print("\n🔄 REVERTING status completion fix...")
            if revert_status_fix():
                print("\n✅ Fix reverted successfully!")
                print("Original behavior restored.")
            break
        elif choice == '3':
            print("👋 Exiting...")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
