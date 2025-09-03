import os
import time
import requests
from datetime import datetime

GCP_BUCKET = os.getenv("GCP_BUCKET_NAME", "aya-internship-mlops-bucket")
VERIFY_GCP = True
MAX_POLL_TIME = 60  # seconds to poll job status

url = "http://localhost:8000/upload"
print(f"🚀 Testing upload to {url}")
print(f"👉 GCP bucket: {GCP_BUCKET}")
print(f"👉 GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'Not set')}")

# Open file handles safely
filenames = ["Juaben_tile_0.tif", "Juaben_tile_1.tif"]  # Use fewer files for faster test
print(f"📁 Using test files: {filenames}")
files = [("files", (name, open(name, "rb"), "image/tiff")) for name in filenames]

webhook_url = "http://example.com/webhook"
data = {"webhook_url": webhook_url}

start_time = datetime.now()
try:
    print(f"\n⏱️ {datetime.now().strftime('%H:%M:%S')} - Sending upload request...")
    response = requests.post(url, files=files, data=data, timeout=30)
    print(f"✅ Status Code: {response.status_code}")
    print(f"⏱️ Upload took {(datetime.now() - start_time).total_seconds():.2f} seconds")
    try:
        print(f"📝 Response JSON: {response.json()}")
        job = response.json()
        job_id = job['job_id']
    except Exception as e:
        print(f"❌ Error parsing response: {e}")
        print(f"📝 Response Text: {response.text}")
        exit(1)
finally:
    # Close file handles
    for _, (_, fh, _) in files:
        fh.close()

if VERIFY_GCP and response.status_code == 200:
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(GCP_BUCKET)
        print(f"\n🔍 Listing objects with job prefix uploads/{job_id} ...")
        prefix = f"uploads/{job_id}"
        
        # Try multiple times since uploads happen in background
        for i in range(1, 4):
            blobs = list(client.list_blobs(GCP_BUCKET, prefix=prefix))
            if not blobs:
                print(f"⚠️ Attempt {i}/3: No GCP objects found yet. Waiting 5 seconds...")
                time.sleep(5)
            else:
                print(f"✅ Found {len(blobs)} objects after {i} attempts:")
                for b in blobs:
                    print(f"  • gs://{GCP_BUCKET}/{b.name} (size={b.size} bytes)")
                break
        else:
            print("❌ No GCP objects found after retries (uploads may be disabled or failed)")
    except Exception as e:
        print(f"❌ GCP verification error: {e}")

# Poll job status 
print(f"\n📊 Polling job status for {job_id}")
poll_count = 0
end_time = datetime.now().timestamp() + MAX_POLL_TIME
while datetime.now().timestamp() < end_time:
    poll_count += 1
    try:
        status_url = f"http://localhost:8000/status/{job_id}"
        status_response = requests.get(status_url)
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"⏱️ {datetime.now().strftime('%H:%M:%S')} - Status poll #{poll_count}: {status_data['status']} ({status_data['progress']}%)")
            
            # Check for completion
            if status_data['status'] in ("completed", "failed"):
                print(f"\n{'✅' if status_data['status'] == 'completed' else '❌'} Job {status_data['status']}!")
                print(f"📝 Final details:")
                print(f"  • Files: {status_data['processed_files']}/{status_data['total_files']}")
                print(f"  • Progress: {status_data['progress']}%")
                if 'webhook_attempts' in status_data and status_data['webhook_attempts'] > 0:
                    print(f"  • Webhook: {status_data['webhook_attempts']} attempts")
                    print(f"    - Last status: {status_data['webhook_last_status_code']}")
                    print(f"    - Error: {status_data['webhook_last_error'] or 'None'}")
                    print(f"    - Delivered: {status_data['webhook_delivered_at'] or 'No'}")
                break
        else:
            print(f"⚠️ Failed to get status: HTTP {status_response.status_code}")
    except Exception as e:
        print(f"⚠️ Error checking status: {e}")
    
    # Wait before next poll
    time.sleep(2)
else:
    print(f"⚠️ Job did not complete within {MAX_POLL_TIME} seconds (still running)")

print(f"\n✨ Test completed in {(datetime.now() - start_time).total_seconds():.2f} seconds")
