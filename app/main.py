from fastapi import FastAPI

app = FastAPI(
    title="DataContractor",
    description="Data contracts and data quality service for ETL pipelines",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
