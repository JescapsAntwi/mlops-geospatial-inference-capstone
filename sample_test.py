import os
import time
import requests

GCP_BUCKET = os.getenv("GCP_BUCKET_NAME", "aya-internship-mlops-bucket")
VERIFY_GCP = True

url = "http://127.0.0.1:8000/upload"

# Open file handles safely
filenames = ["Juaben_tile_0.tif", "Juaben_tile_1.tif", "Juaben_tile_10.tif", "Juaben_tile_100.tif"]
files = [("files", (name, open(name, "rb"), "image/tiff")) for name in filenames]

data = {"webhook_url": "http://example.com/webhook"}

try:
    response = requests.post(url, files=files, data=data, timeout=120)
    print("Status Code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except Exception as e:
        print("Response Text:", response.text)
    job = response.json()
finally:
    # Close file handles
    for _, (_, fh, _) in files:
        fh.close()

if VERIFY_GCP and response.status_code == 200:
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(GCP_BUCKET)
        print(f"Listing objects with job prefix uploads/{job['job_id']}_ ...")
        prefix = f"uploads/{job['job_id']}"
        blobs = list(client.list_blobs(GCP_BUCKET, prefix=prefix))
        if not blobs:
            print("No GCP objects found for this job yet (maybe upload disabled or delayed)")
        else:
            for b in blobs:
                print(f"Found object: gs://{GCP_BUCKET}/{b.name} size={b.size}")
    except Exception as e:
        print(f"GCP verification error: {e}")