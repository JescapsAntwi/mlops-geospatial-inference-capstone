"""
Database module for job tracking and management
Uses SQLite for simplicity, can be easily upgraded to PostgreSQL later
"""

import sqlite3
import asyncio
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum
import aiosqlite

class JobStatus(str, Enum):
    """Enum for job status values"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Job:
    """Data class representing a job"""
    job_id: str
    status: str
    total_files: int
    processed_files: int
    progress: int
    webhook_url: Optional[str]
    created_at: str
    updated_at: str

class Database:
    """Database manager for job tracking"""
    
    def __init__(self, db_path: str = "mlops_pipeline.db"):
        self.db_path = db_path
    
    async def init_db(self):
        """Initialize database and create tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    total_files INTEGER NOT NULL,
                    processed_files INTEGER DEFAULT 0,
                    progress INTEGER DEFAULT 0,
                    webhook_url TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            await db.commit()
            print("📊 Database initialized successfully")
    
    async def create_job(self, job_id: str, total_files: int, webhook_url: Optional[str] = None):
        """Create a new job record"""
        now = datetime.now().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO jobs (job_id, status, total_files, processed_files, progress, webhook_url, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (job_id, JobStatus.QUEUED, total_files, 0, 0, webhook_url, now, now))
            await db.commit()
            print(f"📝 Created job {job_id} with {total_files} files")
    
    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT job_id, status, total_files, processed_files, progress, webhook_url, created_at, updated_at
                FROM jobs WHERE job_id = ?
            """, (job_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return Job(
                        job_id=row[0],
                        status=row[1],
                        total_files=row[2],
                        processed_files=row[3],
                        progress=row[4],
                        webhook_url=row[5],
                        created_at=row[6],
                        updated_at=row[7]
                    )
                return None
    
    async def update_job_status(self, job_id: str, status: JobStatus):
        """Update job status"""
        now = datetime.now().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE jobs SET status = ?, updated_at = ? WHERE job_id = ?
            """, (status, now, job_id))
            await db.commit()
            print(f"🔄 Updated job {job_id} status to {status}")
    
    async def update_job_progress(self, job_id: str, progress: int, processed_files: int):
        """Update job progress and processed file count"""
        now = datetime.now().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE jobs SET progress = ?, processed_files = ?, updated_at = ? WHERE job_id = ?
            """, (progress, processed_files, now, job_id))
            await db.commit()
    
    async def list_jobs(self) -> List[Job]:
        """List all jobs"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT job_id, status, total_files, processed_files, progress, webhook_url, created_at, updated_at
                FROM jobs ORDER BY created_at DESC
            """) as cursor:
                rows = await cursor.fetchall()
                return [
                    Job(
                        job_id=row[0],
                        status=row[1],
                        total_files=row[2],
                        processed_files=row[3],
                        progress=row[4],
                        webhook_url=row[5],
                        created_at=row[6],
                        updated_at=row[7]
                    )
                    for row in rows
                ]
