"""
Webhook Sender Module
Handles sending webhook notifications to clients when processing is complete
"""

import asyncio
import json
from datetime import datetime
from typing import Optional
import httpx

class WebhookSender:
    """
    Handles webhook delivery to client endpoints
    
    This module sends HTTP POST requests to client webhook URLs with:
    - Processing results summary
    - Links to download results
    - Processing statistics
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 5.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    async def send_webhook(
        self, 
        webhook_url: str, 
        job_id: str, 
        results_file: str, 
        total_files: int, 
        processed_files: int,
        api_key: Optional[str] = None
    ) -> bool:
        """
        Send webhook notification to client
        
        Args:
            webhook_url: Client's webhook endpoint URL
            job_id: Unique job identifier
            results_file: Path to the COCO results file
            total_files: Total number of files uploaded
            processed_files: Number of files successfully processed
            api_key: Optional API key for authentication
            
        Returns:
            True if webhook was sent successfully, False otherwise
        """
        try:
            # Prepare webhook payload
            payload = self._prepare_webhook_payload(
                job_id, results_file, total_files, processed_files
            )
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "MLOps-Pipeline/1.0"
            }
            
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            # Send webhook with retry logic
            success = await self._send_with_retry(webhook_url, payload, headers)
            
            if success:
                print(f"✅ Webhook sent successfully to {webhook_url}")
            else:
                print(f"❌ Failed to send webhook to {webhook_url} after {self.max_retries} retries")
            
            return success
            
        except Exception as e:
            print(f"❌ Error sending webhook: {e}")
            return False
    
    def _prepare_webhook_payload(
        self, 
        job_id: str, 
        results_file: str, 
        total_files: int, 
        processed_files: int
    ) -> dict:
        """
        Prepare the webhook payload in the required format
        
        Args:
            job_id: Job identifier
            results_file: Path to results file
            total_files: Total files uploaded
            processed_files: Files successfully processed
            
        Returns:
            Dictionary containing webhook payload
        """
        # Calculate success rate
        success_rate = (processed_files / total_files * 100) if total_files > 0 else 0
        
        payload = {
            "event": "processing_completed",
            "timestamp": datetime.now().isoformat(),
            "job_id": job_id,
            "status": "completed",
            "summary": {
                "total_files_uploaded": total_files,
                "files_successfully_processed": processed_files,
                "success_rate_percentage": round(success_rate, 2),
                "processing_timestamp": datetime.now().isoformat()
            },
            "results": {
                "coco_format_file": results_file,
                "file_size_bytes": self._get_file_size(results_file),
                "download_url": f"/results/{job_id}_coco_results.json"  # Local path for demo
            },
            "metadata": {
                "model_version": "palm_v1.0",
                "pipeline_version": "1.0.0",
                "geospatial_format": "GeoTIFF",
                "output_format": "COCO JSON"
            }
        }
        
        return payload
    
    def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            import os
            return os.path.getsize(file_path)
        except:
            return 0
    
    async def _send_with_retry(
        self, 
        webhook_url: str, 
        payload: dict, 
        headers: dict
    ) -> bool:
        """
        Send webhook with retry logic
        
        Args:
            webhook_url: Target URL
            payload: Webhook payload
            headers: HTTP headers
            
        Returns:
            True if successful, False otherwise
        """
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        webhook_url,
                        json=payload,
                        headers=headers
                    )
                    
                    # Check if request was successful
                    if response.status_code in [200, 201, 202]:
                        print(f"✅ Webhook delivered successfully (attempt {attempt + 1})")
                        return True
                    else:
                        print(f"⚠️ Webhook delivery failed with status {response.status_code} (attempt {attempt + 1})")
                        
            except httpx.TimeoutException:
                print(f"⏰ Webhook timeout (attempt {attempt + 1})")
            except httpx.ConnectError:
                print(f"🔌 Connection error (attempt {attempt + 1})")
            except Exception as e:
                print(f"❌ Webhook error (attempt {attempt + 1}): {e}")
            
            # Wait before retry (except on last attempt)
            if attempt < self.max_retries - 1:
                print(f"🔄 Retrying in {self.retry_delay} seconds...")
                await asyncio.sleep(self.retry_delay)
        
        return False
    
    async def send_test_webhook(self, webhook_url: str) -> bool:
        """
        Send a test webhook to verify the endpoint is working
        
        Args:
            webhook_url: URL to test
            
        Returns:
            True if test was successful
        """
        test_payload = {
            "event": "test_webhook",
            "timestamp": datetime.now().isoformat(),
            "message": "This is a test webhook from the MLOps Pipeline",
            "status": "test"
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(webhook_url, json=test_payload, headers=headers)
                return response.status_code in [200, 201, 202]
        except Exception as e:
            print(f"❌ Test webhook failed: {e}")
            return False
