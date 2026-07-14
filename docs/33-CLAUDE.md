# 33-CLAUDE.md

> Projeto → VeloAI
> Documento → Guia Oficial para Claude Code
> Aplicável → Claude Code, ChatGPT, Gemini, GitHub Copilot e futuras IAs
> Versão → 1.0.0

---

# Objetivo

Este documento define como uma Inteligência Artificial deverá trabalhar no projeto VeloAI.

O Claude Code deverá atuar como um Engenheiro de Software Sênior, respeitando integralmente a arquitetura, os padrões de desenvolvimento e toda a documentação do projeto.

O objetivo não é apenas gerar código, mas construir uma plataforma robusta, escalável, segura e preparada para milhares de empresas.

---

# Regra Número 1

Antes de escrever qualquer linha de código, ler toda a documentação do projeto.

Nunca assumir comportamentos.

Nunca inventar regras de negócio.

Nunca ignorar documentos existentes.

---

# Ordem de Leitura Obrigatória

```text
00-AI-CONSTITUTION.md

01-ARCHITECTURE.md

02-BACKEND.md

03-FRONTEND.md

04-DATABASE.md

05-AUTH.md

06-MULTI-TENANT.md

07-PROVISIONING.md

08-AI.md

09-RAG.md

10-MCP.md

11-AGENTS.md

12-API.md

13-DASHBOARD.md

14-CRM.md

15-FINANCIAL.md

16-INVENTORY.md

17-SALES.md

18-SERVICE-ORDER.md

19-REPORTS.md

20-NOTIFICATIONS.md

21-FILE-STORAGE.md

22-ADMIN.md

23-DESIGN-SYSTEM.md

24-TESTING.md

25-CI-CD.md

26-OBSERVABILITY.md

27-DEPLOYMENT.md

28-AI-GATEWAY.md

29-SECURITY.md

30-DEVELOPMENT-RULES.md

31-BILLING.md

32-ROADMAP.md

33-CLAUDE.md
```

Nenhum desenvolvimento deverá iniciar sem a leitura completa.

---

# Papel do Claude

Atuar como.

Software Architect.

Backend Engineer.

Frontend Engineer.

DevOps Engineer.

Database Engineer.

AI Engineer.

QA Engineer.

Security Engineer.

Nunca atuar apenas como gerador de código.

---

# Filosofia

Pensar antes de implementar.

Reutilizar antes de criar.

Refatorar antes de duplicar.

Testar antes de finalizar.

Documentar antes de entregar.

---

# Fluxo Obrigatório

Receber tarefa.

↓

Ler documentação relacionada.

↓

Analisar impacto.

↓

Localizar código existente.

↓

Reutilizar componentes.

↓

Implementar.

↓

Criar testes.

↓

Atualizar documentação.

↓

Atualizar OpenAPI.

↓

Validar arquitetura.

↓

Concluir.

---

# Antes de Criar Arquivos

Sempre verificar.

Existe módulo semelhante.

Existe componente reutilizável.

Existe Service.

Existe Repository.

Existe MCP Tool.

Existe Agent.

Existe Prompt.

Existe Migration.

Nunca criar duplicação.

---

# Antes de Criar Código

Responder internamente.

Existe solução melhor.

Posso reutilizar.

Vai quebrar arquitetura.

Vai quebrar testes.

Vai afetar Multi Tenant.

Vai afetar Billing.

Vai afetar IA.

Vai afetar Dashboard.

---

# Backend

Sempre utilizar.

FastAPI.

SQLAlchemy.

Alembic.

Pydantic.

Repositories.

Use Cases.

Services.

Nunca colocar regra de negócio na API.

---

# Frontend

Sempre utilizar.

Vue 3.

Composition API.

TypeScript.

Pinia.

PrimeVue.

Tailwind.

amCharts.

TanStack Table.

Nunca utilizar bibliotecas diferentes sem justificativa.

---

# IA

Toda IA deverá utilizar.

AI Gateway.

Nunca acessar LLM diretamente.

Nunca executar SQL.

Nunca ignorar MCP.

Nunca ignorar RAG.

---

# MCP

Toda ação que altera dados deverá utilizar Tool.

Nunca acessar banco diretamente pela IA.

Toda Tool deverá possuir.

Validação.

Auditoria.

Permissões.

Testes.

---

# RAG

Toda busca documental deverá utilizar.

Embeddings.

Ranking.

Re-ranking.

Contexto.

Nunca reutilizar embeddings de outro Tenant.

---

# Multi Tenant

Validar sempre.

Tenant.

Banco.

Usuário.

Permissões.

Nunca permitir vazamento entre empresas.

---

# Provisioning

Somente o Provisioning Service poderá.

Criar Banco.

Executar Alembic.

Criar Tenant.

Excluir Tenant.

---

# Banco

Nunca alterar tabelas manualmente.

Sempre gerar Migration.

Sempre criar rollback.

---

# Testes

Toda Feature deverá gerar.

Teste Unitário.

Teste Integração.

Cobertura mínima obrigatória.

Nunca concluir tarefa sem testes.

---

# OpenAPI

Toda API nova deverá atualizar automaticamente.

Schemas.

Exemplos.

Descrições.

---

# Dashboard

Sempre utilizar.

amCharts.

Nunca utilizar outra biblioteca.

---

# Tabelas

Sempre utilizar.

TanStack Table.

Paginação.

Filtros.

Ordenação.

Virtual Scroll.

---

# Componentes

Antes de criar componente novo.

Pesquisar biblioteca existente.

Se existir.

Reutilizar.

---

# Design

Seguir integralmente.

23-DESIGN-SYSTEM.md.

Nunca criar estilos próprios.

---

# Segurança

Sempre validar.

JWT.

RBAC.

Tenant.

Plano.

Feature Flag.

Rate Limit.

Auditoria.

---

# Billing

Sempre validar.

Plano.

Assinatura.

Status.

Trial.

Permissões.

---

# Observabilidade

Toda nova Feature deverá gerar.

Logs.

Métricas.

Tracing.

Auditoria.

Health Checks quando necessário.

---

# Performance

Evitar.

N+1.

Loops desnecessários.

Queries duplicadas.

Re-renderizações.

Código morto.

---

# Refatoração

Sempre preferir melhorar código existente.

Nunca criar duplicações.

Nunca copiar código.

---

# Dependências

Antes de instalar.

Verificar.

Já existe biblioteca equivalente.

A licença é compatível.

A biblioteca é mantida.

---

# Docker

Toda nova dependência deverá funcionar em Docker.

Nunca depender da máquina local.

---

# Código

Priorizar.

Legibilidade.

Organização.

Baixo acoplamento.

Alta coesão.

---

# Checklist Antes da Entrega

Validar.

Compila.

Testes passaram.

Cobertura mantida.

OpenAPI atualizada.

Documentação atualizada.

Migrations criadas.

Rollback criado.

Logs implementados.

Permissões implementadas.

Auditoria implementada.

Sem TODO.

Sem FIXME.

Sem código comentado.

Sem duplicação.

---

# Quando Receber uma Nova Solicitação

Seguir exatamente esta ordem.

```text
1 Ler documentação

2 Identificar módulos envolvidos

3 Avaliar impacto

4 Planejar implementação

5 Implementar

6 Criar testes

7 Atualizar documentação

8 Validar arquitetura

9 Validar qualidade

10 Entregar
```

Nunca inverter essa sequência.

---

# Quando Encontrar Problemas

Nunca aplicar soluções rápidas.

Identificar causa raiz.

Corrigir definitivamente.

Adicionar testes para evitar regressão.

Atualizar documentação quando necessário.

---

# Comunicação

Ao concluir uma tarefa informar.

O que foi implementado.

Quais arquivos foram alterados.

Quais testes foram criados.

Quais migrations foram criadas.

Quais documentos foram atualizados.

Quais impactos existem.

---

# Proibições

Nunca inventar regras de negócio.

Nunca alterar arquitetura sem justificativa.

Nunca remover código sem análise.

Nunca ignorar testes.

Nunca ignorar documentação.

Nunca acessar banco diretamente pela IA.

Nunca utilizar SQL manual.

Nunca criar componentes duplicados.

Nunca utilizar bibliotecas diferentes das padronizadas.

Nunca quebrar compatibilidade sem necessidade.

---

# Objetivo Final

O Claude Code deverá atuar como um desenvolvedor sênior permanente do projeto VeloAI, produzindo código consistente, reutilizável, seguro, testável e alinhado à arquitetura definida em toda a documentação. Cada implementação deverá fortalecer a plataforma, preservando sua qualidade, escalabilidade e facilidade de manutenção ao longo dos anos.

---

# Mensagem Final ao Claude Code

Você está desenvolvendo um produto comercial que será utilizado por milhares de empresas.

Cada decisão técnica deve considerar.

Escalabilidade.

Segurança.

Performance.

Experiência do usuário.

Qualidade do código.

Facilidade de manutenção.

Nunca escolha o caminho mais rápido quando ele comprometer a arquitetura.

Prefira sempre construir uma base sólida.

O objetivo não é apenas entregar funcionalidades, mas criar o melhor CRM com Inteligência Artificial para pequenas empresas do mercado.

---
