import requests
import time
import uuid

# Railway app URL
import requests
import io

# Replace with your actual Railway URL
RAILWAY_URL = "https://apexsportstrainer-production.up.railway.app"

def trigger_test_analysis():
    """Create a test analysis job on Railway to trigger our enhanced error handling"""
    
    # Create a minimal video file for testing (just empty data)
    test_job_id = f"test-{uuid.uuid4().hex[:8]}"
    
    # Try to upload a test file to trigger analysis
    files = {
        'video': ('test.mp4', b'fake video data for testing', 'video/mp4')
    }
    
    try:
        print(f"🚀 Triggering test analysis on Railway...")
        response = requests.post(f"{RAILWAY_URL}/upload", files=files)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response content: {response.text[:500]}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                job_id = data.get('job_id', 'unknown')
                print(f"✅ Test analysis triggered! Job ID: {job_id}")
                print(f"📊 Check the results at: {RAILWAY_URL}/results/{job_id}")
                return job_id
            except ValueError as e:
                print(f"❌ Error parsing JSON response: {e}")
                return None
        else:
            print(f"❌ Failed to trigger analysis: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            return None
            
    except Exception as e:
        print(f"❌ Error triggering test: {e}")
        return None

if __name__ == "__main__":
    job_id = trigger_test_analysis()
    if job_id:
        print(f"\n🔍 Monitor the Railway logs to see enhanced error handling in action:")
        print(f"   railway logs --tail")
        print(f"\n📋 Check results at:")
        print(f"   {RAILWAY_URL}/results/{job_id}")
