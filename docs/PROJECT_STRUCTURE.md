# Motivate.AI Project Structure

## Overview

This document defines the standard project structure for Motivate.AI to ensure consistency across all components and make it easy for developers to navigate and contribute to the codebase.

## Root Directory Structure

```
motivate.ai/
├── README.md                    # Main project overview and quick start
├── TODO.md                      # Development task tracking
├── DESIGN_RULES.md             # Development standards and guidelines
├── TESTING.md                  # Testing guidelines and procedures
├── TESTING_STYLE_GUIDE.md      # Detailed testing standards
├── initial_idea.md             # Original project concept (historical)
├── pytest.ini                 # Global pytest configuration
├── .gitignore                  # Git ignore patterns
│
├── backend/                    # FastAPI REST API service
├── desktop/                    # Python system tray application
├── mobile/                     # React Native mobile app (future)
├── shared/                     # Shared configuration and utilities
├── docs/                       # Additional documentation
├── scripts/                    # Development and deployment scripts
│
├── setup.bat                   # Initial project setup (Windows)
├── dev_start.bat              # Development environment starter
├── start_backend.bat          # Backend service starter
├── start_desktop.bat          # Desktop app starter
├── start_complete.bat         # All services starter
├── run_tests.bat              # Full test suite runner
├── run_tests_simple.bat       # Quick test suite runner
└── test_system.bat            # System validation tests
```

## Backend Structure (`backend/`)

```
backend/
├── README.md                   # Backend-specific documentation
├── requirements.txt            # Python dependencies
├── pytest.ini                 # Backend-specific pytest config
├── .env                       # Environment variables (created by setup)
├── main.py                    # FastAPI application entry point
├── database.py                # Database connection and setup
│
├── api/                       # FastAPI route handlers
│   ├── __init__.py
│   ├── projects.py            # Project CRUD endpoints
│   ├── tasks.py               # Task management endpoints
│   ├── suggestions.py         # AI suggestion endpoints
│   └── activity.py            # Activity logging endpoints
│
├── models/                    # SQLAlchemy database models
│   ├── __init__.py
│   ├── project.py             # Project model
│   ├── task.py                # Task model
│   └── activity.py            # Activity logging model
│
├── services/                  # Business logic services
│   ├── __init__.py
│   ├── ai_service.py          # AI integration service
│   └── [future_services].py   # Additional business logic
│
├── tests/                     # All backend tests
│   ├── __init__.py
│   ├── conftest.py            # Test fixtures and configuration
│   │
│   ├── test_simple.py         # Fast, no-dependency tests
│   ├── test_endpoints_simple.py  # Endpoint structure tests
│   ├── test_database_simple.py   # Model validation tests
│   │
│   ├── test_integration.py       # HTTP API integration tests
│   ├── test_integration_simple.py # Direct database tests
│   │
│   ├── test_live_api.py          # Tests against running server
│   ├── test_ai_service.py        # AI service tests
│   ├── test_main.py              # Main app tests
│   └── test_projects_api.py      # Project API specific tests
│
├── coverage_backend/          # Coverage reports (generated)
└── venv/                      # Python virtual environment
```

## Desktop Structure (`desktop/`)

```
desktop/
├── README.md                  # Desktop app documentation
├── requirements.txt           # Python dependencies
├── .env                      # Environment variables (created by setup)
├── main.py                   # Desktop application entry point
│
├── ui/                       # User interface components (future)
│   ├── __init__.py
│   ├── tray_menu.py          # System tray menu management
│   ├── notifications.py      # Notification handling
│   └── settings_dialog.py    # Settings interface
│
├── services/                 # Desktop-specific services
│   ├── __init__.py
│   ├── activity_monitor.py   # User activity monitoring
│   ├── api_client.py         # Backend API communication
│   └── notification_service.py # Notification management
│
├── tests/                    # Desktop application tests
│   ├── __init__.py
│   ├── test_main.py          # Main application tests
│   └── [future_tests].py    # Additional test files
│
├── coverage_desktop/         # Coverage reports (generated)
└── venv/                     # Python virtual environment
```

## Mobile Structure (`mobile/`) - Future

```
mobile/
├── README.md                 # Mobile app documentation
├── package.json             # React Native dependencies
├── metro.config.js          # Metro bundler configuration
├── android/                 # Android-specific files
├── ios/                     # iOS-specific files
│
├── src/                     # React Native source code
│   ├── components/          # Reusable UI components
│   ├── screens/             # Application screens
│   ├── services/            # API and business logic
│   ├── utils/               # Utility functions
│   └── navigation/          # Navigation setup
│
└── __tests__/               # Mobile app tests
```

## Shared Structure (`shared/`)

```
shared/
├── config.env.example       # Environment template
└── [future_shared_code]/    # Shared utilities and types
```

## Documentation Structure (`docs/`)

```
docs/
├── GETTING_STARTED.md       # New user setup guide
├── PROJECT_STRUCTURE.md     # This document
└── [future_docs]/           # Additional documentation
```

## Scripts Structure (`scripts/`)

```
scripts/
└── [future_scripts]/        # Development and deployment scripts
```

## File Naming Conventions

### Python Files
- **snake_case.py** - Standard Python module naming
- **test_[component].py** - Basic test files
- **test_[component]_[category].py** - Categorized test files
- **__init__.py** - Package initialization (often empty)

### Configuration Files
- **.env** - Environment variables (never committed)
- **.env.example** - Environment template (committed)
- **requirements.txt** - Python dependencies
- **package.json** - Node.js dependencies
- **pytest.ini** - Pytest configuration

### Documentation Files
- **README.md** - Component or section overview
- **COMPONENT_NAME.md** - Major documentation (all caps)
- **component_guide.md** - Detailed guides (lower case)

### Batch Files (Windows)
- **setup.bat** - Setup and installation
- **start_[service].bat** - Service starters
- **run_[action].bat** - Action runners
- **test_[scope].bat** - Test runners

## Directory Organization Rules

### 1. Separation of Concerns
- **api/** - HTTP interface layer
- **models/** - Data persistence layer
- **services/** - Business logic layer
- **tests/** - All testing code
- **ui/** - User interface components

### 2. Consistent Structure Across Components
Each major component (backend, desktop, mobile) follows the same patterns:
- Main entry point at root (`main.py`, `index.js`)
- Configuration in root (`.env`, `requirements.txt`)
- Source code in logical subdirectories
- Tests in dedicated `tests/` directory
- Generated files in predictable locations

### 3. Test Organization
Tests are organized by complexity and dependencies:
- **Simple tests** - Fast, no external dependencies
- **Integration tests** - With test database or test client
- **Live tests** - Against running services
- **Component-specific tests** - For individual modules

## Environment Configuration

### Development Environment Files
```
# Backend
backend/.env              # Backend environment variables
backend/venv/            # Backend Python virtual environment

# Desktop
desktop/.env             # Desktop environment variables  
desktop/venv/           # Desktop Python virtual environment

# Mobile (future)
mobile/.env             # Mobile environment variables
mobile/node_modules/    # Node.js dependencies
```

### Generated Files and Directories
```
# Test Coverage Reports
backend/coverage_backend/
desktop/coverage_desktop/

# Cache and Build Artifacts
**/__pycache__/         # Python bytecode cache
**/node_modules/        # Node.js dependencies
**/dist/                # Build outputs
**/build/               # Build artifacts

# Databases
backend/*.db            # SQLite databases
backend/*.db-*          # SQLite auxiliary files
```

## Import Conventions

### Python Path Management
All test files use consistent path setup:
```python
import sys
from pathlib import Path

# Add the component directory to Python path
component_dir = Path(__file__).parent.parent
sys.path.insert(0, str(component_dir))
```

### Import Organization
```python
# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
import pytest
from fastapi import FastAPI
from sqlalchemy import Column

# Local imports
from database import Base
from models.project import Project
from services.ai_service import AIService
```

## Development Workflow Integration

### Setting Up New Components
1. Create directory structure following patterns above
2. Add `README.md` with component overview
3. Set up `requirements.txt` or `package.json`
4. Create entry point (`main.py`, `index.js`)
5. Set up basic test structure
6. Add to relevant batch files for automation

### Adding New Features
1. Determine appropriate layer (api, models, services, ui)
2. Follow naming conventions
3. Add corresponding tests
4. Update relevant documentation
5. Follow import conventions

### Code Organization Guidelines
- **Keep it simple** - Don't over-engineer directory structures
- **Be consistent** - Follow established patterns
- **Be predictable** - Developers should know where to find things
- **Separate concerns** - Clear boundaries between layers
- **Test everything** - Every component should have tests

## Integration Points

### Backend ↔ Desktop
- Desktop calls backend REST API
- Configuration in `desktop/.env` points to backend URL
- Shared data models (consider shared types in future)

### Backend ↔ Mobile (Future)
- Mobile calls backend REST API
- Offline data synchronization
- Push notifications through backend

### Common Configuration
- Environment templates in `shared/`
- Consistent API base URLs
- Shared constants and configuration values

This structure ensures the Motivate.AI project remains organized, maintainable, and accessible to new contributors while supporting rapid development and testing. 