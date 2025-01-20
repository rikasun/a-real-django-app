from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timedelta
from models.dashboard import (
    DashboardOverview,
    PerformanceMetrics,
    Alert,
    SystemHealth,
    CleanupStats
)
from services.cleanup import CleanupService
from auth.auth_service import get_current_user
from config.roles import Permission
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
cleanup_service = CleanupService()

@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(current_user = Depends(get_current_user)):
    try:
        metrics = cleanup_service.get_system_metrics()
        disk_usage = cleanup_service.get_disk_usage()
        cleanup_history = await cleanup_service.get_cleanup_history()
        
        # Calculate success rate from recent cleanups
        recent_cleanups = cleanup_history[-10:]
        success_rate = len([c for c in recent_cleanups if c['success']]) / len(recent_cleanups) * 100 if recent_cleanups else 0
        
        return {
            "system_health": SystemHealth(
                status="healthy" if metrics['cpu_percent'] < 80 else "stressed",
                metrics=metrics,
                disk_usage=disk_usage
            ),
            "cleanup_stats": CleanupStats(
                total_records=cleanup_service.total_records_archived,
                last_run_status="success" if recent_cleanups and recent_cleanups[-1]['success'] else "failed",
                success_rate=success_rate,
                next_scheduled_run=cleanup_service.get_next_scheduled_run()
            ),
            "alerts": await get_active_alerts(),
            "recent_activity": recent_cleanups
        }
    except Exception as e:
        logger.error(f"Failed to get dashboard overview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")

@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics(
    time_range: str = "24h",
    current_user = Depends(get_current_user)
):
    try:
        return await cleanup_service.get_performance_metrics(time_range)
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get performance data")

@router.get("/alerts", response_model=List[Alert])
async def get_alerts(current_user = Depends(get_current_user)):
    try:
        return await cleanup_service.get_active_alerts()
    except Exception as e:
        logger.error(f"Failed to get alerts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get alerts") 