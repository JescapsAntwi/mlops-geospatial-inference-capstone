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
    """Data class representing a job (results bucket removed)."""
    job_id: str
    status: str
    total_files: int
    processed_files: int
    progress: int
    webhook_url: Optional[str]
    created_at: str
    updated_at: str
    webhook_attempts: int = 0
    webhook_last_status_code: Optional[int] = None
    webhook_last_error: Optional[str] = None
    webhook_delivered_at: Optional[str] = None

class Database:
    """Database manager for job tracking"""
    
    def __init__(self, db_path: str = "mlops_pipeline.db"):
        self.db_path = db_path

    async def _maybe_migrate(self):
        """Attempt non-destructive schema migrations (add columns if missing)."""
        async with aiosqlite.connect(self.db_path) as db:
            migrations = [
                ("webhook_attempts", "INTEGER DEFAULT 0"),
                ("webhook_last_status_code", "INTEGER"),
                ("webhook_last_error", "TEXT"),
                ("webhook_delivered_at", "TEXT")
            ]
            for col, col_type in migrations:
                try:
                    await db.execute(f"ALTER TABLE jobs ADD COLUMN {col} {col_type}")
                except Exception:
                    pass
            await db.commit()
    
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
                    updated_at TEXT NOT NULL,
                    webhook_attempts INTEGER DEFAULT 0,
                    webhook_last_status_code INTEGER,
                    webhook_last_error TEXT,
                    webhook_delivered_at TEXT
                )
            """)
            await db.commit()
        await self._maybe_migrate()
        print("📊 Database initialized successfully")
    
    async def create_job(self, job_id: str, total_files: int, webhook_url: Optional[str] = None):
        """Create a new job record"""
        now = datetime.now().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO jobs (
                    job_id, status, total_files, processed_files, progress,
                    webhook_url, created_at, updated_at,
                    webhook_attempts, webhook_last_status_code, webhook_last_error, webhook_delivered_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id, JobStatus.QUEUED, total_files, 0, 0,
                webhook_url, now, now,
                0, None, None, None
            ))
            await db.commit()
            print(f"📝 Created job {job_id} with {total_files} files")
    
    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT job_id, status, total_files, processed_files, progress, webhook_url, created_at, updated_at,
                       webhook_attempts, webhook_last_status_code, webhook_last_error, webhook_delivered_at
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
                        updated_at=row[7],
                        webhook_attempts=row[8] or 0,
                        webhook_last_status_code=row[9],
                        webhook_last_error=row[10],
                        webhook_delivered_at=row[11]
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
                SELECT job_id, status, total_files, processed_files, progress, webhook_url, created_at, updated_at,
                       webhook_attempts, webhook_last_status_code, webhook_last_error, webhook_delivered_at
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
                        updated_at=row[7],
                        webhook_attempts=row[8] or 0,
                        webhook_last_status_code=row[9],
                        webhook_last_error=row[10],
                        webhook_delivered_at=row[11]
                    )
                    for row in rows
                ]
    
    # results bucket removed: no setter needed

    async def record_webhook_attempt(
        self,
        job_id: str,
        status_code: Optional[int],
        error: Optional[str],
        delivered: bool
    ):
        """Record details of a webhook delivery attempt.

        If delivered=True and webhook_delivered_at is not yet set, set it.
        """
        now = datetime.now().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            # increment attempts
            await db.execute(
                """
                UPDATE jobs
                SET webhook_attempts = COALESCE(webhook_attempts,0) + 1,
                    webhook_last_status_code = ?,
                    webhook_last_error = ?,
                    webhook_delivered_at = CASE
                        WHEN ? = 1 AND (webhook_delivered_at IS NULL OR webhook_delivered_at = '') THEN ?
                        ELSE webhook_delivered_at
                    END,
                    updated_at = ?
                WHERE job_id = ?
                """,
                (status_code, error, 1 if delivered else 0, now, now, job_id)
            )
            await db.commit()
