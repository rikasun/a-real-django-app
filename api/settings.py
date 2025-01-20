from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict
from datetime import datetime
from models.settings import (
    SchedulerSettings,
    SettingsHistory,
    EmailConfig,
    BackupConfig,
    NotificationSettings
)
from services.settings import SettingsService
from auth.auth_service import get_current_user
from config.roles import Permission
import logging
import json
import shutil
from pathlib import Path

router = APIRouter()
logger = logging.getLogger(__name__)
settings_service = SettingsService()

@router.get("/current", response_model=SchedulerSettings)
async def get_current_settings(current_user = Depends(get_current_user)):
    try:
        return await settings_service.get_settings()
    except Exception as e:
        logger.error(f"Failed to get settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load settings")

@router.put("/update", response_model=SchedulerSettings)
async def update_settings(
    settings: SchedulerSettings,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    try:
        # Validate and save new settings
        await settings_service.validate_settings(settings)
        await settings_service.backup_current_settings()
        updated_settings = await settings_service.update_settings(settings)
        
        # Apply new settings in background
        background_tasks.add_task(settings_service.apply_settings, updated_settings)
        
        logger.info(f"Settings updated by user: {current_user.username}")
        return updated_settings
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update settings")

@router.get("/history", response_model=List[SettingsHistory])
async def get_settings_history(current_user = Depends(get_current_user)):
    try:
        return await settings_service.get_settings_history()
    except Exception as e:
        logger.error(f"Failed to get settings history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load settings history")

@router.post("/restore/{timestamp}")
async def restore_settings(
    timestamp: str,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    try:
        restored_settings = await settings_service.restore_settings(timestamp)
        background_tasks.add_task(settings_service.apply_settings, restored_settings)
        return {"message": "Settings restored successfully"}
    except Exception as e:
        logger.error(f"Failed to restore settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to restore settings") 