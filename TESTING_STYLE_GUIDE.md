# Testing Style Guide for Motivate.AI

## Overview

This guide establishes testing standards and practices for Motivate.AI to ensure consistency, reliability, and maintainability.

## Test Categories

### 1. Simple Tests (`test_simple.py`, `test_endpoints_simple.py`, `test_database_simple.py`)
- **Purpose**: Fast, lightweight tests for core functionality
- **No external dependencies**: No database, no network calls
- **Runtime**: < 5 seconds total
- **Run frequency**: Every code change

### 2. Integration Tests (`test_integration.py`)
- **Purpose**: Test component interactions with test database
- **Isolated environment**: Temporary SQLite database
- **Runtime**: 10-30 seconds
- **Run frequency**: Before commits

### 3. Live API Tests (`test_live_api.py`)
- **Purpose**: Test against running development server
- **Real environment**: Requires API at localhost:8010
- **Graceful failure**: Skip if API not available
- **Runtime**: 5-15 seconds
- **Run frequency**: During active development

## Naming Conventions

### Test Files
```
test_[component]_[category].py
```

Examples:
- `test_simple.py` - Core functionality tests
- `test_endpoints_simple.py` - Endpoint structure tests
- `test_database_simple.py` - Database model tests
- `test_live_api.py` - Live API tests
- `test_integration.py` - Integration tests

### Test Functions
```python
def test_[what_is_being_tested]_[expected_outcome]():
    """Clear description of what this test verifies"""
```

Examples:
- `test_basic_imports_succeed()`
- `test_project_creation_with_valid_data()`
- `test_api_returns_404_for_missing_project()`

## Test Structure Standards

### 1. File Header
```python
"""
Brief description of what this test file covers
Include any special requirements (e.g., "Requires API running")
"""
import pytest
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
```

### 2. Test Function Structure
```python
def test_specific_functionality():
    """
    Clear docstring explaining:
    - What is being tested
    - Expected behavior
    - Any special conditions
    """
    # Arrange - Set up test data
    test_data = {"key": "value"}
    
    # Act - Perform the action
    result = function_under_test(test_data)
    
    # Assert - Verify results
    assert result.status == "expected"
    assert "key" in result.data
```

### 3. Error Handling
```python
def test_with_external_dependency():
    """Test that gracefully handles missing dependencies"""
    try:
        # Test code that might fail
        result = external_api_call()
        assert result.success
    except ConnectionError:
        pytest.skip("External service not available")
```

## Assertion Guidelines

### Use Specific Assertions
```python
# Good
assert response.status_code == 200
assert "error" not in response.json()
assert len(projects) >= 1

# Avoid
assert response.ok
assert response.json()
assert projects
```

### Meaningful Error Messages
```python
# Good
assert hasattr(Project, 'title'), "Project model missing required 'title' field"

# Acceptable
assert hasattr(Project, 'title')
```

## Mock and Test Data Guidelines

### 1. Use Realistic Test Data
```python
# Good
project_data = {
    "title": "Organize Home Office",
    "description": "Set up desk and filing system",
    "priority": "medium"
}

# Avoid
project_data = {"title": "test", "description": "test"}
```

### 2. Mock External Services
```python
@patch('httpx.AsyncClient.post')
def test_ai_service_with_mock(mock_post):
    mock_post.return_value.json.return_value = expected_response
    result = ai_service.generate_suggestions("Test Project")
    assert len(result) > 0
```

## Performance Standards

### Test Execution Time Limits
- **Simple tests**: < 0.1 seconds per test
- **Integration tests**: < 2 seconds per test
- **Live API tests**: < 1 second per test

### Resource Usage
- **Memory**: Tests should not consume > 100MB
- **Database**: Use temporary files, clean up after tests
- **Network**: Mock external calls when possible

## Documentation Standards

### Test Coverage Documentation
```python
def test_project_creation_validation():
    """
    Tests: POST /api/v1/projects
    Validates: Required fields, data types, default values
    Edge cases: Empty title, invalid priority, missing description
    """
```

### Error Scenarios
```python
def test_project_not_found():
    """
    Tests: GET /api/v1/projects/{id}
    Expected: 404 status code with error message
    Validates: Proper error handling for missing resources
    """
```

## CI/CD Integration

### Local Testing Commands
```bash
# Quick development testing (< 30 seconds)
run_tests_simple.bat

# Full test suite with coverage (< 2 minutes)
run_tests.bat

# Specific test categories
cd backend && pytest tests/test_simple.py -v
```

### Test Organization
- **Phase 1**: Simple tests (import, structure, basic functionality)
- **Phase 2**: Integration tests (database, API with test data)
- **Phase 3**: Live tests (running development server)

## Common Patterns

### Testing API Endpoints
```python
def test_endpoint_success(api_client):
    response = api_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_endpoint_error_handling(api_client):
    response = api_client.get("/api/v1/projects/99999")
    assert response.status_code == 404
    assert "error" in response.json()
```

### Testing Database Models
```python
def test_model_creation():
    project = Project(title="Test", status="active")
    assert project.title == "Test"
    assert project.status == "active"

def test_model_validation():
    with pytest.raises(ValueError):
        Project(title="")  # Should fail validation
```

## Style Guidelines

### ASCII Only in Output
- Use `[PASS]` instead of `✓`
- Use `[FAIL]` instead of `✗`
- Use `[OK]` instead of `✅`
- Use `[ERR]` instead of `❌`

### Consistent Formatting
- 4-space indentation
- Clear variable names
- Descriptive test names
- Comprehensive docstrings

This guide ensures our testing infrastructure remains robust, maintainable, and provides clear feedback for development. 