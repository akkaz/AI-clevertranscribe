import requests
import time
import os
import sys

# File to test
FILE_PATH = "WhatsApp Audio 2025-11-24 at 12.58.50.mpeg"
API_URL = "http://localhost:8000/api"

def test_workflow():
    if not os.path.exists(FILE_PATH):
        print(f"File not found: {FILE_PATH}")
        return

    print(f"Uploading {FILE_PATH}...")
    
    try:
        with open(FILE_PATH, 'rb') as f:
            files = {'file': f}
            data = {'language': 'it'}
            response = requests.post(f"{API_URL}/transcribe", files=files, data=data)
            
        if response.status_code != 200:
            print(f"Upload failed: {response.text}")
            return
            
        job = response.json()
        job_id = job['job_id']
        print(f"Job started with ID: {job_id}")
        
        while True:
            status_response = requests.get(f"{API_URL}/status/{job_id}")
            if status_response.status_code != 200:
                print(f"Status check failed: {status_response.text}")
                break
                
            job_status = status_response.json()
            status = job_status['status']
            print(f"Status: {status}")
            
            if status == 'completed':
                print("\n--- Transcription ---")
                print(job_status['result']['transcription'][:500] + "...")
                print("\n--- Analysis ---")
                print(job_status['result']['analysis'])
                break
            elif status == 'failed':
                print(f"Job failed: {job_status.get('error')}")
                break
                
            time.sleep(2)
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Check if requests is installed, if not try to install or warn
    try:
        import requests
    except ImportError:
        print("requests library not found. Please install it to run this test.")
        sys.exit(1)
        
    test_workflow()
