"""Database operations for users."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


class DuplicateUserError(Exception):
    """Raised when the username or email is already registered."""


def create_user(db: Session, user_in: UserCreate) -> User:
    """Create a user, storing only a hash of the password."""
    user = User(username=user_in.username, email=user_in.email)
    user.set_password(user_in.password)
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateUserError("Username or email already exists") from exc
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> User | None:
    """Return the user with this id, or None."""
    return db.get(User, user_id)


def get_user_by_username(db: Session, username: str) -> User | None:
    """Return the user with this username, or None."""
    return db.scalars(select(User).where(User.username == username)).first()