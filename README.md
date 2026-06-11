# DataContractor

DataContractor is a production-like educational data contracts and data quality platform for ETL pipelines. It provides a contract registry, schema compatibility checks, data quality validation, violation tracking, a demo ETL pipeline, and a dashboard for monitoring data contract violations.

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
- **Quality Engine**: 13 configurable quality check types
- **Violation Tracking**: Store and manage data quality violations with severity levels
- **Dashboard**: Streamlit-based monitoring UI
- **Demo ETL Pipeline**: Educational pipeline demonstrating data contract usage
- **REST API**: Full OpenAPI-documented API

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
- GitHub Actions CI

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

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/contracts` | Create contract |
| GET | `/contracts` | List contracts |
| GET | `/contracts/{name}` | Get contract detail |
| GET | `/contracts/{name}/versions` | List versions |
| GET | `/contracts/{name}/versions/{ver}` | Get version |
| POST | `/contracts/{name}/versions` | Add version |
| POST | `/contracts/{name}/validate-data` | Validate dataset |
| POST | `/contracts/{name}/validate-schema` | Validate schema |
| POST | `/contracts/{name}/compare-versions` | Compare versions |
| GET | `/violations` | List violations |
| GET | `/violations/{id}` | Get violation |
| PATCH | `/violations/{id}/status` | Update violation status |
| GET | `/etl/runs` | List ETL runs |
| GET | `/etl/runs/{id}` | Get ETL run |

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

## Quality Checks

| Check | Description |
|-------|-------------|
| `not_null` | Field contains no null values |
| `unique` | Field has no duplicates |
| `allowed_values` | Values are in allowed set |
| `regex` | String matches pattern |
| `min_value` | Numeric value above minimum |
| `max_value` | Numeric value below maximum |
| `type_check` | Value matches expected type |
| `row_count_min` | Dataset has minimum rows |
| `row_count_max` | Dataset has maximum rows |
| `freshness` | Data is recent enough |
| `duplicate_rate` | Duplicate ratio below threshold |
| `null_rate` | Null ratio below threshold |
| `schema_match` | Expected fields present |

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

## Project Structure

```
datacontractor/
  app/
    main.py              # FastAPI application
    api/                 # REST API routes
    core/                # Configuration
    db/                  # Database models and repositories
    schemas/             # Pydantic schemas
    services/            # Business logic
    quality/             # Quality check engine
    dashboard/           # Streamlit dashboard
  data/
    contracts/           # Sample contract YAML files
    datasets/            # Demo CSV datasets
  migrations/            # Alembic migrations
  tests/                 # Unit and integration tests
  docs/                  # Technical documentation
  scripts/               # Utility scripts
```

## Limitations

- No enterprise data catalog integration
- No data lineage system
- No RBAC (role-based access control)
- No Kafka or streaming integration
- No dbt integration
- No ML anomaly detection

## Roadmap

- Data lineage visualization
- Slack/email notifications for violations
- Prometheus metrics export
- Great Expectations integration layer
- Multi-tenant support
- Webhook support for violation alerts

## License

MIT
