#!/bin/sh
set -e

echo "[provisioning] aplicando migrations do Banco Master..."
python -m scripts.migrate_master

echo "[provisioning] garantindo seed do plano inicial..."
python -m scripts.seed_master

echo "[provisioning] iniciando API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8001
