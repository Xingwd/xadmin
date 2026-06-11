import time
from datetime import datetime, timezone

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    ALGORITHM,
    ApiPermissions,
    create_access_token,
    decode_token,
    get_password_hash,
    oauth2_scopes,
    password_hash,
    verify_password,
)
from app.models.security import Permission


def test_get_password_hash() -> None:
    password = "testpassword123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert isinstance(hashed, str)
    assert len(hashed) > 0


def test_verify_password_correct() -> None:
    password = "testpassword123"
    hashed = get_password_hash(password)
    verified, _ = verify_password(password, hashed)
    assert verified is True


def test_verify_password_incorrect() -> None:
    password = "testpassword123"
    hashed = get_password_hash(password)
    verified, _ = verify_password("wrongpassword", hashed)
    assert verified is False


def test_verify_password_with_bcrypt_hash() -> None:
    # Test with a known bcrypt hash format
    password = "testpassword123"
    bcrypt_hash = password_hash.hash(password)
    verified, _ = verify_password(password, bcrypt_hash)
    assert verified is True


def test_verify_password_returns_updated_hash() -> None:
    password = "testpassword123"
    hashed = get_password_hash(password)
    verified, updated_hash = verify_password(password, hashed)
    assert verified is True
    # When hash is already up to date, updated_hash should be None
    assert updated_hash is None


def test_create_access_token() -> None:
    subject = "user123"
    token = create_access_token(subject)
    assert isinstance(token, str)
    assert len(token) > 0

    # Decode and verify payload
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == subject
    assert "exp" in payload
    assert "scopes" in payload
    assert payload["scopes"] == []


def test_create_access_token_with_scopes() -> None:
    subject = "user123"
    scopes = ["read", "write"]
    token = create_access_token(subject, scopes=scopes)

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == subject
    assert payload["scopes"] == scopes


def test_create_access_token_expiration() -> None:
    subject = "user123"
    token = create_access_token(subject)

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    exp_timestamp = payload["exp"]
    now_timestamp = int(time.time())
    # Token should expire in roughly ACCESS_TOKEN_EXPIRE_MINUTES
    expected_exp = now_timestamp + settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    # Allow 10 seconds tolerance for test execution time
    assert abs(exp_timestamp - expected_exp) < 10


def test_decode_token() -> None:
    subject = "user123"
    scopes = ["read"]
    token = create_access_token(subject, scopes=scopes)

    decoded = decode_token(token)
    assert decoded["sub"] == subject
    assert decoded["scopes"] == scopes
    assert "exp" in decoded


def test_decode_token_invalid() -> None:
    with pytest.raises(jwt.exceptions.InvalidTokenError):
        decode_token("invalid.token.here")


def test_decode_token_wrong_secret() -> None:
    token = jwt.encode(
        {"sub": "user123", "exp": datetime.now(timezone.utc)},
        "wrong_secret",
        algorithm=ALGORITHM,
    )
    with pytest.raises(jwt.exceptions.InvalidTokenError):
        decode_token(token)


class TestApiPermissions:
    def test_api_permission_create(self) -> None:
        perm = ApiPermissions.V1_RULES.value.create
        assert isinstance(perm, Permission)
        assert perm.name == f"{settings.API_V1_STR}/rules/:create"
        assert perm.description == f"Create on {settings.API_V1_STR}/rules/"

    def test_api_permission_read(self) -> None:
        perm = ApiPermissions.V1_USERS.value.read
        assert isinstance(perm, Permission)
        assert perm.name == f"{settings.API_V1_STR}/users/:read"
        assert perm.description == f"Read on {settings.API_V1_STR}/users/"

    def test_api_permission_update(self) -> None:
        perm = ApiPermissions.V1_ROLES.value.update
        assert isinstance(perm, Permission)
        assert perm.name == f"{settings.API_V1_STR}/roles/:update"
        assert perm.description == f"Update on {settings.API_V1_STR}/roles/"

    def test_api_permission_delete(self) -> None:
        perm = ApiPermissions.V1_OPERATION_LOGS.value.delete
        assert isinstance(perm, Permission)
        assert perm.name == f"{settings.API_V1_STR}/operation-logs/:delete"
        assert perm.description == f"Delete on {settings.API_V1_STR}/operation-logs/"

    def test_oauth2_scopes_populated(self) -> None:
        # oauth2_scopes should contain entries for all CRUD operations on all ApiPermissions
        assert len(oauth2_scopes) > 0
        # Check that a few expected scopes exist
        create_scope = ApiPermissions.V1_RULES.value.create.name
        read_scope = ApiPermissions.V1_RULES.value.read.name
        assert create_scope in oauth2_scopes
        assert read_scope in oauth2_scopes
        assert (
            oauth2_scopes[create_scope]
            == ApiPermissions.V1_RULES.value.create.description
        )

    def test_api_permissions_values_are_api_permission_instances(self) -> None:
        from app.models.security import ApiPermission

        for p in ApiPermissions:
            assert isinstance(p.value, ApiPermission)
