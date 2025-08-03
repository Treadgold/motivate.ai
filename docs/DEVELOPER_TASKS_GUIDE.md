# Developer Tasks Guide

This guide provides step-by-step instructions for common development tasks in Motivate.AI.

## Table of Contents

1. [Setting Up Development Environment](#setting-up-development-environment)
2. [Adding New API Endpoints](#adding-new-api-endpoints)
3. [Adding New UI Components](#adding-new-ui-components)
4. [Implementing New Features](#implementing-new-features)
5. [Database Migrations](#database-migrations)
6. [Testing Strategies](#testing-strategies)
7. [Debugging Common Issues](#debugging-common-issues)
8. [Performance Optimization](#performance-optimization)

---

## Setting Up Development Environment

### Initial Setup
```bash
# 1. Clone the repository
git clone <repository-url>
cd motivate.ai

# 2. Backend setup
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 3. Desktop setup
cd ../desktop
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 4. Create environment files
copy shared\config.env.example backend\.env
copy shared\config.env.example desktop\.env
```

### Environment Configuration
**Backend (.env)**:
```bash
API_PORT=8010
DATABASE_URL=sqlite:///./motivate_ai.db
DEBUG=true
LOG_LEVEL=DEBUG
```

**Desktop (.env)**:
```bash
API_BASE_URL=http://localhost:8010/api/v1
IDLE_THRESHOLD_MINUTES=10
DEBUG=true
```

### Running the Application
```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start desktop
cd desktop
python main.py
```

---

## Adding New API Endpoints

### Step 1: Create the Data Model
```python
# backend/models/new_model.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from database import Base

class NewModel(Base):
    __tablename__ = "new_models"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

### Step 2: Create Pydantic Schemas
```python
# backend/api/new_endpoint.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models.new_model import NewModel

router = APIRouter(tags=["new_feature"])

class NewModelCreate(BaseModel):
    title: str
    description: Optional[str] = None

class NewModelUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class NewModelResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

### Step 3: Implement CRUD Operations
```python
# Continue in backend/api/new_endpoint.py

@router.get("/new-models", response_model=List[NewModelResponse])
async def get_new_models(db: Session = Depends(get_db)):
    """Get all active new models"""
    return db.query(NewModel).filter(NewModel.is_active == True).all()

@router.get("/new-models/{model_id}", response_model=NewModelResponse)
async def get_new_model(model_id: int, db: Session = Depends(get_db)):
    """Get a specific new model by ID"""
    db_model = db.query(NewModel).filter(NewModel.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    return db_model

@router.post("/new-models", response_model=NewModelResponse)
async def create_new_model(model: NewModelCreate, db: Session = Depends(get_db)):
    """Create a new model"""
    db_model = NewModel(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

@router.put("/new-models/{model_id}", response_model=NewModelResponse)
async def update_new_model(
    model_id: int, 
    model: NewModelUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing model"""
    db_model = db.query(NewModel).filter(NewModel.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    update_data = model.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_model, field, value)
    
    db.commit()
    db.refresh(db_model)
    return db_model

@router.delete("/new-models/{model_id}")
async def delete_new_model(model_id: int, db: Session = Depends(get_db)):
    """Soft delete a model"""
    db_model = db.query(NewModel).filter(NewModel.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    db_model.is_active = False
    db.commit()
    return {"message": "Model deleted successfully"}
```

### Step 4: Register the Router
```python
# backend/main.py
from api.new_endpoint import router as new_endpoint_router

app.include_router(new_endpoint_router, prefix="/api/v1")
```

### Step 5: Write Tests
```python
# backend/tests/test_new_endpoint.py
import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from main import app
from database import get_db, Base, engine

client = TestClient(app)

def test_create_new_model():
    """Test creating a new model"""
    model_data = {
        "title": "Test Model",
        "description": "Test description"
    }
    
    response = client.post("/api/v1/new-models", json=model_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["title"] == model_data["title"]
    assert data["description"] == model_data["description"]
    assert "id" in data

def test_get_new_models():
    """Test getting all models"""
    response = client.get("/api/v1/new-models")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

---

## Adding New UI Components

### Step 1: Create the UI Component
```python
# desktop/ui/new_component.py
import customtkinter as ctk
import tkinter as tk
from typing import Optional, Callable
import requests
import os

class NewComponentDialog:
    def __init__(self, parent, on_success: Optional[Callable] = None):
        self.parent = parent
        self.on_success = on_success
        self.api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8010/api/v1")
        
        # Create modal window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("New Component")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Make modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center on parent
        self.center_on_parent()
        
        # Create UI
        self.create_widgets()
        
    def center_on_parent(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """Create the dialog widgets"""
        # Main container
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Create New Component",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Form fields
        self.create_form_fields(main_frame)
        
        # Buttons
        self.create_buttons(main_frame)
    
    def create_form_fields(self, parent):
        """Create form input fields"""
        # Title field
        ctk.CTkLabel(parent, text="Title*").pack(anchor="w", pady=(0, 5))
        self.title_entry = ctk.CTkEntry(parent, width=400, height=35)
        self.title_entry.pack(pady=(0, 15))
        
        # Description field
        ctk.CTkLabel(parent, text="Description").pack(anchor="w", pady=(0, 5))
        self.desc_text = ctk.CTkTextbox(parent, width=400, height=100)
        self.desc_text.pack(pady=(0, 15))
        
        # Status message
        self.status_label = ctk.CTkLabel(parent, text="", text_color="red")
        self.status_label.pack(pady=(0, 10))
    
    def create_buttons(self, parent):
        """Create action buttons"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=100,
            command=self.cancel,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        # Create button
        create_btn = ctk.CTkButton(
            button_frame,
            text="Create",
            width=100,
            command=self.create_component
        )
        create_btn.pack(side="right")
    
    def create_component(self):
        """Create the new component"""
        title = self.title_entry.get().strip()
        description = self.desc_text.get("0.0", tk.END).strip()
        
        # Validation
        if not title:
            self.status_label.configure(text="Title is required", text_color="red")
            return
        
        # Prepare data
        component_data = {
            "title": title,
            "description": description if description else None
        }
        
        try:
            # API call
            response = requests.post(
                f"{self.api_base_url}/new-models",
                json=component_data,
                timeout=5
            )
            
            if response.status_code == 201:
                self.status_label.configure(
                    text="Component created successfully!", 
                    text_color="green"
                )
                
                # Call success callback
                if self.on_success:
                    self.on_success(response.json())
                
                # Close dialog after delay
                self.dialog.after(1500, self.dialog.destroy)
            else:
                self.status_label.configure(
                    text="Failed to create component", 
                    text_color="red"
                )
                
        except requests.exceptions.RequestException as e:
            self.status_label.configure(
                text="Could not connect to server", 
                text_color="red"
            )
    
    def cancel(self):
        """Cancel and close dialog"""
        self.dialog.destroy()
```

### Step 2: Integrate with Main Window
```python
# In desktop/ui/main_window.py

def show_new_component_dialog(self):
    """Show the new component creation dialog"""
    dialog = NewComponentDialog(
        parent=self.root,
        on_success=self.on_component_created
    )

def on_component_created(self, component_data):
    """Handle successful component creation"""
    print(f"Component created: {component_data}")
    # Refresh any relevant lists or UI elements
    self.refresh_components_list()

# Add button to trigger dialog
new_component_btn = ctk.CTkButton(
    self.sidebar,
    text="➕ New Component",
    command=self.show_new_component_dialog
)
new_component_btn.pack(pady=5)
```

---

## Implementing New Features

### Feature: Task Templates

#### Step 1: Backend Implementation
```python
# backend/models/task_template.py
from sqlalchemy import Column, Integer, String, Text, Boolean
from database import Base

class TaskTemplate(Base):
    __tablename__ = "task_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    title_template = Column(String, nullable=False)
    description_template = Column(Text)
    estimated_minutes = Column(Integer, default=15)
    priority = Column(String, default="medium")
    energy_level = Column(String, default="medium")
    is_active = Column(Boolean, default=True)

# backend/api/task_templates.py
# ... implement CRUD operations following the pattern above
```

#### Step 2: Frontend Implementation
```python
# desktop/ui/task_template_selector.py
class TaskTemplateSelector:
    def __init__(self, parent, on_template_selected):
        self.parent = parent
        self.on_template_selected = on_template_selected
        self.create_selector()
    
    def create_selector(self):
        # Create template selection UI
        self.template_frame = ctk.CTkFrame(self.parent)
        
        # Load templates from API
        self.load_templates()
        
        # Create template buttons
        for template in self.templates:
            btn = ctk.CTkButton(
                self.template_frame,
                text=template["name"],
                command=lambda t=template: self.select_template(t)
            )
            btn.pack(pady=2)
    
    def load_templates(self):
        try:
            response = requests.get(f"{self.api_base_url}/task-templates")
            self.templates = response.json() if response.status_code == 200 else []
        except:
            self.templates = []
    
    def select_template(self, template):
        self.on_template_selected(template)
```

#### Step 3: Integration
```python
# In main_window.py, integrate template selector into task creation
def show_task_creation_with_templates(self):
    # Add template selector to task creation dialog
    template_selector = TaskTemplateSelector(
        parent=self.task_form_frame,
        on_template_selected=self.apply_template_to_form
    )
    
def apply_template_to_form(self, template):
    """Fill form with template data"""
    self.title_entry.delete(0, tk.END)
    self.title_entry.insert(0, template["title_template"])
    
    self.desc_entry.delete("0.0", tk.END)
    self.desc_entry.insert("0.0", template["description_template"])
    
    self.time_var.set(str(template["estimated_minutes"]))
    self.priority_var.set(template["priority"].title())
```

---

## Database Migrations

### Creating a Migration
```python
# backend/migrations/add_new_table.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision = '001_add_new_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Create new table"""
    op.create_table(
        'new_table',
        Column('id', Integer, primary_key=True),
        Column('name', String(255), nullable=False),
        Column('is_active', Boolean, default=True),
        Column('created_at', DateTime, nullable=False)
    )
    
    # Add index
    op.create_index('ix_new_table_name', 'new_table', ['name'])

def downgrade():
    """Drop new table"""
    op.drop_index('ix_new_table_name', table_name='new_table')
    op.drop_table('new_table')
```

### Running Migrations
```bash
# Generate migration
cd backend
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## Testing Strategies

### Unit Tests
```python
# backend/tests/test_models.py
def test_create_model():
    """Test model creation"""
    model = NewModel(title="Test", description="Test description")
    assert model.title == "Test"
    assert model.description == "Test description"
    assert model.is_active == True
```

### Integration Tests
```python
# backend/tests/test_api_integration.py
def test_full_workflow():
    """Test complete create -> read -> update -> delete workflow"""
    # Create
    create_response = client.post("/api/v1/new-models", json={
        "title": "Integration Test",
        "description": "Test description"
    })
    assert create_response.status_code == 201
    model_id = create_response.json()["id"]
    
    # Read
    read_response = client.get(f"/api/v1/new-models/{model_id}")
    assert read_response.status_code == 200
    
    # Update
    update_response = client.put(f"/api/v1/new-models/{model_id}", json={
        "title": "Updated Title"
    })
    assert update_response.status_code == 200
    
    # Delete
    delete_response = client.delete(f"/api/v1/new-models/{model_id}")
    assert delete_response.status_code == 200
```

### UI Tests
```python
# desktop/tests/test_ui_components.py
def test_dialog_creation():
    """Test dialog can be created without errors"""
    root = tk.Tk()
    dialog = NewComponentDialog(root)
    assert dialog.dialog is not None
    root.destroy()
```

---

## Debugging Common Issues

### Backend Issues

#### Database Connection Errors
```python
# Check database connection
try:
    db = next(get_db())
    db.execute("SELECT 1")
    print("Database connected successfully")
except Exception as e:
    print(f"Database connection failed: {e}")
```

#### API Endpoint Not Working
```python
# Add logging to endpoint
import logging
logger = logging.getLogger(__name__)

@router.get("/debug-endpoint")
async def debug_endpoint():
    logger.info("Debug endpoint called")
    return {"status": "working"}
```

### Desktop Issues

#### GUI Thread Errors
```python
# ✅ CORRECT: Use queues for cross-thread communication
import queue
import threading

class SafeUIUpdater:
    def __init__(self, root):
        self.root = root
        self.update_queue = queue.Queue()
        self.process_updates()
    
    def process_updates(self):
        """Process UI updates from queue (runs on main thread)"""
        try:
            while True:
                update_func, args = self.update_queue.get_nowait()
                update_func(*args)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_updates)
    
    def queue_update(self, func, *args):
        """Queue an update from background thread"""
        self.update_queue.put((func, args))

# Usage from background thread
def background_task():
    # Do work...
    ui_updater.queue_update(label.configure, text="Update from background")
```

#### API Connection Issues
```python
# Add connection testing utility
def test_api_connection(api_base_url):
    """Test API connectivity with detailed error reporting"""
    try:
        response = requests.get(f"{api_base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API connection successful")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API - is the backend running?")
        return False
    except requests.exceptions.Timeout:
        print("❌ API request timed out")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
```

---

## Performance Optimization

### Backend Optimization

#### Database Query Optimization
```python
# ❌ AVOID: N+1 queries
def get_projects_with_tasks():
    projects = db.query(Project).all()
    for project in projects:
        project.tasks = db.query(Task).filter(Task.project_id == project.id).all()

# ✅ BETTER: Use joins
from sqlalchemy.orm import joinedload

def get_projects_with_tasks():
    return db.query(Project).options(joinedload(Project.tasks)).all()
```

#### Response Caching
```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache expensive operations
@lru_cache(maxsize=100)
def get_project_statistics(project_id: int, cache_key: str):
    """Cache project statistics (cache_key includes timestamp for TTL)"""
    # Expensive calculation here
    return statistics

def get_cached_project_stats(project_id: int):
    # Create cache key with 5-minute TTL
    cache_time = datetime.now().replace(second=0, microsecond=0)
    cache_key = f"{project_id}_{cache_time.strftime('%Y%m%d_%H%M')}"
    return get_project_statistics(project_id, cache_key)
```

### Frontend Optimization

#### Lazy Loading Components
```python
class OptimizedMainWindow:
    def __init__(self):
        self.components = {}
        
    def get_component(self, component_name):
        """Lazy load UI components"""
        if component_name not in self.components:
            if component_name == "project_dialog":
                self.components[component_name] = NewProjectDialog(self.root)
            elif component_name == "task_dialog":
                self.components[component_name] = NewTaskDialog(self.root)
            # ... other components
        
        return self.components[component_name]
```

#### Efficient List Updates
```python
def update_task_list_incremental(self, new_tasks):
    """Only update changed items instead of rebuilding entire list"""
    current_task_ids = {task.get("id") for task in self.current_tasks}
    new_task_ids = {task.get("id") for task in new_tasks}
    
    # Remove deleted tasks
    for task_id in current_task_ids - new_task_ids:
        self.remove_task_from_ui(task_id)
    
    # Add new tasks
    for task in new_tasks:
        if task.get("id") not in current_task_ids:
            self.add_task_to_ui(task)
        elif self.task_needs_update(task):
            self.update_task_in_ui(task)
    
    self.current_tasks = new_tasks
```

---

## Development Best Practices

### Code Style
- Follow PEP 8 for Python code
- Use type hints where possible
- Write docstrings for all public functions
- Keep functions small and focused (< 20 lines when possible)

### Git Workflow
```bash
# Feature development
git checkout -b feature/new-feature
# ... make changes
git add .
git commit -m "feat(api): add new endpoint for feature"
git push origin feature/new-feature
# ... create pull request

# Bug fixes
git checkout -b fix/bug-description
# ... fix bug
git commit -m "fix(ui): resolve dialog positioning issue"
```

### Documentation
- Update API documentation when adding endpoints
- Add code comments for complex logic
- Update user documentation for new features
- Include examples in documentation

---

*This guide covers the most common development scenarios. For more specific cases, refer to the codebase examples or ask the team for guidance.*