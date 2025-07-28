# Design Rules for Motivate.AI

## Project Vision & Philosophy

Motivate.AI is an AI-guided project companion designed to gently reconnect users with their unfinished projects and goals. The core philosophy is **compassionate productivity** - not optimization, but reconnection.

### Core Principles
1. **Minimal Administration**: The system should require as little manual input as possible
2. **Gentle Nudging**: Prompts should be encouraging, not demanding
3. **15-Minute Focus**: All suggestions should be achievable in 15 minutes or less
4. **Privacy-First**: Local AI processing when possible, minimal data collection
5. **Graceful Degradation**: All features should work even when external services fail

## Architecture Standards

### Overall Structure
```
motivate.ai/
├── backend/          # FastAPI REST API (Python)
├── desktop/          # System tray app (Python + pystray)
├── mobile/           # React Native app (future)
├── shared/           # Common configuration
├── docs/             # Documentation
└── scripts/          # Development and deployment scripts
```

### Technology Stack Constraints

#### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Database**: SQLite for development, PostgreSQL for production
- **ORM**: SQLAlchemy with Alembic migrations
- **AI**: Ollama integration with fallback suggestions
- **Testing**: pytest with coverage reporting

#### Desktop
- **Framework**: Python with CustomTkinter for modern Windows UI
- **System Integration**: pystray for system tray functionality  
- **Threading Model**: Queue-based communication with pre-created GUI components
- **Architecture**: Main thread GUI operations with background service threads
- **Stability**: Windows-optimized patterns (daemon=False threads, error recovery)

#### Desktop Threading Rules (CRITICAL)
⚠️ **All GUI operations MUST happen on the main thread to avoid GIL errors on Windows**

```python
# ✅ CORRECT - Pre-created GUI on main thread
class MotivateAIApp:
    def __init__(self):
        self.main_window = MainWindow()  # Created during app initialization
        self.main_window.root.withdraw() # Hidden until needed
        
# ✅ CORRECT - Queue-based background communication
class TrayManager:
    def __init__(self):
        self.action_queue = queue.Queue()  # Thread-safe communication
        
    def show_main_window(self):
        self.action_queue.put(("show_main_window", None))  # No direct GUI calls

# ✅ CORRECT - Main loop processes queued actions
def main_loop(self):
    while self.running:
        self.process_tray_actions()      # Process queued GUI actions
        self.main_window.root.update()   # Keep GUI responsive
        time.sleep(0.1)                  # Prevent excessive CPU usage
```

#### Desktop Stability Patterns (ESTABLISHED)
```python
# Windows threading stability
thread = threading.Thread(target=service, daemon=False)  # daemon=False for Windows

# API calls with timeouts and fallbacks
try:
    response = requests.get(url, timeout=2)
    return response.json()
except Exception as e:
    logger.warning(f"API unavailable: {e}")
    return get_fallback_data()  # Always provide fallback

# Error recovery for critical services
def restart_service_if_failed(self):
    if not self.service_thread.is_alive():
        logger.info("Restarting failed service")
        self.start_service()
```

#### Mobile (Future)
- **Framework**: React Native for cross-platform support
- **State Management**: Redux or Context API
- **Offline Support**: Required for task logging

#### Forbidden Technologies
- **JavaScript in Backend**: Python-only backend [[memory:2259672]]
- **Heavy UI Frameworks**: Keep desktop app lightweight
- **Complex State Management**: Avoid overengineering

## Desktop Application Architecture Patterns (ESTABLISHED)

### Core Architecture Principles
The desktop application follows **strict threading discipline** and **component isolation** patterns proven through development and testing on Windows systems.

### Threading Architecture
```
Main Application Thread
├── GUI Event Loop (CustomTkinter)
├── Pre-created Window (hidden until needed)
├── Queue Processing (for background actions)
└── Periodic Updates (root.update() every 0.1s)

Background Threads
├── System Tray Thread (daemon=False, queue-based)
├── Service Monitoring Thread (with auto-restart)
└── API Request Threads (short-lived, no GUI operations)
```

### Component Communication Pattern
```python
# Background Thread → Queue → Main Thread → GUI Update
background_thread.action_queue.put(("action_name", data))
main_loop.process_queue_actions()  # Executed on main thread
gui_component.update_display(data)  # Safe GUI operation
```

### Error Recovery Patterns
```python
# Service resilience with auto-restart
class ServiceManager:
    def monitor_service(self):
        while self.running:
            if not self.service_thread.is_alive():
                self.restart_service()
            time.sleep(1)
    
    def restart_service(self):
        try:
            self.service_thread = threading.Thread(
                target=self.service_function, 
                daemon=False  # Critical for Windows stability
            )
            self.service_thread.start()
        except Exception as e:
            logger.error(f"Service restart failed: {e}")
```

### API Integration Pattern
```python
# Graceful degradation with fallbacks
def api_call_with_fallback(self, endpoint, fallback_data):
    try:
        response = requests.get(f"{self.api_base_url}/{endpoint}", timeout=2)
        if response.status_code == 200:
            return response.json()
        else:
            raise requests.RequestException(f"API returned {response.status_code}")
    except Exception as e:
        logger.warning(f"API call failed: {e}")
                 return fallback_data  # Always provide working fallback
```

### Critical Anti-Patterns (AVOID)
Based on debugging experience, these patterns cause crashes and instability:

```python
# ❌ NEVER: Direct GUI calls from background threads
def background_task():
    window.update_text("Done")  # RuntimeError: main thread is not in main loop

# ❌ NEVER: Creating GUI components from background threads  
def tray_callback():
    dialog = tkinter.Toplevel()  # GIL error on Windows

# ❌ NEVER: daemon=True threads for critical services on Windows
thread = threading.Thread(target=service, daemon=True)  # Causes crashes

# ❌ NEVER: Blocking operations on main thread
def load_projects():
    response = requests.get(url)  # Freezes GUI if slow
    update_ui(response.json())

# ❌ NEVER: Async loading with root.after() from background threads
def background_load():
    data = get_data()
    root.after(0, lambda: update_ui(data))  # RuntimeError
```

### Performance & Stability Guidelines
```python
# ✅ Pre-create UI components during initialization
class App:
    def __init__(self):
        self.window = MainWindow()  # Created once
        self.window.root.withdraw() # Hidden until needed

# ✅ Use short timeouts for all API calls
response = requests.get(url, timeout=2)  # Never block indefinitely

# ✅ Always provide immediate feedback to users
self.status_label.configure(text="Loading...")  # Show action immediately
threading.Thread(target=self.load_data).start()  # Then load in background

# ✅ Implement graceful error recovery
if not self.service_thread.is_alive():
    self.restart_service()  # Auto-recovery for failed services
```

## Code Organization Standards

### File Naming Conventions
```
# Python files
snake_case.py           # Standard Python files
test_[component].py     # Test files
test_[component]_[category].py  # Categorized tests

# Configuration
.env                    # Environment variables
config.py              # Python configuration
requirements.txt       # Python dependencies

# Documentation
COMPONENT_NAME.md       # All caps for major docs
component_guide.md      # Lower case for guides
```

### Directory Structure Rules

#### Backend
```
backend/
├── api/                # FastAPI route handlers
│   ├── __init__.py
│   ├── projects.py     # Project endpoints
│   ├── tasks.py        # Task endpoints
│   ├── suggestions.py  # AI suggestion endpoints
│   └── activity.py     # Activity logging endpoints
├── models/             # Database models
│   ├── __init__.py
│   ├── project.py
│   ├── task.py
│   └── activity.py
├── services/           # Business logic
│   ├── __init__.py
│   ├── ai_service.py
│   └── [other_services].py
├── tests/              # All test files
├── database.py         # Database setup and connection
├── main.py            # FastAPI app entry point
└── requirements.txt   # Dependencies
```

#### Desktop (FULLY FUNCTIONAL)
```
desktop/
├── ui/                       # User interface components (WORKING)
│   ├── __init__.py
│   ├── main_window.py        # Main task management interface
│   ├── new_project.py        # Project creation dialog
│   ├── popup_manager.py      # Smart notification system
│   ├── quick_add.py          # Quick task addition dialog
│   └── components/           # Reusable UI components
├── services/                 # Background services (WORKING)
│   ├── __init__.py
│   ├── tray_manager_fixed.py # System tray with queue communication
│   └── idle_monitor.py       # Activity monitoring (temp. disabled)
├── models/                   # Data models and state management
├── assets/                   # Icons and UI resources
├── tests/                    # Desktop application tests
├── main.py                  # Application orchestrator and main loop
├── DESIGN_GUIDE.md          # Comprehensive architecture documentation
└── requirements.txt         # Dependencies (simplified for stability)
```

## Database Design Standards

### Model Conventions
```python
class ProjectModel(Base):
    __tablename__ = "projects"
    
    # Primary key always 'id'
    id = Column(Integer, primary_key=True, index=True)
    
    # Timestamps for audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Business fields
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    
    # Soft delete support
    is_deleted = Column(Boolean, default=False)
```

### Relationship Rules
- Use foreign keys with proper constraints
- Implement soft deletes, not hard deletes
- Always include created_at/updated_at timestamps
- Use indexes on frequently queried fields

## API Design Standards

### Endpoint Conventions
```
# Resource-based URLs
GET    /api/v1/projects              # List projects
POST   /api/v1/projects              # Create project
GET    /api/v1/projects/{id}         # Get specific project
PUT    /api/v1/projects/{id}         # Update project
DELETE /api/v1/projects/{id}         # Soft delete project

# Action-based endpoints (when needed)
POST   /api/v1/projects/{id}/suggest # Generate suggestions for project
```

### Response Standards
```python
# Success responses
{
    "data": {...},           # The actual response data
    "message": "string",     # Optional success message
    "timestamp": "ISO8601"   # Response timestamp
}

# Error responses  
{
    "error": "error_type",   # Machine-readable error code
    "message": "string",     # Human-readable error message
    "details": {...},        # Optional additional error details
    "timestamp": "ISO8601"   # Response timestamp
}
```

### Status Code Standards
- `200 OK` - Successful GET, PUT
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Client error (validation, etc.)
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Testing Standards

### Test Categories
1. **Simple Tests** (`test_simple.py`) - No external dependencies
2. **Integration Tests** (`test_integration.py`) - With test database
3. **Live API Tests** (`test_live_api.py`) - Against running server
4. **Component Tests** (`test_[component]_simple.py`) - Specific components

### Test File Organization
```python
# File header template
"""
Brief description of test file purpose
Any special requirements (e.g., "Requires API running")
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

def test_specific_functionality():
    """
    Clear description of what this test verifies
    Expected behavior and any special conditions
    """
    # Arrange
    test_data = setup_test_data()
    
    # Act
    result = function_under_test(test_data)
    
    # Assert
    assert result.status == "expected"
```

### Coverage Requirements
- **Minimum Coverage**: 80% overall
- **Critical Components**: 95% coverage (database models, API endpoints)
- **Test Performance**: Simple tests < 0.1s each, Integration tests < 2s each

## Configuration Management

### Environment Variables
```bash
# Development (.env files)
DATABASE_URL=sqlite:///./motivate_ai.db
DEBUG=true
LOG_LEVEL=DEBUG
API_BASE_URL=http://localhost:8010

# Production (environment variables)
DATABASE_URL=postgresql://...
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=...
```

### Configuration Hierarchy
1. Environment variables (highest priority)
2. .env files (development)
3. Default values in code (lowest priority)

## AI Integration Rules

### Ollama Integration
```python
# Always provide fallbacks
try:
    ai_response = await ollama_client.generate(prompt)
    return parse_ai_response(ai_response)
except Exception as e:
    logger.warning(f"AI service unavailable: {e}")
    return get_fallback_suggestions()
```

### Prompt Engineering
- Keep prompts simple and focused
- Include context about user's energy level and available time
- Always request specific, actionable suggestions
- Limit responses to 3-5 suggestions maximum

## Error Handling Standards

### Exception Hierarchy
```python
class MotivateAIException(Exception):
    """Base exception for all Motivate.AI errors"""
    pass

class DatabaseError(MotivateAIException):
    """Database-related errors"""
    pass

class AIServiceError(MotivateAIException):
    """AI service integration errors"""
    pass
```

### Logging Standards
```python
import logging

# Use structured logging
logger = logging.getLogger(__name__)

# Log levels
logger.debug("Detailed information for debugging")
logger.info("General application flow")
logger.warning("Something unexpected but not an error")
logger.error("Error occurred but application continues")
logger.critical("Serious error, application may not continue")
```

## Security Guidelines

### API Security
- Use CORS appropriately (not `allow_origins=["*"]` in production)
- Validate all input data
- Sanitize user-provided content
- Use HTTPS in production

### Data Privacy
- Store minimal user data
- No tracking without explicit consent
- Provide data export/deletion capabilities
- Local AI processing preferred over cloud

## Performance Standards

### Response Time Targets
- API endpoints: < 200ms average
- Database queries: < 50ms average
- AI suggestions: < 5 seconds
- Desktop app startup: < 3 seconds

### Resource Usage
- Memory usage: < 100MB per component
- Database size: Reasonable growth (implement archiving)
- Background tasks: Minimal CPU when idle

## Documentation Requirements

### Code Documentation
```python
def generate_suggestions(project_id: int, context: dict) -> List[Suggestion]:
    """
    Generate AI-powered suggestions for a specific project.
    
    Args:
        project_id: The ID of the project to generate suggestions for
        context: Additional context including user energy, available time
        
    Returns:
        List of Suggestion objects with actionable 15-minute tasks
        
    Raises:
        AIServiceError: When AI service is unavailable and fallbacks fail
        DatabaseError: When project data cannot be retrieved
    """
```

### API Documentation
- All endpoints must have OpenAPI/Swagger documentation
- Include request/response examples
- Document error conditions
- Provide usage examples

## Version Control Standards

### Commit Messages
```
type(scope): description

# Types: feat, fix, docs, test, refactor, style, chore
# Examples:
feat(api): add project suggestion endpoint
fix(desktop): resolve system tray icon display issue
docs(readme): update installation instructions
test(backend): add integration tests for projects API
```

### Branch Strategy
- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/description` - Individual features
- `fix/description` - Bug fixes

## Development Workflow

### Local Development
1. Run `setup.bat` for initial setup
2. Use `dev_start.bat` for development environment
3. Run `run_tests_simple.bat` frequently during development
4. Run `run_tests.bat` before committing

### Code Review Requirements
- All changes require testing
- Documentation updates for API changes
- Performance impact consideration
- Security review for sensitive changes

## Deployment Standards

### Environment Separation
- **Development**: Local SQLite, debug logging, mock AI
- **Staging**: Production-like setup with test data
- **Production**: PostgreSQL, structured logging, real AI services

### Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "database": await check_database_health(),
        "ai_service": await check_ai_service_health()
    }
```

These design rules have been proven through development of the working desktop and backend components. They ensure consistent, maintainable, and scalable development of Motivate.AI while staying true to its core philosophy of compassionate productivity.

## Implementation Status

### ✅ Proven Patterns (In Production)
- **Desktop Threading Architecture**: Queue-based communication prevents GIL errors
- **Pre-created UI Components**: Instant window opening without creation delays
- **API Integration with Fallbacks**: Graceful degradation when backend unavailable
- **Error Recovery Mechanisms**: Auto-restart for failed services
- **Windows Stability Patterns**: daemon=False threads, proper thread lifecycle

### 📚 Reference Documentation
- **desktop/DESIGN_GUIDE.md**: Comprehensive desktop architecture guide
- **docs/PROJECT_STRUCTURE.md**: Current working project structure
- **Component READMEs**: Setup and usage for each component

These patterns have been tested extensively and provide a stable foundation for future development. 