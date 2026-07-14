# 04-MULTI-TENANCY.md

> Projeto → VeloAI
> Documento → Multi-Tenancy
> Versão → 1.0.0

---

# Objetivo

O VeloAI será um SaaS Multi-Tenant utilizando **Database per Tenant**, onde cada empresa possuirá seu próprio banco PostgreSQL.

Esta decisão foi tomada visando:

- Segurança.
- Escalabilidade.
- Backup individual.
- Performance.
- Facilidade de migração.
- Facilidade de restauração.
- Isolamento completo dos dados.

---

# Modelo de Multi-Tenant

Modelo adotado:

```
Database per Tenant
```

Cada empresa possuirá:

- Banco PostgreSQL exclusivo.
- Usuários exclusivos.
- Dados exclusivos.
- Configurações exclusivas.
- Vetores exclusivos (Qdrant).
- Arquivos exclusivos (MinIO).

Jamais compartilhar dados entre empresas.

---

# Arquitetura

```text
                    PostgreSQL

┌─────────────────────────────────────┐
│ veloai_master                       │
│                                     │
│ companies                           │
│ tenants                             │
│ subscriptions                       │
│ plans                               │
│ audit_global                        │
└─────────────────────────────────────┘

               │
               │ cria automaticamente
               ▼

┌───────────────────────────┐
│ tenant_8f41a9             │
│                           │
│ customers                 │
│ products                  │
│ orders                    │
│ finance                   │
│ users                     │
│ stock                     │
│ services                  │
│ ...                       │
└───────────────────────────┘

┌───────────────────────────┐
│ tenant_93bd72             │
│                           │
│ customers                 │
│ products                  │
│ orders                    │
│ finance                   │
│ users                     │
│ stock                     │
│ services                  │
└───────────────────────────┘
```

---

# Banco Master

O banco Master nunca armazenará dados de negócio.

Somente:

- Empresas.
- Planos.
- Assinaturas.
- Pagamentos.
- Domínios.
- Configurações globais.
- Licenciamento.
- Auditoria Global.

Nunca armazenar:

- Clientes.
- Produtos.
- Ordens.
- Financeiro.
- Estoque.

---

# Banco do Tenant

Cada banco possuirá exatamente a mesma estrutura.

Exemplo:

```
customers

suppliers

products

categories

stock

orders

services

finance

accounts_receivable

accounts_payable

cash_flow

users

roles

permissions

dashboard

reports

audit

notifications
```

Todos os bancos serão idênticos.

---

# Fluxo de Cadastro

```text
Usuário cria conta

↓

Validação Email

↓

Criar Empresa

↓

Criar Tenant

↓

Criar Banco PostgreSQL

↓

Executar Alembic

↓

Executar Seeds

↓

Criar Bucket MinIO

↓

Criar Collection Qdrant

↓

Criar Usuário Admin

↓

Empresa pronta para uso
```

Todo esse processo deverá ser automático.

---

# Nome do Banco

Formato:

```
tenant_<uuid_curto>
```

Exemplo:

```
tenant_2ab34f

tenant_9fc812

tenant_71ceab
```

Nunca utilizar nome da empresa.

---

# Identificação do Tenant

Cada Tenant possuirá:

- UUID.
- Nome.
- Domínio.
- Plano.
- Status.
- Data de criação.

Exemplo:

```
tenant_id

company_name

database_name

database_host

database_port

database_user

database_password

status

plan

created_at
```

---

# Conexão Dinâmica

Fluxo:

```text
Login

↓

Banco Master

↓

Localiza Tenant

↓

Obtém configuração

↓

Cria conexão SQLAlchemy

↓

Armazena Pool

↓

Requisições utilizam conexão correta
```

A conexão deverá ser reutilizada.

Nunca criar conexão a cada request.

---

# Pool de Conexões

Utilizar SQLAlchemy Pool.

Cada Tenant possuirá seu próprio pool.

Configuração deverá ser parametrizada.

---

# Alembic

Toda nova empresa executará automaticamente:

```
alembic upgrade head
```

Nunca criar banco manualmente.

---

# Seeds

Após executar migrations deverão ser criados:

- Usuário Administrador.
- Permissões.
- Perfis.
- Configurações.
- Categorias padrão.
- Dashboard padrão.
- Configuração Fiscal.
- Configuração Financeira.

Tudo automaticamente.

---

# Buckets MinIO

Cada empresa possuirá um bucket lógico.

Formato:

```
tenant-uuid
```

Estrutura:

```
logo/

documents/

orders/

reports/

products/

customers/

attachments/
```

---

# Collections Qdrant

Cada empresa possuirá sua própria Collection.

Formato:

```
tenant_uuid_vectors
```

Nunca compartilhar embeddings.

---

# Isolamento

Toda requisição deverá validar:

- Tenant.
- Usuário.
- Permissão.

Caso exista inconsistência:

HTTP 403.

---

# Exclusão de Empresa

Fluxo:

```text
Cancelar assinatura

↓

Bloquear Login

↓

Período de retenção

↓

Backup

↓

Excluir Banco

↓

Excluir Bucket

↓

Excluir Vetores

↓

Remover Tenant
```

Tempo de retenção configurável.

---

# Backup

Cada empresa possuirá backup independente.

Tipos:

- Diário.
- Semanal.
- Mensal.

Backups criptografados.

---

# Restore

Será possível restaurar apenas um cliente.

Sem impactar outros tenants.

---

# Migração

Será possível mover apenas um Tenant para outro servidor PostgreSQL.

Sem indisponibilidade dos demais.

---

# Escalabilidade

A arquitetura permitirá distribuir bancos entre múltiplos servidores.

Exemplo:

```
Servidor A

tenant_1

tenant_2

tenant_3

Servidor B

tenant_4

tenant_5

tenant_6

Servidor C

tenant_7

tenant_8

tenant_9
```

O sistema localizará automaticamente o servidor correto.

---

# Cache

Cada empresa possuirá namespace próprio.

Exemplo:

```
tenant:abc123:dashboard

tenant:abc123:customers

tenant:abc123:products
```

Nunca compartilhar cache.

---

# Filas

Cada Job deverá possuir Tenant ID.

Fluxo:

```text
Criar Job

↓

Adicionar Tenant ID

↓

Worker

↓

Abrir conexão correta

↓

Executar

↓

Finalizar
```

---

# Logs

Todo log deverá registrar:

- Tenant.
- Usuário.
- IP.
- Data.
- Hora.
- Endpoint.

---

# Auditoria

Toda auditoria deverá possuir:

- tenant_id
- user_id
- resource
- action
- before
- after
- created_at

---

# Segurança

Nunca permitir:

- Troca manual de Tenant.
- Alteração de tenant_id.
- Consulta cruzada.
- Compartilhamento de conexões.

Toda conexão deverá ser obtida pelo Tenant Manager.

---

# Tenant Manager

Será criado um serviço central responsável por:

- Criar Tenant.
- Criar Banco.
- Abrir conexão.
- Fechar conexão.
- Cachear Pools.
- Executar Migrations.
- Criar Seeds.
- Criar Bucket.
- Criar Collection.
- Excluir Tenant.
- Backup.
- Restore.

Nenhum módulo poderá criar conexões diretamente.

---

# Benefícios

- Isolamento completo.
- Segurança.
- Escalabilidade.
- Backups independentes.
- Restore individual.
- Melhor performance.
- Facilidade de manutenção.
- Facilidade para Enterprise.
- Facilidade para White Label.

---

# Objetivo Final

O sistema deverá permitir que milhares de empresas utilizem a mesma plataforma com isolamento total, garantindo segurança, alta disponibilidade e capacidade de crescimento horizontal sem alterações na arquitetura.

---