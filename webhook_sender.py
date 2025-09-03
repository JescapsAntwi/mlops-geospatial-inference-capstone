"""
Webhook Sender Module
Handles sending webhook notifications to clients when processing is complete
"""

import asyncio
import json
import hmac
import hashlib
import os
import random
from datetime import datetime
from typing import Optional, Callable, Awaitable
import httpx

class WebhookSender:
    """
    Handles webhook delivery to client endpoints
    
    This module sends HTTP POST requests to client webhook URLs with:
    - Processing results summary
    - Links to download results
    - Processing statistics
    """
    
    def __init__(
        self,
        max_retries: int = 5,
        base_retry_delay: float = 2.0,
        timeout_seconds: float = 20.0,
        signing_secret: Optional[str] = None,
        attempt_recorder: Optional[Callable[[str, Optional[int], Optional[str], bool], Awaitable[None]]] = None
    ):
        """Initialize the webhook sender.

        Args:
            max_retries: Maximum delivery attempts (including first try)
            base_retry_delay: Base delay for exponential backoff
            timeout_seconds: HTTP request timeout
            signing_secret: Optional secret used to compute HMAC SHA256 signature
            attempt_recorder: Async callback to record attempt details in persistence layer
        """
        self.max_retries = max_retries
        self.base_retry_delay = base_retry_delay
        self.timeout_seconds = timeout_seconds
        self.signing_secret = signing_secret or os.getenv("WEBHOOK_SIGNING_SECRET")
        self.attempt_recorder = attempt_recorder
    
    async def send_webhook(
        self,
        webhook_url: str,
        job_id: str,
        results_file: str,
        total_files: int,
        processed_files: int,
    results_gcs_path: Optional[str] = None,
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
                job_id=job_id,
                results_file=results_file,
                total_files=total_files,
                processed_files=processed_files,
                results_gcs_path=results_gcs_path
            )
            
            # Prepare headers
            body_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")

            headers = {
                "Content-Type": "application/json",
                "User-Agent": "MLOps-Pipeline/1.0"
            }
            
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            # Optional request signing (HMAC SHA256)
            if self.signing_secret:
                timestamp = str(int(datetime.utcnow().timestamp()))
                signature_payload = f"{timestamp}.".encode("utf-8") + body_bytes
                digest = hmac.new(self.signing_secret.encode("utf-8"), signature_payload, hashlib.sha256).hexdigest()
                headers["X-Signature-Timestamp"] = timestamp
                headers["X-Signature-Version"] = "v1"
                headers["X-Signature"] = f"sha256={digest}"
            
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
        processed_files: int,
        results_gcs_path: Optional[str] = None
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
        
        results_section = {
            "coco_format_file": results_file,
            "file_size_bytes": self._get_file_size(results_file),
            "download_url": f"/results/{job_id}_coco_results.json"
        }
    # results bucket removed; gcs_path omitted
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
            "results": results_section,
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
        for attempt in range(1, self.max_retries + 1):
            error_msg = None
            status_code = None
            try:
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    response = await client.post(
                        webhook_url,
                        json=payload,
                        headers=headers
                    )
                    status_code = response.status_code
                    if status_code in (200, 201, 202):
                        print(f"✅ Webhook delivered successfully (attempt {attempt})")
                        if self.attempt_recorder:
                            await self.attempt_recorder(payload.get("job_id"), status_code, None, True)
                        return True
                    else:
                        error_msg = f"Non-success status code {status_code}" if status_code else None
                        print(f"⚠️ Webhook delivery failed with status {status_code} (attempt {attempt})")
            except httpx.TimeoutException:
                error_msg = "timeout"
                print(f"⏰ Webhook timeout (attempt {attempt})")
            except httpx.ConnectError:
                error_msg = "connection_error"
                print(f"🔌 Connection error (attempt {attempt})")
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Webhook error (attempt {attempt}): {e}")

            if self.attempt_recorder:
                try:
                    await self.attempt_recorder(payload.get("job_id"), status_code, error_msg, False)
                except Exception:
                    pass

            # Backoff (except on last attempt)
            if attempt < self.max_retries:
                # Exponential backoff with jitter
                delay = self.base_retry_delay * (2 ** (attempt - 1))
                jitter = random.uniform(0, delay * 0.2)
                wait_time = delay + jitter
                print(f"🔄 Retrying in {wait_time:.1f} seconds...")
                await asyncio.sleep(wait_time)
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
