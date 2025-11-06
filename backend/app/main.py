"""FastAPI application entry point."""

from __future__ import annotations

import signal
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

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


@app.get("/", tags=["system"], summary="Service root")
async def root() -> dict[str, str]:
    return {"message": "Novel RAG backend is running"}


__all__ = ["app"]

