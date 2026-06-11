# API Reference

## Base URL

```
http://localhost:8000
```

## Authentication

No authentication required in the current version.

## Endpoints

### Health Check

```
GET /health
```

**Response:**
```json
{
  "status": "ok"
}
```

---

### Create Contract

```
POST /contracts
```

**Request:**
```json
{
  "name": "users_events",
  "description": "User activity events",
  "owner": "user-platform-team",
  "version": "1.0.0",
  "schema": {
    "fields": [
      {
        "name": "user_id",
        "type": "integer",
        "required": true,
        "nullable": false,
        "description": "Unique user identifier"
      }
    ]
  },
  "quality_rules": [
    {
      "name": "user_id_not_null",
      "type": "not_null",
      "field": "user_id",
      "severity": "critical"
    }
  ],
  "sla": {
    "update_frequency": "daily",
    "max_delay_minutes": 1440
  },
  "compatibility": {
    "mode": "backward"
  }
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "name": "users_events",
  "description": "User activity events",
  "owner": "user-platform-team",
  "status": "active",
  "created_at": "2025-06-11T10:00:00Z",
  "updated_at": "2025-06-11T10:00:00Z"
}
```

**Errors:**
- `400` - Contract with this name already exists

---

### List Contracts

```
GET /contracts
```

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "users_events",
    "description": "User activity events",
    "owner": "user-platform-team",
    "status": "active",
    "created_at": "2025-06-11T10:00:00Z",
    "updated_at": "2025-06-11T10:00:00Z"
  }
]
```

---

### Get Contract

```
GET /contracts/{contract_name}
```

**Response:** Contract with all versions included.

---

### List Versions

```
GET /contracts/{contract_name}/versions
```

**Response:** Array of version objects.

---

### Get Version

```
GET /contracts/{contract_name}/versions/{version}
```

**Response:** Single version object with schema, quality rules, SLA.

---

### Add Version

```
POST /contracts/{contract_name}/versions
```

**Request:**
```json
{
  "version": "2.0.0",
  "schema": { ... },
  "quality_rules": [ ... ],
  "allow_breaking": false
}
```

**Response (201):** New version object.

**Errors:**
- `409` - Breaking changes detected (with compatibility report)
- `400` - Contract not found

---

### Validate Data

```
POST /contracts/{contract_name}/validate-data
```

**Request:**
```json
{
  "dataset_path": "data/datasets/users_events_valid.csv",
  "dataset_name": "users_events_valid.csv"
}
```

**Response:**
```json
{
  "contract": "users_events",
  "version": "1.0.0",
  "dataset": "users_events_valid.csv",
  "status": "passed",
  "rows_checked": 10,
  "violations_count": 0,
  "violations": []
}
```

---

### Validate Schema

```
POST /contracts/{contract_name}/validate-schema
```

**Request:** Schema definition to compare against active version.

**Response:** Compatibility report.

---

### Compare Versions

```
POST /contracts/{contract_name}/compare-versions
```

**Request:**
```json
{
  "old_version": "1.0.0",
  "new_version": "2.0.0"
}
```

**Response:**
```json
{
  "compatible": false,
  "breaking_changes": [...],
  "warnings": [...]
}
```

---

### List Violations

```
GET /violations
```

**Response:** Array of violation objects.

---

### Get Violation

```
GET /violations/{violation_id}
```

**Response:** Single violation object.

---

### Update Violation Status

```
PATCH /violations/{violation_id}/status
```

**Request:**
```json
{
  "status": "acknowledged"
}
```

**Valid statuses:** `open`, `acknowledged`, `resolved`, `ignored`

---

### List ETL Runs

```
GET /etl/runs
```

**Response:** Array of validation run objects.

---

### Get ETL Run

```
GET /etl/runs/{run_id}
```

**Response:** Single validation run object.
