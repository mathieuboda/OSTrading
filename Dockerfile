FROM python:3.12-slim

# Install cron + timezone data
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install Python deps (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy project
COPY config/ config/
COPY skills/ skills/
COPY scripts/ scripts/
COPY docker/trading.crontab /etc/cron.d/trading

RUN chmod 0644 /etc/cron.d/trading \
    && mkdir -p logs

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV TZ=America/New_York \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH"

HEALTHCHECK --interval=5m --timeout=30s --retries=3 \
    CMD python scripts/healthcheck.py || exit 1

ENTRYPOINT ["/entrypoint.sh"]
