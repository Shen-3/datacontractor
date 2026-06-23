"""Security utilities for DataContractor.

Provides safe path resolution to prevent path traversal attacks.
"""

from pathlib import Path

from app.core.config import settings

_ALLOWED_DATA_DIR = Path(settings.ALLOWED_DATA_DIR).resolve()


def safe_resolve_path(user_path: str) -> Path:
    """Resolve a user-supplied path guaranteed to be inside the allowed data directory.

    Args:
        user_path: A filesystem path supplied by the caller (e.g. from an API request).

    Returns:
        A resolved absolute ``Path`` inside the allowed data directory.

    Raises:
        ValueError: If the resolved path escapes the allowed data directory
            or does not point to an existing file.
    """
    if not user_path or not user_path.strip():
        raise ValueError("Path must not be empty")

    resolved = (_ALLOWED_DATA_DIR / user_path).resolve()

    # Ensure the resolved path is inside the allowed directory
    try:
        resolved.relative_to(_ALLOWED_DATA_DIR)
    except ValueError:
        raise ValueError(f"Path '{user_path}' is outside the allowed data directory ({_ALLOWED_DATA_DIR})")

    if not resolved.exists():
        raise ValueError(f"Dataset not found: {user_path}")

    if not resolved.is_file():
        raise ValueError(f"Path is not a file: {user_path}")

    return resolved
