from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, Annotated

from sqlmodel import Field, Relationship, SQLModel

from .common import TableRecordCreatedDateTime, TableRecordUpdatedDateTime
from .link import UserRoleLink
from .rule import UserRuleTreePublic

if TYPE_CHECKING:
    from .role import Role


UsernameField = Annotated[str, Field(min_length=2, max_length=50)]
FullNameField = Annotated[str, Field(max_length=50)]
PasswordField = Annotated[str, Field(min_length=8, max_length=40)]


class UserSource(str, Enum):
    system = "system"
    signup = "signup"


# Shared properties
class UserBase(SQLModel):
    username: UsernameField = Field(unique=True, index=True)
    is_active: bool = Field(default=True, index=True)
    is_superuser: bool = Field(default=False, index=True)
    full_name: FullNameField | None = Field(default=None, index=True)
    source: UserSource = Field(default=UserSource.system)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: PasswordField
    roles: list[int] | None = Field(default=None)


class UserRegister(SQLModel):
    username: UsernameField
    password: PasswordField
    full_name: FullNameField | None = Field(default=None)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    username: UsernameField | None = Field(default=None)
    password: PasswordField | None = Field(default=None)
    roles: list[int] | None = Field(default=None)


# Properties to receive via API on update me, all are optional
class UserUpdateMe(SQLModel):
    full_name: FullNameField | None = Field(default=None)
    password: PasswordField | None = Field(default=None)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    last_login_at: datetime | None = Field(default=None, index=True)
    created_at: TableRecordCreatedDateTime
    updated_at: TableRecordUpdatedDateTime
    roles: list["Role"] = Relationship(back_populates="users", link_model=UserRoleLink)


class UserRole(SQLModel):
    id: int
    name: str


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: int
    last_login_at: datetime | None = Field(default=None)
    created_at: datetime
    updated_at: datetime
    roles: list[UserRole] | None = Field(default=None)


class UsersPublic(SQLModel):
    data: list[UserPublic]
    total: int


class UserMePublic(UserPublic):
    rules: list[UserRuleTreePublic] = Field(default=[])


class UserBehaviorCount(SQLModel):
    dt: date
    behavior: str
    count: int


class UserMenuCount(SQLModel):
    menu: str
    count: int


class UserHome(SQLModel):
    logins_1w: int = Field(default=0)
    previous_logins_1w: int = Field(default=0)
    logins_1m: int = Field(default=0)
    previous_logins_1m: int = Field(default=0)
    operations_1w: int = Field(default=0)
    previous_operations_1w: int = Field(default=0)
    operations_1m: int = Field(default=0)
    previous_operations_1m: int = Field(default=0)
    behavior_1w: list[UserBehaviorCount] | None = Field(default=None)
    behavior_1m: list[UserBehaviorCount] | None = Field(default=None)
    menus: list[UserMenuCount] | None = Field(default=None)
