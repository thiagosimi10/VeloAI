# 03-STACK-TECNOLOGICA.md

> Projeto → VeloAI
> Documento → Stack Tecnológica
> Versão → 1.0.0

---

# Objetivo

Definir oficialmente todas as tecnologias utilizadas no projeto.

Nenhuma tecnologia deverá ser adicionada sem justificativa.

Sempre priorizar estabilidade, comunidade, documentação e performance.

---

# Backend

| Item | Tecnologia | Versão |
|-------|------------|---------|
| Linguagem | Python | 3.13 |
| Framework | FastAPI | Última Estável |
| ORM | SQLAlchemy | 2.x |
| Migrations | Alembic | Última |
| Validação | Pydantic | v2 |
| Servidor | Uvicorn | Última |
| ASGI | Starlette | Nativo |

---

# Frontend

| Item | Tecnologia |
|-------|------------|
| Framework | Vue 3 |
| Linguagem | TypeScript |
| Build | Vite |
| Estado Global | Pinia |
| Router | Vue Router |
| HTTP | Axios |
| Cache | TanStack Query |
| CSS | TailwindCSS |
| Componentes | shadcn-vue |
| Ícones | Heroicons |
| Utilitários | VueUse |

---

# Tabelas

Tecnologia oficial → TanStack Table

Recursos obrigatórios:

- Ordenação
- Pesquisa
- Filtros
- Paginação
- Virtual Scroll
- Exportação
- Colunas configuráveis
- Responsividade

Caso seja necessário recursos empresariais avançados utilizar:

AG Grid Community.

Nunca utilizar:

- jQuery DataTables
- Bootstrap Tables

---

# Dashboard

Biblioteca oficial:

amCharts 5

Todos os gráficos deverão utilizar amCharts.

Tipos previstos:

- Line
- Column
- Bar
- Area
- Pie
- Donut
- Gauge
- Radar
- Heatmap
- Timeline
- Funnel
- Sankey
- Treemap
- Calendar
- Financial
- Map

---

# Design

Framework → TailwindCSS

Componentes → shadcn-vue

Ícones → Heroicons

Fonte principal → Inter

Fonte para código → JetBrains Mono

Dark Mode obrigatório.

Light Mode obrigatório.

---

# Banco de Dados

| Item | Tecnologia |
|-------|------------|
| Banco | PostgreSQL |
| ORM | SQLAlchemy |
| Migration | Alembic |

Cada empresa possuirá um banco exclusivo.

---

# Cache

Tecnologia → Redis

Responsável por:

- Cache
- Sessões
- Tokens
- Dashboard
- Relatórios
- Configurações
- Rate Limit

---

# Mensageria

Tecnologia → RabbitMQ

Responsável por:

- IA
- Emails
- WhatsApp
- PDFs
- OCR
- Integrações
- Importações
- Exportações

---

# Workers

Tecnologia → Celery

Responsável por tarefas assíncronas.

---

# Storage

Tecnologia → MinIO

Responsável por:

- Logos
- PDFs
- Imagens
- Documentos
- Assinaturas
- Anexos

Preparado para migração futura para AWS S3.

---

# Banco Vetorial

Tecnologia → Qdrant

Responsável por:

- Embeddings
- RAG
- Busca Semântica
- Memória da IA
- Base de Conhecimento

Cada Tenant possuirá uma Collection exclusiva.

---

# Inteligência Artificial

## Provider Inicial

Google AI

```env
AI_PROVIDER=google
AI_REPORT_MODEL=gemini-3.1-flash-lite
GEMINI_API_KEY=
AI_TEMPERATURE=0.2
AI_MAX_TOKENS=8192
AI_EMBEDDING_MODEL=text-embedding-004
```

---

## Frameworks

| Item | Tecnologia |
|-------|------------|
| Orquestração | LangGraph |
| Cadeias | LangChain |
| MCP | MCP Server |
| Vetores | Qdrant |

---

## Providers Compatíveis

A arquitetura deverá suportar:

- Google
- OpenAI
- Anthropic
- Ollama
- DeepSeek
- Grok
- Mistral
- Llama

A troca ocorrerá apenas por configuração.

---

# MCP

Implementação oficial:

Model Context Protocol.

Cada módulo possuirá suas próprias Tools.

Exemplos:

- CreateCustomer
- UpdateCustomer
- DeleteCustomer
- SearchCustomer
- CreateProduct
- UpdateProduct
- CreateOrder
- GenerateReport
- CreateInvoice
- UpdateStock

---

# RAG

Tecnologia:

- LangChain
- Qdrant
- Embeddings Google

Responsável por:

- Documentação
- FAQ
- Histórico
- Conhecimento da Empresa
- Procedimentos
- Catálogo

---

# OCR

Tecnologia prevista:

- Tesseract OCR
- Google Vision AI (futuro)

Utilização:

- Leitura de documentos
- Leitura de notas fiscais
- Leitura de etiquetas
- Leitura de cartões

---

# PDFs

Biblioteca oficial:

WeasyPrint

Responsável por:

- Ordens de Serviço
- Orçamentos
- Relatórios
- Financeiro
- Recibos

Todos deverão utilizar HTML + CSS.

Nunca gerar PDFs manualmente.

---

# Excel

Biblioteca oficial:

OpenPyXL

Utilização:

- Exportações
- Importações
- Relatórios

---

# Datas

Biblioteca:

Pendulum

Nunca utilizar datetime puro quando existir manipulação complexa de datas.

---

# Autenticação

JWT

Refresh Token

Argon2

OAuth preparado para futuras integrações.

---

# API

REST

OpenAPI

Swagger

JSON

Versionamento:

```text
/api/v1
```

---

# Logs

Biblioteca:

Structlog

Formato:

JSON

Integração:

OpenTelemetry

---

# Monitoramento

Ferramentas:

- Prometheus
- Grafana
- OpenTelemetry

---

# Docker

Docker obrigatório.

Docker Compose obrigatório.

Nenhuma instalação manual.

---

# Proxy

Nginx

Responsável por:

- HTTPS
- Proxy Reverso
- Compressão
- Cache Estático

---

# Testes Backend

| Tipo | Ferramenta |
|--------|------------|
| Unitários | pytest |
| Integração | pytest |
| Cobertura | pytest-cov |
| Mock | unittest.mock |

Cobertura mínima:

90%.

---

# Testes Frontend

| Tipo | Ferramenta |
|--------|------------|
| Unitários | Vitest |
| Componentes | Vue Test Utils |
| E2E | Playwright |

Cobertura mínima:

80%.

---

# Qualidade

Backend:

- Ruff
- Black
- Mypy
- Pre-Commit

Frontend:

- ESLint
- Prettier

---

# Git

Obrigatório:

- Conventional Commits
- Git Flow simplificado
- Pull Request
- Code Review

Branches:

- main
- develop
- feature/*
- hotfix/*
- release/*

---

# CI

GitHub Actions.

Executar automaticamente:

- Lint Backend
- Lint Frontend
- Testes Backend
- Testes Frontend
- Coverage
- Build Docker
- Verificação Alembic

---

# Deploy Futuro

Arquitetura preparada para:

- AWS ECS
- AWS EKS
- Kubernetes
- Azure
- GCP

Sem alterações na aplicação.

---

# Dependências

Sempre priorizar:

- Bibliotecas ativas
- Comunidade forte
- Boa documentação
- Performance
- Compatibilidade LTS

Nunca adicionar bibliotecas abandonadas.

---

# Objetivo Final

Toda a stack foi escolhida para garantir alta performance, escalabilidade, facilidade de manutenção e integração nativa com Inteligência Artificial, permitindo que o VeloAI evolua continuamente sem necessidade de mudanças estruturais.

---
