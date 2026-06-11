from fastapi import FastAPI

from app.api.routes_contracts import router as contracts_router
from app.api.routes_etl import router as etl_router
from app.api.routes_health import router as health_router
from app.api.routes_validation import router as validation_router
from app.api.routes_violations import router as violations_router

app = FastAPI(
    title="DataContractor",
    description="Data contracts and data quality service for ETL pipelines",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(contracts_router)
app.include_router(validation_router)
app.include_router(violations_router)
app.include_router(etl_router)


@app.get("/")
def root():
    return {"message": "DataContractor API", "docs": "/docs"}
