"""Unit tests for password hashing."""

import pytest

from app.security import hash_password, verify_password


def test_hash_is_not_plain_text():
    hashed = hash_password("SecurePass123")
    assert hashed != "SecurePass123"
    assert hashed.startswith("$2")  # bcrypt hash prefix


def test_verify_correct_password():
    hashed = hash_password("SecurePass123")
    assert verify_password("SecurePass123", hashed) is True


@pytest.mark.parametrize("wrong", ["securepass123", "SecurePass124", "", "SecurePass123 "])
def test_verify_wrong_password(wrong):
    hashed = hash_password("SecurePass123")
    assert verify_password(wrong, hashed) is False


def test_same_password_gives_different_hashes():
    """bcrypt adds a random salt, so two hashes of the same password differ."""
    assert hash_password("SecurePass123") != hash_password("SecurePass123")


def test_verify_against_invalid_hash_returns_false():
    assert verify_password("SecurePass123", "not-a-real-hash") is False