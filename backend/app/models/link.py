from sqlmodel import Field, SQLModel


class RoleRuleLink(SQLModel, table=True):
    role_id: int = Field(foreign_key="role.id", primary_key=True)
    rule_id: int = Field(foreign_key="rule.id", primary_key=True)


class UserRoleLink(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    role_id: int = Field(foreign_key="role.id", primary_key=True)
