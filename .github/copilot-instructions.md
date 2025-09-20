# DividaFácil Web - Expense Splitting Application

DividaFácil is a FastAPI web application with CLI interface for splitting expenses, similar to Splitwise. The application has both a web interface and command-line interface for managing users, groups, and expenses with installment support and notification system.

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Environment Setup and Dependencies
- **ALWAYS use Python 3.12+** (README mentions 3.13 but 3.12.3 works fine)
- Create virtual environment: `python -m venv .venv` -- takes 3 seconds
- Activate virtual environment: `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows)
- Install dependencies: `pip install -r requirements.txt` -- takes 15 seconds, NEVER CANCEL
- **NEVER CANCEL installations** - pip install can take up to 15 seconds to complete
- **Network issues**: If pip install fails with timeout/SSL errors, this indicates network connectivity issues in restricted environments

### Running the Applications
- **Web Application**: `uvicorn web_app:app --reload` or `uvicorn web_app:app --host 127.0.0.1 --port 8000`
  - Access at: `http://localhost:8000` or `http://127.0.0.1:8000`
  - Health check endpoint: `GET /healthz` returns `{"status":"ok"}`
  - **Note**: HEAD requests to main page return 500 error, but GET requests work correctly
- **CLI Application**: `python main.py`
  - Interactive command-line interface for managing expenses
  - Creates test user automatically and provides menu-driven interface

### Testing and Validation
- **Run tests**: `pytest -q` -- takes 1.7 seconds total, 20 tests pass
- **NEVER CANCEL test runs** - Set timeout to 30+ seconds minimum
- **Create test data**: `python create_test_data.py` -- takes 0.3 seconds
  - Creates sample users, groups, and expenses for testing notifications
- **Test notification system**:
  - Check overdue: `python notifications.py overdue --report-only`
  - Check upcoming: `python notifications.py upcoming --report-only`
  - Help: `python notifications.py --help`

### Code Quality and Linting
- **Black formatter**: `black --check .` or `black .` to format
  - **WARNING**: Current codebase is not formatted according to Black standards
  - Set timeout to 60+ seconds for large codebases
- **Import sorting**: `isort --check-only .` or `isort .`
- **Ruff linting**: `ruff check .`
  - **WARNING**: Current pyproject.toml has configuration issues with ruff (W503 rule)
- **ALWAYS run these before committing**: Install tools first with `pip install black ruff isort`

### Docker Support (Note: Currently Has Issues)
- **Build**: `docker build -t dividafacil .`
  - **WARNING**: Docker build currently fails in test environments due to SSL certificate issues
  - Dockerfile is present and properly configured but external network issues prevent PyPI access
  - **DO NOT rely on Docker build in restricted environments**
- **Run**: `docker run -p 8000:8000 --env LOG_LEVEL=INFO dividafacil` (when build works)

## Validation Scenarios

**ALWAYS manually validate changes by running through these complete scenarios:**

### Web Application Testing
1. Start web application: `uvicorn web_app:app --reload`
2. **Test health endpoint**: `curl http://127.0.0.1:8000/healthz` should return `{"status":"ok"}`
3. **Test main page**: Open `http://127.0.0.1:8000/` in browser or `curl http://127.0.0.1:8000/`
4. **Create users**: Use web interface to add users (test with Portuguese characters)
5. **Create groups**: Add groups with multiple users
6. **Add expenses**: Test different split types (EQUAL, EXACT, PERCENTAGE)
7. **Test installments**: Create expenses with multiple installments

### CLI Application Testing
1. Run CLI: `python main.py`
2. **Create group**: Select option 1, create a test group
3. **Add expense**: Select option 2, add expense with equal split
4. **View balances**: Select option 3, verify calculations
5. **Exit**: Select option 5 to properly exit

### Notification System Testing
1. **Create test data**: `python create_test_data.py`
2. **Test overdue notifications**: `python notifications.py overdue --report-only`
3. **Test upcoming notifications**: `python notifications.py upcoming --report-only`
4. **Verify output format**: Check for proper Portuguese text and date formatting

## Critical Configuration and Environment

### Environment Variables (Optional but Recommended)
- `APP_NAME` (default: DividaFácil)
- `DEBUG` (default: false)
- `LOG_LEVEL` (default: INFO)
- `TEMPLATES_DIR` (default: templates)
- `STATIC_DIR` (default: static)
- `DATABASE_URL` (default: SQLite for dev, PostgreSQL for production)

### Email Notification Configuration (Optional)
- `SMTP_SERVER` - SMTP server hostname
- `SMTP_PORT` - SMTP server port (default: 587)
- `SMTP_USERNAME` - SMTP username for authentication
- `SMTP_PASSWORD` - SMTP password for authentication

### Database Configuration
- **Development**: Uses SQLite database (`sqlite:///./dividafacil.db`)
- **Production**: Supports PostgreSQL via `DATABASE_URL` environment variable
- **Auto-initialization**: Database tables are created automatically on startup

## Key Projects and Structure

### Main Application Files
- `web_app.py` - FastAPI web application entry point and main routes
- `main.py` - Command-line interface application
- `notifications.py` - Notification system CLI for installment reminders
- `create_test_data.py` - Utility to create sample data for testing

### Source Code Organization
- `src/models/` - Domain entities (User, Group, Expense, Installment)
- `src/services/` - Business logic (ExpenseService, DatabaseService, NotificationService)
- `src/routers/` - FastAPI route handlers (organized by feature)
- `src/repositories/` - Data access layer (when using repository pattern)
- `src/schemas/` - Pydantic models for API validation
- `templates/` - Jinja2 HTML templates for web interface
- `static/` - CSS, JavaScript, and static assets
- `tests/` - Test suite with pytest

### Important Files to Check After Changes
- **Always check `src/services/expense_service.py`** after modifying expense calculations
- **Always check `src/models/expense.py`** after changing expense structure
- **Always check `web_app.py`** after modifying API routes
- **Always verify templates in `templates/`** after UI changes

## Common Issues and Troubleshooting

### Application Startup Issues
- **Error: Module not found**: Ensure virtual environment is activated
- **Error: Database connection**: Check DATABASE_URL format for PostgreSQL
- **Error: Port already in use**: Kill existing process or use different port
- **Network/SSL issues during pip install**: These indicate restricted environments with limited internet access

### Testing Issues
- **Tests fail**: Run `python create_test_data.py` first to ensure proper data setup
- **Import errors**: Ensure all dependencies installed with `pip install -r requirements.txt`
- **Network timeouts**: May occur in restricted environments, retry or use pre-configured environments

### Development Workflow
- **Before committing**: Run `pytest -q` to ensure tests pass
- **Before committing**: Check code formatting (though current code is not Black-formatted)
- **After model changes**: Run test suite to verify calculations
- **After UI changes**: Test both web interface and CLI functionality

## Timing Expectations and Timeouts

- **Virtual environment creation**: 3 seconds - Set timeout: 30+ seconds
- **Dependency installation**: 15 seconds - Set timeout: 60+ seconds, NEVER CANCEL
- **Test execution**: 1.7 seconds (20 tests) - Set timeout: 30+ seconds, NEVER CANCEL
- **Test data creation**: 0.3 seconds - Set timeout: 30+ seconds
- **Application startup**: 2-3 seconds - Set timeout: 30+ seconds
- **Code formatting (Black)**: 1 second - Set timeout: 60+ seconds for large codebases

**CRITICAL**: NEVER CANCEL any build, test, or installation commands. Always wait for completion or set appropriate timeouts.