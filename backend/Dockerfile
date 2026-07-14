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
COPY backend/requirements.txt /srv/backend/requirements.txt
WORKDIR /srv/backend
RUN pip install --user -r requirements.txt

FROM base AS runtime
RUN useradd --create-home --uid 1000 veloai
COPY --from=builder /root/.local /home/veloai/.local
COPY shared /srv/shared
COPY backend/app /srv/backend/app

ENV PATH=/home/veloai/.local/bin:$PATH \
    PYTHONPATH=/srv/backend

WORKDIR /srv/backend
USER veloai

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
