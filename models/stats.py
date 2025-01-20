from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Optional, List

class SystemMetrics(BaseModel):
    cpu_percent: float
    memory_usage: float
    disk_usage: float
    process_memory: float

class DiskUsage(BaseModel):
    total: int
    used: int
    free: int
    percent: float

class SchedulerStats(BaseModel):
    uptime: float
    last_cleanup: Optional[datetime]
    records_archived: int
    next_scheduled_run: datetime
    metrics: SystemMetrics
    disk_usage: DiskUsage
    active_jobs: int

class CleanupHistory(BaseModel):
    timestamp: datetime
    records_archived: int
    duration_seconds: float
    success: bool
    error_message: Optional[str] 