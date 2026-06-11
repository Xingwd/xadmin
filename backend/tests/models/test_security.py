from app.models.security import (
    ApiPermission,
    Operation,
    Permission,
    Token,
    TokenPayload,
)


def test_token_model() -> None:
    token = Token(access_token="test_token")
    assert token.access_token == "test_token"
    assert token.token_type == "bearer"


def test_token_payload_defaults() -> None:
    payload = TokenPayload()
    assert payload.sub is None
    assert payload.scopes == []


def test_token_payload_with_values() -> None:
    payload = TokenPayload(sub="user123", scopes=["read", "write"])
    assert payload.sub == "user123"
    assert payload.scopes == ["read", "write"]


def test_permission_model() -> None:
    perm = Permission(name="test:read", description="Read on test")
    assert perm.name == "test:read"
    assert perm.description == "Read on test"


class TestApiPermission:
    def test_api_permission_path(self) -> None:
        api_perm = ApiPermission(path="/api/v1/users/")
        assert api_perm.path == "/api/v1/users/"

    def test_build_permission_create(self) -> None:
        api_perm = ApiPermission(path="/api/v1/test/")
        result = api_perm._build_permission(Operation.CREATE)
        assert result == "/api/v1/test/:create"

    def test_build_permission_read(self) -> None:
        api_perm = ApiPermission(path="/api/v1/test/")
        result = api_perm._build_permission(Operation.READ)
        assert result == "/api/v1/test/:read"

    def test_build_permission_update(self) -> None:
        api_perm = ApiPermission(path="/api/v1/test/")
        result = api_perm._build_permission(Operation.UPDATE)
        assert result == "/api/v1/test/:update"

    def test_build_permission_delete(self) -> None:
        api_perm = ApiPermission(path="/api/v1/test/")
        result = api_perm._build_permission(Operation.DELETE)
        assert result == "/api/v1/test/:delete"

    def test_create_property(self) -> None:
        api_perm = ApiPermission(path="/api/v1/items/")
        perm = api_perm.create
        assert isinstance(perm, Permission)
        assert perm.name == "/api/v1/items/:create"
        assert perm.description == "Create on /api/v1/items/"

    def test_read_property(self) -> None:
        api_perm = ApiPermission(path="/api/v1/items/")
        perm = api_perm.read
        assert isinstance(perm, Permission)
        assert perm.name == "/api/v1/items/:read"
        assert perm.description == "Read on /api/v1/items/"

    def test_update_property(self) -> None:
        api_perm = ApiPermission(path="/api/v1/items/")
        perm = api_perm.update
        assert isinstance(perm, Permission)
        assert perm.name == "/api/v1/items/:update"
        assert perm.description == "Update on /api/v1/items/"

    def test_delete_property(self) -> None:
        api_perm = ApiPermission(path="/api/v1/items/")
        perm = api_perm.delete
        assert isinstance(perm, Permission)
        assert perm.name == "/api/v1/items/:delete"
        assert perm.description == "Delete on /api/v1/items/"

    def test_permission_equality_same_path(self) -> None:
        perm1 = ApiPermission(path="/api/v1/test/")
        perm2 = ApiPermission(path="/api/v1/test/")
        assert perm1.path == perm2.path

    def test_permission_different_paths(self) -> None:
        perm1 = ApiPermission(path="/api/v1/users/")
        perm2 = ApiPermission(path="/api/v1/roles/")
        assert perm1.path != perm2.path
