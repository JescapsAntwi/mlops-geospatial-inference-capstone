"""
Webhook test receiver for MLOps pipeline.

This script creates a simple HTTP server to receive webhooks from the MLOps pipeline.
It listens on port 9000 by default and logs received webhooks to the console.

Run with:
    uvicorn webhook_receiver:app --port 9000 --reload
"""

import hmac
import hashlib
import json
from fastapi import FastAPI, Request, Header
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Webhook Test Receiver")

# Set this to match WEBHOOK_SIGNING_SECRET in your MLOps API env
# Set to None to disable signature verification
SECRET = b"supersecret"  

class WebhookEvent(BaseModel):
    job_id: str
    status: str
    timestamp: str
    
    class Config:
        extra = "allow"

def verify_signature(sig_header: str, timestamp: str, body: bytes) -> bool:
    """Verify the webhook signature using HMAC SHA256."""
    if not SECRET:
        return True  # Skip verification if no secret is set
    
    if not sig_header or not timestamp:
        return False
        
    sig_parts = sig_header.split('=')
    if len(sig_parts) != 2 or sig_parts[0] != "sha256":
        return False
        
    sig_value = sig_parts[1]
    expected = hmac.new(SECRET, f"{timestamp}.".encode() + body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig_value, expected)

@app.post("/hook")
async def webhook_handler(request: Request, 
                          x_signature: Optional[str] = Header(None),
                          x_signature_timestamp: Optional[str] = Header(None)):
    """Handle incoming webhooks from the MLOps Pipeline."""
    body = await request.body()
    valid_sig = verify_signature(x_signature or "", x_signature_timestamp or "", body)
    
    # Log the webhook metadata
    print(f"\n--- Webhook Received {datetime.now().isoformat()} ---")
    print(f"Signature valid: {valid_sig}")
    
    try:
        data = json.loads(body)
        print(f"Event: {data.get('event')}")
        print(f"Job ID: {data.get('job_id')}")
        print(f"Status: {data.get('status')}")
        
        # Print summary if available
        if summary := data.get('summary'):
            print(f"Files: {summary.get('files_successfully_processed')}/{summary.get('total_files_uploaded')}")
            print(f"Success rate: {summary.get('success_rate_percentage')}%")
            
        # Print results info if available
        if results := data.get('results'):
            print(f"Results file: {results.get('coco_format_file')}")
            print(f"Download URL: {results.get('download_url')}")
            if gcs_path := results.get('gcs_path'):
                print(f"GCS Path: {gcs_path}")
    except Exception as e:
        print(f"Error parsing webhook data: {e}")
        print(f"Raw body: {body.decode()[:500]}...")
        
    # Return 200 OK to acknowledge receipt
    return {"status": "received", "signature_valid": valid_sig}

@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "name": "Webhook Test Receiver",
        "endpoint": "/hook",
        "signature_verification": SECRET is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
