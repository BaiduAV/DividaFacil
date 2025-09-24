"""Application constants for better maintainability."""

from decimal import Decimal
from typing import Final

# Expense calculation constants
MIN_BALANCE_THRESHOLD: Final[Decimal] = Decimal("0.01")
DECIMAL_PLACES: Final[int] = 2
PERCENTAGE_BASE: Final[Decimal] = Decimal("100.0")

# Split type constants
SPLIT_EQUAL: Final[str] = "EQUAL"
SPLIT_EXACT: Final[str] = "EXACT"
SPLIT_PERCENTAGE: Final[str] = "PERCENTAGE"

# Application constants
API_PREFIX: Final[str] = "/api/"
SESSION_COOKIE_NAME: Final[str] = "session_id"
HEALTH_CHECK_RESPONSE: Final[dict] = {"status": "ok"}

# Authentication constants
LOGIN_REDIRECT_URL: Final[str] = "/login"
REDIRECT_STATUS_CODE: Final[int] = 303

# Database constants
DEFAULT_DATABASE_URL: Final[str] = "sqlite:///./dividafacil.db"

# Template constants
DEFAULT_TEMPLATE_DIR: Final[str] = "templates"
DEFAULT_STATIC_DIR: Final[str] = "static"

# Error messages
ERROR_USER_NOT_FOUND: Final[str] = "User not found"
ERROR_GROUP_NOT_FOUND: Final[str] = "Group not found"
ERROR_EXPENSE_NOT_FOUND: Final[str] = "Expense not found"
ERROR_INVALID_SPLIT_TYPE: Final[str] = "Invalid split type"
ERROR_NO_USERS_TO_SPLIT: Final[str] = "No users to split among"
ERROR_NO_SPLIT_VALUES: Final[str] = "No split values provided"

# Logging constants
DEFAULT_LOG_LEVEL: Final[str] = "INFO"
LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# CLI constants
CLI_PROMPT_COLOR: Final[str] = "blue"
CLI_ERROR_COLOR: Final[str] = "red"
CLI_SUCCESS_COLOR: Final[str] = "green"
CLI_WARNING_COLOR: Final[str] = "yellow"
