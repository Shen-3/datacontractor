"""DataContractor — FastAPI application entry point."""

import time
from collections import defaultdict
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.dependencies import verify_api_key
from app.api.routes_contracts import router as contracts_router
from app.api.routes_etl import router as etl_router
from app.api.routes_health import router as health_router
from app.api.routes_validation import router as validation_router
from app.api.routes_violations import router as violations_router
from app.core.config import settings
from app.core.errors import global_exception_handler
from app.core.logging import setup_logging

logger = setup_logging(settings.APP_LOG_LEVEL)


# --- Simple in-process rate limiter ---
_rate_limit_buckets: dict[str, list[float]] = defaultdict(list)


def _rate_limiter(request: Request):
    """Check rate limit for the requesting IP."""
    if settings.APP_ENV == "development":
        return  # no rate limiting in development
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window = 60.0
    max_requests = settings.API_RATE_LIMIT

    bucket = _rate_limit_buckets[client_ip]
    # Remove timestamps outside the window
    while bucket and bucket[0] < now - window:
        bucket.pop(0)

    if len(bucket) >= max_requests:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded ({max_requests} requests per {int(window)} seconds).",
        )
    bucket.append(now)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifecycle: startup and shutdown."""
    logger.info(
        "Starting DataContractor v0.1.0 in %s mode",
        settings.APP_ENV,
    )
    if settings.API_KEY:
        logger.info("API key authentication is enabled")
    else:
        logger.info("API key authentication is disabled (development mode)")
    yield
    logger.info("Shutting down DataContractor")


app = FastAPI(
    title="DataContractor",
    description="Data contracts and data quality service for ETL pipelines",
    version="0.1.0",
    lifespan=lifespan,
)

# --- CORS ---
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# --- Exception handlers ---
app.add_exception_handler(Exception, global_exception_handler)


# --- Global dependencies (applied to every route) ---
app.dependency_overrides = {}


# --- Include routers ---
app.include_router(health_router, dependencies=[Depends(_rate_limiter)])
app.include_router(contracts_router, dependencies=[Depends(_rate_limiter), Depends(verify_api_key)])
app.include_router(validation_router, dependencies=[Depends(_rate_limiter), Depends(verify_api_key)])
app.include_router(violations_router, dependencies=[Depends(_rate_limiter), Depends(verify_api_key)])
app.include_router(etl_router, dependencies=[Depends(_rate_limiter), Depends(verify_api_key)])


# --- Request size middleware ---
@app.middleware("http")
async def _request_size_middleware(request: Request, call_next):
    content_length_str = request.headers.get("content-length")
    if content_length_str:
        content_length = int(content_length_str)
        max_bytes = settings.MAX_REQUEST_SIZE_MB * 1024 * 1024
        if content_length > max_bytes:
            return JSONResponse(
                status_code=413,
                content={"detail": f"Request body too large (max {settings.MAX_REQUEST_SIZE_MB} MB)"},
            )
    return await call_next(request)


@app.get("/")
def root():
    return {"message": "DataContractor API", "docs": "/docs"}
