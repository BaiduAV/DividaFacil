import logging
import logging.config
import os


def configure_logging(level: str = None) -> None:
    """Configure basic structured logging for the app.

    Use LOG_LEVEL env var or provided level.
    """
    log_level = (level or os.getenv("LOG_LEVEL") or "INFO").upper()
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": log_level,
                }
            },
            "root": {
                "handlers": ["console"],
                "level": log_level,
            },
        }
    )
