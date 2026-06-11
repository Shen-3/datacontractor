# Quality Checks

DataContractor supports 13 quality check types.

## not_null

Fails if field contains null/NaN/empty values.

```yaml
- name: user_id_not_null
  type: not_null
  field: user_id
  severity: critical
```

## unique

Fails if duplicate values exist in the field.

```yaml
- name: user_id_unique
  type: unique
  field: user_id
  severity: error
```

## allowed_values

Fails if value is not in the configured allowed list.

```yaml
- name: event_type_allowed
  type: allowed_values
  field: event_type
  values: [login, logout, purchase]
  severity: error
```

## regex

Fails if string does not match the configured regex pattern.

```yaml
- name: email_valid
  type: regex
  field: email
  pattern: "^.+@.+\\..+$"
  severity: error
```

## min_value

Fails if numeric value is below the configured minimum.

```yaml
- name: amount_min
  type: min_value
  field: amount
  min_value: 0
  severity: error
```

## max_value

Fails if numeric value exceeds the configured maximum.

```yaml
- name: amount_max
  type: max_value
  field: amount
  max_value: 10000
  severity: error
```

## type_check

Fails if value cannot be cast to the expected type.

```yaml
- name: id_type
  type: type_check
  field: user_id
  expected_type: integer
  severity: error
```

## row_count_min

Fails if dataset has fewer rows than the minimum.

```yaml
- name: min_rows
  type: row_count_min
  min_rows: 100
  severity: warning
```

## row_count_max

Fails if dataset has more rows than the maximum.

```yaml
- name: max_rows
  type: row_count_max
  max_rows: 1000000
  severity: warning
```

## freshness

Fails if the maximum timestamp in the field is older than the threshold.

```yaml
- name: event_freshness
  type: freshness
  field: event_time
  max_delay_minutes: 1440
  severity: warning
```

## duplicate_rate

Fails if the ratio of duplicate values exceeds the threshold.

```yaml
- name: user_dup_rate
  type: duplicate_rate
  field: user_id
  threshold: 0.01
  severity: warning
```

## null_rate

Fails if the ratio of null values exceeds the threshold.

```yaml
- name: amount_null_rate
  type: null_rate
  field: amount
  threshold: 0.05
  severity: warning
```

## schema_match

Fails if expected fields are missing from the dataset.

```yaml
- name: schema_check
  type: schema_match
  fields: [user_id, event_type, event_time]
  severity: warning
```

## Severity Levels

| Level | Description |
|-------|-------------|
| info | Informational, no action needed |
| warning | Potential issue, ETL continues |
| error | Data quality problem, ETL load blocked |
| critical | Serious issue, ETL load blocked |
