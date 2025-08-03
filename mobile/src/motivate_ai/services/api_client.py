"""
API Client for Motivate.AI Backend Communication

This service handles all HTTP communication with the Motivate.AI backend,
including project and task CRUD operations, error handling, and offline support.
"""

import asyncio
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin
import httpx

from ..models.simple_models import Project, ProjectCreate, ProjectUpdate, Task, TaskCreate, TaskUpdate
from .. import DEFAULT_API_URL, API_TIMEOUT


class APIError(Exception):
    """Custom exception for API-related errors"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class APIClient:
    """HTTP client for Motivate.AI backend API"""
    
    def __init__(self, base_url: str = DEFAULT_API_URL, timeout: int = API_TIMEOUT):
        """Initialize API client
        
        Args:
            base_url: Backend API base URL
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (relative to base_url)
            **kwargs: Additional request parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            APIError: If request fails
        """
        try:
            response = await self.client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            
            # Handle empty responses (e.g., DELETE operations)
            if response.status_code == 204 or not response.content:
                return {}
                
            return response.json()
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            raise APIError(error_msg, e.response.status_code)
        except httpx.ConnectError:
            raise APIError("Could not connect to backend server")
        except httpx.TimeoutException:
            raise APIError("Request timed out")
        except Exception as e:
            raise APIError(f"Unexpected error: {str(e)}")
    
    # Health check
    async def health_check(self) -> bool:
        """Check if backend is accessible
        
        Returns:
            True if backend is healthy, False otherwise
        """
        try:
            # Health endpoint is at root level, not under /api/v1
            health_url = self.base_url.replace('/api/v1', '') + '/health'
            print(f"🔍 DEBUG: Trying to connect to: {health_url}")
            print(f"🔍 DEBUG: Base URL was: {self.base_url}")
            
            # Make direct request to health endpoint
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(health_url)
                print(f"🔍 DEBUG: Response status: {response.status_code}")
                response.raise_for_status()
                print("✅ DEBUG: Health check successful!")
                return True
        except Exception as e:
            print(f"❌ DEBUG: Health check failed: {str(e)}")
            print(f"❌ DEBUG: Exception type: {type(e).__name__}")
            return False
    
    # Project operations
    async def get_projects(self) -> List[Project]:
        """Get all projects
        
        Returns:
            List of Project objects
            
        Raises:
            APIError: If request fails
        """
        try:
            data = await self._request("GET", "/projects")
            return [Project(**project) for project in data]
        except Exception as e:
            raise APIError(f"Invalid project data from server: {e}")
    
    async def get_project(self, project_id: int) -> Project:
        """Get a specific project
        
        Args:
            project_id: Project ID
            
        Returns:
            Project object
            
        Raises:
            APIError: If request fails or project not found
        """
        try:
            data = await self._request("GET", f"/projects/{project_id}")
            return Project(**data)
        except Exception as e:
            raise APIError(f"Invalid project data from server: {e}")
    
    async def create_project(self, project: ProjectCreate) -> Project:
        """Create a new project
        
        Args:
            project: Project creation data
            
        Returns:
            Created Project object
            
        Raises:
            APIError: If creation fails
        """
        try:
            data = await self._request("POST", "/projects", json=project.to_dict())
            return Project(**data)
        except Exception as e:
            raise APIError(f"Invalid project data from server: {e}")
    
    async def update_project(self, project_id: int, project: ProjectUpdate) -> Project:
        """Update an existing project
        
        Args:
            project_id: Project ID
            project: Project update data
            
        Returns:
            Updated Project object
            
        Raises:
            APIError: If update fails
        """
        try:
            data = await self._request("PUT", f"/projects/{project_id}", 
                                     json=project.to_dict())
            return Project(**data)
        except Exception as e:
            raise APIError(f"Invalid project data from server: {e}")
    
    async def delete_project(self, project_id: int) -> bool:
        """Delete a project
        
        Args:
            project_id: Project ID
            
        Returns:
            True if successful
            
        Raises:
            APIError: If deletion fails
        """
        await self._request("DELETE", f"/projects/{project_id}")
        return True
    
    # Task operations
    async def get_tasks(self, project_id: Optional[int] = None) -> List[Task]:
        """Get tasks, optionally filtered by project
        
        Args:
            project_id: Optional project ID to filter by
            
        Returns:
            List of Task objects
            
        Raises:
            APIError: If request fails
        """
        try:
            endpoint = "/tasks"
            params = {}
            if project_id is not None:
                params["project_id"] = project_id
                
            data = await self._request("GET", endpoint, params=params)
            return [Task(**task) for task in data]
        except Exception as e:
            raise APIError(f"Invalid task data from server: {e}")
    
    async def get_task(self, task_id: int) -> Task:
        """Get a specific task
        
        Args:
            task_id: Task ID
            
        Returns:
            Task object
            
        Raises:
            APIError: If request fails or task not found
        """
        try:
            data = await self._request("GET", f"/tasks/{task_id}")
            return Task(**data)
        except Exception as e:
            raise APIError(f"Invalid task data from server: {e}")
    
    async def create_task(self, task: TaskCreate) -> Task:
        """Create a new task
        
        Args:
            task: Task creation data
            
        Returns:
            Created Task object
            
        Raises:
            APIError: If creation fails
        """
        try:
            data = await self._request("POST", "/tasks", json=task.to_dict())
            return Task(**data)
        except Exception as e:
            raise APIError(f"Invalid task data from server: {e}")
    
    async def update_task(self, task_id: int, task: TaskUpdate) -> Task:
        """Update an existing task
        
        Args:
            task_id: Task ID
            task: Task update data
            
        Returns:
            Updated Task object
            
        Raises:
            APIError: If update fails
        """
        try:
            data = await self._request("PUT", f"/tasks/{task_id}", 
                                     json=task.to_dict())
            return Task(**data)
        except Exception as e:
            raise APIError(f"Invalid task data from server: {e}")
    
    async def delete_task(self, task_id: int) -> bool:
        """Delete a task
        
        Args:
            task_id: Task ID
            
        Returns:
            True if successful
            
        Raises:
            APIError: If deletion fails
        """
        await self._request("DELETE", f"/tasks/{task_id}")
        return True
    
    async def toggle_task_completion(self, task_id: int) -> Task:
        """Toggle task completion status
        
        Args:
            task_id: Task ID
            
        Returns:
            Updated Task object
            
        Raises:
            APIError: If update fails
        """
        # First get current task to determine new status
        current_task = await self.get_task(task_id)
        new_status = "completed" if not current_task.is_completed else "pending"
        new_is_completed = not current_task.is_completed
        
        update_data = TaskUpdate(
            status=new_status,
            is_completed=new_is_completed
        )
        
        return await self.update_task(task_id, update_data)