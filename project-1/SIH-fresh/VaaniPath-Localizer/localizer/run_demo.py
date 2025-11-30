import os
import time
import requests

def run_demo():
    url = "http://127.0.0.1:8001/upload"
    file_path = "localizer/uploads/demo-input.mp4"

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Sending request to {url} with {file_path}...")
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'source': 'en',
                'target': 'hi-IN',
                'course_id': 'demo',
                'job_id': 'demo_run_1',
                'mode': 'fast'
            }
            response = requests.post(url, files=files, data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            job_id = response.json().get('job_id')
            print(f"Job started with ID: {job_id}")
            # Poll for status
            status_url = f"http://127.0.0.1:8002/jobs/{job_id}/stats"
            while True:
                time.sleep(2)
                try:
                    stats_resp = requests.get(status_url)
                    if stats_resp.status_code == 200:
                        stats = stats_resp.json()
                        print(f"Status: {stats}")
                        if stats.get('status') in ['completed', 'failed']:
                            break
                    else:
                        print(f"Failed to get stats: {stats_resp.status_code}")
                except Exception as e:
                    print(f"Error polling stats: {e}")
    except Exception as e:
        print(f"Error sending request: {e}")

if __name__ == "__main__":
    # Wait a bit for server to start if needed
    time.sleep(5)
    run_demo()
