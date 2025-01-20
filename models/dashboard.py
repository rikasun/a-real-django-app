from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum

class SystemStatus(str, Enum):
    HEALTHY = "healthy"
    STRESSED = "stressed"
    CRITICAL = "critical"

class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class SystemHealth(BaseModel):
    status: SystemStatus
    metrics: Dict[str, float]
    disk_usage: Dict[str, float]

class CleanupStats(BaseModel):
    total_records: int
    last_run_status: str
    success_rate: float
    next_scheduled_run: datetime

class Alert(BaseModel):
    id: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    resolved: bool
    details: Optional[Dict]

class PerformanceMetric(BaseModel):
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    cleanup_duration: Optional[float]
    records_processed: Optional[int]

class PerformanceMetrics(BaseModel):
    time_range: str
    data_points: List[PerformanceMetric]
    average_cpu: float
    average_memory: float
    peak_cpu: float
    peak_memory: float

class DashboardOverview(BaseModel):
    system_health: SystemHealth
    cleanup_stats: CleanupStats
    alerts: List[Alert]
    recent_activity: List[Dict] 