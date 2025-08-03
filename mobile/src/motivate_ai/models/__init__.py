"""
Data models for Motivate.AI Mobile Application

This module contains simplified Python data models that represent the core 
data structures used throughout the application, optimized for mobile deployment.
"""

from .simple_models import Project, ProjectCreate, ProjectUpdate, Task, TaskCreate, TaskUpdate

__all__ = [
    "Project",
    "ProjectCreate", 
    "ProjectUpdate",
    "Task",
    "TaskCreate",
    "TaskUpdate",
]