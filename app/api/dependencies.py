"""FastAPI dependency injection utilities."""

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Depends(api_key_header)) -> None:
    """Verify the API key from the X-API-Key header.

    This is a simple API key authentication scheme suitable for
    single-service deployments.  When ``settings.API_KEY`` is empty
    (the default in development) authentication is disabled.
    """
    if not settings.API_KEY:
        return
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key required. Set X-API-Key header.",
        )
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )
