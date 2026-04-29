from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


# ─────────────────────────────────────────
# Request schemas — what the client sends
# ─────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: str = "buyer"

    @field_validator("username")
    @classmethod
    def username_valid(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(v) > 50:
            raise ValueError("Username must be less than 50 characters")
        if not v.isalnum():
            raise ValueError("Username must contain only letters and numbers")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_valid(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("role")
    @classmethod
    def role_valid(cls, v):
        if v not in ["buyer", "seller"]:
            raise ValueError("Role must be buyer or seller")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ─────────────────────────────────────────
# Response schemas — what we send back
# ─────────────────────────────────────────

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    is_active: bool
    created_at: datetime

    # This tells Pydantic to read from SQLAlchemy model attributes
    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
