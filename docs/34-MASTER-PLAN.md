# 34-MASTER-PLAN.md

> Projeto → VeloAI
> Documento → Plano Mestre de Desenvolvimento
> Versão → 1.0.0

---

# Objetivo

Este documento é o ponto de entrada oficial do projeto VeloAI.

Todo desenvolvedor, seja humano ou Inteligência Artificial, deverá iniciar por este documento.

Seu objetivo é organizar toda a documentação existente, definir a ordem correta de desenvolvimento, estabelecer dependências entre módulos e garantir que o sistema seja construído de forma incremental, consistente e sem retrabalho.

Este documento possui prioridade máxima abaixo apenas do 00-AI-CONSTITUTION.md.

---

# Visão do Produto

O VeloAI é uma plataforma SaaS AI First destinada a pequenas empresas e prestadores de serviço.

Seu principal diferencial é permitir que praticamente todas as operações possam ser realizadas por linguagem natural através de Inteligência Artificial.

Exemplos.

"Cadastrar um cliente."

"Criar uma Ordem de Serviço."

"Registrar uma venda."

"Gerar um relatório."

"Consultar o faturamento."

A IA será a principal interface do sistema.

---

# Stack Oficial

Backend.

Python 3.13.

FastAPI.

SQLAlchemy.

Alembic.

Celery.

Redis.

Frontend.

Vue 3.

TypeScript.

Tailwind CSS.

PrimeVue.

TanStack Table.

amCharts.

Banco.

PostgreSQL.

Arquivos.

MinIO.

IA.

Gemini 3.1 Flash Lite.

AI Gateway.

MCP.

RAG.

Docker.

Docker Compose.

GitHub Actions.

---

# Ordem Oficial de Leitura

```text
00-AI-CONSTITUTION.md

34-MASTER-PLAN.md

01 até 33 em ordem crescente
```

Nenhuma implementação poderá iniciar antes da leitura destes documentos.

---

# Ordem Oficial de Desenvolvimento

## Fase 1

Infraestrutura.

Docker.

Docker Compose.

CI.

Observabilidade.

Segurança.

Deploy.

---

## Fase 2

Provisioning Service.

Multi Tenant.

Banco Master.

Criação automática de bancos.

Alembic.

Seeds.

---

## Fase 3

Autenticação.

JWT.

Refresh Token.

RBAC.

Permissões.

Usuários.

Empresas.

---

## Fase 4

Backend Base.

FastAPI.

Repositories.

Services.

Use Cases.

Middlewares.

Logs.

OpenAPI.

---

## Fase 5

Frontend Base.

Vue.

Layout.

Sidebar.

Header.

Tema.

Login.

Dark Mode.

Design System.

---

## Fase 6

CRM.

Clientes.

Fornecedores.

Produtos.

Categorias.

Serviços.

---

## Fase 7

Estoque.

Movimentações.

Inventário.

Alertas.

Custos.

---

## Fase 8

Ordens de Serviço.

Status.

Técnicos.

Equipamentos.

Histórico.

Assinaturas.

---

## Fase 9

Vendas.

PDV.

Pedidos.

Orçamentos.

Pagamento.

Comissões.

---

## Fase 10

Financeiro.

Contas.

Fluxo de Caixa.

DRE.

Relatórios.

---

## Fase 11

Dashboard.

KPIs.

amCharts.

Widgets.

Indicadores.

---

## Fase 12

Storage.

Uploads.

Documentos.

Imagens.

MinIO.

OCR.

---

## Fase 13

AI Gateway.

Planner.

Agents.

Prompt Builder.

Cache.

Billing IA.

---

## Fase 14

MCP.

Tools.

Executor.

Workflow.

Permissões.

---

## Fase 15

RAG.

Embeddings.

Chunking.

Vetores.

Busca Semântica.

---

## Fase 16

IA Integrada.

Chat Global.

Chat por Tela.

Automações.

Relatórios.

Análises.

---

## Fase 17

Billing.

Assinaturas.

Trial.

Pagamento.

Webhooks.

---

## Fase 18

Painel Administrativo.

Tenants.

Billing.

Logs.

Monitoramento.

---

## Fase 19

Testes.

Performance.

Segurança.

Carga.

Refatorações.

---

## Fase 20

Release 1.0.

Congelamento.

Correções.

Documentação.

Publicação.

---

# Dependências

Provisioning depende da Infraestrutura.

Autenticação depende do Multi Tenant.

CRM depende da Autenticação.

Financeiro depende do CRM.

Dashboard depende do Financeiro.

IA depende do AI Gateway.

MCP depende do AI Gateway.

RAG depende do Storage.

Billing depende do Multi Tenant.

Painel Administrativo depende de todos os módulos anteriores.

---

# Critério para Concluir um Módulo

Implementação concluída.

Testes aprovados.

Cobertura mínima atingida.

Documentação atualizada.

OpenAPI atualizada.

Migrations criadas.

Rollback validado.

CI aprovado.

Sem erros conhecidos.

---

# Checklist Global

Infraestrutura pronta.

Provisionamento funcionando.

Multi Tenant validado.

Autenticação concluída.

Frontend funcional.

CRM completo.

Financeiro completo.

Ordens de Serviço completas.

Vendas completas.

Dashboard completo.

Storage funcional.

AI Gateway funcional.

MCP funcional.

RAG funcional.

Billing funcional.

Painel Administrativo funcional.

Observabilidade funcional.

Segurança validada.

Testes aprovados.

Deploy validado.

---

# Indicadores do Projeto

Cobertura Backend maior que 95%.

Cobertura Frontend maior que 90%.

Tempo médio da API menor que 300 ms.

Tempo médio das respostas da IA menor que 5 segundos.

Disponibilidade maior que 99,9%.

Zero vazamento entre Tenants.

Zero credenciais versionadas.

---

# Definition of Done Global

Todos os documentos implementados.

Todos os módulos entregues.

Todos os testes aprovados.

Todos os pipelines aprovados.

Documentação completa.

Docker funcionando.

Deploy funcionando.

Sistema operacional.

Primeiro cliente criado.

Primeira venda registrada.

Primeira Ordem de Serviço emitida.

Primeiro relatório gerado por IA.

Primeira conversa com IA funcionando.

---

# Missão do Projeto

Construir o melhor CRM AI First para pequenas empresas do Brasil.

Permitir que qualquer usuário consiga operar o sistema conversando naturalmente com a Inteligência Artificial.

Eliminar tarefas repetitivas.

Automatizar processos.

Reduzir tempo operacional.

Aumentar produtividade.

Escalar com segurança.

---

# Objetivo Final

O VeloAI deverá ser uma plataforma moderna, escalável e inteligente, capaz de atender milhares de empresas utilizando arquitetura Multi Tenant, Inteligência Artificial Generativa, RAG, MCP e agentes especializados, mantendo alta qualidade técnica, excelente experiência do usuário e evolução contínua.

---

# Mensagem Final

Todo desenvolvimento deverá seguir este documento como guia principal.

Em caso de conflito entre documentos, seguir esta ordem de prioridade.

```text
00-AI-CONSTITUTION.md

34-MASTER-PLAN.md

Demais documentos específicos
```

Nenhuma implementação deverá violar os princípios estabelecidos nesses documentos.

---

# Status Geral da Documentação

Documentos criados.

00 até 34.

Arquitetura definida.

Stack definida.

Design definido.

Infraestrutura definida.

Segurança definida.

Observabilidade definida.

IA definida.

Billing definido.

Roadmap definido.

Plano mestre definido.

Projeto oficialmente pronto para iniciar o desenvolvimento.

---
