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
    CREATE = "c"
    READ = "r"
    UPDATE = "u"
    DELETE = "d"


class ApiPermission(SQLModel):
    path: str
    description: str

    @property
    def resource(self) -> str:
        if self.path.startswith("/"):
            self.path = self.path[1:]
        if self.path.endswith("/"):
            self.path = self.path[:-1]
        return self.path.replace("/", ":")

    @property
    def create(self) -> Permission:
        return Permission(
            name=self._build_permission(Operation.CREATE),
            description=f"Create on {self.description}",
        )

    @property
    def read(self) -> Permission:
        return Permission(
            name=self._build_permission(Operation.READ),
            description=f"Read on {self.description}",
        )

    @property
    def update(self) -> Permission:
        return Permission(
            name=self._build_permission(Operation.UPDATE),
            description=f"Update on {self.description}",
        )

    @property
    def delete(self) -> Permission:
        return Permission(
            name=self._build_permission(Operation.DELETE),
            description=f"Delete on {self.description}",
        )

    def _build_permission(self, operation: Operation) -> str:
        return f"{self.resource}:{operation.value}"
