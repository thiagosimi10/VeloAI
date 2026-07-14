# 18-DATABASE.md

> Projeto → VeloAI
> Documento → Arquitetura do Banco de Dados
> Banco → PostgreSQL 17 + pgvector
> Versão → 1.0.0

---

# Objetivo

O banco de dados do VeloAI deverá ser totalmente preparado para uma arquitetura Multi Tenant Database Per Tenant.

Cada empresa cadastrada possuirá um banco PostgreSQL exclusivo.

Nenhuma empresa compartilhará tabelas com outra empresa.

O banco deverá ser altamente normalizado, preparado para milhões de registros e otimizado para consultas rápidas.

Toda estrutura deverá ser criada automaticamente através de Alembic Migrations.

---

# Arquitetura Multi Tenant

Fluxo.

```text
Novo Cliente

↓

Cadastro da Empresa

↓

Criação Database PostgreSQL

↓

Execução Alembic

↓

Criação Usuário Administrador

↓

Carga Dados Iniciais

↓

Empresa pronta para uso
```

Banco Master.

Responsável apenas por.

Empresas.

Assinaturas.

Planos.

Cobranças.

Licenciamento.

Autenticação Inicial.

Tenant Registry.

Nunca armazenar dados operacionais.

---

# Banco Master

Tabelas.

companies

subscriptions

plans

users_master

tenant_registry

domains

billing

audit_master

feature_flags

api_keys

webhooks

---

# Banco do Tenant

Cada empresa possuirá exatamente a mesma estrutura.

---

# Módulo Empresa

Tabelas.

companies

company_settings

company_branding

company_integrations

company_preferences

company_documents

company_addresses

company_contacts

company_holidays

---

# Módulo Usuários

users

roles

permissions

role_permissions

user_roles

sessions

refresh_tokens

login_history

password_history

api_tokens

mfa_codes

notifications_preferences

---

# Módulo Clientes

customers

customer_addresses

customer_contacts

customer_notes

customer_tags

customer_files

customer_history

customer_documents

customer_equipment

customer_custom_fields

---

# Módulo Produtos

products

product_categories

product_brands

product_units

product_prices

product_images

product_suppliers

product_stock

product_stock_movements

product_serial_numbers

product_batches

product_custom_fields

---

# Módulo Serviços

services

service_categories

service_prices

service_checklists

service_templates

---

# Módulo Ordens de Serviço

service_orders

service_order_items

service_order_products

service_order_services

service_order_files

service_order_photos

service_order_signatures

service_order_comments

service_order_checklists

service_order_timeline

service_order_history

---

# Módulo Comercial

quotes

quote_items

sales

sale_items

sale_services

sales_commissions

sales_history

sales_payments

---

# Módulo Financeiro

accounts_receivable

accounts_receivable_payments

accounts_payable

accounts_payable_payments

cash_flow

cash_register

financial_categories

cost_centers

bank_accounts

bank_reconciliation

financial_projections

---

# Módulo Agenda

calendar_events

calendar_resources

calendar_participants

calendar_notifications

---

# Módulo Estoque

stock_movements

stock_adjustments

stock_inventory

stock_inventory_items

stock_transfers

purchase_orders

purchase_order_items

suppliers

supplier_contacts

---

# Módulo Dashboard

dashboard_widgets

dashboard_layouts

dashboard_preferences

dashboard_filters

---

# Módulo Relatórios

saved_reports

scheduled_reports

report_history

report_exports

---

# Módulo IA

ai_conversations

ai_messages

ai_tool_calls

ai_tool_results

ai_feedback

ai_embeddings

ai_documents

ai_prompts

ai_token_usage

ai_models

ai_context_cache

---

# Módulo Automações

automation_workflows

automation_versions

automation_nodes

automation_connections

automation_variables

automation_executions

automation_logs

automation_templates

automation_schedules

---

# Módulo Notificações

notifications

notification_templates

notification_logs

notification_channels

email_queue

sms_queue

whatsapp_queue

push_notifications

---

# Módulo Auditoria

audit_logs

audit_events

entity_versions

change_history

security_events

---

# Módulo Arquivos

files

folders

attachments

file_versions

file_permissions

---

# Módulo Fiscal

invoice_queue

invoice_history

invoice_settings

tax_rules

future_integrations

---

# Módulo Configuração

settings

feature_flags

system_preferences

custom_fields

tags

labels

number_sequences

---

# Campos Padrão

Todas as tabelas deverão possuir.

```text
id UUID

created_at TIMESTAMP

updated_at TIMESTAMP

deleted_at TIMESTAMP NULL

created_by UUID

updated_by UUID

version INTEGER

active BOOLEAN
```

Soft Delete obrigatório.

---

# Índices

Criar índices para.

Foreign Keys.

Campos de Busca.

Datas.

Status.

Número Documento.

Código Produto.

CPF.

CNPJ.

Email.

Telefone.

Serial.

---

# Chaves

Utilizar UUID v7.

Nunca utilizar Integer Auto Increment.

---

# Relacionamentos

Sempre utilizar Foreign Keys.

Nunca criar relacionamento implícito.

Integridade referencial obrigatória.

---

# Auditoria

Toda alteração deverá gerar registro.

Tabela.

Registro.

Usuário.

Antes.

Depois.

Data.

IP.

Origem.

---

# Versionamento

Registros críticos.

Clientes.

Produtos.

OS.

Financeiro.

Vendas.

Deverão possuir histórico de alterações.

---

# Exclusão

Nunca excluir fisicamente.

Sempre utilizar Soft Delete.

Exclusão definitiva apenas por rotinas administrativas.

---

# Performance

Utilizar.

Índices Compostos.

Partial Index.

GIN.

BRIN.

Materialized Views.

Views.

Query Plans.

EXPLAIN ANALYZE.

---

# Busca

Implementar.

Full Text Search.

ILIKE.

Trigram.

Vetores.

Busca Semântica.

---

# Vetores

Tabela.

ai_embeddings

Campos.

Documento.

Chunk.

Embedding.

Modelo.

Metadata.

Fonte.

Hash.

Tenant.

Utilizar pgvector.

---

# Backup

Cada Tenant.

Backup independente.

Restore independente.

Agendamento automático.

Compressão.

Criptografia.

---

# Criptografia

Criptografar.

Senhas.

Tokens.

Secrets.

Credenciais.

Chaves API.

Nunca armazenar texto puro.

---

# Migrações

Todas utilizando Alembic.

Nunca alterar banco manualmente.

Nunca executar SQL diretamente em produção.

Toda alteração deverá possuir Migration.

---

# Seed Inicial

Criar automaticamente.

Empresa.

Administrador.

Permissões.

Papéis.

Categorias padrão.

Centros de custo.

Configurações.

Dashboard padrão.

Templates.

Workflow padrão.

---

# Convenções

Tabela.

snake_case.

Colunas.

snake_case.

Constraints nomeadas.

Foreign Keys nomeadas.

Índices nomeados.

---

# Proibições

Nunca utilizar cascade delete sem justificativa.

Nunca remover colunas diretamente.

Nunca quebrar compatibilidade de migrações.

Nunca criar tabelas sem índices adequados.

Nunca compartilhar dados entre Tenants.

---

# Roadmap

Preparado para.

Read Replicas.

Particionamento.

Sharding.

TimescaleDB.

ClickHouse para Analytics.

Data Warehouse.

Lakehouse.

---

# Objetivo Final

O banco de dados do VeloAI deverá fornecer uma base sólida, segura e altamente escalável para suportar milhares de empresas utilizando bancos isolados por Tenant. A estrutura deverá priorizar integridade, desempenho, auditoria completa, facilidade de evolução através de Alembic e integração nativa com Inteligência Artificial utilizando pgvector para armazenamento de embeddings e RAG.

---
