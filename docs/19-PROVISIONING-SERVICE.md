# 19-PROVISIONING-SERVICE.md

> Projeto → VeloAI
> Documento → Serviço de Provisionamento de Tenants
> Módulo → Infrastructure
> Versão → 1.0.0

---

# Objetivo

O Provisioning Service será um microserviço interno responsável exclusivamente pela criação, manutenção e gerenciamento da infraestrutura dos Tenants do VeloAI.

Nenhum outro serviço do sistema poderá criar bancos de dados, executar migrations ou realizar operações administrativas no PostgreSQL.

O Backend principal nunca deverá possuir permissões de administrador do banco.

Todo o provisionamento será centralizado neste serviço.

---

# Responsabilidades

Criar novos bancos PostgreSQL.

Criar Schemas.

Executar Alembic.

Executar Seeds.

Criar usuário administrador.

Criar configurações padrão.

Criar Dashboard padrão.

Criar papéis e permissões.

Criar categorias iniciais.

Criar centros de custo.

Criar templates.

Criar workflows padrão.

Registrar Tenant.

Executar upgrades.

Executar rollback.

Executar backup.

Executar restore.

Executar validações.

Monitorar saúde dos bancos.

---

# Filosofia

Backend Principal.

↓

Solicita Provisionamento.

↓

Provisioning Service.

↓

Executa todas as operações administrativas.

↓

Retorna resultado.

O Backend nunca acessará comandos administrativos do PostgreSQL.

---

# Arquitetura

```text
Frontend

↓

Backend API

↓

Provisioning API

↓

PostgreSQL

↓

Alembic

↓

Seeds

↓

Tenant Registry

↓

Resposta
```

---

# Stack

Python 3.13

FastAPI

SQLAlchemy

Alembic

PostgreSQL

Redis

Celery

Docker

Docker Compose

Pydantic v2

Structlog

Prometheus

OpenTelemetry

Pytest

GitHub Actions

---

# Estrutura

```text
provisioning/

api/

services/

repositories/

workers/

schemas/

models/

tasks/

events/

validators/

scripts/

tests/

docker/

migrations/
```

---

# Fluxo de Criação

```text
Empresa criada

↓

Validar dados

↓

Criar banco PostgreSQL

↓

Criar Schema system

↓

Criar Schema public

↓

Executar Alembic

↓

Executar Seeds

↓

Criar Usuário Admin

↓

Criar Configurações

↓

Criar Dashboard

↓

Criar Templates

↓

Registrar Tenant

↓

Executar Health Check

↓

Retornar sucesso
```

---

# Criação do Banco

Nome padrão.

```
tenant_{uuid}
```

Nunca utilizar o nome da empresa.

Nunca permitir caracteres especiais.

Nunca reutilizar nomes.

---

# Schemas

Criar automaticamente.

```
public
```

```
system
```

---

# Alembic

Executar.

Base.

Módulos.

IA.

Automações.

Dashboard.

Relatórios.

Configurações.

Sempre validar sucesso.

---

# Seeds

Criar automaticamente.

Administrador.

Perfil Administrador.

Papéis.

Permissões.

Empresa.

Categorias.

Centros de Custo.

Dashboard.

Templates.

Workflows.

Configurações.

Numerações.

---

# Usuário Administrador

Criar automaticamente.

Receber.

Nome.

Email.

Senha temporária.

Obrigar troca no primeiro login.

---

# Registro Master

Após criação.

Atualizar.

tenant_registry.

companies.

subscriptions.

feature_flags.

---

# Health Check

Validar.

Banco.

Schemas.

Permissões.

Migrações.

Seeds.

Usuário.

Conexão.

Tempo de resposta.

---

# Provisionamento Assíncrono

Todo provisionamento ocorrerá em Background.

Fluxo.

```text
Solicitação

↓

Fila Celery

↓

Worker

↓

Provisionamento

↓

Notificação

↓

Finalização
```

Nunca bloquear requisições HTTP.

---

# Upgrade de Tenant

Fluxo.

```text
Nova versão

↓

Selecionar Tenant

↓

Backup

↓

Executar Alembic

↓

Executar Scripts

↓

Validar

↓

Registrar Resultado
```

---

# Rollback

Caso falhe.

```text
Migration

↓

Erro

↓

Rollback

↓

Restaurar Backup

↓

Registrar Erro

↓

Notificar Administrador
```

---

# Backup

Permitir.

Backup Manual.

Backup Automático.

Backup Agendado.

Backup Incremental.

Backup Completo.

Compressão.

Criptografia.

---

# Restore

Fluxo.

Selecionar Backup.

Criar Banco Temporário.

Validar Integridade.

Substituir Banco.

Atualizar Registry.

Executar Health Check.

---

# Clonagem

Permitir criar.

Ambiente de Homologação.

Ambiente de Testes.

Ambiente Temporário.

Sempre mascarando dados sensíveis quando configurado.

---

# Exclusão

Nunca excluir imediatamente.

Fluxo.

Cancelar assinatura.

↓

Marcar Tenant.

↓

Período de retenção.

↓

Backup Final.

↓

Exclusão definitiva.

---

# Segurança

Somente o Provisioning Service possuirá.

CREATE DATABASE.

DROP DATABASE.

CREATE USER.

ALTER DATABASE.

CREATE SCHEMA.

O Backend principal nunca possuirá essas permissões.

---

# APIs

```
POST /provisioning/tenant

GET /provisioning/tenant/{id}

POST /provisioning/tenant/{id}/upgrade

POST /provisioning/tenant/{id}/backup

POST /provisioning/tenant/{id}/restore

POST /provisioning/tenant/{id}/clone

DELETE /provisioning/tenant/{id}

GET /provisioning/jobs

GET /provisioning/health
```

---

# Eventos

TenantProvisionStarted.

TenantProvisionFinished.

TenantProvisionFailed.

TenantBackupCreated.

TenantRestored.

TenantUpgraded.

TenantRollbackExecuted.

TenantDeleted.

---

# Logs

Registrar.

Empresa.

Tenant.

Tempo.

Usuário.

Servidor.

Migration.

Seed.

Erro.

Resultado.

Worker.

---

# Auditoria

Registrar.

Quem solicitou.

Quando.

Qual Tenant.

Resultado.

Tempo.

Versão.

Rollback.

---

# Observabilidade

OpenTelemetry.

Prometheus.

Grafana.

Sentry.

Métricas.

Tempo médio.

Falhas.

Provisionamentos.

Backups.

Restores.

---

# Retry

Permitir.

Número de Tentativas.

Intervalo.

Backoff Exponencial.

Fila de Erros.

Dead Letter Queue.

---

# Permissões

Somente usuários Master.

Nunca usuários do Tenant.

Nunca chamadas públicas.

---

# Docker

Serviço independente.

```yaml
provisioning

postgres

redis

celery-worker

celery-beat
```

---

# CI

Executar.

Lint.

Testes.

Coverage.

Build Docker.

Validação Alembic.

Validação Seeds.

---

# Testes

Cobertura mínima.

95%.

Testar.

Criação de Banco.

Schemas.

Alembic.

Seeds.

Rollback.

Upgrade.

Backup.

Restore.

Clone.

Retry.

Permissões.

---

# Roadmap

Provisionamento em Kubernetes.

Provisionamento Multi Região.

Provisionamento Multi Cloud.

Suporte ao Amazon Aurora.

Suporte ao Cloud SQL.

Suporte ao Azure Database.

Provisionamento automático por Terraform.

Integração com HashiCorp Vault.

---

# Regras de Negócio

Cada empresa possuirá exatamente um banco PostgreSQL.

Todo banco possuirá os schemas public e system.

Toda criação deverá gerar auditoria.

Todo upgrade deverá executar backup antes.

Nenhuma operação administrativa poderá ser executada pelo Backend principal.

Nenhum Tenant poderá acessar outro banco.

Toda operação deverá ser idempotente.

---

# Objetivo Final

O Provisioning Service será o responsável por toda a infraestrutura de bancos de dados do VeloAI, garantindo que a criação, atualização, backup, restauração e exclusão de Tenants ocorram de forma segura, automatizada, auditável e escalável. Essa separação elimina privilégios administrativos do Backend principal, aumenta a segurança da plataforma e prepara o sistema para operar milhares de empresas distribuídas em múltiplos servidores e provedores de nuvem.

---

# Status

✅ Documento concluído.

**ACABAMOS O 19-PROVISIONING-SERVICE.md**