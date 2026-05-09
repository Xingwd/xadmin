from fastapi import APIRouter

from app.api.routes import login, operation_logs, roles, rules, users

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(
    operation_logs.router, prefix="/operation-logs", tags=["operation-logs"]
)
