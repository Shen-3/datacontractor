# =============================================================================
# Stage 1 — Builder: install build dependencies and Python packages
# =============================================================================
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir -e "."


# =============================================================================
# Stage 2 — Runtime: minimal image with non-root user
# =============================================================================
FROM python:3.11-slim AS runtime

WORKDIR /app

# Create a non-root user
RUN groupadd -r datacontractor && \
    useradd -r -g datacontractor -d /app -s /sbin/nologin datacontractor && \
    mkdir -p /app/data && \
    chown -R datacontractor:datacontractor /app

# Copy installed packages from builder (avoids installing build tools in runtime)
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code
COPY --chown=datacontractor:datacontractor . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

USER datacontractor

CMD ["bash", "./scripts/startup.sh"]
