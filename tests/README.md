# Tests

This directory contains all the test files for the DividaFacil application.

## Test Structure

- `conftest.py` - Pytest configuration and fixtures
- `test_*.py` - Individual test files for different components

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_group_creation.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src
```

## Test Fixtures

- `test_users` - Creates 3 test users with unique emails
- `test_user` - Creates a single test user
- `unique_email` - Generates a unique email for testing

## Test Categories

- **API Tests**: Test API endpoints and responses
- **Database Tests**: Test database operations and models
- **Logic Tests**: Test business logic and calculations
- **Integration Tests**: Test end-to-end functionality

## Test Data

Tests use fixtures to create isolated test data that doesn't interfere with production data. Each test gets fresh, unique test users and data.