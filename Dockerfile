
FROM python:3.14.10-bookworm


ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:/root/.local/bin:$PATH"

# System dependencies and uv
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    build-essential \
    libssl-dev \
    libffi-dev \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

# Virtual environment
RUN uv venv /opt/venv --python /usr/local/bin/python

# Application dependencies (27)
RUN uv pip install --python /opt/venv/bin/python \
    "Django>=5.2.8,<5.3" \
    pydantic-settings \
    python-dotenv \
    structlog \
    djangorestframework \
    drf-spectacular \
    djangorestframework-simplejwt \
    django-axes \
    django-auditlog \
    cassandra-driver \
    httpx \
    tenacity \
    "psycopg[binary]" \
    numpy \
    pandas \
    django-prometheus \
    prometheus-client \
    opentelemetry-api \
    opentelemetry-sdk \
    opentelemetry-distro \
    opentelemetry-exporter-otlp \
    opentelemetry-instrumentation-django \
    opentelemetry-instrumentation-logging \
    opentelemetry-instrumentation-httpx \
    sentry-sdk \
    django-cors-headers \
    django-filter

# Development dependencies (12)
RUN uv pip install --python /opt/venv/bin/python \
    django-debug-toolbar \
    pytest \
    pytest-django \
    pytest-cov \
    ruff \
    mypy \
    django-stubs \
    pre-commit \
    hypothesis \
    factory-boy \
    freezegun \
    respx \
    pytest-html \
    coverage

WORKDIR /workspace

EXPOSE 8000

CMD ["tail", "-f", "/dev/null"]
