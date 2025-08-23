from fastapi.templating import Jinja2Templates

from src.settings import get_settings
from src.filters import brl, datebr, split_label, monthbr

_settings = get_settings()

templates = Jinja2Templates(directory=_settings.TEMPLATES_DIR)
# Globals
templates.env.globals["APP_NAME"] = _settings.APP_NAME
# Filters
templates.env.filters["brl"] = brl
templates.env.filters["datebr"] = datebr
templates.env.filters["split_label"] = split_label
templates.env.filters["monthbr"] = monthbr
