# Testing Guide for Motivate.AI

This guide covers all testing approaches for local development of Motivate.AI.

## Quick Start Testing

For rapid development cycles, use the quick test suite:

```bash
# Run quick tests (recommended during development)
run_tests_simple.bat
```

This runs:
- ✅ Basic import tests
- ✅ FastAPI app creation
- ✅ Health endpoints
- ✅ Desktop app tests
- ✅ Quick integration check

## Full Testing

For comprehensive testing before commits:

```bash
# Run complete test suite with coverage
run_tests.bat
```

This includes:
- ✅ All unit tests
- ✅ Integration tests with database
- ✅ Coverage reporting
- ✅ Live API integration tests

## Individual Test Commands

### Backend Tests

```bash
cd backend
call venv\Scripts\activate.bat

# Quick basic tests (no database required)
pytest tests/test_simple.py -v

# Integration tests (with database)
pytest tests/test_integration.py -v

# All backend tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=. --cov-report=html
```

### Desktop Tests

```bash
cd desktop
call venv\Scripts\activate.bat

# All desktop tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=. --cov-report=html
```

## Test Structure

### Backend Tests

- **`test_simple.py`** - Fast tests without database setup
  - Import validation
  - Basic app creation
  - Service initialization

- **`test_endpoints_simple.py`** - Endpoint structure tests
  - Route registration verification
  - App configuration tests
  - Middleware validation

- **`test_database_simple.py`** - Database model tests
  - Model import validation
  - Basic model structure
  - Object creation (no DB)

- **`test_live_api.py`** - Live API tests
  - Real HTTP requests to localhost:8010
  - Skip if API not running
  - CORS and documentation tests

- **`test_integration.py`** - Tests requiring database
  - Project CRUD operations
  - Database interactions
  - Full API workflows

- **`test_ai_service.py`** - AI service tests
  - Mocked Ollama interactions
  - Fallback behavior
  - Error handling

- **`conftest.py`** - Test fixtures and setup
  - Database fixtures
  - Test client setup

### Desktop Tests

- **`test_main.py`** - Desktop application tests
  - Import validation
  - System tray mocking
  - Configuration loading

## Test Database

Integration tests use an isolated SQLite database that's automatically:
- Created for each test session
- Populated with test data
- Cleaned up after tests complete

## Coverage Reports

After running tests with coverage, view reports:

- **Backend**: `backend/coverage_backend/index.html`
- **Desktop**: `desktop/coverage_desktop/index.html`

## Common Issues

### Import Errors

If you see `ModuleNotFoundError: No module named 'backend'`:
- Tests automatically adjust Python path
- Make sure you're running from the correct directory
- Use the provided batch files

### Database Errors

If integration tests fail with database errors:
- Check that SQLAlchemy models are properly imported
- Ensure database fixtures are working
- Run simple tests first to isolate the issue

### AI Service Tests

AI service tests are mocked by default:
- Don't require Ollama to be running
- Test both success and failure scenarios
- Check fallback behavior

## Development Workflow

1. **During Development**: Use `run_tests_simple.bat` frequently
2. **Before Commits**: Run `run_tests.bat` for full validation
3. **Debugging**: Run specific test files with `-v` flag
4. **Coverage**: Check HTML reports to ensure good test coverage

## Adding New Tests

### For Backend

1. Simple tests → Add to `test_simple.py`
2. Database tests → Add to `test_integration.py`  
3. New modules → Create new `test_[module].py` files

### For Desktop

1. Add tests to `test_main.py`
2. Mock external dependencies (system tray, etc.)
3. Test configuration and error handling

## Performance

- **Quick tests**: ~10 seconds
- **Full test suite**: ~30-60 seconds
- **Coverage generation**: +10-15 seconds

The testing infrastructure is designed for rapid development cycles while ensuring comprehensive validation before releases. 