from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from services.database import Database
from services.notifications import EmailService
import logging
import psutil
import os
from typing import Dict, Any
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CleanupConfig:
    retention_days: int
    batch_size: int = 1000
    optimize_db: bool = False
    backup_first: bool = True

class CleanupService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.db = Database()
        self.email_service = EmailService()
        self.backup_path = Path("./backups")
        self.backup_path.mkdir(exist_ok=True)

    def get_system_metrics(self) -> Dict[str, Any]:
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'process_memory': psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        }

    async def cleanup_old_records(self, config: CleanupConfig):
        try:
            logger.info(f"Starting cleanup with config: {config}")
            metrics_before = self.get_system_metrics()

            if config.backup_first:
                await self.create_backup()

            # Get records older than specified days
            cutoff_date = datetime.now() - timedelta(days=config.retention_days)
            archived_count = await self.db.archive_old_records(
                cutoff_date, 
                batch_size=config.batch_size
            )

            if config.optimize_db:
                await self.db.optimize_tables()

            metrics_after = self.get_system_metrics()
            
            # Send summary email
            report_data = {
                'job_type': 'Cleanup Job',
                'archived_records': archived_count,
                'timestamp': datetime.now(),
                'status': 'SUCCESS',
                'metrics_before': metrics_before,
                'metrics_after': metrics_after
            }
            
            await self.email_service.send_admin_report(report_data)
            logger.info(f"Cleanup completed. Archived {archived_count} records.")
            
        except Exception as e:
            logger.error(f"Error in cleanup job: {str(e)}", exc_info=True)
            await self.email_service.send_alert('Cleanup job failed', str(e))

    async def create_backup(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_path / f"backup_{timestamp}.sql"
        await self.db.create_backup(backup_file)
        logger.info(f"Created backup: {backup_file}")

cleanup_service = CleanupService()

# Run at 2 AM and 2 PM every day
cleanup_service.scheduler.add_job(
    lambda: cleanup_service.cleanup_old_records(
        CleanupConfig(retention_days=30, optimize_db=False)
    ),
    'cron',
    hour='2,14'
)

# Run every Monday and Thursday at 3 AM with optimization
cleanup_service.scheduler.add_job(
    lambda: cleanup_service.cleanup_old_records(
        CleanupConfig(retention_days=90, optimize_db=True, backup_first=True)
    ),
    'cron',
    day_of_week='mon,thu',
    hour=3
)

# Health check every 30 minutes
cleanup_service.scheduler.add_job(
    lambda: logger.info(f"Health check: {cleanup_service.get_system_metrics()}"),
    'interval',
    minutes=30
)

cleanup_service.scheduler.start() 