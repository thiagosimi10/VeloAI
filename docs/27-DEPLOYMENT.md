# 27-DEPLOYMENT.md

> Projeto → VeloAI
> Documento → Arquitetura de Deploy
> Stack → Docker + Docker Compose + Nginx
> Versão → 1.0.0

---

# Objetivo

Definir a arquitetura oficial de deploy do VeloAI.

Toda a plataforma deverá ser executada utilizando containers Docker.

Nenhum componente do sistema deverá exigir instalação manual de dependências na máquina do cliente ou do desenvolvedor.

Todo o ambiente deverá ser reproduzível através de Docker Compose.

A arquitetura deverá estar preparada para futura migração para Kubernetes sem necessidade de grandes alterações.

---

# Filosofia

Infraestrutura como Código.

Containers Imutáveis.

Ambientes Idênticos.

Deploy Reproduzível.

Configuração Centralizada.

Escalabilidade Horizontal.

---

# Ambientes

Development.

Testing.

Homologation.

Production.

Cada ambiente possuirá suas próprias variáveis, bancos, buckets, logs e configurações.

---

# Stack

Docker.

Docker Compose.

Nginx.

FastAPI.

Vue.

PostgreSQL.

Redis.

MinIO.

Celery.

OpenTelemetry Collector.

Prometheus.

Grafana.

Loki.

Tempo.

Sentry.

---

# Estrutura

```text
infra/

docker/

compose/

nginx/

certificates/

scripts/

monitoring/

backups/

postgres/

redis/

minio/
```

---

# Serviços

Frontend.

Backend API.

Provisioning Service.

Celery Worker.

Celery Beat.

Redis.

PostgreSQL Master.

MinIO.

Nginx.

Prometheus.

Grafana.

Loki.

Tempo.

OpenTelemetry Collector.

---

# Docker Compose

Arquivos.

```
docker-compose.dev.yml

docker-compose.test.yml

docker-compose.hml.yml

docker-compose.prod.yml
```

Arquivo base.

```
docker-compose.yml
```

---

# Containers

Frontend.

```
veloai-frontend
```

Backend.

```
veloai-backend
```

Provisioning.

```
veloai-provisioning
```

Worker.

```
veloai-worker
```

Scheduler.

```
veloai-beat
```

---

# Banco

Master.

```
veloai_master
```

Tenant.

```
tenant_xxxxx
```

Um banco PostgreSQL por empresa.

---

# Volumes

Persistir.

Banco.

Uploads.

Logs.

MinIO.

Backups.

Configurações.

Nunca armazenar dados importantes dentro dos containers.

---

# Redes Docker

Criar redes separadas.

Frontend.

Backend.

Database.

Monitoring.

Internal.

Nunca expor serviços internos diretamente para a internet.

---

# Nginx

Responsável por.

HTTPS.

SSL.

Compressão.

Cache.

Proxy Reverso.

Headers de Segurança.

Rate Limiting.

HTTP/2.

Preparado para HTTP/3.

---

# SSL

Let's Encrypt.

Renovação automática.

TLS 1.3.

HSTS.

Redirecionamento obrigatório para HTTPS.

---

# Variáveis de Ambiente

Arquivo.

```
.env
```

Nunca versionar.

Separar.

Backend.

Frontend.

Provisioning.

Workers.

Monitoramento.

---

# Variáveis Obrigatórias

```
GEMINI_API_KEY

AI_REPORT_MODEL=gemini-3.1-flash-lite

DATABASE_URL

REDIS_URL

MINIO_ENDPOINT

MINIO_ACCESS_KEY

MINIO_SECRET_KEY

JWT_SECRET

JWT_REFRESH_SECRET

ENCRYPTION_KEY

OTEL_EXPORTER_OTLP_ENDPOINT
```

---

# Build

Cada serviço possuirá Dockerfile próprio.

Nunca utilizar Dockerfile único.

Builds independentes.

---

# Multi Stage Build

Obrigatório.

Reduzir tamanho das imagens.

Remover dependências de desenvolvimento.

Melhorar segurança.

---

# Health Checks

Todos os containers deverão possuir.

Health Check.

Readiness.

Liveness.

Restart automático.

---

# Restart Policy

```
unless-stopped
```

Para produção.

---

# Logs

Enviar para.

Loki.

Nunca depender apenas de logs do Docker.

---

# Backup

Automático.

Banco Master.

Todos os Tenants.

MinIO.

Configurações.

Logs críticos.

---

# Restore

Executar.

Backup.

Validação.

Banco temporário.

Substituição.

Health Check.

---

# Atualizações

Fluxo.

Backup.

↓

Nova versão.

↓

Migration.

↓

Health Check.

↓

Smoke Test.

↓

Disponibilização.

---

# Rollback

Fluxo.

Falha.

↓

Restaurar versão anterior.

↓

Restaurar banco.

↓

Health Check.

↓

Notificação.

---

# Uploads

Todos os arquivos deverão ser armazenados no MinIO.

Nunca no sistema de arquivos do Backend.

---

# Escalabilidade

Preparar.

Backend.

Workers.

Provisioning.

IA.

Monitoramento.

Separadamente.

---

# Deploy Local

Executar apenas.

```
docker compose up -d
```

Toda a plataforma deverá iniciar automaticamente.

---

# Scripts

Criar.

```
start.sh

stop.sh

restart.sh

backup.sh

restore.sh

update.sh

health.sh
```

Todos documentados.

---

# Recursos

Permitir configuração de.

CPU.

Memória.

Limites.

Reservas.

Por container.

---

# Monitoramento

Integrar.

Prometheus.

Grafana.

Loki.

Tempo.

Sentry.

OpenTelemetry.

---

# Segurança

Containers sem privilégios.

Usuário não root.

Filesystem somente leitura quando possível.

Secrets externos.

Headers de segurança.

Firewall.

---

# Deploy Futuro

Preparado para.

Kubernetes.

Helm.

ArgoCD.

AWS ECS.

AWS EKS.

Azure AKS.

Google GKE.

Docker Swarm.

---

# Multi Região

Arquitetura preparada para.

Replicação.

Failover.

Balanceamento.

CDN.

Storage distribuído.

---

# CI

Ao final do CI.

Executar.

Docker Build.

Docker Compose Validation.

Health Checks.

Smoke Tests.

---

# Estrutura de Pastas

```text
infra/

docker/

compose/

nginx/

monitoring/

scripts/

backups/

certificates/

volumes/
```

---

# Regras Obrigatórias

Toda aplicação deverá executar em Docker.

Todo serviço deverá possuir Health Check.

Todo deploy deverá executar backup antes das migrations.

Toda atualização deverá executar Smoke Tests.

Todo upload deverá utilizar MinIO.

Todo container deverá ser independente.

Nenhuma configuração sensível poderá ser versionada.

---

# Roadmap

Adicionar.

Kubernetes.

Helm.

Terraform.

GitOps.

ArgoCD.

Blue Green Deploy.

Canary Deploy.

Auto Scaling.

Disaster Recovery.

Multi Cloud.

---

# Objetivo Final

A infraestrutura de deploy do VeloAI deverá fornecer um ambiente totalmente containerizado, seguro, reproduzível e escalável. Desde o desenvolvimento local até a produção, todos os componentes deverão seguir o mesmo padrão arquitetural, permitindo evolução contínua da plataforma sem alterações significativas na forma de implantação.

---
