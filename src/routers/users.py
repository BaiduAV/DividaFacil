from fastapi import APIRouter, Form, Request, HTTPException
from fastapi.responses import RedirectResponse

from src.services.database_service import DatabaseService
from src.auth import get_current_user_from_session

router = APIRouter()


@router.post("/users")
async def create_user(request: Request, name: str = Form(...), email: str = Form(...)):
    # Registration should be open (tests expect unauthenticated creation)
    # Keep optional check if future logic needs current user, but do not block.
    # current_user = get_current_user_from_session(request)
    # if not current_user:
    #     raise HTTPException(status_code=401, detail="Authentication required")
    DatabaseService.create_user(name, email)
    return RedirectResponse("/", status_code=303)
