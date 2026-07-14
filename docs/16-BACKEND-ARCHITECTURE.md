# 16-BACKEND-ARCHITECTURE.md

> Projeto → VeloAI
> Documento → Arquitetura Backend
> Stack → Python + FastAPI
> Versão → 1.0.0

---

# Objetivo

O Backend do VeloAI deverá ser moderno, escalável, modular e preparado para crescimento durante muitos anos.

A arquitetura deverá seguir princípios de Domain Driven Design (DDD), Clean Architecture, SOLID, Event Driven Architecture e CQRS onde fizer sentido.

O objetivo é permitir que dezenas de desenvolvedores trabalhem simultaneamente sem gerar acoplamento entre módulos.

Toda regra de negócio deverá existir apenas no Backend.

O Frontend nunca conterá regras de negócio.

---

# Stack

Linguagem.

Python 3.13+

Framework.

FastAPI

Servidor ASGI.

Uvicorn

ORM.

SQLAlchemy 2.x

Migrações.

Alembic

Validação.

Pydantic v2

Autenticação.

JWT + Refresh Token

Hash.

Argon2

Banco.

PostgreSQL 17+

Vetores.

pgvector

Cache.

Redis

Fila.

Celery + Redis

Storage.

MinIO

Logs.

Structlog

Testes.

Pytest

Qualidade.

Ruff

Black

MyPy

Bandit

Pre-commit

Documentação.

OpenAPI

Swagger

ReDoc

Container.

Docker

Docker Compose

CI.

GitHub Actions

---

# Estrutura

```text
backend/

app/

api/

core/

modules/

shared/

ai/

mcp/

events/

workers/

tests/

scripts/

alembic/

docker/

docs/
```

---

# Organização dos Módulos

```text
modules/

customers/

products/

sales/

service_orders/

finance/

users/

companies/

reports/

dashboard/

automation/

notifications/
```

Cada módulo deverá ser completamente independente.

---

# Estrutura Interna do Módulo

Exemplo.

```text
customers/

api/

schemas/

models/

repositories/

services/

use_cases/

events/

mcp_tools/

permissions/

tests/

exceptions/

validators/
```

Nunca criar arquivos gigantes.

---

# Camadas

```text
API

↓

Use Cases

↓

Services

↓

Repositories

↓

Database
```

A API nunca acessará o banco diretamente.

---

# API

Responsável apenas por.

Receber requisições.

Validar.

Autenticar.

Autorizar.

Chamar Use Cases.

Retornar resposta.

Nenhuma regra de negócio.

---

# Use Cases

Responsáveis por.

Executar casos de uso.

Exemplo.

CreateCustomer.

UpdateCustomer.

GenerateReport.

CloseServiceOrder.

ReceivePayment.

---

# Services

Responsáveis por.

Regras de negócio.

Validações.

Eventos.

Integrações.

Nunca acessar HTTP diretamente.

---

# Repositories

Responsáveis por.

Consultar banco.

Persistir dados.

Nunca conter regra de negócio.

---

# Schemas

Utilizar Pydantic v2.

Separar.

Create.

Update.

Response.

Filter.

Pagination.

Nunca reutilizar o mesmo Schema para tudo.

---

# Models

SQLAlchemy 2.x.

Utilizar.

Mapped.

mapped_column.

Relationships.

Typing completo.

Soft Delete.

UUID.

Created At.

Updated At.

Deleted At.

Tenant ID.

---

# Multi Tenancy

Cada empresa possuirá.

Banco PostgreSQL exclusivo.

Nunca compartilhar banco.

Ao criar uma empresa.

↓

Criar Database.

↓

Executar Alembic.

↓

Criar usuário administrador.

↓

Criar configurações padrão.

↓

Criar permissões.

↓

Criar dados iniciais.

Toda conexão deverá ser resolvida dinamicamente.

---

# Connection Manager

Criar um TenantConnectionManager.

Responsável por.

Resolver Tenant.

Abrir conexão.

Pool.

Fechar conexão.

Cache.

Health Check.

Nunca manter conexões desnecessárias.

---

# Autenticação

JWT.

Refresh Token.

Rotação automática.

Blacklist.

Expiração.

Multi dispositivo.

---

# Autorização

RBAC.

Permissões granulares.

Exemplo.

```
customers.create

customers.update

sales.cancel

finance.receive

dashboard.view
```

Nunca validar permissões no Frontend.

---

# Eventos

Arquitetura orientada a eventos.

Exemplos.

CustomerCreated.

ProductUpdated.

SaleFinished.

StockChanged.

PaymentReceived.

Eventos nunca deverão depender entre si.

---

# Filas

Celery.

Redis.

Executar.

Emails.

WhatsApp.

PDF.

OCR.

IA.

Importações.

Relatórios.

Backup.

Nunca bloquear requisições HTTP.

---

# Cache

Redis.

Utilizar.

Dashboard.

Configurações.

Relatórios.

KPIs.

Permissões.

Usuário.

Empresa.

Nunca utilizar cache para dados inconsistentes.

---

# Storage

MinIO.

Salvar.

Fotos.

Vídeos.

Documentos.

PDF.

Logos.

Anexos.

Nunca armazenar arquivos dentro do PostgreSQL.

---

# IA

Criar módulo próprio.

```text
ai/

gateway/

agents/

planner/

executor/

rag/

memory/

providers/

prompts/

tools/

observability/
```

Toda IA deverá utilizar esta camada.

---

# MCP

Criar módulo.

```text
mcp/

server/

tools/

registry/

permissions/

executor/
```

Toda Tool será registrada automaticamente.

---

# Configuração

Utilizar.

.env

Pydantic Settings.

Separar.

Development.

Testing.

Production.

Nunca utilizar valores fixos.

---

# Variáveis Obrigatórias

```env
APP_NAME=VeloAI

APP_ENV=development

DATABASE_ADMIN_URL=

REDIS_URL=

MINIO_URL=

MINIO_ACCESS_KEY=

MINIO_SECRET_KEY=

JWT_SECRET=

JWT_REFRESH_SECRET=

GEMINI_API_KEY=

AI_REPORT_MODEL=gemini-3.1-flash-lite

LOG_LEVEL=INFO
```

---

# Logs

Structlog.

Registrar.

Request.

Response.

Tempo.

Usuário.

Tenant.

IP.

Erro.

Tool IA.

Evento.

Nunca registrar senhas.

Nunca registrar tokens completos.

---

# Tratamento de Erros

Criar padrão único.

```json
{
  "success": false,
  "message": "...",
  "code": "...",
  "details": []
}
```

Nunca retornar Traceback para o usuário.

---

# Paginação

Padrão.

```
page

page_size

total

items
```

---

# Filtros

Padronizar.

```
search

sort

order

page

page_size
```

Todos os endpoints deverão seguir este padrão.

---

# Versionamento

```text
/api/v1/
```

Preparado para futuras versões.

---

# Health Check

Endpoints.

```
/health

/ready

/live
```

---

# Observabilidade

OpenTelemetry.

Prometheus.

Grafana.

Sentry.

Métricas.

Logs.

Tracing.

---

# Docker

Cada serviço separado.

Backend.

Redis.

PostgreSQL Admin.

MinIO.

Celery Worker.

Celery Beat.

Nginx.

Frontend.

Todos iniciados via Docker Compose.

Nenhuma instalação manual deverá ser necessária.

---

# Testes

Unitários.

Integração.

API.

Repositories.

Services.

Use Cases.

MCP Tools.

IA.

Cobertura mínima.

90%.

---

# CI

GitHub Actions.

Executar.

Lint.

Ruff.

Black.

MyPy.

Bandit.

Pytest.

Coverage.

Build Docker.

Validar Alembic.

Validar OpenAPI.

Nenhum merge permitido com falhas.

---

# Convenções

Utilizar.

Type Hints.

Async/Await.

Dependency Injection.

SOLID.

DRY.

KISS.

YAGNI.

PEP8.

Imports absolutos.

---

# Proibições

Nunca utilizar lógica de negócio nas rotas.

Nunca utilizar SQL puro sem necessidade.

Nunca acessar banco diretamente na API.

Nunca utilizar print().

Nunca utilizar valores hardcoded.

Nunca misturar módulos.

Nunca quebrar isolamento entre Tenants.

Nunca acessar banco de outro cliente.

---

# Roadmap

Preparado para.

Kubernetes.

Horizontal Scaling.

Múltiplos Workers.

RabbitMQ.

Kafka.

Microserviços.

GraphQL.

gRPC.

Event Sourcing.

---

# Objetivo Final

O Backend do VeloAI deverá ser robusto, modular, altamente escalável e preparado para suportar milhares de empresas utilizando bancos isolados por Tenant. Toda a lógica de negócio deverá residir nesta camada, garantindo segurança, rastreabilidade, facilidade de manutenção e integração transparente com a plataforma de Inteligência Artificial, MCP, automações e aplicações Web e Mobile.

---
