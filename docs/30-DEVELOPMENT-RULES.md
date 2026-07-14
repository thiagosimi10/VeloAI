# 30-DEVELOPMENT-RULES.md

> Projeto → VeloAI
> Documento → Regras Oficiais de Desenvolvimento
> Aplicável → Claude Code, ChatGPT, Gemini, GitHub Copilot e Desenvolvedores
> Versão → 1.0.0

---

# Objetivo

Este documento define as regras obrigatórias para qualquer código produzido no VeloAI.

Todo código desenvolvido, seja por Inteligência Artificial ou por desenvolvedores humanos, deverá seguir rigorosamente estas diretrizes.

O objetivo é manter um código limpo, padronizado, escalável, testável e de fácil manutenção durante toda a vida útil da plataforma.

Nenhuma regra deste documento poderá ser ignorada sem justificativa técnica.

---

# Filosofia

Clean Architecture.

SOLID.

DRY.

KISS.

YAGNI.

Composition over Inheritance.

Domain Driven Design quando aplicável.

Código simples sempre será preferido ao código inteligente.

Legibilidade sempre será mais importante que quantidade de linhas.

---

# Arquitetura

Toda nova funcionalidade deverá seguir obrigatoriamente.

```text
Controller

↓

Use Case

↓

Service

↓

Repository

↓

Database
```

Nunca acessar Repository diretamente pela API.

Nunca colocar regra de negócio dentro da Controller.

Nunca colocar regra de negócio dentro do Frontend.

---

# Backend

Stack oficial.

Python 3.13.

FastAPI.

SQLAlchemy 2.

Alembic.

Pydantic v2.

PostgreSQL.

Redis.

Celery.

---

# Frontend

Stack oficial.

Vue 3.

Composition API.

TypeScript.

Pinia.

Vue Router.

Tailwind CSS.

PrimeVue.

amCharts.

TanStack Table.

Lucide Icons.

---

# Organização

Cada módulo deverá possuir.

```text
module/

api/

schemas/

models/

repositories/

services/

use_cases/

validators/

permissions/

mcp_tools/

tests/
```

Nunca criar módulos fora desse padrão.

---

# Limite de Arquivos

Python.

Máximo.

500 linhas.

Vue.

Máximo.

400 linhas.

TypeScript.

Máximo.

400 linhas.

Markdown.

Sem limite.

Quando atingir o limite.

Refatorar.

Dividir.

Nunca criar arquivos gigantes.

---

# Limite de Funções

Máximo.

50 linhas.

Ideal.

30 linhas.

Funções grandes deverão ser divididas.

---

# Classes

Máximo.

300 linhas.

Responsabilidade única.

---

# Complexidade

Evitar.

If aninhado.

Loops desnecessários.

Código duplicado.

Acoplamento.

---

# Nomenclatura

Classes.

PascalCase.

Funções.

snake_case no Backend.

camelCase no Frontend.

Constantes.

UPPER_CASE.

Arquivos Python.

snake_case.py.

Componentes Vue.

PascalCase.vue.

---

# Comentários

Escrever comentários apenas quando agregarem contexto.

Nunca comentar código óbvio.

Nunca deixar código comentado.

Nunca deixar TODO.

Nunca deixar FIXME.

---

# Logs

Nunca utilizar.

print().

console.log().

Utilizar.

Structlog.

Logger oficial.

---

# Tipagem

Obrigatória.

Python.

Type Hints.

TypeScript.

Strict Mode.

Nunca utilizar.

Any.

Sem justificativa.

---

# Erros

Utilizar Exceptions próprias.

Nunca retornar Exception diretamente.

Nunca utilizar.

try/except genérico.

---

# Banco

Nunca escrever SQL diretamente.

Utilizar.

SQLAlchemy.

Migrations.

Repositories.

---

# Alembic

Toda alteração estrutural deverá gerar Migration.

Nunca alterar banco manualmente.

Toda Migration deverá possuir rollback.

---

# Testes

Toda funcionalidade deverá possuir.

Teste Unitário.

Teste Integração.

Cobertura obrigatória.

---

# Cobertura

Backend.

95%.

Frontend.

90%.

MCP.

95%.

RAG.

95%.

Provisioning.

95%.

---

# API

Toda rota deverá possuir.

OpenAPI.

Validação.

Autenticação.

Permissões.

Logs.

Auditoria.

---

# Segurança

Nunca armazenar.

Senha.

JWT.

API Key.

Credenciais.

Em código.

---

# Docker

Toda dependência deverá executar em Docker.

Nunca depender da máquina local.

---

# Variáveis

Toda configuração deverá utilizar.

.env.

Nunca valores fixos.

---

# IA

Nunca acessar banco diretamente.

Nunca executar SQL.

Sempre utilizar.

MCP.

RAG.

AI Gateway.

---

# MCP

Toda nova funcionalidade deverá possuir Tools quando aplicável.

Toda Tool deverá possuir.

Teste.

Auditoria.

Permissões.

Documentação.

---

# RAG

Toda indexação deverá utilizar.

Embeddings.

Chunking.

Versionamento.

Nunca acessar embeddings diretamente.

---

# Frontend

Nunca utilizar CSS Inline.

Nunca utilizar Bootstrap.

Nunca utilizar jQuery.

Sempre utilizar.

Tailwind.

PrimeVue.

Design System.

---

# Componentes

Todo componente deverá ser.

Reutilizável.

Tipado.

Documentado.

Testado.

---

# DataTables

Utilizar.

TanStack Table.

Nunca criar tabelas manuais para listas complexas.

---

# Dashboards

Utilizar exclusivamente.

amCharts.

Nunca utilizar Chart.js.

Nunca utilizar ApexCharts.

---

# Estado Global

Utilizar.

Pinia.

Nunca utilizar Event Bus.

---

# Assincronismo

Backend.

async/await.

Frontend.

Promises.

Nunca bloquear Threads.

---

# Performance

Evitar.

N+1.

Consultas desnecessárias.

Re-renderizações.

Código morto.

Imports desnecessários.

---

# Git

Commits.

Conventional Commits.

Branches.

Feature.

Fix.

Hotfix.

Release.

---

# Pull Requests

Obrigatórios.

Descrição.

Checklist.

Testes.

Screenshots quando necessário.

---

# Code Review

Nenhum Merge sem aprovação.

---

# CI

Todo Pull Request deverá executar.

Lint.

Type Check.

Testes.

Coverage.

Docker Build.

Security.

---

# Dependências

Adicionar apenas quando necessário.

Preferir bibliotecas maduras.

Licença compatível.

Comunidade ativa.

---

# Documentação

Toda nova Feature deverá atualizar.

Markdown.

OpenAPI.

Storybook quando aplicável.

---

# Refatoração

Sempre preferir.

Melhorar código existente.

Evitar duplicação.

Criar abstrações apenas quando necessário.

---

# Padrões Proibidos

Nunca utilizar.

Código duplicado.

Funções gigantes.

Classes gigantes.

SQL manual.

print().

console.log().

TODO.

FIXME.

Magic Numbers.

Magic Strings.

Dependências sem uso.

Código morto.

---

# Checklist Obrigatório

Antes de concluir qualquer tarefa verificar.

Código compila.

Testes executados.

Cobertura mantida.

Lint aprovado.

Docker Build aprovado.

OpenAPI atualizada.

Migrations criadas.

Documentação atualizada.

Nenhum TODO.

Nenhum código comentado.

Nenhum Warning.

---

# Checklist para Claude Code

Antes de responder "tarefa concluída", validar obrigatoriamente.

Leu toda a documentação relevante.

Respeitou a arquitetura do projeto.

Criou testes automatizados.

Criou ou atualizou migrations quando necessário.

Atualizou documentação.

Criou MCP Tools quando aplicável.

Atualizou o AI Gateway quando necessário.

Atualizou o RAG quando necessário.

Atualizou os Schemas Pydantic.

Atualizou o OpenAPI.

Executou validações de qualidade.

Não duplicou código.

Não criou arquivos acima do limite.

Não criou funções acima do limite.

Não violou nenhuma regra deste documento.

---

# Princípios para IA

Sempre reutilizar código existente.

Sempre procurar componentes existentes antes de criar novos.

Sempre manter compatibilidade.

Sempre preferir simplicidade.

Sempre perguntar apenas quando uma decisão impactar a arquitetura.

Nunca inventar regras de negócio.

Nunca assumir comportamento não documentado.

Nunca remover funcionalidades sem solicitação explícita.

---

# Definição de Pronto (Definition of Done)

Uma funcionalidade somente será considerada concluída quando.

Código implementado.

Testes aprovados.

Cobertura mantida.

Documentação atualizada.

Migrations criadas.

OpenAPI atualizada.

Logs implementados.

Auditoria implementada.

Permissões implementadas.

Responsividade validada.

Dark Mode validado quando aplicável.

Acessibilidade validada.

CI aprovado.

Sem bugs conhecidos.

---

# Objetivo Final

Este documento representa a constituição técnica do desenvolvimento do VeloAI. Todas as contribuições, humanas ou geradas por Inteligência Artificial, deverão seguir rigorosamente estas diretrizes para garantir um código consistente, seguro, escalável e de alta qualidade durante toda a evolução da plataforma.

---
