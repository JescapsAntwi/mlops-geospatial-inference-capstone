"""
Main FastAPI application for the MLOps Pipeline
This is the core API server that handles all client interactions
"""

import os
import asyncio
import json
import uuid
from datetime import datetime
from typing import List, Optional
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx

# Import our custom modules
from database import Database, JobStatus
from inference_worker_simple import InferenceWorker
from post_processor import PostProcessor
from webhook_sender import WebhookSender

# Create FastAPI app
app = FastAPI(
    title="MLOps Geospatial Inference Pipeline",
    description="API for processing GeoTIFF images with Palm model",
    version="1.0.0"
)

# Initialize components
db = Database()
inference_worker = InferenceWorker()
post_processor = PostProcessor()
webhook_sender = WebhookSender()

# Data models for API requests/responses
class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str
    created_at: str

class StatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    total_files: int
    processed_files: int
    created_at: str
    updated_at: str

class WebhookConfig(BaseModel):
    webhook_url: str
    api_key: Optional[str] = None

# Create necessary directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("results", exist_ok=True)
os.makedirs("temp", exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """Initialize database and create tables on startup"""
    await db.init_db()
    print("🚀 MLOps Pipeline API started successfully!")

@app.post("/upload", response_model=JobResponse)
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    webhook_url: Optional[str] = None
):
    """
    Upload GeoTIFF files for processing
    
    This endpoint accepts multiple GeoTIFF files and starts the inference pipeline.
    Files are saved locally and a job is created for processing.
    """
    try:
        # Validate files
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Check if files are GeoTIFF
        for file in files:
            if not file.filename.lower().endswith(('.tif', '.tiff')):
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {file.filename} is not a GeoTIFF file"
                )
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Create job record in database
        await db.create_job(
            job_id=job_id,
            total_files=len(files),
            webhook_url=webhook_url
        )
        
        # Save uploaded files
        file_paths = []
        for file in files:
            file_path = f"uploads/{job_id}_{file.filename}"
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            file_paths.append(file_path)
        
        # Start processing in background
        background_tasks.add_task(
            process_job,
            job_id=job_id,
            file_paths=file_paths
        )
        
        return JobResponse(
            job_id=job_id,
            status="queued",
            message=f"Job created successfully. {len(files)} files uploaded.",
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{job_id}", response_model=StatusResponse)
async def get_job_status(job_id: str):
    """
    Check the status of a processing job
    
    Returns current progress, status, and metadata about the job.
    """
    try:
        job = await db.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return StatusResponse(
            job_id=job.job_id,
            status=job.status,
            progress=job.progress,
            total_files=job.total_files,
            processed_files=job.processed_files,
            created_at=job.created_at,
            updated_at=job.updated_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs")
async def list_jobs():
    """List all jobs with their current status"""
    try:
        jobs = await db.list_jobs()
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_job(job_id: str, file_paths: List[str]):
    """
    Main processing pipeline for a job
    
    This function runs the complete workflow:
    1. Run inference on all files
    2. Post-process results into COCO format
    3. Send webhook notification
    """
    try:
        print(f"🔄 Starting processing for job {job_id}")
        
        # Update job status to processing
        await db.update_job_status(job_id, JobStatus.PROCESSING)
        
        # Run inference on all files
        print(f"🔍 Running inference on {len(file_paths)} files...")
        inference_results = []
        
        for i, file_path in enumerate(file_paths):
            try:
                # Run inference on single file
                result = await inference_worker.process_file(file_path)
                inference_results.append(result)
                
                # Update progress
                progress = int((i + 1) / len(file_paths) * 100)
                await db.update_job_progress(job_id, progress, i + 1)
                
                print(f"✅ Processed {i+1}/{len(file_paths)} files")
                
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
                # Continue with other files
        
        # Post-process results into COCO format
        print("📝 Converting results to COCO format...")
        coco_results = post_processor.convert_to_coco(inference_results)
        
        # Save COCO results
        results_file = f"results/{job_id}_coco_results.json"
        with open(results_file, "w") as f:
            json.dump(coco_results, f, indent=2)
        
        # Update job status to completed
        await db.update_job_status(job_id, JobStatus.COMPLETED)
        await db.update_job_progress(job_id, 100, len(file_paths))
        
        # Send webhook notification
        job = await db.get_job(job_id)
        if job.webhook_url:
            print(f"🔔 Sending webhook to {job.webhook_url}")
            await webhook_sender.send_webhook(
                job.webhook_url,
                job_id,
                results_file,
                len(file_paths),
                len(inference_results)
            )
        
        print(f"🎉 Job {job_id} completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in job {job_id}: {e}")
        await db.update_job_status(job_id, JobStatus.FAILED)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "MLOps Geospatial Inference Pipeline API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload - Upload GeoTIFF files for processing",
            "status": "/status/{job_id} - Check job status",
            "jobs": "/jobs - List all jobs",
            "docs": "/docs - API documentation"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
