# Testing Guide - Career Automation System

## Table of Contents
1. [Quick Start](#quick-start)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Writing Tests](#writing-tests)
5. [Coverage Requirements](#coverage-requirements)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Troubleshooting](#troubleshooting)

## Quick Start

```bash
# Install dependencies
make install

# Run all tests
make test

# Run with coverage
make coverage

# Run specific test categories
make test-unit      # Unit tests only
make test-int       # Integration tests only
make test-email     # Email tests only

# Format and lint before committing
make dev-commit
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures
├── test_email_auth.py         # Email authentication tests
├── test_job_discovery.py      # Job discovery tests
├── test_application_generation.py  # Application generation tests
├── test_database.py           # Database operation tests
├── test_api_integration.py    # API integration tests
└── fixtures/                  # Test data files
    ├── sample_job.json
    ├── sample_resume.json
    └── test_credentials.env
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_email_auth.py

# Run specific test class
pytest tests/test_email_auth.py::TestEmailAuthentication

# Run specific test method
pytest tests/test_email_auth.py::TestEmailAuthentication::test_env_loading
```

### Test Categories (Markers)

Tests are categorized with markers for selective execution:

```bash
# Run only unit tests (fast, isolated)
pytest -m unit

# Run only integration tests (may need external services)
pytest -m integration

# Run email-related tests
pytest -m email

# Run database tests
pytest -m database

# Run critical tests that must pass
pytest -m critical

# Exclude slow tests
pytest -m "not slow"
```

### Coverage Reports

```bash
# Generate coverage report
pytest --cov=. --cov-report=html --cov-report=term

# View HTML coverage report
open htmlcov/index.html

# Coverage with minimum threshold (fails if below 70%)
pytest --cov=. --cov-fail-under=70

# Coverage for specific module
pytest --cov=email_auth --cov-report=term-missing
```

## Writing Tests

### Test Structure Template

```python
"""
Tests for [module name]
"""

import pytest
from unittest.mock import Mock, patch
from your_module import YourClass


class TestYourFeature:
    """Test suite for [feature]"""
    
    @pytest.fixture
    def setup_data(self):
        """Setup test data"""
        return {
            'key': 'value'
        }
    
    @pytest.mark.unit
    def test_basic_functionality(self, setup_data):
        """Test basic feature works"""
        # Arrange
        expected = 'expected_result'
        
        # Act
        result = your_function(setup_data)
        
        # Assert
        assert result == expected
    
    @pytest.mark.integration
    @pytest.mark.email
    def test_email_integration(self):
        """Test email integration"""
        with patch('smtplib.SMTP') as mock_smtp:
            # Test implementation
            pass
```

### Common Test Patterns

#### Mocking External Services

```python
@patch('requests.get')
def test_api_call(mock_get):
    """Test API call with mock"""
    mock_get.return_value.json.return_value = {'status': 'success'}
    result = fetch_data()
    assert result['status'] == 'success'
```

#### Testing Database Operations

```python
@pytest.fixture
def test_db(tmp_path):
    """Create temporary test database"""
    db_path = tmp_path / "test.db"
    # Initialize database
    return db_path

def test_database_insert(test_db):
    """Test database insertion"""
    conn = sqlite3.connect(test_db)
    # Test operations
    conn.close()
```

#### Testing with Environment Variables

```python
def test_with_env(monkeypatch):
    """Test with mocked environment variables"""
    monkeypatch.setenv('EMAIL_ADDRESS', 'test@example.com')
    assert os.getenv('EMAIL_ADDRESS') == 'test@example.com'
```

## Coverage Requirements

### Minimum Coverage Targets

- **Overall**: 70% minimum
- **Core modules**: 80% minimum
  - `email_auth.py`: 85%
  - `job_discovery.py`: 80%
  - `application_generator.py`: 80%
- **Utilities**: 60% minimum
- **Tests**: Excluded from coverage

### Coverage Configuration

See `pytest.ini` for coverage settings:

```ini
[coverage:run]
source = .
omit = 
    */tests/*
    */test_*.py
    */__pycache__/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## CI/CD Pipeline

### GitHub Actions Workflow

The CI pipeline runs automatically on:
- Every push to `main` or `develop`
- Every pull request
- Daily at 2 AM UTC (scheduled tests)

#### Pipeline Stages

1. **Linting** - Code style checks
2. **Type Checking** - MyPy type validation
3. **Security** - Bandit security scanning
4. **Unit Tests** - Fast, isolated tests
5. **Integration Tests** - External service tests
6. **Coverage** - Report to Codecov
7. **Documentation** - Build and deploy docs

### Pre-commit Hooks

Install pre-commit hooks:

```bash
make pre-commit
```

Hooks run automatically before each commit:
- **black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking
- **bandit** - Security checks
- **pytest** - Quick test run

### Local CI Simulation

Run full CI pipeline locally:

```bash
make ci-local
```

## Troubleshooting

### Common Issues

#### 1. Import Errors in Tests

```python
# Add to test file
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

#### 2. Email Authentication Failures

```bash
# Check credentials
python3 test_gmail_auth.py

# Verify .env file
cat .env | grep EMAIL
```

#### 3. Database Lock Errors

```bash
# Close all database connections
pkill -f sqlite3

# Remove lock files
rm *.db-journal *.db-wal
```

#### 4. Coverage Not Meeting Threshold

```bash
# Find uncovered lines
pytest --cov=. --cov-report=term-missing

# Generate detailed HTML report
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### Debug Mode

Run tests in debug mode:

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger at specific point
import pdb; pdb.set_trace()

# Use IPython debugger
pytest --pdbcls=IPython.terminal.debugger:TerminalPdb
```

### Test Performance

```bash
# Show slowest tests
pytest --durations=10

# Run tests in parallel
pytest -n auto

# Profile test execution
pytest --profile
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Names**: Test names should describe what they test
3. **AAA Pattern**: Arrange, Act, Assert
4. **One Assert**: Prefer one logical assert per test
5. **Mock External**: Always mock external services in unit tests
6. **Use Fixtures**: Share setup code via fixtures
7. **Mark Tests**: Use appropriate markers for categorization
8. **Document Why**: Comments should explain why, not what

## Continuous Improvement

- Review coverage reports weekly
- Add tests for every bug fix
- Refactor tests when they become complex
- Update this guide as patterns evolve

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Python Testing Best Practices](https://realpython.com/python-testing/)
- [Test-Driven Development](https://testdriven.io/)