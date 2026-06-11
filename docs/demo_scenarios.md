# Demo Scenarios

## Scenario 1: Valid Dataset

**Command:** `make demo-valid`

**Dataset:** `data/datasets/users_events_valid.csv`

**Expected:**
- Schema validation passes
- All quality checks pass
- Validation run status = `passed`
- No violations

## Scenario 2: Missing Required Field

**Command:** `make demo-invalid-schema`

**Dataset:** `data/datasets/users_events_missing_field.csv`

**Expected:**
- Schema validation fails
- `user_id` field is missing (required)
- Violation severity = `critical`
- Validation run status = `blocked`
- ETL load blocked

## Scenario 3: Invalid Enum Values

**Command:** `make demo-invalid-enum`

**Dataset:** `data/datasets/users_events_invalid_enum.csv`

**Expected:**
- `allowed_values` check fails
- Values `signup` and `click` not in allowed set
- Violations recorded
- Validation run status = `failed`

## Scenario 4: Null Values

**Command:** `make demo-nulls`

**Dataset:** `data/datasets/users_events_nulls.csv`

**Expected:**
- `not_null` check fails for `user_id` and `event_type`
- Failed rows samples saved
- Validation run status = `failed`

## Scenario 5: Duplicates

**Command:** `make demo-duplicates`

**Dataset:** `data/datasets/users_events_duplicates.csv`

**Expected:**
- `unique` check fails for `user_id`
- Duplicate rows identified
- Validation run status = `failed`

## Scenario 6: Stale Data

**Command:** `make demo-stale`

**Dataset:** `data/datasets/users_events_stale.csv`

**Expected:**
- `freshness` check fails
- Timestamps are from January 2024 (older than 1440 minutes)
- Validation run status = `failed`

## Scenario 7: Breaking Schema Change

**Input:** `data/contracts/users_events_v2_breaking.yaml`

**Expected:**
- Compatibility checker detects breaking changes:
  - `user_id` renamed to `client_id` (field_removed)
  - `amount` field removed
- Breaking change report generated
- Version cannot be added without `allow_breaking: true`
