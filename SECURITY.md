# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in DataContractor, please open a
[GitHub Issue](https://github.com/your-org/datacontractor/issues) describing
the issue.  Do **not** open a public issue for critical vulnerabilities;
instead, contact the maintainers directly.

We will acknowledge receipt within 48 hours and provide a timeline for a fix.

---

## Security Features

### API Key Authentication

API requests are authenticated via the `X-API-Key` header when
`API_KEY` is set in the environment.  In development mode (empty
`API_KEY`) all requests proceed without authentication.

**Configuration:**
```ini
# .env
API_KEY=your-secret-key
```

### Path Traversal Protection

The `ALLOWED_DATA_DIR` setting (default `/app/data`) restricts which
directories the validation endpoint can read CSV files from.  Any
path that resolves outside this directory is rejected with a 400 error.

**Configuration:**
```ini
# .env
ALLOWED_DATA_DIR=/app/data
```

### Rate Limiting

Requests are rate-limited per IP address when `APP_ENV=production`.
The limit is controlled by `API_RATE_LIMIT` (default 60 requests per
minute).  In development mode rate limiting is disabled.

### Request Size Limits

Requests with a body larger than `MAX_REQUEST_SIZE_MB` (default 10 MB)
are rejected with a 413 status code.

### CORS

Cross-Origin requests are restricted to origins configured in
`CORS_ORIGINS` (comma-separated list, default `http://localhost:8501`).

---

## Production Deployment Checklist

- [ ] `API_KEY` is set to a strong, unique value
- [ ] `APP_ENV=production`
- [ ] `APP_DEBUG=false` (never `true` in production — may leak SQL)
- [ ] `DATABASE_URL` uses a strong, unique password
- [ ] `CORS_ORIGINS` is restricted to known frontend origins
- [ ] Database port (5432) is **not** exposed to the public internet
- [ ] HTTPS is terminated at a reverse proxy (nginx, Traefik, or
      cloud LB) — the application does **not** handle TLS directly
- [ ] Container runs as non-root user (default in the production
      Docker image)
- [ ] Regular `pg_dump` backups are configured for the PostgreSQL
      volume
- [ ] Secrets are injected via environment variables or a `.env` file,
      **not** baked into the container image

---

## Known Security Limitations

- **No HTTPS termination**: The application serves plain HTTP.  Use a
  reverse proxy for TLS.
- **No RBAC**: API key authentication is all-or-nothing.  All
  authenticated users have full access.
- **No audit log**: API requests are not logged at the application
  level (only uvicorn access logs).
- **Sample records may contain PII**: Violation records store up to 10
  sample rows from validated datasets.  Ensure datasets do not contain
  PII if violations are exposed to unauthorized users.
