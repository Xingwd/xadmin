import string

from app.utils import generate_secure_password


def test_generate_secure_password_default_length() -> None:
    password = generate_secure_password()
    # Default: 8 chars + 6 nums + 2 symbols = 16 characters
    assert len(password) == 16


def test_generate_secure_password_custom_length() -> None:
    password = generate_secure_password(chars=4, nums=3, symbols=1)
    assert len(password) == 8


def test_generate_secure_password_contains_letters() -> None:
    password = generate_secure_password(chars=10, nums=0, symbols=0)
    assert len(password) == 10
    assert all(c in string.ascii_letters for c in password)


def test_generate_secure_password_contains_digits() -> None:
    password = generate_secure_password(chars=0, nums=10, symbols=0)
    assert len(password) == 10
    assert all(c in string.digits for c in password)


def test_generate_secure_password_contains_symbols() -> None:
    password = generate_secure_password(chars=0, nums=0, symbols=8)
    assert len(password) == 8
    assert all(c in "!@#$%^&*" for c in password)


def test_generate_secure_password_contains_all_types() -> None:
    password = generate_secure_password(chars=8, nums=6, symbols=2)
    has_letters = any(c in string.ascii_letters for c in password)
    has_digits = any(c in string.digits for c in password)
    has_symbols = any(c in "!@#$%^&*" for c in password)
    assert has_letters
    assert has_digits
    assert has_symbols


def test_generate_secure_password_randomness() -> None:
    password1 = generate_secure_password()
    password2 = generate_secure_password()
    assert password1 != password2


def test_generate_secure_password_zero_length() -> None:
    password = generate_secure_password(chars=0, nums=0, symbols=0)
    assert len(password) == 0
    assert password == ""
