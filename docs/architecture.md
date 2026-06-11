# Architecture

## System Overview

DataContractor is a service for managing data contracts, validating data quality, and tracking violations in ETL pipelines.

## Components

### Contract Registry
Stores data contracts with versioning. Each contract has a schema definition, quality rules, SLA constraints, and compatibility settings.

### Schema Validator
Validates incoming data against contract schemas. Checks field presence, types, enum values, and nullability.

### Compatibility Checker
Compares contract versions to detect breaking changes (field removal, type changes, nullable changes, enum value removal) and non-breaking changes (new optional fields, new enum values).

### Quality Engine
Runs configurable quality checks on data: not_null, unique, allowed_values, regex, min/max values, row count bounds, freshness, duplicate rate, null rate, and schema match.

### Violation Store
Records all violations from schema validation and quality checks with severity, status, sample records, and timestamps.

### Dashboard
Streamlit-based UI showing contracts, validation runs, violations by severity, and demo scenarios.

## Data Flow

```
Data Source → ETL Pipeline → Schema Validation → Quality Checks → Warehouse
                                     ↓                    ↓
                              Contract Registry    Quality Engine
                                     ↓                    ↓
                                     └──── Violations Store ────┘
                                                  ↓
                                           Dashboard / API
```

## Validation Flow

1. Load contract and active version from registry
2. Load dataset (CSV)
3. Run schema validation (field presence, types, enums)
4. Run quality checks (defined in contract rules)
5. Collect all violations
6. Determine status: passed / failed / blocked (if critical)
7. Store validation run and violations in database
8. Return summary via API

## Database Model

- **contracts**: Contract metadata (name, owner, status)
- **contract_versions**: Versioned schema, quality rules, SLA
- **validation_runs**: Each validation execution with status and metrics
- **violations**: Individual check failures with severity and samples
