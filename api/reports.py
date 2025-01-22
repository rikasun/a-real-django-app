from fastapi import APIRouter, HTTPException, Depends, Query, Response, BackgroundTasks
from typing import List, Optional
from datetime import datetime, timedelta
from models.reports import (
    PerformanceReport,
    CleanupStats,
    ReportSchedule,
    ReportFormat,
    ReportType
)
from services.report_service import ReportService
from services.email_service import EmailService
from auth.auth_service import get_current_user
import logging
import pandas as pd
import io

router = APIRouter()
logger = logging.getLogger(__name__)
report_service = ReportService()
email_service = EmailService()

@router.get("/performance", response_model=PerformanceReport)
async def get_performance_report(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    format: ReportFormat = ReportFormat.JSON,
    current_user = Depends(get_current_user)
):
    try:
        report_data = await report_service.generate_performance_report(
            start_date,
            end_date
        )

        if format == ReportFormat.EXCEL:
            excel_data = await report_service.generate_excel_report(report_data)
            return Response(
                content=excel_data,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=performance-report.xlsx"}
            )
        elif format == ReportFormat.PDF:
            pdf_data = await report_service.generate_pdf_report(report_data)
            return Response(
                content=pdf_data,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=performance-report.pdf"}
            )

        return report_data
    except Exception as e:
        logger.error(f"Failed to generate performance report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate report")

@router.get("/cleanup-stats", response_model=CleanupStats)
async def get_cleanup_statistics(
    period: str = "30d",
    current_user = Depends(get_current_user)
):
    try:
        return await report_service.get_cleanup_stats(period)
    except Exception as e:
        logger.error(f"Failed to get cleanup stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get cleanup statistics")

@router.post("/schedule")
async def schedule_report(
    report_schedule: ReportSchedule,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    try:
        job_id = await report_service.schedule_report(
            report_schedule,
            background_tasks
        )
        return {"message": "Report scheduled successfully", "job_id": job_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to schedule report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to schedule report") 