from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int
