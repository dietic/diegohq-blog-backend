"""
DiegoHQ Blog Backend - FastAPI Application.

A gamified backend for "The Adventurer's Journal" programming blog.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.api.v1.router import api_v1_router
from src.config import settings
from src.core.rate_limit import limiter
from src.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan handler.

    Manages startup and shutdown events for the FastAPI application.
    """
    # Startup
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for The Adventurer's Journal - a gamified programming blog",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint returning API information."""
    return {
        "name": settings.APP_NAME,
        "version": "0.1.0",
        "docs": f"{settings.API_V1_PREFIX}/docs" if settings.DEBUG else "disabled",
    }
