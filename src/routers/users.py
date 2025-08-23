from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse

from src.services.database_service import DatabaseService

router = APIRouter()


@router.post("/users")
async def create_user(name: str = Form(...), email: str = Form(...)):
    DatabaseService.create_user(name, email)
    return RedirectResponse("/", status_code=303)
