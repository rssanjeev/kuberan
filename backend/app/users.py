from app.models import User
from passlib.context import CryptContext
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_by_username(username: str) -> Optional[User]:
    return await User.find_one(User.username == username)

async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def create_user(username: str, email: str, password: str, full_name: str = None) -> User:
    hashed_pw = await hash_password(password)
    user = User(username=username, email=email, full_name=full_name, hashed_password=hashed_pw)
    await user.insert()
    return user
