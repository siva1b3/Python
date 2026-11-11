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
    pkg-config \
    libssl-dev \
    libffi-dev \
    libev-dev \
    libpq-dev \
    libmagic1 \
    libjpeg-dev \
    zlib1g-dev \
    libwebp-dev \
    tzdata \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

# Virtual environment
RUN uv venv /opt/venv --python /usr/local/bin/python

# Application dependencies
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
    "cassandra-driver>=3.30.1,<4" \
    httpx \
    tenacity \
    "psycopg[binary,pool]" \
    dj-database-url \
    hdfs \
    elasticsearch \
    boto3 \
    "django-storages[s3]" \
    numpy \
    pandas \
    "uvicorn[standard]" \
    "celery>=5.7,<6" \
    django-celery-beat \
    django-celery-results \
    flower \
    pika \
    redis \
    django-redis \
    channels \
    channels-redis \
    argon2-cffi \
    cryptography \
    Pillow \
    python-magic \
    clamd \
    pybreaker \
    django-waffle \
    django-prometheus \
    prometheus-client \
    opentelemetry-api \
    opentelemetry-sdk \
    opentelemetry-distro \
    opentelemetry-exporter-otlp \
    opentelemetry-instrumentation-django \
    opentelemetry-instrumentation-asgi \
    opentelemetry-instrumentation-logging \
    opentelemetry-instrumentation-httpx \
    opentelemetry-instrumentation-requests \
    opentelemetry-instrumentation-celery \
    opentelemetry-instrumentation-psycopg \
    opentelemetry-instrumentation-cassandra \
    opentelemetry-instrumentation-redis \
    opentelemetry-instrumentation-elasticsearch \
    opentelemetry-instrumentation-botocore \
    pyroscope-io \
    sentry-sdk \
    django-cors-headers \
    django-filter

# Development dependencies
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