from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models.activity import Activity

router = APIRouter(tags=["activity"])

class ActivityCreate(BaseModel):
    project_id: int = None
    task_id: int = None
    activity_type: str  # work_session, note, break, completion
    description: str = None
    duration_minutes: int = None
    mood: str = None
    productivity_rating: int = None
    notes: str = None
    source: str = "manual"

class ActivityResponse(BaseModel):
    id: int
    project_id: int = None
    task_id: int = None
    activity_type: str
    description: str = None
    duration_minutes: int = None
    mood: str = None
    productivity_rating: int = None
    notes: str = None
    source: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/activity", response_model=List[ActivityResponse])
async def get_activities(
    project_id: int = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get recent activities, optionally filtered by project"""
    query = db.query(Activity).order_by(Activity.created_at.desc())
    
    if project_id:
        query = query.filter(Activity.project_id == project_id)
    
    activities = query.limit(limit).all()
    return activities

@router.post("/activity", response_model=ActivityResponse)
async def log_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    """Log a new activity"""
    db_activity = Activity(**activity.dict())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@router.post("/activity/idle-detected")
async def log_idle_detection(
    duration_minutes: int,
    last_active_app: str = None,
    db: Session = Depends(get_db)
):
    """Log when the desktop app detects user has been idle"""
    activity = Activity(
        activity_type="idle_detected",
        description=f"User idle for {duration_minutes} minutes",
        duration_minutes=duration_minutes,
        notes=f"Last active app: {last_active_app}" if last_active_app else None,
        source="desktop_app"
    )
    
    db.add(activity)
    db.commit()
    
    return {"message": "Idle time logged", "duration": duration_minutes}

@router.post("/activity/work-session")
async def start_work_session(
    project_id: int,
    task_id: int = None,
    mood: str = None,
    db: Session = Depends(get_db)
):
    """Start a work session"""
    activity = Activity(
        project_id=project_id,
        task_id=task_id,
        activity_type="work_session_start",
        mood=mood,
        source="manual"
    )
    
    db.add(activity)
    db.commit()
    
    return {"message": "Work session started", "activity_id": activity.id} 