# Data Contract Format

Contracts are defined in YAML format and stored both as files and in the database.

## Structure

```yaml
name: users_events
version: 1.0.0
description: User activity events
owner: user-platform-team
consumers:
  - analytics-team
  - marketing-bi

schema:
  fields:
    - name: user_id
      type: integer
      required: true
      nullable: false
      description: Unique user identifier

    - name: event_type
      type: enum
      required: true
      nullable: false
      values:
        - login
        - logout
        - purchase

quality_rules:
  - name: user_id_not_null
    type: not_null
    field: user_id
    severity: critical

sla:
  update_frequency: daily
  max_delay_minutes: 1440

compatibility:
  mode: backward
```

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | yes | Unique contract identifier |
| version | string | yes | Semantic version (e.g. 1.0.0) |
| description | string | no | Human-readable description |
| owner | string | yes | Team or person responsible |
| consumers | list | no | Teams that depend on this data |

## Schema Fields

Each field in `schema.fields` supports:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| name | string | required | Column name |
| type | string | required | One of: string, integer, float, decimal, boolean, date, timestamp, enum |
| required | bool | true | Whether field must be present |
| nullable | bool | false | Whether field can contain null values |
| description | string | null | Human-readable description |
| values | list | null | Allowed values (for enum type) |

## Quality Rules

Each rule has:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| name | string | required | Unique rule name |
| type | string | required | Check type (see quality_checks.md) |
| field | string | null | Field to check (required for most checks) |
| severity | string | warning | info / warning / error / critical |
| values | list | null | For allowed_values check |
| pattern | string | null | For regex check |
| threshold | float | null | For rate checks |
| min_value | float | null | For min_value check |
| max_value | float | null | For max_value check |
| max_delay_minutes | int | null | For freshness check |

## Compatibility Modes

- **backward**: New version must be backward-compatible with the old one
