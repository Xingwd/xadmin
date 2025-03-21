from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .common import TableRecordCreatedDateTime, TableRecordUpdatedDateTime
from .link import RoleRuleLink

if TYPE_CHECKING:
    from .role import Role


class RuleType(str, Enum):
    menu_dir = "menu_dir"  # 菜单目录
    menu_item = "menu_item"  # 菜单项
    permission = "permission"  # 权限，绑定后端接口权限


class MenuItemType(str, Enum):
    tab = "tab"
    link = "link"
    iframe = "iframe"


# Shared properties
class RuleBase(SQLModel):
    parent_id: int | None = Field(default=None)
    type: RuleType
    title: str = Field(index=True)
    name: str = Field(
        unique=True,
        description="将注册为前端路由名称，同时用作前后端鉴权。当type=RuleType.permission时，name和对应的后端接口权限名一致。",
    )
    path: str | None = Field(default=None)
    icon: str | None = Field(default=None)
    menu_item_type: MenuItemType | None = Field(default=None)
    url: str | None = Field(default=None)
    component: str | None = Field(default=None)
    remark: str | None = Field(default=None)
    cache: bool = Field(default=False)


class RuleRowBase(RuleBase):
    weight: int = Field(default=0)
    status: bool = Field(default=True)


# Properties to receive via API on creation
class RuleCreate(RuleRowBase):
    pass


# Properties to receive via API on update, all are optional
class RuleUpdate(RuleRowBase):
    type: RuleType | None = Field(default=None)
    title: str | None = Field(default=None)
    name: str | None = Field(default=None)


# Database model, database table inferred from class name
class Rule(RuleRowBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: TableRecordCreatedDateTime
    updated_at: TableRecordUpdatedDateTime
    parent_id: int | None = Field(
        default=None, foreign_key="rule.id", ondelete="SET NULL"
    )
    parent: "Rule" = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "[Rule.id]"}
    )
    children: list["Rule"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"order_by": "Rule.weight.desc()"},
    )
    roles: list["Role"] = Relationship(
        back_populates="permissions", link_model=RoleRuleLink
    )


# Properties to return via API
class RuleTreePublic(RuleRowBase):
    id: int
    created_at: datetime
    updated_at: datetime
    children: list["RuleTreePublic"] | None = Field(default=None)


class RuleTreesPublic(SQLModel):
    data: list[RuleTreePublic]


class UserRuleTreePublic(RuleBase):
    id: int
    children: list["UserRuleTreePublic"] | None = Field(default=None)
