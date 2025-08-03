# Troubleshooting Guide

Common issues and solutions for Motivate.AI development and deployment.

## Table of Contents

1. [Development Environment Issues](#development-environment-issues)
2. [Backend API Issues](#backend-api-issues)
3. [Desktop Application Issues](#desktop-application-issues)
4. [Database Issues](#database-issues)
5. [API Integration Issues](#api-integration-issues)
6. [Performance Issues](#performance-issues)
7. [Deployment Issues](#deployment-issues)
8. [Debugging Tools and Techniques](#debugging-tools-and-techniques)

---

## Development Environment Issues

### Python Virtual Environment Problems

#### Issue: `ModuleNotFoundError` despite installing packages
```bash
ModuleNotFoundError: No module named 'fastapi'
```

**Causes & Solutions:**
1. **Not in virtual environment**
   ```bash
   # Activate virtual environment first
   cd backend
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

2. **Wrong Python interpreter**
   ```bash
   # Check which Python you're using
   which python
   python --version
   
   # Should point to venv/bin/python or venv\Scripts\python.exe
   ```

3. **Corrupted virtual environment**
   ```bash
   # Delete and recreate virtual environment
   rmdir /s venv  # Windows
   rm -rf venv    # Linux/Mac
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

#### Issue: `pip install` fails with permission errors
```bash
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solutions:**
1. **Use virtual environment** (recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **User install** (if virtual env not possible)
   ```bash
   pip install --user -r requirements.txt
   ```

### Environment Configuration Issues

#### Issue: Environment variables not loaded
```python
KeyError: 'API_BASE_URL'
```

**Solutions:**
1. **Check .env file exists**
   ```bash
   # Backend
   ls backend/.env
   
   # Desktop
   ls desktop/.env
   ```

2. **Create .env from template**
   ```bash
   copy shared\config.env.example backend\.env
   copy shared\config.env.example desktop\.env
   ```

3. **Verify .env format**
   ```bash
   # .env file should have no spaces around =
   API_BASE_URL=http://localhost:8010/api/v1
   # Not: API_BASE_URL = http://localhost:8010/api/v1
   ```

4. **Check python-dotenv is installed**
   ```bash
   pip list | grep python-dotenv
   # If not found: pip install python-dotenv
   ```

---

## Backend API Issues

### Server Won't Start

#### Issue: Port already in use
```bash
OSError: [Errno 98] Address already in use
```

**Solutions:**
1. **Find process using port 8010**
   ```bash
   # Windows
   netstat -ano | findstr :8010
   taskkill /PID <process_id> /F
   
   # Linux/Mac
   lsof -i :8010
   kill -9 <process_id>
   ```

2. **Use different port**
   ```bash
   # In backend/.env
   API_PORT=8011
   
   # Update desktop/.env accordingly
   API_BASE_URL=http://localhost:8011/api/v1
   ```

#### Issue: Import errors when starting server
```python
ImportError: No module named 'database'
```

**Solutions:**
1. **Check working directory**
   ```bash
   # Must be in backend directory
   cd backend
   python main.py
   ```

2. **Verify file structure**
   ```bash
   backend/
   ├── main.py
   ├── database.py
   ├── api/
   └── models/
   ```

### Database Connection Issues

#### Issue: Database file not found
```bash
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: projects
```

**Solutions:**
1. **Initialize database**
   ```python
   # In backend directory
   python -c "from database import engine, Base; Base.metadata.create_all(bind=engine)"
   ```

2. **Check database file location**
   ```bash
   # Should be in backend directory
   ls backend/motivate_ai.db
   ```

3. **Reset database** (development only)
   ```bash
   # Delete and recreate
   rm backend/motivate_ai.db
   python -c "from database import engine, Base; Base.metadata.create_all(bind=engine)"
   ```

### API Endpoint Issues

#### Issue: 404 Not Found for valid endpoints
```json
{"detail": "Not Found"}
```

**Solutions:**
1. **Check endpoint registration**
   ```python
   # In main.py, ensure routers are included
   from api.projects import router as projects_router
   app.include_router(projects_router, prefix="/api/v1")
   ```

2. **Verify URL format**
   ```bash
   # Correct
   GET http://localhost:8010/api/v1/projects
   
   # Incorrect
   GET http://localhost:8010/projects  # Missing /api/v1
   ```

3. **Check FastAPI auto-documentation**
   ```bash
   # Visit in browser
   http://localhost:8010/docs
   ```

#### Issue: 422 Unprocessable Entity
```json
{"detail": [{"loc": ["body", "title"], "msg": "field required", "type": "value_error.missing"}]}
```

**Solutions:**
1. **Check request body format**
   ```python
   # Correct JSON format
   {
       "title": "My Project",
       "description": "Project description"
   }
   ```

2. **Verify Pydantic model**
   ```python
   class ProjectCreate(BaseModel):
       title: str  # Required field
       description: Optional[str] = None  # Optional field
   ```

---

## Desktop Application Issues

### GUI Startup Issues

#### Issue: Application starts but no GUI appears
**Symptoms:** Python process running but no window visible

**Solutions:**
1. **Check system tray**
   - Look for Motivate.AI icon in system tray
   - Right-click icon → "Open Main Window"

2. **Check for errors in console**
   ```bash
   cd desktop
   python main.py
   # Look for error messages
   ```

3. **Force window to show**
   ```python
   # Add to main.py for debugging
   self.main_window.root.deiconify()
   self.main_window.root.lift()
   ```

#### Issue: GUI freezes or becomes unresponsive
**Symptoms:** Window exists but doesn't respond to clicks

**Solutions:**
1. **Check for blocking operations on main thread**
   ```python
   # ❌ WRONG: Blocking operation on main thread
   def load_projects(self):
       response = requests.get(url, timeout=30)  # Blocks GUI
       self.update_ui(response.json())
   
   # ✅ CORRECT: Use background thread
   def load_projects(self):
       threading.Thread(target=self._load_projects_background).start()
   
   def _load_projects_background(self):
       response = requests.get(url, timeout=5)
       # Use queue to update GUI safely
       self.update_queue.put(("update_ui", response.json()))
   ```

2. **Add regular GUI updates**
   ```python
   def main_loop(self):
       while self.running:
           self.root.update()  # Keep GUI responsive
           time.sleep(0.1)
   ```

### System Tray Issues

#### Issue: System tray icon not appearing
**Symptoms:** No icon in system tray

**Solutions:**
1. **Check Windows notification area settings**
   - Right-click taskbar → "Taskbar settings"
   - Click "Select which icons appear on the taskbar"
   - Ensure "Show all icons" or manually enable Motivate.AI

2. **Verify icon file exists**
   ```bash
   ls desktop/assets/icon.ico
   # If missing, create or copy icon file
   ```

3. **Check pystray installation**
   ```bash
   pip show pystray
   # If not found: pip install pystray
   ```

#### Issue: System tray menu not working
**Symptoms:** Right-click on tray icon shows no menu or empty menu

**Solutions:**
1. **Check menu creation code**
   ```python
   # Ensure menu items are properly defined
   menu = pystray.Menu(
       pystray.MenuItem("Open Main Window", self.show_main_window),
       pystray.MenuItem("Exit", self.quit_application)
   )
   ```

2. **Verify callback functions exist**
   ```python
   def show_main_window(self, icon, item):
       # Function must accept icon and item parameters
       self.main_window.show()
   ```

### Threading Issues

#### Issue: RuntimeError: main thread is not in main loop
```python
RuntimeError: main thread is not in main loop
```

**This is the most common desktop issue. Solutions:**

1. **Never call GUI methods from background threads**
   ```python
   # ❌ WRONG: GUI call from background thread
   def background_task():
       self.status_label.configure(text="Done")  # CRASHES
   
   # ✅ CORRECT: Use queue-based communication
   def background_task():
       self.update_queue.put(("set_status", "Done"))
   
   def process_queue(self):
       try:
           while True:
               action, data = self.update_queue.get_nowait()
               if action == "set_status":
                   self.status_label.configure(text=data)
       except queue.Empty:
           pass
       self.root.after(100, self.process_queue)  # Schedule next check
   ```

2. **Use proper thread creation**
   ```python
   # ✅ CORRECT: daemon=False for Windows stability
   thread = threading.Thread(target=background_task, daemon=False)
   thread.start()
   ```

---

## Database Issues

### Data Corruption

#### Issue: Database file corrupted
```bash
sqlite3.DatabaseError: database disk image is malformed
```

**Solutions:**
1. **Attempt repair** (development only)
   ```bash
   # Backup first
   cp motivate_ai.db motivate_ai.db.backup
   
   # Try to repair
   echo ".recover" | sqlite3 motivate_ai.db > recovered.sql
   rm motivate_ai.db
   sqlite3 motivate_ai.db < recovered.sql
   ```

2. **Restore from backup**
   ```bash
   cp motivate_ai.db.backup motivate_ai.db
   ```

3. **Start fresh** (loses data)
   ```bash
   rm motivate_ai.db
   python -c "from database import engine, Base; Base.metadata.create_all(bind=engine)"
   ```

### Performance Issues

#### Issue: Slow database queries
**Symptoms:** API requests taking > 1 second

**Solutions:**
1. **Add missing indexes**
   ```sql
   -- Check query performance
   EXPLAIN QUERY PLAN SELECT * FROM tasks WHERE project_id = 1;
   
   -- Add index if using table scan
   CREATE INDEX ix_tasks_project_id ON tasks(project_id);
   ```

2. **Optimize queries**
   ```python
   # ❌ SLOW: N+1 query problem
   projects = db.query(Project).all()
   for project in projects:
       project.tasks = db.query(Task).filter(Task.project_id == project.id).all()
   
   # ✅ FAST: Use JOIN
   from sqlalchemy.orm import joinedload
   projects = db.query(Project).options(joinedload(Project.tasks)).all()
   ```

---

## API Integration Issues

### Connection Problems

#### Issue: Desktop can't connect to backend
```python
requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8010): Max retries exceeded
```

**Diagnostic Steps:**
1. **Check if backend is running**
   ```bash
   # Visit in browser
   http://localhost:8010/health
   
   # Or use curl
   curl http://localhost:8010/health
   ```

2. **Verify port configuration**
   ```bash
   # Backend .env
   cat backend/.env | grep API_PORT
   
   # Desktop .env
   cat desktop/.env | grep API_BASE_URL
   ```

3. **Test network connectivity**
   ```bash
   # Windows
   telnet localhost 8010
   
   # Linux/Mac
   nc -zv localhost 8010
   ```

#### Issue: Field name mismatches
**Symptoms:** Tasks not saving, field validation errors

**Common Mismatches:**
- Frontend sends `estimated_time`, backend expects `estimated_minutes`
- Frontend sends `name`, backend expects `title`
- Frontend sends `id`, backend expects `project_id`

**Solutions:**
1. **Check API documentation**
   - Visit `http://localhost:8010/docs`
   - Verify exact field names and types

2. **Add request/response logging**
   ```python
   # In desktop app
   import logging
   logging.basicConfig(level=logging.DEBUG)
   
   # This will log all HTTP requests
   response = requests.post(url, json=data)
   print(f"Request data: {data}")
   print(f"Response: {response.text}")
   ```

### Authentication Issues

#### Issue: 401 Unauthorized (future versions)
**When authentication is implemented:**

**Solutions:**
1. **Check API key configuration**
   ```bash
   # In .env file
   API_KEY=your_api_key_here
   ```

2. **Verify header format**
   ```python
   headers = {
       "Authorization": f"Bearer {api_key}",
       "Content-Type": "application/json"
   }
   ```

---

## Performance Issues

### Slow Application Startup

#### Issue: Desktop app takes > 5 seconds to start
**Causes & Solutions:**

1. **Slow API health check**
   ```python
   # Reduce timeout
   try:
       response = requests.get(f"{api_url}/health", timeout=2)  # Was 10s
   except requests.Timeout:
       print("API unavailable, continuing in offline mode")
   ```

2. **Heavy UI component creation**
   ```python
   # ✅ Lazy load heavy components
   def get_project_dialog(self):
       if not hasattr(self, '_project_dialog'):
           self._project_dialog = NewProjectDialog(self.root)
       return self._project_dialog
   ```

### Memory Usage Issues

#### Issue: Application memory usage keeps growing
**Symptoms:** Task Manager shows increasing memory usage

**Solutions:**
1. **Clear cached data periodically**
   ```python
   def cleanup_cache(self):
       if len(self.projects_cache) > 100:
           # Keep only recent items
           self.projects_cache = dict(list(self.projects_cache.items())[-50:])
   ```

2. **Properly close database connections**
   ```python
   # Always use context managers
   def get_projects():
       db = next(get_db())
       try:
           return db.query(Project).all()
       finally:
           db.close()
   ```

---

## Deployment Issues

### Production Environment Setup

#### Issue: Application works in development but fails in production
**Common Causes:**

1. **Environment variable differences**
   ```bash
   # Check all environment variables
   printenv | grep -i motivate
   ```

2. **File path issues**
   ```python
   # Use absolute paths in production
   import os
   from pathlib import Path
   
   BASE_DIR = Path(__file__).parent
   DB_PATH = BASE_DIR / "motivate_ai.db"
   ```

3. **Missing dependencies**
   ```bash
   # Generate complete requirements
   pip freeze > requirements.txt
   
   # Install exact versions in production
   pip install -r requirements.txt
   ```

---

## Debugging Tools and Techniques

### Backend Debugging

#### Enable Debug Logging
```python
# In main.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add to endpoint functions
logger = logging.getLogger(__name__)

@router.post("/projects")
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating project: {project.dict()}")
    # ... rest of function
```

#### API Testing with curl
```bash
# Test project creation
curl -X POST http://localhost:8010/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Project", "description": "Test description"}'

# Test with verbose output
curl -v -X GET http://localhost:8010/api/v1/projects
```

### Desktop Debugging

#### Enable Console Output
```python
# Add to main.py
import sys

# Redirect stdout to console (if running as .exe)
if hasattr(sys, '_MEIPASS'):  # PyInstaller
    sys.stdout = open('motivate_ai_debug.log', 'w')
    sys.stderr = sys.stdout

print("Debug: Application starting...")
```

#### GUI Inspector Tool
```python
# Add debugging widget
import tkinter as tk

def show_debug_info(self):
    debug_window = tk.Toplevel(self.root)
    debug_window.title("Debug Info")
    
    info = f"""
    API Base URL: {self.api_base_url}
    Projects loaded: {len(self.projects)}
    Selected project: {self.selected_project}
    Last API call: {self.last_api_call}
    Thread count: {threading.active_count()}
    """
    
    tk.Label(debug_window, text=info, justify="left").pack(padx=20, pady=20)
```

### Network Debugging

#### Monitor API Calls
```python
# Add request/response logging
import requests
import logging

# Enable requests debugging
logging.getLogger("requests.packages.urllib3").setLevel(logging.DEBUG)
logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.DEBUG)

# Or create custom session with logging
session = requests.Session()

def log_request(response, *args, **kwargs):
    print(f"API Call: {response.request.method} {response.request.url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}...")

session.hooks['response'] = log_request
```

### Database Debugging

#### SQL Query Logging
```python
# In database.py
import logging

# Enable SQLAlchemy query logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# This will print all SQL queries to console
```

#### Database Inspection Tools
```bash
# SQLite command line
sqlite3 motivate_ai.db

# Common inspection commands
.tables                    # List all tables
.schema projects          # Show table structure
SELECT COUNT(*) FROM projects;  # Count records
.quit                     # Exit
```

---

## Getting Help

### Log Collection
When reporting issues, collect these logs:

1. **Backend logs**
   ```bash
   cd backend
   python main.py > backend.log 2>&1
   ```

2. **Desktop logs**
   ```bash
   cd desktop
   python main.py > desktop.log 2>&1
   ```

3. **System information**
   ```bash
   # Windows
   systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type"
   python --version
   
   # Linux/Mac
   uname -a
   python --version
   ```

### Common Debug Commands
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Check installed packages
pip list

# Test API connectivity
curl -f http://localhost:8010/health || echo "API not responding"

# Check database
sqlite3 motivate_ai.db "SELECT COUNT(*) FROM projects;"
```

---

*This troubleshooting guide is continuously updated based on real-world issues encountered during development and deployment. If you encounter an issue not covered here, please document the solution for future developers.*