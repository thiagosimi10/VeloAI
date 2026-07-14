# 05-BANCO-DE-DADOS.md

> Projeto → VeloAI
> Documento → Banco de Dados
> Banco Oficial → PostgreSQL 17+
> ORM → SQLAlchemy 2
> Migrations → Alembic

---

# Objetivo

Definir todas as regras do banco de dados do VeloAI.

O banco deverá ser altamente performático, preparado para milhares de empresas, fácil de evoluir e totalmente compatível com SQLAlchemy.

---

# Padrões

- Banco → PostgreSQL
- ORM → SQLAlchemy 2
- Migrations → Alembic
- UUID → UUIDv7 (preferencialmente)
- Datas → UTC
- Charset → UTF-8
- Soft Delete → Obrigatório
- Auditoria → Obrigatória

---

# Convenções

Tabelas:

```text
snake_case
plural
```

Exemplos:

```
customers
products
service_orders
accounts_receivable
accounts_payable
```

---

Colunas:

```
snake_case
```

Exemplos:

```
first_name

last_name

created_at

updated_at
```

---

Chaves Primárias

Sempre:

```
id UUID
```

Nunca utilizar:

```
AUTO_INCREMENT
```

---

Campos Obrigatórios

Todas as tabelas deverão possuir quando aplicável:

```
id

created_at

updated_at

deleted_at

created_by

updated_by
```

---

Soft Delete

Nunca apagar registros fisicamente.

Sempre utilizar:

```
deleted_at
```

---

Auditoria

Toda alteração deverá gerar histórico.

Registrar:

- usuário
- ação
- antes
- depois
- data
- ip

---

Relacionamentos

Sempre utilizar Foreign Keys.

Nunca armazenar IDs "soltos".

---

Índices

Criar índices para:

- Foreign Keys
- Campos pesquisáveis
- Datas
- Status
- Código

Nunca criar índices desnecessários.

---

Paginação

Todas as consultas deverão suportar paginação.

Nunca retornar milhares de registros.

---

Busca

Toda busca deverá suportar:

- LIKE
- Busca parcial
- Ordenação
- Paginação
- Filtros

---

Estrutura Geral

```text
Empresa

↓

Usuários

↓

Clientes

↓

Produtos

↓

Serviços

↓

Ordens

↓

Financeiro

↓

Relatórios
```

---

# Entidades

## Empresa

Tabela:

```
companies
```

Campos:

- id
- legal_name
- trade_name
- document
- email
- phone
- mobile
- zipcode
- street
- number
- district
- city
- state
- country
- logo
- primary_color
- secondary_color
- timezone
- currency
- language
- fiscal_enabled
- active

---

## Usuários

Tabela:

```
users
```

Campos:

- id
- company_id
- role_id
- first_name
- last_name
- email
- password
- avatar
- phone
- active
- last_login

---

## Perfis

Tabela:

```
roles
```

Campos:

- id
- name
- description

---

## Permissões

Tabela:

```
permissions
```

Campos:

- id
- module
- action

---

## Role Permissions

Tabela:

```
role_permissions
```

Relacionamento N:N

---

## Clientes

Tabela:

```
customers
```

Campos:

- id
- code
- type
- name
- document
- state_registration
- municipal_registration
- email
- phone
- mobile
- whatsapp
- zipcode
- street
- number
- district
- city
- state
- country
- notes
- active

---

## Fornecedores

Tabela:

```
suppliers
```

Mesmo padrão dos clientes.

---

## Categorias

Tabela:

```
categories
```

Campos:

- id
- name
- description

---

## Produtos

Tabela:

```
products
```

Campos:

- id
- category_id
- supplier_id
- sku
- barcode
- name
- description
- cost_price
- sale_price
- stock
- minimum_stock
- maximum_stock
- unit
- weight
- active

---

## Serviços

Tabela:

```
services
```

Campos:

- id
- code
- name
- description
- estimated_time
- price
- active

---

## Estoque

Tabela:

```
stock_movements
```

Campos:

- id
- product_id
- movement
- quantity
- previous_stock
- current_stock
- reason

---

## Ordens de Serviço

Tabela:

```
service_orders
```

Campos:

- id
- number
- customer_id
- technician_id
- status
- equipment
- serial_number
- problem
- diagnosis
- solution
- total
- opened_at
- finished_at

---

## Itens da Ordem

Tabela:

```
service_order_items
```

Campos:

- id
- service_order_id
- product_id
- service_id
- quantity
- unit_price
- total

---

## Vendas

Tabela:

```
sales
```

Campos:

- id
- customer_id
- total
- discount
- status
- payment_method

---

## Itens da Venda

Tabela:

```
sale_items
```

Campos:

- id
- sale_id
- product_id
- quantity
- unit_price

---

## Contas a Receber

Tabela:

```
accounts_receivable
```

Campos:

- id
- customer_id
- due_date
- amount
- status
- payment_date

---

## Contas a Pagar

Tabela:

```
accounts_payable
```

Campos:

- id
- supplier_id
- due_date
- amount
- payment_date
- status

---

## Fluxo de Caixa

Tabela:

```
cash_flow
```

Campos:

- id
- type
- category
- description
- amount
- date

---

## Agenda

Tabela:

```
calendar_events
```

Campos:

- id
- title
- description
- start_at
- end_at
- customer_id
- user_id

---

## Notificações

Tabela:

```
notifications
```

Campos:

- id
- user_id
- title
- message
- type
- read_at

---

## Dashboard Cache

Tabela:

```
dashboard_cache
```

Responsável por acelerar consultas pesadas.

---

## Auditoria

Tabela:

```
audit_logs
```

Campos:

- id
- user_id
- resource
- action
- before
- after
- ip
- created_at

---

## Configurações

Tabela:

```
settings
```

Campos:

- id
- key
- value

---

## IA

Tabela:

```
ai_conversations
```

Campos:

- id
- user_id
- prompt
- response
- tokens
- model
- execution_time

---

## Histórico da IA

Tabela:

```
ai_actions
```

Campos:

- id
- conversation_id
- tool
- service
- execution
- success

---

# Seeds

Toda empresa deverá iniciar com:

- Usuário Administrador
- Perfil Administrador
- Permissões
- Configurações
- Categorias padrão
- Dashboard padrão

---

# Índices Obrigatórios

Criar índices para:

- email
- document
- sku
- barcode
- status
- created_at
- customer_id
- product_id
- service_order_id

---

# Constraints

Obrigatório:

- Foreign Keys
- Unique Keys
- Check Constraints
- NOT NULL onde aplicável

---

# Performance

Utilizar:

- Índices compostos
- Paginação
- Consultas específicas
- Cache Redis

Nunca utilizar SELECT *.

---

# Objetivo Final

O banco deverá ser simples de evoluir, altamente performático e preparado para suportar milhares de empresas sem necessidade de alterações estruturais.

---
