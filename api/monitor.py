from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import logging
from typing import List, Dict
from services.cleanup import CleanupService
from models.stats import SchedulerStats, CleanupHistory

router = APIRouter()
logger = logging.getLogger(__name__)
cleanup_service = CleanupService()

@router.get("/stats", response_model=SchedulerStats)
async def get_scheduler_stats():
    try:
        metrics = cleanup_service.get_system_metrics()
        disk_usage = cleanup_service.get_disk_usage()
        
        return {
            "uptime": cleanup_service.get_uptime(),
            "last_cleanup": cleanup_service.last_cleanup_time,
            "records_archived": cleanup_service.total_records_archived,
            "next_scheduled_run": cleanup_service.get_next_scheduled_run(),
            "metrics": metrics,
            "disk_usage": disk_usage,
            "active_jobs": len(cleanup_service.scheduler.get_jobs())
        }
    except Exception as e:
        logger.error(f"Failed to get scheduler stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get scheduler statistics")

@router.get("/history", response_model=List[CleanupHistory])
async def get_cleanup_history():
    try:
        return await cleanup_service.get_cleanup_history()
    except Exception as e:
        logger.error(f"Failed to get cleanup history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get cleanup history") 