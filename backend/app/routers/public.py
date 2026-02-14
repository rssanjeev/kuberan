from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.users import create_user, get_user_by_username

router = APIRouter()

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None

@router.post("/register")
async def register(user: UserRegister):
    existing = await get_user_by_username(user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user_obj = await create_user(user.username, user.email, user.password, user.full_name)
    return {"username": user_obj.username, "email": user_obj.email, "full_name": user_obj.full_name}

@router.get("/public")
def public_endpoint():
    return {"message": "This is a public endpoint."}
