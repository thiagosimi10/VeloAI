# syntax=docker/dockerfile:1
FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /srv

FROM base AS builder
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY shared /srv/shared
COPY provisioning/requirements.txt /srv/provisioning/requirements.txt
WORKDIR /srv/provisioning
RUN pip install --user -r requirements.txt

FROM base AS runtime
RUN useradd --create-home --uid 1000 veloai
COPY --from=builder /root/.local /home/veloai/.local
COPY shared /srv/shared
COPY provisioning/app /srv/provisioning/app
COPY provisioning/alembic_master /srv/provisioning/alembic_master
COPY provisioning/alembic_tenant /srv/provisioning/alembic_tenant
COPY provisioning/alembic_master.ini provisioning/alembic_tenant.ini /srv/provisioning/
COPY provisioning/scripts /srv/provisioning/scripts
COPY provisioning/docker-entrypoint.sh /srv/provisioning/docker-entrypoint.sh

ENV PATH=/home/veloai/.local/bin:$PATH \
    PYTHONPATH=/srv/provisioning

WORKDIR /srv/provisioning
RUN chmod +x docker-entrypoint.sh
USER veloai

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

ENTRYPOINT ["./docker-entrypoint.sh"]
