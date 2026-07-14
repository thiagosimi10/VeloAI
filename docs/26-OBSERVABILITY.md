# 26-OBSERVABILITY.md

> Projeto → VeloAI
> Documento → Observabilidade
> Stack → OpenTelemetry + Prometheus + Grafana + Loki + Tempo + Sentry
> Versão → 1.0.0

---

# Objetivo

Definir a arquitetura oficial de observabilidade do VeloAI.

Todo componente da plataforma deverá ser monitorado continuamente.

Toda requisição deverá ser rastreável.

Todo erro deverá ser registrado.

Toda métrica deverá ser coletada.

Todo evento importante deverá ser auditado.

A observabilidade deverá permitir identificar rapidamente falhas, gargalos, problemas de performance e comportamento inesperado da plataforma.

---

# Filosofia

Monitorar tudo.

Medir tudo.

Registrar tudo.

Correlacionar tudo.

Alertar rapidamente.

Resolver antes do cliente perceber.

---

# Pilares

Logs.

Métricas.

Tracing.

Eventos.

Auditoria.

Alertas.

Dashboards.

---

# Stack Oficial

OpenTelemetry.

Prometheus.

Grafana.

Loki.

Tempo.

Sentry.

PostgreSQL.

Redis.

Celery.

FastAPI.

Docker.

---

# Arquitetura

```text
Frontend

↓

OpenTelemetry

↓

Backend

↓

Workers

↓

Provisioning

↓

Collector

↓

Prometheus

↓

Loki

↓

Tempo

↓

Grafana
```

---

# Logs

Todos os serviços deverão gerar logs estruturados.

Formato.

JSON.

Nunca utilizar logs em texto simples.

---

# Campos Obrigatórios

Timestamp.

Level.

Request ID.

Trace ID.

Span ID.

Tenant ID.

User ID.

Conversation ID.

Job ID.

Service.

Module.

Endpoint.

Tempo.

Mensagem.

Erro.

Stack Trace.

---

# Níveis

TRACE.

DEBUG.

INFO.

WARNING.

ERROR.

CRITICAL.

---

# Correlação

Toda requisição deverá possuir.

Trace ID.

Span ID.

Request ID.

Todos os serviços deverão propagar esses identificadores.

---

# Métricas

Backend.

Tempo de resposta.

Requests.

Erros.

Latência.

CPU.

Memória.

Banco.

Redis.

Workers.

Provisionamento.

IA.

---

# Métricas da IA

Quantidade de prompts.

Tokens enviados.

Tokens recebidos.

Tempo de resposta.

Modelo utilizado.

Custo estimado.

Quantidade de chamadas MCP.

Quantidade de consultas RAG.

Falhas.

Timeouts.

---

# Métricas do RAG

Documentos indexados.

Embeddings.

Consultas.

Tempo de busca.

Tempo de re-ranking.

Cache Hit.

Cache Miss.

Precisão.

---

# Métricas MCP

Tools executadas.

Tempo médio.

Falhas.

Timeout.

Permissões negadas.

Ferramentas mais utilizadas.

---

# Métricas Financeiras

Receitas.

Despesas.

Ordens de Serviço.

Produtos vendidos.

Clientes ativos.

Novos clientes.

Cancelamentos.

MRR.

ARR.

Churn.

---

# Métricas Multi Tenant

Quantidade de Tenants.

Uso por Tenant.

Espaço utilizado.

Chamadas IA.

Banco.

Storage.

Usuários.

Uploads.

---

# Métricas do Banco

Conexões.

Locks.

Deadlocks.

Consultas lentas.

Tempo médio.

Uso de Disco.

Replicação.

Vacuum.

---

# Métricas Docker

Containers.

Restart.

CPU.

Memória.

Disco.

Rede.

Health Check.

---

# Tracing

Todas as requisições deverão gerar traces.

Exemplo.

```text
Frontend

↓

API

↓

Service

↓

Repository

↓

PostgreSQL
```

Todo fluxo deverá ser rastreável.

---

# Dashboards Grafana

Dashboard Geral.

Backend.

Frontend.

Banco.

Redis.

Docker.

Provisioning.

IA.

RAG.

MCP.

Financeiro.

Negócio.

---

# Dashboard Executivo

Exibir.

MRR.

ARR.

Churn.

Empresas Ativas.

Usuários.

Chamadas IA.

Receita.

Performance.

Disponibilidade.

---

# Alertas

CPU.

Memória.

Disco.

Erros.

Timeouts.

Banco.

Redis.

Workers.

Provisionamento.

IA.

Rate Limit.

---

# Alertas Críticos

Banco indisponível.

Fila parada.

Worker parado.

Erro de Migration.

Erro de Provisionamento.

Erro IA.

Erro RAG.

Erro MCP.

---

# Auditoria

Registrar.

Usuário.

Tenant.

Ação.

IP.

Browser.

Sistema.

Resultado.

Data.

---

# Eventos

Login.

Logout.

Criação.

Alteração.

Exclusão.

Importação.

Exportação.

Uploads.

Downloads.

Provisionamento.

Backups.

---

# Frontend

Monitorar.

Tempo de carregamento.

Largest Contentful Paint.

First Input Delay.

Cumulative Layout Shift.

JavaScript Errors.

---

# Sentry

Capturar.

Exceptions.

Unhandled Errors.

Performance.

Releases.

Source Maps.

Frontend.

Backend.

Workers.

---

# Health Check

Todos os serviços deverão expor.

```
/health

/ready

/live

/metrics
```

---

# OpenTelemetry

Instrumentar.

FastAPI.

SQLAlchemy.

Redis.

Celery.

HTTP.

Requests.

Workers.

IA.

MCP.

---

# Logs da IA

Registrar.

Modelo.

Prompt.

Tempo.

Tokens.

Tool utilizada.

Resultado.

Nunca registrar informações sensíveis.

Nunca registrar documentos completos.

---

# Logs do Provisioning

Criar banco.

Criar schema.

Alembic.

Seeds.

Backup.

Restore.

Upgrade.

Rollback.

---

# Retenção

Logs.

90 dias.

Métricas.

180 dias.

Auditoria.

5 anos.

Backups conforme política definida.

---

# Segurança

Anonimizar.

Dados sensíveis.

Tokens.

Senhas.

Cartões.

Credenciais.

Nunca registrar dados protegidos.

---

# Performance

Toda instrumentação deverá gerar impacto mínimo.

Priorizar processamento assíncrono.

Compressão.

Batch.

Sampling configurável.

---

# APIs

```
GET /metrics

GET /health

GET /ready

GET /live
```

---

# Testes

Validar.

Logs.

Tracing.

Alertas.

Métricas.

Dashboards.

Health Checks.

---

# Regras Obrigatórias

Todo serviço deverá gerar métricas.

Todo endpoint deverá gerar Trace ID.

Todo erro deverá ser enviado ao Sentry.

Toda Tool MCP deverá registrar métricas.

Toda consulta RAG deverá registrar métricas.

Toda operação crítica deverá gerar auditoria.

Todo serviço deverá possuir endpoint de Health Check.

---

# Roadmap

Adicionar.

eBPF.

AIOps.

Detecção automática de anomalias.

Predição de falhas.

Auto Scaling baseado em métricas.

Dashboards personalizados por Tenant.

Custos por Tenant.

Observabilidade distribuída entre regiões.

---

# Objetivo Final

A observabilidade do VeloAI deverá fornecer visibilidade completa sobre toda a plataforma, permitindo rastrear qualquer requisição, identificar rapidamente problemas, medir desempenho, acompanhar indicadores técnicos e de negócio e garantir alta disponibilidade. Todos os componentes deverão produzir logs estruturados, métricas e traces integrados em uma única plataforma de monitoramento.

---
