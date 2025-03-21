import json

from fastapi import FastAPI, Request
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.routing import APIRoute
from fastapi.utils import generate_unique_id
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.crud import operation_log as operation_log_crud
from app.crud.rule import get_full_title
from app.models.operation_log import OperationLogCreate


def custom_generate_unique_id(route: APIRoute) -> str:
    if route.include_in_schema:
        return f"{route.tags[0]}-{route.name}"
    return generate_unique_id


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    docs_url=None,
    redoc_url=None,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.middleware("http")
async def save_operation_log(request: Request, call_next):
    response = await call_next(request)

    method, path = request.method, request.url.path
    if path not in settings.LOG_EXCLUDE_PATHS and method != "OPTIONS":
        # 获取用户信息
        user = getattr(request.state, "user", None)
        if user:
            user_id, username = user.id, user.username
        else:
            user_id, username = None, None

        # 获取标题
        name, title = "", ""
        if path in settings.LOG_STATIC_PATHS.keys():
            name = settings.LOG_STATIC_PATHS[path]
            if name == "query_params.rule_name":
                name = request.query_params.get("rule_name")
                title = get_full_title(name)
            else:
                title = name
        else:
            scopes = getattr(request.state, "scopes", [])
            if scopes:
                name = scopes[0]
                title = get_full_title(name)

        operation_log_crud.create_operation_log(
            OperationLogCreate(
                user_id=user_id,
                username=username,
                name=name,
                title=title,
                request_method=method,
                request_path=path,
                request_query_params=json.dumps(
                    request.query_params._dict, ensure_ascii=False
                ),
                response_status_code=response.status_code,
            )
        )

    return response


app.include_router(api_router, prefix=settings.API_V1_STR)
