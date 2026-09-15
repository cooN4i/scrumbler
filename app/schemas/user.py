import re
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Пароль должен содержать не менее 8 символов")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву (A-Z)")
        if not re.search(r"[a-z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву (a-z)")
        if not re.search(r"\d", v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру (0-9)")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_+=\[\]\\/`~]", v):
            raise ValueError("Пароль должен содержать хотя бы один специальный символ (!@#$%^&*...)")
        return v


class UserLogin(UserBase):
    """Schema for user login. Does not re-validate password complexity on existing passwords."""
    password: str = Field(..., min_length=1, max_length=100)


class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    sub: str | None = None
