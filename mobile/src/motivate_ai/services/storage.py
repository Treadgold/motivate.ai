"""
Local Storage Service for Motivate.AI Mobile Application

This service handles local data persistence and caching,
providing offline support and data synchronization capabilities.
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.simple_models import Project, Task
from .. import STORAGE_VERSION, MAX_OFFLINE_TASKS


class StorageService:
    """Local storage service for offline data persistence"""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize storage service
        
        Args:
            storage_dir: Custom storage directory (defaults to user data dir)
        """
        if storage_dir is None:
            # Use platform-appropriate user data directory
            if os.name == 'nt':  # Windows
                base_dir = Path(os.environ.get('APPDATA', Path.home()))
            else:  # macOS, Linux
                base_dir = Path.home() / '.local' / 'share'
            
            storage_dir = base_dir / 'motivate_ai'
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.projects_file = self.storage_dir / 'projects.json'
        self.tasks_file = self.storage_dir / 'tasks.json'
        self.metadata_file = self.storage_dir / 'metadata.json'
        
        # Initialize storage if needed
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize storage files with default data"""
        metadata = self._load_metadata()
        
        # Check if we need to initialize or migrate
        if metadata.get('version', 0) < STORAGE_VERSION:
            self._create_default_files()
            self._save_metadata({
                'version': STORAGE_VERSION,
                'created_at': datetime.now().isoformat(),
                'last_sync': None
            })
    
    def _create_default_files(self):
        """Create default storage files"""
        if not self.projects_file.exists():
            self._save_json(self.projects_file, [])
        
        if not self.tasks_file.exists():
            self._save_json(self.tasks_file, [])
    
    def _load_json(self, file_path: Path) -> Any:
        """Load JSON data from file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON data or empty list if file doesn't exist
        """
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except (json.JSONDecodeError, IOError):
            return []
    
    def _save_json(self, file_path: Path, data: Any):
        """Save data to JSON file
        
        Args:
            file_path: Path to JSON file
            data: Data to save
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except IOError as e:
            print(f"Failed to save {file_path}: {e}")
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata"""
        return self._load_json(self.metadata_file) or {}
    
    def _save_metadata(self, metadata: Dict[str, Any]):
        """Save metadata"""
        self._save_json(self.metadata_file, metadata)
    
    # Project operations
    def save_projects(self, projects: List[Project]):
        """Save projects to local storage
        
        Args:
            projects: List of Project objects
        """
        project_data = [project.to_dict() for project in projects]
        self._save_json(self.projects_file, project_data)
        
        # Update sync timestamp
        metadata = self._load_metadata()
        metadata['last_projects_sync'] = datetime.now().isoformat()
        self._save_metadata(metadata)
    
    def load_projects(self) -> List[Project]:
        """Load projects from local storage
        
        Returns:
            List of Project objects
        """
        try:
            project_data = self._load_json(self.projects_file)
            return [Project(**project) for project in project_data]
        except Exception as e:
            print(f"Failed to load projects: {e}")
            return []
    
    def save_project(self, project: Project):
        """Save or update a single project
        
        Args:
            project: Project object to save
        """
        projects = self.load_projects()
        
        # Find and update existing project or add new one
        updated = False
        for i, existing_project in enumerate(projects):
            if existing_project.id == project.id:
                projects[i] = project
                updated = True
                break
        
        if not updated:
            projects.append(project)
        
        self.save_projects(projects)
    
    def delete_project(self, project_id: int):
        """Delete a project from local storage
        
        Args:
            project_id: Project ID to delete
        """
        projects = self.load_projects()
        projects = [p for p in projects if p.id != project_id]
        self.save_projects(projects)
        
        # Also delete associated tasks
        tasks = self.load_tasks()
        tasks = [t for t in tasks if t.project_id != project_id]
        self.save_tasks(tasks)
    
    # Task operations  
    def save_tasks(self, tasks: List[Task]):
        """Save tasks to local storage
        
        Args:
            tasks: List of Task objects
        """
        # Limit storage to prevent excessive disk usage
        if len(tasks) > MAX_OFFLINE_TASKS:
            # Keep most recent tasks
            tasks = sorted(tasks, key=lambda t: t.updated_at, reverse=True)[:MAX_OFFLINE_TASKS]
        
        task_data = [task.to_dict() for task in tasks]
        self._save_json(self.tasks_file, task_data)
        
        # Update sync timestamp
        metadata = self._load_metadata()
        metadata['last_tasks_sync'] = datetime.now().isoformat()
        self._save_metadata(metadata)
    
    def load_tasks(self, project_id: Optional[int] = None) -> List[Task]:
        """Load tasks from local storage
        
        Args:
            project_id: Optional project ID to filter by
            
        Returns:
            List of Task objects
        """
        try:
            task_data = self._load_json(self.tasks_file)
            tasks = [Task(**task) for task in task_data]
            
            # Filter by project if specified
            if project_id is not None:
                tasks = [task for task in tasks if task.project_id == project_id]
            
            return tasks
        except Exception as e:
            print(f"Failed to load tasks: {e}")
            return []
    
    def save_task(self, task: Task):
        """Save or update a single task
        
        Args:
            task: Task object to save
        """
        tasks = self.load_tasks()
        
        # Find and update existing task or add new one
        updated = False
        for i, existing_task in enumerate(tasks):
            if existing_task.id == task.id:
                tasks[i] = task
                updated = True
                break
        
        if not updated:
            tasks.append(task)
        
        self.save_tasks(tasks)
    
    def delete_task(self, task_id: int):
        """Delete a task from local storage
        
        Args:
            task_id: Task ID to delete
        """
        tasks = self.load_tasks()
        tasks = [t for t in tasks if t.id != task_id]
        self.save_tasks(tasks)
    
    # Utility methods
    def clear_all_data(self):
        """Clear all local storage data"""
        self._save_json(self.projects_file, [])
        self._save_json(self.tasks_file, [])
        
        metadata = self._load_metadata()
        metadata.update({
            'last_projects_sync': None,
            'last_tasks_sync': None,
            'cleared_at': datetime.now().isoformat()
        })
        self._save_metadata(metadata)
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get information about local storage
        
        Returns:
            Dictionary with storage statistics
        """
        projects = self.load_projects()
        tasks = self.load_tasks()
        metadata = self._load_metadata()
        
        return {
            'storage_version': metadata.get('version', 0),
            'project_count': len(projects),
            'task_count': len(tasks),
            'last_projects_sync': metadata.get('last_projects_sync'),
            'last_tasks_sync': metadata.get('last_tasks_sync'),
            'storage_size_mb': self._get_storage_size_mb()
        }
    
    def _get_storage_size_mb(self) -> float:
        """Get total storage size in MB"""
        total_size = 0
        for file_path in [self.projects_file, self.tasks_file, self.metadata_file]:
            if file_path.exists():
                total_size += file_path.stat().st_size
        
        return round(total_size / (1024 * 1024), 2)