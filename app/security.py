"""Password hashing and verification using bcrypt."""

import bcrypt


def hash_password(plain_password: str) -> str:
    """Return a salted bcrypt hash of the plain-text password."""
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Return True if the plain-text password matches the stored hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        # Raised when the stored value is not a valid bcrypt hash
        return False