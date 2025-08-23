import os
from functools import lru_cache


class Settings:
    """Lightweight settings without external deps.

    Values can be overridden via environment variables.
    """

    APP_NAME: str = "DividaFácil"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in {"1", "true", "yes", "on"}
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    TEMPLATES_DIR: str = os.getenv("TEMPLATES_DIR", "templates")
    STATIC_DIR: str = os.getenv("STATIC_DIR", "static")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
