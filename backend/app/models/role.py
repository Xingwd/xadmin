from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .common import TableRecordCreatedDateTime, TableRecordUpdatedDateTime
from .link import RoleRuleLink, UserRoleLink

if TYPE_CHECKING:
    from .rule import Rule
    from .user import User


# Shared properties
class RoleBase(SQLModel):
    name: str = Field(min_length=1, max_length=100, unique=True, index=True)


# Properties to receive on creation
class RoleCreate(RoleBase):
    permissions: list[int] | None = Field(default=None)
    users: list[int] | None = Field(default=None)


# Properties to receive on update
class RoleUpdate(RoleBase):
    permissions: list[int] | None = Field(default=None)
    users: list[int] | None = Field(default=None)


# Database model, database table inferred from class name
class Role(RoleBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: TableRecordCreatedDateTime
    updated_at: TableRecordUpdatedDateTime
    permissions: list["Rule"] = Relationship(
        back_populates="roles", link_model=RoleRuleLink
    )
    users: list["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)


class RoleRule(SQLModel):
    id: int
    name: str
    title: str
    parent_id: int | None


class RoleUser(SQLModel):
    id: int
    username: str


# Properties to return via API
class RolePublic(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    permissions: list[RoleRule] | None = Field(default=None)
    users: list[RoleUser] | None = Field(default=None)


class RolesPublic(SQLModel):
    data: list[RolePublic]
