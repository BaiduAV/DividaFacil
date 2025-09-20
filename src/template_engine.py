from fastapi.templating import Jinja2Templates
from fastapi import Request

from src.settings import get_settings
from src.filters import brl, datebr, split_label, monthbr
from src.i18n import get_i18n_service

_settings = get_settings()
_i18n = get_i18n_service()

templates = Jinja2Templates(directory=_settings.TEMPLATES_DIR)

# Globals
templates.env.globals["APP_NAME"] = _settings.APP_NAME

# I18n functions
def _t(key: str, locale: str = None, **kwargs) -> str:
    """Template function for translation."""
    if locale is None:
        locale = _settings.DEFAULT_LOCALE
    return _i18n.t(key, locale, **kwargs)

def _get_locale() -> str:
    """Template function to get current locale."""
    return _settings.DEFAULT_LOCALE

def _get_available_locales() -> list:
    """Template function to get available locales."""
    return _i18n.get_available_locales()

templates.env.globals["t"] = _t
templates.env.globals["get_locale"] = _get_locale
templates.env.globals["get_available_locales"] = _get_available_locales

# Filters
templates.env.filters["brl"] = brl
templates.env.filters["datebr"] = datebr
templates.env.filters["split_label"] = split_label
templates.env.filters["monthbr"] = monthbr
