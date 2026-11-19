"""
CivicMind AI — Core FastAPI Application Entrypoint
AI-Powered Citizen Grievance Intelligence and Resolution Prediction Platform
"""

import time
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from datetime import datetime, timezone

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.database import async_engine, check_db_health, check_pgvector_extension
from app.core.redis import get_redis_client, close_redis_connection, check_redis_health
from app.schemas.health import (
    ComponentStatus,
    SystemHealthResponse,
    SingleComponentHealthResponse,
)
from app.api.v1.router import api_router
from app.utils.logger import setup_logging

# Initialize structured logging
setup_logging()
logger = logging.getLogger("civicmind.app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifecycle management.
    Performs pre-flight database and cache connectivity checks on boot,
    and cleanly disposes resource pools on termination.
    """
    logger.info("Initializing %s (Environment: %s)", settings.PROJECT_NAME, settings.ENVIRONMENT)

    # Pre-flight check: PostgreSQL
    db_ok, db_msg = await check_db_health()
    if db_ok:
        logger.info("Database pre-flight check passed: %s", db_msg)
    else:
        logger.warning("Database pre-flight check warning: %s", db_msg)

    # Pre-flight check: pgvector extension
    vector_ok, vector_msg = await check_pgvector_extension()
    if vector_ok:
        logger.info("pgvector extension check passed: %s", vector_msg)
    else:
        logger.warning("pgvector extension check warning: %s", vector_msg)

    # Pre-flight check: Redis
    redis_ok, redis_msg = await check_redis_health()
    if redis_ok:
        logger.info("Redis pre-flight check passed: %s", redis_msg)
    else:
        logger.warning("Redis pre-flight check warning: %s", redis_msg)

    yield

    # Clean shutdown
    logger.info("Shutting down %s...", settings.PROJECT_NAME)
    await close_redis_connection()
    await async_engine.dispose()
    logger.info("Resource connections disposed cleanly.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Production backend API for CivicMind AI — AI-Powered Citizen Grievance "
        "Intelligence and Resolution Prediction Platform."
    ),
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan,
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# Centralized Exception Handlers
# ==============================================================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": request.url.path,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning("Request validation failed on path %s: %s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "status_code": 422,
            "message": "Request payload validation error",
            "details": exc.errors(),
            "path": request.url.path,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled server exception on path %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "status_code": 500,
            "message": "Internal server error occurred",
            "path": request.url.path,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


# ==============================================================================
# Health Check Endpoints
# ==============================================================================

@app.get(
    "/health",
    response_model=SystemHealthResponse,
    summary="Comprehensive System Health Check",
    description="Evaluates connectivity to PostgreSQL, pgvector extension, and Redis broker.",
    tags=["Health"],
)
async def system_health() -> SystemHealthResponse:
    # Measure DB Latency
    t0 = time.perf_counter()
    db_ok, db_msg = await check_db_health()
    db_latency = (time.perf_counter() - t0) * 1000

    # Measure Vector Latency
    t1 = time.perf_counter()
    vec_ok, vec_msg = await check_pgvector_extension()
    vec_latency = (time.perf_counter() - t1) * 1000

    # Measure Redis Latency
    t2 = time.perf_counter()
    redis_ok, redis_msg = await check_redis_health()
    redis_latency = (time.perf_counter() - t2) * 1000

    overall_status = "healthy"
    if not db_ok or not redis_ok:
        overall_status = "unhealthy"
    elif not vec_ok:
        overall_status = "degraded"

    return SystemHealthResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc),
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database=ComponentStatus(
            status="healthy" if db_ok else "unhealthy",
            reachable=db_ok,
            message=db_msg,
            latency_ms=round(db_latency, 2),
        ),
        redis=ComponentStatus(
            status="healthy" if redis_ok else "unhealthy",
            reachable=redis_ok,
            message=redis_msg,
            latency_ms=round(redis_latency, 2),
        ),
        pgvector=ComponentStatus(
            status="healthy" if vec_ok else "unhealthy",
            reachable=vec_ok,
            message=vec_msg,
            latency_ms=round(vec_latency, 2),
            details={"dimension": settings.EMBEDDING_DIMENSION},
        ),
    )


@app.get(
    "/health/database",
    response_model=SingleComponentHealthResponse,
    summary="Database Connectivity Probe",
    description="Dedicated health probe for containerized PostgreSQL and pgvector.",
    tags=["Health"],
)
async def database_health() -> SingleComponentHealthResponse:
    start_time = time.perf_counter()
    db_ok, db_msg = await check_db_health()
    vec_ok, vec_msg = await check_pgvector_extension()
    elapsed = (time.perf_counter() - start_time) * 1000

    status_str = "healthy" if (db_ok and vec_ok) else ("degraded" if db_ok else "unhealthy")

    return SingleComponentHealthResponse(
        service="postgresql-pgvector",
        status=status_str,
        reachable=db_ok,
        message=f"{db_msg}. {vec_msg}",
        latency_ms=round(elapsed, 2),
        timestamp=datetime.now(timezone.utc),
    )


@app.get(
    "/health/redis",
    response_model=SingleComponentHealthResponse,
    summary="Redis Connectivity Probe",
    description="Dedicated health probe for Redis broker and caching layer.",
    tags=["Health"],
)
async def redis_health() -> SingleComponentHealthResponse:
    start_time = time.perf_counter()
    redis_ok, redis_msg = await check_redis_health()
    elapsed = (time.perf_counter() - start_time) * 1000

    return SingleComponentHealthResponse(
        service="redis",
        status="healthy" if redis_ok else "unhealthy",
        reachable=redis_ok,
        message=redis_msg,
        latency_ms=round(elapsed, 2),
        timestamp=datetime.now(timezone.utc),
    )


# ==============================================================================
# Mount API Versioned Routers
# ==============================================================================

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "documentation": f"{settings.API_V1_PREFIX}/docs",
        "health": "/health",
    }
