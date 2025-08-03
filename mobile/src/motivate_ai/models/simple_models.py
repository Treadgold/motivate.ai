"""
Simplified data models for Motivate.AI Mobile Application

These models use plain Python classes instead of Pydantic to avoid
compilation issues on Android while maintaining type safety.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal

# Type definitions
TaskStatus = Literal["pending", "in_progress", "completed", "cancelled"]
TaskPriority = Literal["low", "normal", "high", "urgent"]


class BaseModel:
    """Base model with dictionary conversion utilities"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, BaseModel):
                result[key] = value.to_dict()
            elif isinstance(value, list) and value and isinstance(value[0], BaseModel):
                result[key] = [item.to_dict() for item in value]
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create model from dictionary"""
        instance = cls()
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance


class Project(BaseModel):
    """Project model"""
    
    def __init__(self, **kwargs):
        self.id: int = kwargs.get('id', 0)
        self.title: str = kwargs.get('title', '')
        self.description: Optional[str] = kwargs.get('description')
        self.color: Optional[str] = kwargs.get('color')
        self.is_active: bool = kwargs.get('is_active', True)
        self.created_at: datetime = self._parse_datetime(kwargs.get('created_at'))
        self.updated_at: datetime = self._parse_datetime(kwargs.get('updated_at'))
        
        # Task statistics
        self.task_count: int = kwargs.get('task_count', 0)
        self.completed_tasks: int = kwargs.get('completed_tasks', 0)
        self.pending_tasks: int = kwargs.get('pending_tasks', 0)
        self.in_progress_tasks: int = kwargs.get('in_progress_tasks', 0)
        self.completion_percentage: float = kwargs.get('completion_percentage', 0.0)
    
    def _parse_datetime(self, value) -> datetime:
        """Parse datetime from various formats"""
        if isinstance(value, datetime):
            return value
        elif isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except:
                return datetime.now()
        else:
            return datetime.now()
    
    @property
    def status_icon(self) -> str:
        """Get appropriate status icon based on completion"""
        if self.task_count == 0:
            return "📝"  # Empty project
        elif self.completion_percentage == 100:
            return "✅"  # Completed project
        elif self.completion_percentage > 0:
            return "🔄"  # In progress
        else:
            return "📋"  # Not started

    @property
    def status_text(self) -> str:
        """Get human-readable status text"""
        if self.task_count == 0:
            return "No tasks yet"
        elif self.completion_percentage == 100:
            return "Completed"
        elif self.in_progress_tasks > 0:
            return f"{self.completed_tasks}/{self.task_count} completed • {self.in_progress_tasks} in progress"
        else:
            return f"{self.completed_tasks}/{self.task_count} completed"


class Task(BaseModel):
    """Task model"""
    
    def __init__(self, **kwargs):
        self.id: int = kwargs.get('id', 0)
        self.title: str = kwargs.get('title', '')
        self.description: Optional[str] = kwargs.get('description')
        self.project_id: Optional[int] = kwargs.get('project_id')
        self.estimated_minutes: int = kwargs.get('estimated_minutes', 15)
        self.priority: TaskPriority = kwargs.get('priority', 'normal')
        self.status: TaskStatus = kwargs.get('status', 'pending')
        self.is_completed: bool = kwargs.get('is_completed', False)
        self.created_at: datetime = self._parse_datetime(kwargs.get('created_at'))
        self.updated_at: datetime = self._parse_datetime(kwargs.get('updated_at'))
    
    def _parse_datetime(self, value) -> datetime:
        """Parse datetime from various formats"""
        if isinstance(value, datetime):
            return value
        elif isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except:
                return datetime.now()
        else:
            return datetime.now()

    @property
    def priority_icon(self) -> str:
        """Get priority icon"""
        priority_icons = {
            "low": "🔵",
            "normal": "⚪", 
            "high": "🟡",
            "urgent": "🔴"
        }
        return priority_icons.get(self.priority, "⚪")

    @property
    def status_icon(self) -> str:
        """Get status icon"""
        status_icons = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "cancelled": "❌"
        }
        return status_icons.get(self.status, "⏳")

    @property
    def display_time(self) -> str:
        """Get formatted time display"""
        if self.estimated_minutes < 60:
            return f"{self.estimated_minutes}m"
        else:
            hours = self.estimated_minutes // 60
            minutes = self.estimated_minutes % 60
            if minutes > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{hours}h"

    def toggle_completion(self) -> "Task":
        """Toggle task completion status"""
        new_task = Task(**self.to_dict())
        if new_task.is_completed:
            new_task.is_completed = False
            new_task.status = "pending"
        else:
            new_task.is_completed = True
            new_task.status = "completed"
        return new_task


# Create and Update classes for API requests
class ProjectCreate(BaseModel):
    """Model for creating a new project"""
    
    def __init__(self, title: str, description: Optional[str] = None, 
                 color: Optional[str] = None, is_active: bool = True):
        self.title = title
        self.description = description
        self.color = color
        self.is_active = is_active


class TaskCreate(BaseModel):
    """Model for creating a new task"""
    
    def __init__(self, title: str, description: Optional[str] = None,
                 project_id: Optional[int] = None, estimated_minutes: int = 15,
                 priority: TaskPriority = "normal", status: TaskStatus = "pending"):
        self.title = title
        self.description = description
        self.project_id = project_id
        self.estimated_minutes = estimated_minutes
        self.priority = priority
        self.status = status
        self.is_completed = status == "completed"


class ProjectUpdate(BaseModel):
    """Model for updating an existing project"""
    
    def __init__(self, **kwargs):
        # Only set attributes that are provided
        for key, value in kwargs.items():
            if hasattr(self, key) or key in ['title', 'description', 'color', 'is_active']:
                setattr(self, key, value)


class TaskUpdate(BaseModel):
    """Model for updating an existing task"""
    
    def __init__(self, **kwargs):
        # Only set attributes that are provided
        for key, value in kwargs.items():
            if hasattr(self, key) or key in ['title', 'description', 'project_id', 
                                           'estimated_minutes', 'priority', 'status', 'is_completed']:
                setattr(self, key, value)