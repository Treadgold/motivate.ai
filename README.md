# Motivate.AI

AI-guided project companion that transforms overwhelming tasks into manageable, motivated action through intelligent suggestions and progress tracking.

## Features

- **Smart Project Management**: AI-powered suggestions for your next 15-minute action
- **Desktop Integration**: System tray app that monitors your activity and provides timely nudges
- **Cross-Platform Support**: Backend API, desktop app, and future mobile/web interfaces
- **Local AI**: Uses Ollama for privacy-focused AI suggestions

## Quick Start

### 1. Setup
```bash
# Clone and setup the project
git clone <your-repo-url>
cd motivate.ai
setup.bat  # On Windows
```

### 2. Development Mode
```bash
# Start all services for development
dev_start.bat

# Or start individual components
start_backend.bat    # Backend API only
start_desktop.bat    # Desktop app only
start_complete.bat   # All services with Ollama
```

### 3. Testing
```bash
# Run the complete test suite
run_tests.bat

# Test individual components
cd backend && pytest tests/
cd desktop && pytest tests/
```

## Development

### Architecture
- **Backend**: FastAPI-based REST API (Python)
- **Desktop**: System tray application with pystray (Python)
- **Mobile**: React Native (coming soon)
- **Database**: SQLite with SQLAlchemy ORM
- **AI**: Ollama integration with qwen3max model

### Available Commands

| Command | Description |
|---------|-------------|
| `setup.bat` | Initial project setup and dependency installation |
| `dev_start.bat` | Start development environment with health checks |
| `run_tests.bat` | Run complete test suite with coverage |
| `start_complete.bat` | Start all services (production-like) |

### Testing

We use pytest for comprehensive testing:

- **Unit Tests**: Test individual components and functions
- **Integration Tests**: Test API endpoints and service interactions  
- **Coverage Reports**: Generated in `backend/coverage_backend/` and `desktop/coverage_desktop/`

```bash
# Run tests with coverage
run_tests.bat

# Run specific test categories
cd backend
pytest tests/ -m "not slow"           # Skip slow tests
pytest tests/ -m "integration"        # Only integration tests
pytest tests/test_projects_api.py     # Specific test file
```

### CI/CD

GitHub Actions pipeline includes:
- ✅ Unit and integration testing
- ✅ Code quality checks (Black, flake8, isort)
- ✅ Security scanning (safety, bandit)
- ✅ Coverage reporting
- ✅ Multi-platform testing (Ubuntu, Windows)

## API Documentation

When running locally, visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Requirements

- Python 3.9+
- Node.js 16+ (for future web interface)
- Ollama (optional, for AI features)

## Configuration

Environment files are created automatically during setup:
- `backend/.env` - Backend configuration
- `desktop/.env` - Desktop app configuration

## Contributing

1. Run `setup.bat` to initialize the development environment
2. Create a feature branch
3. Write tests for new functionality
4. Run `run_tests.bat` to ensure all tests pass
5. Submit a pull request

The CI pipeline will automatically test your changes across multiple platforms.

## License

MIT License - see LICENSE file for details. 