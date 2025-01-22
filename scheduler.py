from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from services.database import Database
from services.notifications import EmailService
import logging
import psutil
import os
from typing import Dict, Any, List
from dataclasses import dataclass
from pathlib import Path
import shutil
import asyncio

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
        self.last_cleanup_time = None
        self.total_records_archived = 0
        self.cleanup_history = []
        self.start_time = datetime.now()

    def get_system_metrics(self) -> Dict[str, Any]:
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'process_memory': psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        }

    async def cleanup_old_records(self, config: CleanupConfig):
        start_time = datetime.now()
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
            
            self.last_cleanup_time = datetime.now()
            self.total_records_archived += archived_count
            
            # Record history
            self.cleanup_history.append({
                'timestamp': self.last_cleanup_time,
                'records_archived': archived_count,
                'duration_seconds': (datetime.now() - start_time).total_seconds(),
                'success': True,
                'error_message': None
            })
            
            # Keep only last 100 entries
            if len(self.cleanup_history) > 100:
                self.cleanup_history = self.cleanup_history[-100:]
                
        except Exception as e:
            # Record failed cleanup
            self.cleanup_history.append({
                'timestamp': datetime.now(),
                'records_archived': 0,
                'duration_seconds': (datetime.now() - start_time).total_seconds(),
                'success': False,
                'error_message': str(e)
            })
            logger.error(f"Error in cleanup job: {str(e)}", exc_info=True)
            await self.email_service.send_alert('Cleanup job failed', str(e))
            raise

    async def create_backup(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_path / f"backup_{timestamp}.sql"
        await self.db.create_backup(backup_file)
        logger.info(f"Created backup: {backup_file}")

    def get_uptime(self) -> float:
        return (datetime.now() - self.start_time).total_seconds()

    def get_next_scheduled_run(self) -> datetime:
        jobs = self.scheduler.get_jobs()
        if not jobs:
            return None
        return min(job.next_run_time for job in jobs)

    async def get_cleanup_history(self) -> List[Dict]:
        return self.cleanup_history

    async def generate_scheduler_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Generate a comprehensive report of scheduler activities and performance metrics for a specified time period.

        This function analyzes scheduler performance, cleanup operations, and system metrics to create
        a detailed report. It includes statistics about cleanup jobs, system resource utilization,
        and overall efficiency metrics.

        Args:
            start_date (datetime): The start date for the report period
            end_date (datetime): The end date for the report period

        Returns:
            Dict[str, Any]: A dictionary containing the following report sections:
                - performance_metrics: CPU and memory usage statistics
                - cleanup_stats: Statistics about cleanup operations
                - disk_usage: Storage utilization metrics
                - job_history: Historical data about scheduled jobs
                Example:
                {
                    'performance_metrics': {
                        'avg_cpu_usage': 45.2,
                        'peak_memory_usage': 1024.5,
                        'avg_job_duration': 120.5
                    },
                    'cleanup_stats': {
                        'total_jobs': 48,
                        'successful_jobs': 45,
                        'records_archived': 15000,
                        'success_rate': 93.75
                    },
                    'disk_usage': {
                        'space_reclaimed': 1024000,
                        'efficiency_ratio': 0.85
                    },
                    'job_history': [
                        {
                            'timestamp': '2024-03-10T15:30:00',
                            'status': 'success',
                            'duration': 118.5,
                            'records_processed': 500
                        },
                        ...
                    ]
                }

        Raises:
            ValueError: If end_date is before start_date or if the date range is invalid
            RuntimeError: If there's an error accessing the metrics or generating the report

        Example:
            >>> start = datetime(2024, 3, 1)
            >>> end = datetime(2024, 3, 15)
            >>> report = await scheduler.generate_scheduler_report(start, end)
            >>> print(f"Success rate: {report['cleanup_stats']['success_rate']}%")
            Success rate: 93.75%
        """
        try:
            # Validate date range
            if end_date < start_date:
                raise ValueError("End date must be after start date")
            
            # Get performance metrics
            metrics = self.get_system_metrics()
            
            # Get cleanup history for the period
            cleanup_history = [job for job in self.cleanup_history 
                             if start_date <= job['timestamp'] <= end_date]
            
            # Calculate cleanup statistics
            total_jobs = len(cleanup_history)
            successful_jobs = len([job for job in cleanup_history if job['success']])
            success_rate = (successful_jobs / total_jobs * 100) if total_jobs > 0 else 0
            
            # Calculate total records archived
            total_records = sum(job['records_archived'] for job in cleanup_history if job['success'])
            
            # Calculate average job duration
            durations = [job['duration_seconds'] for job in cleanup_history if job['success']]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            # Compile the report
            report = {
                'performance_metrics': {
                    'avg_cpu_usage': metrics['cpu_percent'],
                    'peak_memory_usage': metrics['memory_usage'],
                    'avg_job_duration': avg_duration
                },
                'cleanup_stats': {
                    'total_jobs': total_jobs,
                    'successful_jobs': successful_jobs,
                    'records_archived': total_records,
                    'success_rate': success_rate
                },
                'disk_usage': {
                    'space_reclaimed': self.calculate_space_reclaimed(),
                    'efficiency_ratio': self.calculate_efficiency_ratio()
                },
                'job_history': cleanup_history
            }
            
            logger.info(f"Generated scheduler report for period: {start_date} to {end_date}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate scheduler report: {str(e)}")
            raise RuntimeError(f"Error generating scheduler report: {str(e)}")

class DiskSpaceMonitor:
    def __init__(self, threshold_percent: float = 85.0):
        self.threshold_percent = threshold_percent
        self.emergency_mode = False

    def get_disk_usage(self, path: str = "/") -> float:
        usage = shutil.disk_usage(path)
        return (usage.used / usage.total) * 100

    async def check_disk_space(self) -> None:
        try:
            usage_percent = self.get_disk_usage()
            logger.info(f"Current disk usage: {usage_percent:.2f}%")

            if usage_percent > self.threshold_percent:
                if not self.emergency_mode:
                    logger.warning(f"Disk usage critical ({usage_percent:.2f}%), initiating emergency cleanup")
                    self.emergency_mode = True
                    await self.perform_emergency_cleanup()
            else:
                self.emergency_mode = False

        except Exception as e:
            logger.error(f"Disk space check failed: {str(e)}", exc_info=True)

    async def perform_emergency_cleanup(self) -> None:
        try:
            # 1. Clear old log files
            await self.cleanup_old_logs(days=2)

            # 2. Aggressive database cleanup
            config = CleanupConfig(
                retention_days=7,
                batch_size=5000,
                optimize_db=True,
                backup_first=False  # Skip backup in emergency mode
            )
            await cleanup_service.cleanup_old_records(config)

            # 3. Clear temporary files
            temp_files_removed = await self.cleanup_temp_files()

            # 4. Send emergency notification
            await self.send_emergency_report(temp_files_removed)

        except Exception as e:
            logger.error(f"Emergency cleanup failed: {str(e)}", exc_info=True)

    async def cleanup_old_logs(self, days: int) -> List[str]:
        removed_files = []
        log_dir = Path("./logs")
        if not log_dir.exists():
            return removed_files

        cutoff_date = datetime.now() - timedelta(days=days)
        
        for log_file in log_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                log_file.unlink()
                removed_files.append(log_file.name)
                logger.info(f"Removed old log file: {log_file.name}")

        return removed_files

    async def cleanup_temp_files(self) -> int:
        temp_dir = Path("./temp")
        if not temp_dir.exists():
            return 0

        count = 0
        for temp_file in temp_dir.glob("*"):
            if temp_file.is_file():
                temp_file.unlink()
                count += 1

        return count

    async def send_emergency_report(self, temp_files_removed: int):
        current_usage = self.get_disk_usage()
        report = {
            'type': 'Emergency Cleanup Report',
            'timestamp': datetime.now(),
            'initial_disk_usage': f"{self.threshold_percent}%+",
            'current_disk_usage': f"{current_usage:.2f}%",
            'actions_taken': {
                'temp_files_removed': temp_files_removed,
                'aggressive_cleanup_performed': True,
                'logs_cleaned': True
            }
        }
        
        await cleanup_service.email_service.send_admin_report(report)

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

# Initialize disk monitor
disk_monitor = DiskSpaceMonitor()

# Add disk space monitoring job (every 15 minutes)
cleanup_service.scheduler.add_job(
    disk_monitor.check_disk_space,
    'interval',
    minutes=15,
    id='disk_space_monitor'
)

cleanup_service.scheduler.start() 