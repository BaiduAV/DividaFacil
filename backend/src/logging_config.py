import logging
import logging.config
import os
import json
from typing import Optional


def configure_logging(level: Optional[str] = None) -> None:
    """Configure basic structured logging for the app.

    Use LOG_LEVEL env var or provided level.
    """
    log_level = (level or os.getenv("LOG_LEVEL") or "INFO").upper()
    use_json = os.getenv("LOG_FORMAT", "text").lower() == "json"

    def json_formatter(record: logging.LogRecord) -> str:  # pragma: no cover (format helper)
        payload = {
            "ts": record.__dict__.get("asctime") or None,
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = True
        return json.dumps(payload, ensure_ascii=False)

    formatters = {
        "default": {
            "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        }
    }
    if use_json:
        formatters["json"] = {"()": "logging.Formatter", "fmt": "%(message)s"}

    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json" if use_json else "default",
            "level": log_level,
        }
    }

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": formatters,
            "handlers": handlers,
            "root": {"handlers": ["console"], "level": log_level},
        }
    )
    if use_json:
        # Monkey patch emit to build JSON line on the fly
        orig_format = logging.StreamHandler.format

        def _format(self, record):  # type: ignore
            if self.formatter and self.formatter._fmt == "%(message)s":  # noqa: SLF001
                return json_formatter(record)
            return orig_format(self, record)

        logging.StreamHandler.format = _format  # type: ignore
