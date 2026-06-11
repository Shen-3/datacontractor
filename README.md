# DataContractor

Data contracts and data quality service for ETL pipelines.

## Architecture

```
                    ┌────────────────────────┐
                    │   Contract Registry    │
                    │  versions, owners, SLA │
                    └───────────┬────────────┘
                                │
                                ▼
┌──────────────┐      ┌─────────────────────┐      ┌──────────────┐
│ Data Source  │ ───▶ │ ETL Validation Step │ ───▶ │ Data Warehouse│
└──────────────┘      └──────────┬──────────┘      └──────────────┘
                                 │
                                 ▼
                       ┌───────────────────┐
                       │ Quality Engine    │
                       │ schema + rules    │
                       └─────────┬─────────┘
                                 │
                                 ▼
                       ┌───────────────────┐
                       │ Violations Store  │
                       └─────────┬─────────┘
                                 │
                                 ▼
                       ┌───────────────────┐
                       │ Dashboard / API   │
                       └───────────────────┘
```

## Features

- **Contract Registry**: Create, version, and manage data contracts
- **Schema Validation**: Validate data against contract schemas
- **Compatibility Checker**: Detect breaking changes between contract versions
- **Quality Engine**: Run configurable quality checks on data
- **Violation Tracking**: Store and manage data quality violations
- **Dashboard**: Monitor contracts, validation runs, and violations
- **Demo ETL Pipeline**: Educational pipeline demonstrating data contract usage

## Tech Stack

- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- Pandas
- Streamlit
- Docker / Docker Compose

## Quick Start

### Using Docker Compose (recommended)

```bash
docker compose up --build
```

### Local Development

```bash
# Install dependencies
make install

# Start PostgreSQL (via Docker)
docker compose up postgres -d

# Run migrations
make migrate

# Seed demo data
make seed

# Start API server
make api

# Start dashboard
make dashboard
```

## API Documentation

Once the API is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Demo Scenarios

```bash
# Valid dataset - should pass all checks
make demo-valid

# Invalid enum values - should fail allowed_values check
make demo-invalid-enum

# Missing required field - should fail schema validation
make demo-invalid-schema

# Null values - should fail not_null check
make demo-nulls

# Duplicates - should fail unique check
make demo-duplicates

# Stale data - should fail freshness check
make demo-stale
```

## Testing

```bash
make test
```

## Development

```bash
# Lint
make lint

# Format
make format

# Run all checks
make lint && make format && make test
```

## License

MIT
