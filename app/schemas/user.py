"""Pydantic schemas for creating and reading users."""

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Fields shared by every user schema."""

    username: str = Field(min_length=3, max_length=50, examples=["alice"])
    email: EmailStr = Field(examples=["alice@example.com"])

    @field_validator("username")
    @classmethod
    def username_is_valid(cls, value: str) -> str:
        """Allow only letters, digits, dots, hyphens and underscores."""
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", value):
            raise ValueError("username may only contain letters, digits, '.', '-' and '_'")
        return value


class UserCreate(UserBase):
    """Data a client sends to register. Includes the plain-text password."""

    password: str = Field(min_length=8, max_length=64, examples=["SecurePass123"])

    @field_validator("password")
    @classmethod
    def password_is_strong(cls, value: str) -> str:
        """Require at least one letter and one digit."""
        if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
            raise ValueError("password must contain at least one letter and one digit")
        return value


class UserRead(UserBase):
    """Data returned to clients. Never includes the password or its hash."""

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)