#!/usr/bin/env python3
"""
Test script to reproduce the save_results_to_file issue locally
"""

import sys
import os
import json
from datetime import datetime

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_app import save_results_to_file

def test_save_results():
    """Test the save_results_to_file function with sample data"""
    
    # Sample results data based on the structure we see in successful jobs
    test_job_id = "test-save-function-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    
    test_results = {
        "video_path": f"uploads/{test_job_id}.mov",
        "analysis_complete": True,
        "processed_at": datetime.now().isoformat(),
        "flaw_stills": [
            {"phase": "preparation", "timestamp": 0.5, "image_path": f"test_{test_job_id}_prep.jpg"},
            {"phase": "execution", "timestamp": 1.0, "image_path": f"test_{test_job_id}_exec.jpg"}
        ],
        "feedback_stills": [
            {"phase": "preparation", "timestamp": 0.5, "image_path": f"test_{test_job_id}_feedback_prep.jpg"},
            {"phase": "execution", "timestamp": 1.0, "image_path": f"test_{test_job_id}_feedback_exec.jpg"}
        ],
        "detailed_flaws": [
            {"phase": "preparation", "flaw": "Elbow alignment", "description": "Test flaw description"},
            {"phase": "execution", "flaw": "Follow through", "description": "Test follow through issue"}
        ],
        "shot_phases": [
            {"phase": "preparation", "start_time": 0.0, "end_time": 0.8},
            {"phase": "execution", "start_time": 0.8, "end_time": 1.5}
        ],
        "feedback_points": [
            "Improve elbow alignment during preparation",
            "Focus on follow through completion"
        ],
        "improvement_plan_pdf": f"test_{test_job_id}_improvement_plan.pdf"
    }
    
    print(f"Testing save_results_to_file with job_id: {test_job_id}")
    print(f"Test results keys: {list(test_results.keys())}")
    
    # Try to save the results
    try:
        success = save_results_to_file(test_job_id, test_results)
        if success:
            print("✅ save_results_to_file returned True - Success!")
            
            # Verify the file was created
            results_file = f"jobs/{test_job_id}_results.json"
            if os.path.exists(results_file):
                print(f"✅ Results file created: {results_file}")
                
                # Try to read it back
                with open(results_file, 'r') as f:
                    saved_data = json.load(f)
                    print(f"✅ File readable, keys: {list(saved_data.keys())}")
                    
                # Clean up test file
                os.remove(results_file)
                print("🧹 Test file cleaned up")
            else:
                print(f"❌ Results file NOT found: {results_file}")
        else:
            print("❌ save_results_to_file returned False - Failed!")
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_save_results()
