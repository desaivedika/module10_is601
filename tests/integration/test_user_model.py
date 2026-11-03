"""Integration tests for the User model against a real PostgreSQL database."""

import pytest
from sqlalchemy.exc import IntegrityError

from app import crud
from app.models.user import User
from app.schemas.user import UserCreate


def new_user(username="alice", email="alice@example.com", password="SecurePass123"):
    return UserCreate(username=username, email=email, password=password)


def test_create_user_stores_hash_not_plain_password(db):
    user = crud.create_user(db, new_user())

    assert user.id is not None
    assert user.password_hash != "SecurePass123"
    assert user.check_password("SecurePass123")
    assert user.created_at is not None


def test_user_can_be_read_back(db):
    created = crud.create_user(db, new_user())

    assert crud.get_user(db, created.id).username == "alice"
    assert crud.get_user_by_username(db, "alice").email == "alice@example.com"
    assert crud.get_user(db, 9999) is None


def test_duplicate_username_rejected(db):
    crud.create_user(db, new_user())
    with pytest.raises(crud.DuplicateUserError):
        crud.create_user(db, new_user(email="other@example.com"))


def test_duplicate_email_rejected(db):
    crud.create_user(db, new_user())
    with pytest.raises(crud.DuplicateUserError):
        crud.create_user(db, new_user(username="alice2"))


def test_database_unique_constraint_enforced_directly(db):
    """The UNIQUE constraint lives in the database itself, not just in our code."""
    db.add(User(username="carol", email="carol@example.com", password_hash="x"))
    db.commit()
    db.add(User(username="carol", email="carol2@example.com", password_hash="y"))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_failed_insert_does_not_break_session(db):
    crud.create_user(db, new_user())
    with pytest.raises(crud.DuplicateUserError):
        crud.create_user(db, new_user())
    # Session is still usable after the rollback
    crud.create_user(db, new_user(username="bob", email="bob@example.com"))
    assert crud.get_user_by_username(db, "bob") is not None