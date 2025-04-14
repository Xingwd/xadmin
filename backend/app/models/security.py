from enum import Enum

from sqlmodel import SQLModel


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None
    scopes: list[str] = []


class Permission(SQLModel):
    name: str
    description: str


class Operation(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


class ApiPermission(SQLModel):
    path: str

    @property
    def create(self) -> Permission:
        return Permission(
            name=self._build_permission(Operation.CREATE),
            description=f"Create on {self.path}",
        )

    @property
    def read(self) -> Permission:
        return Permission(
            name=self._build_permission(Operation.READ),
            description=f"Read on {self.path}",
        )

    @property
    def update(self) -> Permission:
        return Permission(
            name=self._build_permission(Operation.UPDATE),
            description=f"Update on {self.path}",
        )

    @property
    def delete(self) -> Permission:
        return Permission(
            name=self._build_permission(Operation.DELETE),
            description=f"Delete on {self.path}",
        )

    def _build_permission(self, operation: Operation) -> str:
        return f"{self.path}:{operation.value}"
