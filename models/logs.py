from pydantic import BaseModel, validator
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class LogEntry(BaseModel):
    timestamp: datetime
    level: LogLevel
    message: str
    module: str
    function: Optional[str]
    line_number: Optional[int]
    details: Optional[Dict]
    stack_trace: Optional[str]

class LogFilter(BaseModel):
    level: Optional[LogLevel]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    search: Optional[str]

    @validator('end_date')
    def validate_date_range(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('end_date must be after start_date')
        return v

class LogSummary(BaseModel):
    total_size: int
    error_count: int
    warning_count: int
    oldest_log: datetime
    newest_log: datetime
    logs_by_level: Dict[LogLevel, int]
    storage_usage: float
    file_count: int

class PaginatedLogs(BaseModel):
    logs: List[LogEntry]
    total: int
    page: int
    total_pages: int
    has_next: bool
    has_previous: bool 