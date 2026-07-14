# 00-AI-CONSTITUTION.md

> Projeto → VeloAI
> Produto → AI Business OS
> Versão → 1.0.0
> Prioridade → MÁXIMA

---

# Objetivo

Este documento define as regras obrigatórias que deverão ser seguidas por qualquer IA (Claude Code, Codex, Cursor, Gemini CLI, OpenAI Codex ou qualquer outro agente), bem como por qualquer desenvolvedor que trabalhe no projeto.

Este documento possui prioridade absoluta.

Caso exista conflito entre qualquer outro documento e este, este documento prevalece.

Nenhuma funcionalidade poderá ser implementada violando estas regras.

---

# O que é o VeloAI

O VeloAI não é um CRM.

O VeloAI não é um ERP.

O VeloAI não é um sistema de Ordem de Serviço.

O VeloAI é um **AI Business OS**.

Seu objetivo é centralizar toda a operação de pequenas e médias empresas em uma única plataforma, utilizando Inteligência Artificial como principal interface entre usuário e sistema.

Toda decisão arquitetural deverá priorizar simplicidade, escalabilidade, automação e experiência do usuário.

---

# Filosofia

Toda implementação deverá responder obrigatoriamente às seguintes perguntas:

- Isso reduz o número de cliques do usuário?
- A IA consegue executar esta tarefa automaticamente?
- Esta funcionalidade pode ser reutilizada?
- Esta solução continuará escalando para milhares de clientes?
- Existe uma forma mais simples de implementar?
- A solução é segura?
- A solução é testável?
- A solução é desacoplada?

Caso qualquer resposta seja negativa, a implementação deverá ser revista.

---

# Princípios

- IA First → Toda funcionalidade deverá possuir integração com IA.
- API First → Toda funcionalidade nasce na API.
- Mobile Ready → O Backend nunca dependerá do Frontend Web.
- Cloud Native → Toda aplicação deverá funcionar em containers.
- Multi Tenant First → Sempre assumir milhares de empresas.
- Security First → Segurança nunca será opcional.
- Performance First → Performance sempre terá prioridade.
- Clean Code Always → Código limpo é obrigatório.
- Test First → Toda funcionalidade deverá possuir testes.
- Documentation First → Toda funcionalidade deverá possuir documentação.

---

# Regras Gerais

- Nunca gerar código duplicado.
- Nunca copiar lógica entre módulos.
- Nunca utilizar "gambiarras".
- Nunca deixar TODO sem justificativa.
- Nunca comentar código morto.
- Nunca criar funções gigantes.
- Nunca criar arquivos gigantes.
- Nunca misturar responsabilidades.
- Nunca acessar banco diretamente pela API.
- Nunca colocar regra de negócio em Controllers.
- Nunca colocar regra de negócio em Repositories.
- Nunca utilizar SQL bruto sem necessidade comprovada.
- Nunca utilizar SELECT *.
- Nunca confiar em dados vindos do Frontend.
- Nunca confiar em dados enviados pela IA.
- Sempre validar todas as entradas.
- Sempre validar permissões.
- Sempre registrar logs.
- Sempre escrever código pensando em manutenção.

---

# Arquitetura Obrigatória

Toda implementação deverá seguir:

```
Frontend
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
Database
```

Nenhuma camada poderá "pular" outra camada.

---

# Regras para IA

A IA nunca poderá:

- Acessar banco diretamente.
- Gerar SQL.
- Alterar dados sem utilizar Tools.
- Ignorar regras de negócio.
- Criar registros diretamente.

A IA sempre deverá:

- Identificar intenção.
- Selecionar o agente correto.
- Selecionar a Tool correta.
- Executar validações.
- Chamar o Service.
- Aguardar resposta.
- Retornar resultado ao usuário.

---

# Fluxo obrigatório da IA

```
Usuário

↓

LLM

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

↓

Resposta

↓

Usuário
```

---

# Organização do Projeto

Todo projeto deverá seguir organização por Feature.

Nunca organizar por tipo de arquivo.

Errado:

```
controllers/
services/
repositories/
models/
```

Correto:

```
customers/
products/
orders/
finance/
reports/
dashboard/
users/
company/
services/
stock/
auth/
ai/
common/
```

Cada módulo deverá possuir sua própria estrutura interna.

---

# Estrutura mínima de um módulo

```
api/
services/
repositories/
models/
schemas/
domain/
tools/
tests/
exceptions/
mappers/
```

---

# Controllers

Responsabilidade:

- Receber requisição.
- Validar autenticação.
- Validar autorização.
- Chamar Service.
- Retornar resposta.

Nunca:

- Fazer cálculos.
- Fazer regras de negócio.
- Acessar Repository.
- Acessar Banco.

---

# Services

Responsabilidade:

- Implementar regras de negócio.
- Coordenar processos.
- Chamar Repositories.
- Chamar outros Services.
- Chamar integrações.

Nunca:

- Conhecer HTTP.
- Retornar Response.
- Fazer renderização.
- Criar SQL.

---

# Repositories

Responsabilidade:

- Acesso ao banco.
- Persistência.
- Consultas.

Nunca:

- Validar regras.
- Fazer cálculos.
- Conhecer HTTP.
- Conhecer Frontend.

---

# Models

Responsabilidade:

- Representar entidades.

Nunca:

- Fazer lógica de negócio.
- Fazer consultas.

---

# DTOs / Schemas

Toda entrada deverá possuir DTO.

Toda saída deverá possuir DTO.

Nunca retornar Models diretamente.

---

# Banco de Dados

Toda tabela deverá possuir quando aplicável:

- id
- created_at
- updated_at
- deleted_at
- created_by
- updated_by
- tenant_id

Soft Delete será obrigatório.

Delete físico somente quando tecnicamente necessário.

---

# Multi Tenancy

Cada empresa possuirá:

- Banco exclusivo.
- Storage exclusivo.
- Configurações exclusivas.
- Vetor exclusivo.
- Usuários exclusivos.
- Dados exclusivos.

Jamais compartilhar banco entre empresas.

Jamais compartilhar dados entre tenants.

---

# Migrations

Toda alteração deverá possuir Migration.

Toda Migration deverá possuir:

- upgrade()
- downgrade()

Nunca alterar banco manualmente.

---

# API

Toda API deverá:

- Possuir documentação OpenAPI.
- Possuir tipagem.
- Possuir autenticação.
- Possuir autorização.
- Possuir testes.
- Possuir tratamento de erros.

---

# Versionamento

Sempre utilizar:

```
/api/v1
```

Preparar arquitetura para futuras versões.

---

# Frontend

Obrigatório:

- Vue 3
- TypeScript
- Composition API
- Script Setup
- Componentização
- Responsividade
- Dark Mode
- TailwindCSS

Nunca utilizar:

- Options API
- Mixins
- jQuery
- Código duplicado

---

# Componentes

Todo componente deverá:

- Ter responsabilidade única.
- Ser reutilizável.
- Ser pequeno.
- Ser tipado.
- Ser testável.

Nunca criar componentes gigantes.

---

# UX

Toda tela deverá:

- Ser intuitiva.
- Possuir feedback visual.
- Possuir loading.
- Possuir skeleton.
- Possuir tratamento de erro.
- Funcionar no Desktop.
- Funcionar no Tablet.
- Funcionar no Mobile.

---

# IA na Interface

Toda tela obrigatoriamente deverá possuir integração com IA.

Exemplo:

Clientes → IA.

Produtos → IA.

Financeiro → IA.

Estoque → IA.

Dashboard → IA.

Relatórios → IA.

Ordem de Serviço → IA.

Configurações → IA.

Não existirão telas "sem IA".

---

# Dashboard

O Dashboard será inteligente.

Não apenas mostrará informações.

Ele deverá:

- Detectar problemas.
- Sugerir ações.
- Encontrar oportunidades.
- Explicar indicadores.
- Criar gráficos.
- Criar relatórios.
- Comparar períodos.
- Gerar previsões.

---

# Segurança

Obrigatório:

- JWT.
- Refresh Token.
- HTTPS.
- Argon2.
- Rate Limit.
- Logs.
- Auditoria.
- CORS.
- Sanitização.
- Validação.
- LGPD.

Nunca armazenar informações sensíveis em texto puro.

---

# Logs

Todo erro deverá ser registrado.

Todo acesso deverá ser registrado.

Toda alteração deverá ser registrada.

Nunca utilizar print().

Sempre utilizar logging estruturado.

---

# Auditoria

Registrar:

- Usuário.
- Empresa.
- Data.
- Hora.
- IP.
- Recurso.
- Ação.
- Valor anterior.
- Valor novo.

Nada poderá ser apagado da auditoria.

---

# Testes

Cobertura mínima:

- Backend → 90%
- Frontend → 80%

Todo Service deverá possuir testes unitários.

Toda API deverá possuir testes de integração.

Toda funcionalidade crítica deverá possuir testes End-to-End.

Nenhum Pull Request poderá ser aceito sem testes passando.

---

# Performance

Sempre utilizar:

- Paginação.
- Lazy Loading.
- Cache.
- Redis.
- Background Jobs.
- Compressão.
- Índices no banco.

Nunca carregar milhares de registros em uma única consulta.

---

# Filas

Toda tarefa pesada deverá ser assíncrona.

Exemplos:

- IA.
- OCR.
- PDFs.
- Relatórios.
- WhatsApp.
- Email.
- Importações.
- Exportações.

---

# Docker

Todo o sistema deverá iniciar utilizando apenas:

```bash
docker compose up -d
```

Nenhuma instalação manual será necessária.

---

# Git

Obrigatório utilizar:

- Conventional Commits.
- Feature Branches.
- Pull Requests.
- Code Review.
- Semantic Versioning.

---

# Qualidade

Obrigatório utilizar:

- Ruff.
- Black.
- Mypy.
- Pre-Commit.
- ESLint.
- Prettier.

Nenhum código poderá ser enviado sem passar pelas ferramentas de qualidade.

---

# CI

Todo Push deverá executar:

- Lint.
- Testes Backend.
- Testes Frontend.
- Coverage.
- Build Docker.
- Verificação das Migrations.

Nenhum merge poderá ocorrer com falhas.

---

# Documentação

Toda funcionalidade deverá possuir:

- Documentação técnica.
- Fluxo.
- Regras de negócio.
- Critérios de aceite.
- Casos de erro.
- Exemplos.

---

# Objetivo Final

O objetivo do VeloAI é tornar-se a principal plataforma de gestão empresarial com Inteligência Artificial da América Latina.

Toda decisão técnica deverá priorizar qualidade, escalabilidade, simplicidade, reutilização e experiência do usuário.

O VeloAI deverá possuir qualidade comparável a produtos como Stripe, Linear, Notion, ClickUp e HubSpot, mantendo foco nas necessidades das pequenas empresas brasileiras.

---
