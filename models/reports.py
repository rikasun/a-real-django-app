from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class ReportFormat(str, Enum):
    JSON = "json"
    PDF = "pdf"
    EXCEL = "excel"

class ReportType(str, Enum):
    PERFORMANCE = "performance"
    CLEANUP = "cleanup"
    STORAGE = "storage"
    COMPREHENSIVE = "comprehensive"

class PerformanceMetrics(BaseModel):
    average_cpu: float
    peak_cpu: float
    average_memory: float
    peak_memory: float
    average_duration: float
    peak_duration: float

class StorageMetrics(BaseModel):
    average_usage: float
    peak_usage: float
    space_reclaimed: float
    growth_rate: float

class DailyStats(BaseModel):
    date: datetime
    jobs_run: int
    success_rate: float
    records_processed: int
    average_duration: float

class PerformanceReport(BaseModel):
    period: Dict[str, datetime]
    summary: Dict[str, float]
    performance: PerformanceMetrics
    storage: StorageMetrics
    trends: Dict[str, List[DailyStats]]

class CleanupStats(BaseModel):
    total_jobs: int
    success_rate: float
    total_records: int
    average_duration: float
    records_per_job: float
    failure_reasons: Dict[str, int]

class ReportSchedule(BaseModel):
    report_type: ReportType
    schedule: str  # cron expression
    recipients: List[EmailStr]
    format: ReportFormat = ReportFormat.PDF
    custom_params: Optional[Dict]

    @validator('schedule')
    def validate_cron(cls, v):
        # Add cron expression validation
        return v 