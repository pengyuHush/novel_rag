"""FastAPI application entry point."""

from __future__ import annotations

import signal
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse, JSONResponse

from app.api import api_router
from app.core.config import settings
from app.core.logger import logger, setup_logging
from app.core.redis import close_redis
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Novel RAG backend")
    await init_db()
    yield
    await close_redis()
    logger.info("Stopping Novel RAG backend")


setup_logging("DEBUG" if settings.DEBUG else "INFO")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    # Configure Pydantic to use aliases (camelCase) in JSON responses
    json_schema_extra={"by_alias": True},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误，记录详细的错误信息以便排查问题"""
    
    # 记录详细的验证错误信息
    logger.error(f"Validation error for {request.method} {request.url.path}")
    logger.error(f"Request body: {await request.body()}")
    logger.error(f"Validation errors: {exc.errors()}")
    
    # 构建友好的错误响应
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error['loc'])
        errors.append({
            "field": field,
            "message": error['msg'],
            "type": error['type']
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "请求参数验证失败",
            "errors": errors
        }
    )


@app.get("/", tags=["system"], summary="Service root")
async def root() -> dict[str, str]:
    return {"message": "Novel RAG backend is running"}


__all__ = ["app"]

