from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional, Dict
from datetime import datetime, time
from enum import Enum

class ScheduleType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class EmailConfig(BaseModel):
    enabled: bool
    smtp_host: str
    smtp_port: int
    username: str
    password: str
    from_address: EmailStr
    admin_emails: List[EmailStr]

class BackupConfig(BaseModel):
    enabled: bool
    retention_days: int
    backup_path: str
    compress: bool = True

class NotificationSettings(BaseModel):
    email_on_failure: bool = True
    email_on_success: bool = False
    slack_webhook: Optional[str]
    teams_webhook: Optional[str]

class SchedulerSettings(BaseModel):
    cleanup_schedule: str
    retention_days: int
    batch_size: int
    disk_threshold: int
    optimize_db: bool = False
    email_config: EmailConfig
    backup_config: BackupConfig
    notification_settings: NotificationSettings
    
    @validator('retention_days')
    def validate_retention_days(cls, v):
        if v < 1:
            raise ValueError('Retention days must be at least 1')
        return v
    
    @validator('batch_size')
    def validate_batch_size(cls, v):
        if not (100 <= v <= 10000):
            raise ValueError('Batch size must be between 100 and 10000')
        return v
    
    @validator('disk_threshold')
    def validate_disk_threshold(cls, v):
        if not (50 <= v <= 95):
            raise ValueError('Disk threshold must be between 50 and 95')
        return v

class SettingsHistory(BaseModel):
    timestamp: datetime
    user: str
    settings: SchedulerSettings
    comment: Optional[str] 