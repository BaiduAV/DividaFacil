from fastapi import APIRouter, Form, Request, HTTPException
from fastapi.responses import RedirectResponse

from src.services.database_service import DatabaseService
from src.services.session_manager import SessionManager

router = APIRouter()


@router.post("/users")
async def create_user(request: Request, name: str = Form(...), email: str = Form(...)):
    # Check if user is authenticated
    user_id = SessionManager.get_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    DatabaseService.create_user(name, email)
    return RedirectResponse("/", status_code=303)
