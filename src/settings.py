import os
from functools import lru_cache


class Settings:
    """Lightweight settings without external deps.

    Values can be overridden via environment variables.
    """

    APP_NAME: str = "DividaFácil"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in {"1", "true", "yes", "on"}
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SESSION_SECRET_KEY: str = os.getenv(
        "SESSION_SECRET_KEY", "your-secret-key-change-in-production"
    )

    STATIC_DIR: str = os.getenv("STATIC_DIR", "static")
    LOCALES_DIR: str = os.getenv("LOCALES_DIR", "locales")
    DEFAULT_LOCALE: str = os.getenv("DEFAULT_LOCALE", "pt-BR")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
