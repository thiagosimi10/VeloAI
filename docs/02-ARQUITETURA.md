# 02-ARQUITETURA.md

> Projeto → VeloAI
> Arquitetura → AI Business OS
> Versão → 1.0.0

---

# Objetivo

Definir toda a arquitetura técnica do VeloAI.

A arquitetura deverá ser escalável, modular, desacoplada, preparada para milhares de empresas e permitir evolução sem necessidade de grandes refatorações.

---

# Arquitetura Geral

```text
                        Internet
                            │
                        Cloudflare
                            │
                         Nginx
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
     Frontend                              Backend API
      Vue 3                                  FastAPI
        │                                       │
        └───────────────────┬───────────────────┘
                            │
                     Authentication
                            │
                     Authorization
                            │
                    Business Services
                            │
       ┌───────────────┬───────────────┬───────────────┐
       │               │               │               │
     PostgreSQL      Redis         RabbitMQ        Qdrant
       │                               │
       │                           Celery
       │                               │
       └───────────────┬───────────────┘
                       │
                    MinIO
```

---

# Arquitetura por Camadas

Toda funcionalidade seguirá obrigatoriamente:

```text
Vue

↓

API

↓

Controller

↓

Service

↓

Domain

↓

Repository

↓

PostgreSQL
```

Nunca pular camadas.

---

# Clean Architecture

Cada módulo será independente.

Exemplo:

```text
Customers

API

↓

Services

↓

Domain

↓

Repository

↓

Database
```

Outro módulo nunca acessará diretamente Repository de outro módulo.

Toda comunicação ocorrerá através de Services.

---

# Organização do Backend

```text
backend/

app/

auth/
company/
users/
customers/
suppliers/
products/
categories/
stock/
services/
orders/
sales/
finance/
reports/
dashboard/
notifications/
automation/
fiscal/
integrations/
ai/
common/
```

Cada pasta será um módulo independente.

---

# Organização do Frontend

```text
frontend/

src/

modules/

dashboard/
customers/
products/
stock/
services/
orders/
sales/
finance/
reports/
company/
users/
settings/
auth/

shared/

components/
layouts/
router/
stores/
composables/
utils/
types/
assets/
```

---

# Comunicação

Frontend → Backend → Services → Banco

Nunca:

Frontend → Banco

Frontend → IA

Frontend → Repository

---

# API

Toda comunicação ocorrerá através de REST.

Padrão:

```text
/api/v1/
```

Preparada para:

```
/api/v2/
/api/v3/
```

---

# Padrão REST

GET → Consultar

POST → Criar

PUT → Atualizar

PATCH → Atualização parcial

DELETE → Soft Delete

---

# Autenticação

JWT.

Refresh Token.

Tempo curto para Access Token.

Refresh Token renovável.

---

# Permissões

RBAC.

Perfis iniciais:

Administrador

Gerente

Financeiro

Vendedor

Técnico

Funcionário

Cliente (Portal)

---

# Multi Tenant

Cada empresa possuirá:

- Banco PostgreSQL exclusivo.
- Bucket MinIO exclusivo.
- Vetor Qdrant exclusivo.
- Configurações exclusivas.
- Usuários exclusivos.

Fluxo:

```text
Cadastro Empresa

↓

Criar Tenant

↓

Criar Banco

↓

Executar Alembic

↓

Executar Seeds

↓

Criar Admin

↓

Empresa pronta
```

---

# Banco

Engine → PostgreSQL

ORM → SQLAlchemy 2

Migration → Alembic

Soft Delete obrigatório.

Auditoria obrigatória.

---

# Cache

Redis será utilizado para:

- Sessões.
- Tokens.
- Cache.
- Dashboard.
- Relatórios.
- Rate Limit.
- Configurações.
- Feature Flags.

---

# Filas

RabbitMQ + Celery.

Responsável por:

- IA.
- PDFs.
- OCR.
- Emails.
- WhatsApp.
- Importações.
- Exportações.
- Processamentos longos.

Nunca bloquear requisições HTTP.

---

# Storage

MinIO.

Responsável por:

- Logos.
- PDFs.
- Imagens.
- Documentos.
- Assinaturas.
- Anexos.
- Backups temporários.

Cada empresa possuirá seu próprio bucket lógico.

---

# Vetores

Qdrant.

Responsável por:

- Embeddings.
- RAG.
- Documentação.
- FAQ.
- Base de Conhecimento.
- Histórico contextual.

Cada Tenant possuirá sua própria Collection.

---

# Inteligência Artificial

Provider inicial:

```env
AI_PROVIDER=google
AI_REPORT_MODEL=gemini-3.1-flash-lite
GEMINI_API_KEY=
```

Arquitetura preparada para:

- OpenAI
- Anthropic
- Ollama
- DeepSeek
- Grok
- Mistral

Troca apenas por configuração.

---

# Arquitetura da IA

```text
Usuário

↓

Planner Agent

↓

Executor Agent

↓

Tool

↓

Service

↓

Repository

↓

Banco
```

Nunca permitir:

IA → Banco.

IA → SQL.

IA → Repository.

---

# MCP

Toda funcionalidade deverá possuir Tool.

Exemplos:

CreateCustomer

CreateProduct

UpdateProduct

DeleteProduct

CreateOrder

CreateServiceOrder

GenerateReport

UpdateStock

CreateInvoice

SearchCustomer

SearchProduct

ListOrders

Todas serão disponibilizadas pelo MCP Server.

---

# RAG

O RAG será utilizado para:

- Manual do sistema.
- FAQ.
- Produtos.
- Serviços.
- Base técnica.
- Histórico.
- Procedimentos internos.
- Conhecimento da empresa.

Cada empresa possuirá sua própria base vetorial.

---

# Dashboard

Toda informação exibida será construída através de Services.

Nunca consultar banco diretamente pela tela.

Gráficos → amCharts 5.

Tabelas → TanStack Table.

Insights → IA.

---

# Comunicação entre Módulos

Permitido:

CustomerService → FinanceService.

OrderService → StockService.

SalesService → ProductService.

Proibido:

CustomerRepository → FinanceRepository.

ProductRepository → OrderRepository.

Toda comunicação entre módulos ocorrerá por Services.

---

# Eventos

O sistema será preparado para Event Driven.

Eventos iniciais:

CustomerCreated

ProductCreated

OrderCreated

OrderFinished

InvoiceIssued

PaymentReceived

StockUpdated

UserCreated

CompanyCreated

Esses eventos poderão disparar:

- IA.
- Notificações.
- Emails.
- WhatsApp.
- Webhooks.
- Auditoria.
- Logs.

---

# Integrações Futuras

Arquitetura preparada para:

- WhatsApp.
- Mercado Pago.
- Stripe.
- Asaas.
- Open Finance.
- Google Calendar.
- Google Drive.
- Outlook.
- NFS-e.
- NFe.
- NFC-e.

Nenhuma integração deverá acoplar diretamente aos módulos.

Sempre utilizar camada de Providers.

---

# Docker

Containers:

- frontend
- backend
- postgres
- redis
- rabbitmq
- celery-worker
- celery-beat
- qdrant
- minio
- nginx

Comando único:

```bash
docker compose up -d
```

---

# Observabilidade

Obrigatório:

- OpenTelemetry.
- Prometheus.
- Grafana.
- Health Check.
- Readiness.
- Liveness.
- Structured Logs.

---

# Segurança

Obrigatório:

- HTTPS.
- JWT.
- Refresh Token.
- Argon2.
- Rate Limit.
- Auditoria.
- Logs.
- CORS.
- Sanitização.
- Validação de Entrada.
- LGPD.

---

# Escalabilidade

Arquitetura preparada para:

- Docker Swarm.
- Kubernetes.
- AWS ECS.
- AWS EKS.
- Azure AKS.

Todos os serviços deverão ser stateless, exceto banco e armazenamento.

---

# Objetivo Final

A arquitetura do VeloAI deverá suportar milhares de empresas utilizando isolamento completo entre tenants, alta disponibilidade, integração nativa com IA e capacidade de expansão sem necessidade de reescrita da aplicação.

---
