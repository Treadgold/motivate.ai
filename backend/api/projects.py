from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models.project import Project
from models.task import Task

router = APIRouter(tags=["projects"])

# Pydantic schemas
class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    estimated_time: Optional[int] = None
    tags: Optional[str] = None
    location: Optional[str] = None
    next_action: Optional[str] = None

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    estimated_time: Optional[int] = None
    actual_time: Optional[int] = None
    tags: Optional[str] = None
    location: Optional[str] = None
    next_action: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    estimated_time: Optional[int] = None
    actual_time: Optional[int] = None
    tags: Optional[str] = None
    location: Optional[str] = None
    next_action: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_worked_on: Optional[datetime] = None
    
    # Task statistics
    task_count: int = 0
    completed_tasks: int = 0
    pending_tasks: int = 0
    in_progress_tasks: int = 0
    completion_percentage: float = 0.0

    class Config:
        from_attributes = True

# Routes
@router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Get projects with task statistics
    projects = db.query(Project).filter(Project.is_active == True).offset(skip).limit(limit).all()
    
    # Calculate task statistics for each project
    result = []
    for project in projects:
        # Get task counts by status using simpler approach
        total_tasks = db.query(func.count(Task.id)).filter(Task.project_id == project.id).scalar() or 0
        completed_tasks = db.query(func.count(Task.id)).filter(
            Task.project_id == project.id, Task.is_completed == True
        ).scalar() or 0
        pending_tasks = db.query(func.count(Task.id)).filter(
            Task.project_id == project.id, Task.status == 'pending'
        ).scalar() or 0
        in_progress_tasks = db.query(func.count(Task.id)).filter(
            Task.project_id == project.id, Task.status == 'in_progress'
        ).scalar() or 0
        
        # Calculate completion percentage
        completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
        
        # Create project response with statistics
        project_dict = {
            **{c.name: getattr(project, c.name) for c in project.__table__.columns},
            'task_count': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress_tasks,
            'completion_percentage': round(completion_percentage, 1)
        }
        
        result.append(ProjectResponse(**project_dict))
    
    return result

@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get task statistics for this project using simpler approach
    total_tasks = db.query(func.count(Task.id)).filter(Task.project_id == project.id).scalar() or 0
    completed_tasks = db.query(func.count(Task.id)).filter(
        Task.project_id == project.id, Task.is_completed == True
    ).scalar() or 0
    pending_tasks = db.query(func.count(Task.id)).filter(
        Task.project_id == project.id, Task.status == 'pending'
    ).scalar() or 0
    in_progress_tasks = db.query(func.count(Task.id)).filter(
        Task.project_id == project.id, Task.status == 'in_progress'
    ).scalar() or 0
    
    completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
    
    # Create project response with statistics
    project_dict = {
        **{c.name: getattr(project, c.name) for c in project.__table__.columns},
        'task_count': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completion_percentage': round(completion_percentage, 1)
    }
    
    return ProjectResponse(**project_dict)

@router.post("/projects", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Add task statistics (new project has no tasks)
    project_dict = {
        **{c.name: getattr(db_project, c.name) for c in db_project.__table__.columns},
        'task_count': 0,
        'completed_tasks': 0,
        'pending_tasks': 0,
        'in_progress_tasks': 0,
        'completion_percentage': 0.0
    }
    
    return ProjectResponse(**project_dict)

@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    
    # Get task statistics for updated project
    total_tasks = db.query(func.count(Task.id)).filter(Task.project_id == db_project.id).scalar() or 0
    completed_tasks = db.query(func.count(Task.id)).filter(
        Task.project_id == db_project.id, Task.is_completed == True
    ).scalar() or 0
    pending_tasks = db.query(func.count(Task.id)).filter(
        Task.project_id == db_project.id, Task.status == 'pending'
    ).scalar() or 0
    in_progress_tasks = db.query(func.count(Task.id)).filter(
        Task.project_id == db_project.id, Task.status == 'in_progress'
    ).scalar() or 0
    
    completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
    
    # Create project response with statistics
    project_dict = {
        **{c.name: getattr(db_project, c.name) for c in db_project.__table__.columns},
        'task_count': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completion_percentage': round(completion_percentage, 1)
    }
    
    return ProjectResponse(**project_dict)

@router.delete("/projects/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_project.is_active = False
    db.commit()
    return {"message": "Project archived successfully"} 