from fastapi import APIRouter, Form, Request, HTTPException
from fastapi.responses import RedirectResponse

from src.services.database_service import DatabaseService
from src.auth import get_current_user_from_session

router = APIRouter()


@router.post("/users")
async def create_user(request: Request, name: str = Form(...), email: str = Form(...)):
    # Check if user is authenticated
    current_user = get_current_user_from_session(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    DatabaseService.create_user(name, email)
    return RedirectResponse("/", status_code=303)
