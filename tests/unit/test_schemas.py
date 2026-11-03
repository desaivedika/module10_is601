"""Unit tests for the Pydantic user schemas."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models.user import User
from app.schemas.user import UserCreate, UserRead


def test_valid_user_create():
    user = UserCreate(username="alice", email="alice@example.com", password="SecurePass123")
    assert user.username == "alice"
    assert user.email == "alice@example.com"


@pytest.mark.parametrize("email", ["not-an-email", "alice@", "@example.com", "alice.example.com"])
def test_invalid_email_rejected(email):
    with pytest.raises(ValidationError):
        UserCreate(username="alice", email=email, password="SecurePass123")


@pytest.mark.parametrize("password", ["short1", "allletters", "12345678", "a" * 65 + "1"])
def test_weak_or_invalid_password_rejected(password):
    with pytest.raises(ValidationError):
        UserCreate(username="alice", email="alice@example.com", password=password)


@pytest.mark.parametrize("username", ["ab", "a" * 51, "bad name", "bad!name"])
def test_invalid_username_rejected(username):
    with pytest.raises(ValidationError):
        UserCreate(username=username, email="alice@example.com", password="SecurePass123")


def test_user_read_from_orm_object_excludes_password():
    user = User(id=1, username="alice", email="alice@example.com",
                created_at=datetime.now(timezone.utc))
    user.set_password("SecurePass123")

    data = UserRead.model_validate(user).model_dump()

    assert data["username"] == "alice"
    assert data["id"] == 1
    assert "password" not in data
    assert "password_hash" not in data


def test_user_model_password_helpers():
    user = User(username="bob", email="bob@example.com")
    user.set_password("SecurePass123")
    assert user.password_hash != "SecurePass123"
    assert user.check_password("SecurePass123") is True
    assert user.check_password("wrong-pass1") is False
    assert "bob" in repr(user)