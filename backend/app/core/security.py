from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from app.core.config import settings
from app.models.security import ApiPermission

password_hash = PasswordHash(
    (
        Argon2Hasher(),
        BcryptHasher(),
    )
)


ALGORITHM = "HS256"


def create_access_token(subject: str | Any, scopes: Sequence[str] = []) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {"exp": expire, "sub": str(subject), "scopes": scopes}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(
    plain_password: str, hashed_password: str
) -> tuple[bool, str | None]:
    return password_hash.verify_and_update(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


# API权限
class ApiPermissions(Enum):
    # rules
    V1_RULES = ApiPermission(path=f"{settings.API_V1_STR}/rules/")
    # roles
    V1_ROLES = ApiPermission(path=f"{settings.API_V1_STR}/roles/")
    # users
    V1_USERS = ApiPermission(path=f"{settings.API_V1_STR}/users/")
    V1_USERS_ME = ApiPermission(path=f"{settings.API_V1_STR}/users/me")
    V1_USERS_HOME = ApiPermission(path=f"{settings.API_V1_STR}/users/home")
    # operation-logs
    V1_OPERATION_LOGS = ApiPermission(path=f"{settings.API_V1_STR}/operation-logs/")


# OAuth2 作用域
oauth2_scopes = {}
for p in ApiPermissions:
    oauth2_scopes[p.value.create.name] = p.value.create.description
    oauth2_scopes[p.value.read.name] = p.value.read.description
    oauth2_scopes[p.value.update.name] = p.value.update.description
    oauth2_scopes[p.value.delete.name] = p.value.delete.description
