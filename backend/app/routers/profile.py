from fastapi import APIRouter, Depends, HTTPException, status
from app.models import User
from app.auth import get_current_user

router = APIRouter()

@router.get("/profile")
async def read_profile(current_user: User = Depends(get_current_user)):
    return {"user": current_user}
