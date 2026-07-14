# 22-API-STANDARDS.md

> Projeto → VeloAI
> Documento → Padrões de APIs
> Stack → FastAPI + REST
> Versão → 1.0.0

---

# Objetivo

Definir um padrão único para todas as APIs do VeloAI.

Toda API deverá seguir exatamente estas regras.

Nenhum módulo poderá criar padrões próprios.

Toda comunicação entre Frontend, Mobile, IA, MCP, Provisioning Service e integrações externas deverá utilizar estas especificações.

---

# Filosofia

As APIs deverão ser.

Simples.

Consistentes.

Previsíveis.

Versionadas.

Documentadas.

Seguras.

Performáticas.

Preparadas para evolução sem quebrar compatibilidade.

---

# Arquitetura

```text
Frontend

↓

API Gateway

↓

FastAPI

↓

Use Cases

↓

Services

↓

Repositories

↓

PostgreSQL
```

Nunca acessar banco diretamente pelas rotas.

---

# Versionamento

Toda API iniciará com.

```text
/api/v1/
```

Exemplo.

```
/api/v1/customers

/api/v1/products

/api/v1/sales

/api/v1/reports
```

---

# Formato

Sempre JSON.

UTF-8.

Content-Type.

```
application/json
```

Uploads.

```
multipart/form-data
```

Downloads.

```
application/pdf

application/octet-stream

text/csv
```

---

# Métodos HTTP

GET.

Consultar.

POST.

Criar.

PUT.

Atualizar completamente.

PATCH.

Atualização parcial.

DELETE.

Soft Delete.

Nunca utilizar POST para atualização.

---

# Padrão de URLs

Correto.

```
GET /customers

GET /customers/{id}

POST /customers

PATCH /customers/{id}

DELETE /customers/{id}
```

Nunca utilizar.

```
/getCustomer

/createProduct

/updateSale
```

---

# Resposta de Sucesso

Padrão obrigatório.

```json
{
  "success": true,
  "message": "Operação realizada com sucesso.",
  "data": {},
  "meta": {}
}
```

---

# Resposta de Erro

```json
{
  "success": false,
  "message": "Cliente não encontrado.",
  "code": "CUSTOMER_NOT_FOUND",
  "errors": [],
  "trace_id": "uuid"
}
```

Nunca retornar Traceback.

---

# Paginação

Padrão.

```
GET /customers?page=1&page_size=20
```

Resposta.

```json
{
  "success": true,
  "data": [],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 540,
    "pages": 27
  }
}
```

---

# Filtros

Padrão.

```
search

status

sort

order

page

page_size
```

Exemplo.

```
GET /products?search=ssd&status=active&sort=name&order=asc
```

---

# Ordenação

Sempre utilizar.

```
sort

order
```

Exemplo.

```
sort=created_at

order=desc
```

---

# Busca

Busca textual.

```
search=notebook
```

Busca avançada.

```
filters={}
```

Preparado para filtros complexos.

---

# Headers

Obrigatórios.

```
Authorization

Content-Type

Accept

X-Request-ID

X-Tenant-ID (uso interno)

Accept-Language
```

Nunca confiar no X-Tenant-ID enviado pelo cliente. O Tenant será resolvido pelo backend autenticado.

---

# Autenticação

JWT.

Refresh Token.

Cookies HttpOnly.

Bearer Token para APIs externas quando necessário.

---

# Permissões

RBAC.

Cada endpoint validará.

Usuário.

Tenant.

Permissão.

Plano.

Feature Flag.

---

# Idempotência

Endpoints críticos aceitarão.

```
Idempotency-Key
```

Obrigatório para.

Financeiro.

Vendas.

Provisionamento.

Pagamentos.

---

# Upload

Uploads deverão retornar.

```json
{
  "file_id": "...",
  "url": "...",
  "size": 12345
}
```

Nunca armazenar arquivos no banco.

---

# Downloads

Utilizar.

Streaming.

Range Requests.

Compressão.

Cache.

---

# Datas

Formato.

ISO 8601.

UTC no Backend.

Conversão para Timezone do usuário no Frontend.

Exemplo.

```
2026-07-14T18:30:00Z
```

---

# Valores Monetários

Nunca utilizar Float.

Utilizar Decimal.

Sempre retornar.

```json
1250.50
```

---

# UUID

Todos os IDs utilizarão.

UUID v7.

Nunca Integer Auto Increment.

---

# Erros HTTP

200.

Sucesso.

201.

Criado.

202.

Processamento Assíncrono.

204.

Sem Conteúdo.

400.

Requisição inválida.

401.

Não autenticado.

403.

Sem permissão.

404.

Não encontrado.

409.

Conflito.

422.

Erro de validação.

429.

Rate Limit.

500.

Erro interno.

503.

Serviço indisponível.

---

# Validação

Toda entrada deverá utilizar.

Pydantic v2.

Nunca validar manualmente nas rotas.

---

# OpenAPI

Gerado automaticamente.

Swagger.

ReDoc.

Documentação obrigatória.

Todos os endpoints deverão possuir.

Descrição.

Exemplos.

Schemas.

Tags.

Respostas.

---

# Async

Todas as rotas deverão ser.

Async.

Sempre que possível.

---

# Compressão

Gzip.

Brotli.

ETag.

Cache-Control.

---

# Rate Limiting

Implementar.

Por usuário.

Por Tenant.

Por IP.

Por API Key.

Configuração dinâmica.

---

# Logs

Registrar.

Request ID.

Usuário.

Tenant.

Endpoint.

Tempo.

Status.

IP.

Método.

---

# Auditoria

Registrar.

Quem.

Quando.

Qual endpoint.

Resultado.

Entidade alterada.

Valores.

---

# Segurança

Nunca retornar Stack Trace.

Nunca expor SQL.

Nunca expor credenciais.

Sanitizar entradas.

Validar permissões.

Escapar conteúdo.

---

# Performance

Paginação.

Lazy Loading.

Streaming.

Compressão.

Cache.

Background Jobs.

---

# APIs Assíncronas

Operações demoradas deverão retornar.

```json
{
  "job_id": "...",
  "status": "processing"
}
```

Consulta posterior.

```
GET /jobs/{id}
```

---

# Webhooks

Suportar.

Retry.

Assinatura HMAC.

Logs.

Fila.

Versionamento.

---

# API Keys

Permitir geração.

Escopo.

Expiração.

Rotação.

Revogação.

Auditoria.

---

# Convenções

snake_case para JSON.

Plural nas rotas.

Versionamento obrigatório.

Respostas padronizadas.

Nunca quebrar contratos.

---

# Testes

Cobertura mínima.

90%.

Testar.

Autenticação.

Permissões.

Validações.

Paginação.

Filtros.

Rate Limit.

Uploads.

Downloads.

---

# CI

Validar.

OpenAPI.

Schemas.

Breaking Changes.

Coverage.

---

# Roadmap

Preparado para.

GraphQL.

gRPC.

WebSockets.

Server Sent Events.

API Gateway.

Multi Região.

---

# Regras Obrigatórias

Toda API deverá possuir documentação OpenAPI.

Toda API deverá possuir autenticação.

Toda API deverá validar Tenant.

Toda API deverá validar permissões.

Toda API deverá gerar logs.

Toda API deverá gerar auditoria.

Toda API deverá retornar JSON padronizado.

Toda API deverá possuir testes automatizados.

---

# Objetivo Final

As APIs do VeloAI deverão fornecer uma camada de comunicação consistente, segura e previsível para todos os consumidores da plataforma. O padrão definido neste documento deverá ser seguido por todos os módulos, garantindo facilidade de integração, manutenção e evolução do sistema sem quebra de compatibilidade entre versões.

---
