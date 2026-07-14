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
COPY ai-gateway/requirements.txt /srv/ai-gateway/requirements.txt
WORKDIR /srv/ai-gateway
RUN pip install --user -r requirements.txt

FROM base AS runtime
RUN useradd --create-home --uid 1000 veloai
COPY --from=builder /root/.local /home/veloai/.local
COPY shared /srv/shared
COPY ai-gateway/app /srv/ai-gateway/app

ENV PATH=/home/veloai/.local/bin:$PATH \
    PYTHONPATH=/srv/ai-gateway

WORKDIR /srv/ai-gateway
USER veloai

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
