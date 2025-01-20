from fastapi import APIRouter, HTTPException, Depends, Query, Response
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from models.logs import (
    LogEntry,
    LogSummary,
    LogFilter,
    PaginatedLogs
)
from services.log_service import LogService
from auth.auth_service import get_current_user
from config.roles import Permission
import logging
from pathlib import Path

router = APIRouter()
logger = logging.getLogger(__name__)
log_service = LogService()

@router.get("/", response_model=PaginatedLogs)
async def get_logs(
    level: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, gt=0),
    limit: int = Query(100, gt=0, le=1000),
    current_user = Depends(get_current_user)
):
    try:
        log_filter = LogFilter(
            level=level,
            start_date=start_date,
            end_date=end_date,
            search=search
        )
        return await log_service.get_logs(log_filter, page, limit)
    except Exception as e:
        logger.error(f"Failed to get logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve logs")

@router.get("/summary", response_model=LogSummary)
async def get_log_summary(current_user = Depends(get_current_user)):
    try:
        return await log_service.get_summary()
    except Exception as e:
        logger.error(f"Failed to get log summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get log summary")

@router.get("/download/{filename}")
async def download_log(
    filename: str,
    current_user = Depends(get_current_user)
):
    try:
        file_content = await log_service.get_log_file(filename)
        return Response(
            content=file_content,
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to download log: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download log file")

@router.delete("/cleanup")
async def cleanup_logs(
    days_to_keep: int = Query(30, gt=0),
    current_user = Depends(get_current_user)
):
    try:
        deleted_count = await log_service.cleanup_old_logs(days_to_keep)
        return {
            "message": "Logs cleaned up successfully",
            "deleted_count": deleted_count
        }
    except Exception as e:
        logger.error(f"Failed to cleanup logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cleanup logs") 