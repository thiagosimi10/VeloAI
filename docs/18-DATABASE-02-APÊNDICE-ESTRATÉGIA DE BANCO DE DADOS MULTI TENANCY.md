# APÊNDICE — ESTRATÉGIA DE BANCO DE DADOS MULTI TENANCY

> Projeto → VeloAI
> Documento Complementar do 18-DATABASE.md
> Assunto → Arquitetura de Bancos PostgreSQL
> Versão → 1.0.0

---

# Objetivo

Definir a arquitetura oficial de Multi Tenancy do VeloAI.

Esta arquitetura deverá permitir milhares de empresas utilizando o sistema com total isolamento entre clientes, facilidade de backup, facilidade de restauração, excelente performance e simplicidade operacional.

---

# Arquitetura Oficial

O VeloAI utilizará o modelo.

```
1 Banco Master

+

1 Banco PostgreSQL exclusivo para cada empresa
```

Exemplo.

```
veloai_master

↓

cliente_acme

↓

cliente_oficina_silva

↓

cliente_alpha

↓

cliente_beta

↓

cliente_gama
```

Cada banco possuirá exatamente a mesma estrutura.

---

# Banco Master

O banco Master nunca armazenará dados operacionais.

Sua única responsabilidade será administrar toda a plataforma SaaS.

---

## Responsabilidades

Cadastro das empresas.

Planos.

Assinaturas.

Licenciamento.

Billing.

Autenticação inicial.

Registro dos bancos.

Feature Flags.

Integrações Globais.

Auditoria Global.

---

## Estrutura

```text
veloai_master

public

companies

subscriptions

plans

billing

tenant_registry

master_users

api_keys

domains

audit_logs

feature_flags
```

---

# Banco do Tenant

Cada empresa possuirá um banco exclusivo.

Exemplo.

```
cliente_oficina_silva
```

Dentro dele existirão dois schemas.

---

# Schema public

Responsável pelos dados da empresa.

```text
public

customers

products

sales

service_orders

finance

users

reports

dashboard

automation

notifications

...
```

Toda informação operacional ficará aqui.

---

# Schema system

Responsável pela infraestrutura interna do VeloAI.

Nunca conterá dados do cliente.

---

## Estrutura

```text
system

internal_settings

migration_history

system_jobs

cache_metadata

event_store

queue_control

worker_status

health_checks

locks

feature_flags_local

scheduler

audit_system

tool_registry

ai_cache
```

---

# Benefícios do Schema system

Separação completa entre.

Dados do Cliente.

Infraestrutura.

Isso evita.

Misturar tabelas técnicas.

Poluir o schema public.

Problemas durante upgrades.

Conflitos em migrações futuras.

---

# Alembic

As migrations deverão executar automaticamente.

Primeiro.

```text
Schema system
```

Depois.

```text
Schema public
```

Assim toda infraestrutura já estará disponível.

---

# Criação de Novo Tenant

Fluxo.

```text
Empresa criada

↓

Criar Database

↓

Criar Schema system

↓

Criar Schema public

↓

Executar Alembic

↓

Executar Seeds

↓

Criar Usuário Administrador

↓

Criar Dashboard

↓

Criar Configurações

↓

Empresa pronta
```

Todo processo deverá ser automático.

---

# Tenant Registry

No banco Master.

Tabela.

```
tenant_registry
```

Campos.

```text
tenant_id

company_name

database_name

database_host

database_port

database_user

encrypted_database_password

status

created_at

updated_at
```

Nunca armazenar senha em texto puro.

---

# Connection Manager

Criar componente.

```
TenantConnectionManager
```

Responsabilidades.

Resolver Tenant.

Localizar banco.

Abrir conexão.

Gerenciar Pool.

Cache.

Fechar conexões inativas.

Health Check.

Reconexão automática.

---

# Pool de Conexões

Cada Tenant possuirá.

Pool independente.

Nunca compartilhar conexão entre bancos.

---

# Health Check

Verificar periodicamente.

Banco disponível.

Migrações pendentes.

Espaço.

Tempo de resposta.

Versão PostgreSQL.

---

# Backup

Cada empresa poderá possuir.

Backup completo.

Backup incremental.

Restore individual.

Nunca restaurar todos os bancos.

---

# Restore

Fluxo.

```text
Selecionar Empresa

↓

Selecionar Backup

↓

Criar Banco Temporário

↓

Validar Integridade

↓

Substituir Banco

↓

Atualizar Tenant Registry
```

---

# Migrações

Nunca executar migrations manualmente.

Fluxo.

```text
Nova Release

↓

Detectar Bancos

↓

Executar Alembic

↓

Validar

↓

Registrar Resultado

↓

Próximo Tenant
```

Caso uma migration falhe.

Parar apenas naquele Tenant.

Nunca interromper os demais.

---

# Versionamento

Tabela.

```
system.migration_history
```

Campos.

Migration.

Versão.

Data.

Tempo.

Resultado.

Erro.

Rollback.

---

# Scheduler

Tabela.

```
system.scheduler
```

Controlará.

Jobs.

Cron.

Workflows.

Execuções.

Retry.

---

# Queue

Tabela.

```
system.queue_control
```

Controlará.

Eventos.

Filas.

Retries.

Dead Letter Queue.

---

# IA

Tabela.

```
system.ai_cache
```

Armazenará.

Cache.

Embeddings temporários.

Prompt Cache.

Tokens.

Nunca armazenar documentos do cliente.

---

# Auditoria Técnica

Tabela.

```
system.audit_system
```

Registrar.

Migrações.

Falhas.

Workers.

Atualizações.

Eventos internos.

---

# Segurança

Usuários nunca terão acesso ao schema system.

Apenas a aplicação.

---

# Permissões PostgreSQL

Criar usuário.

```
veloai_app
```

Permissões.

Schema public.

Schema system.

Nunca utilizar usuário postgres na aplicação.

---

# Criptografia

Credenciais dos bancos.

Sempre criptografadas.

Nunca armazenar senha em texto puro.

Utilizar.

AES-256.

Secrets Manager futuramente.

---

# Escalabilidade

Preparado para.

Read Replica.

Write Replica.

Cluster PostgreSQL.

Patroni.

PgBouncer.

HAProxy.

Kubernetes.

Cloud SQL.

Aurora PostgreSQL.

---

# Monitoramento

Prometheus.

Grafana.

OpenTelemetry.

Sentry.

Métricas.

Conexões.

Tempo.

Locks.

Deadlocks.

CPU.

Memória.

Disco.

---

# Roadmap

Preparado para.

Múltiplos servidores PostgreSQL.

Sharding por Região.

Replicação Geográfica.

Failover Automático.

Backup em Nuvem.

Disaster Recovery.

Multi Cloud.

---

# Padrão Oficial do Projeto

O VeloAI adotará oficialmente a arquitetura.

```text
Banco Master

↓

Banco Individual por Empresa

↓

Schema public

↓

Dados Operacionais

+

Schema system

↓

Infraestrutura Interna
```

Esta arquitetura deverá ser seguida por todos os módulos do sistema, garantindo isolamento total entre empresas, facilidade de manutenção, escalabilidade horizontal, segurança e simplicidade nas operações de backup, restore, migrações e monitoramento.

---
