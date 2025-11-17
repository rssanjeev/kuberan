"""
Authentication and user management models.

Models:
- User: User authentication and profile data
"""

from beanie import Document
from pydantic import EmailStr
from typing import Optional


class User(Document):
    """User authentication and profile information."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    hashed_password: str
    disabled: bool = False

    class Settings:
        name = "users"
