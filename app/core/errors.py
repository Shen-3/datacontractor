from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class ContractNotFoundError(HTTPException):
    def __init__(self, name: str):
        super().__init__(status_code=404, detail=f"Contract '{name}' not found")


class ContractAlreadyExistsError(HTTPException):
    def __init__(self, name: str):
        super().__init__(status_code=400, detail=f"Contract '{name}' already exists")


class BreakingChangesError(HTTPException):
    def __init__(self, report: dict):
        super().__init__(status_code=409, detail=report)


class ValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


class DatasetLoadError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=f"Failed to load dataset: {detail}")


async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
