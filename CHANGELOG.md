# Changelog

Todas as mudanças relevantes deste projeto são documentadas neste arquivo, organizadas
por Fase do `docs/34-MASTER-PLAN.md` — o roteiro oficial de desenvolvimento. Este é o
primeiro release do VeloAI; não há histórico anterior de versões publicadas.

## [1.0.0] — Release inicial (MVP comercial)

Cobre as Fases 1 a 20 do Master Plan. Cada entrada abaixo resume o que foi
efetivamente construído — e, quando relevante, o que foi deliberadamente deixado de
fora e por quê (normalmente por depender de infraestrutura que não existe neste
ambiente: gateway de pagamento, stack de observabilidade, fila de mensagens, motor de
automação).

### Fase 1 — Infraestrutura
Docker Compose orquestrando todos os serviços (Postgres, Redis, MinIO, Qdrant,
Provisioning, Backend, AI Gateway, Frontend); CI (lint/testes/build/segurança) via
GitHub Actions; papéis de PostgreSQL separados (`veloai_admin` administrativo vs.
`veloai_app` de aplicação, sem privilégios de DDL).

### Fase 2 — Provisioning Service / Multi-Tenancy
Banco Master; provisionamento automático de um banco PostgreSQL exclusivo por tenant
(database-per-tenant); migrations Alembic (master e template de tenant); seed do
usuário Administrador de cada novo tenant.

### Fase 3 — Autenticação
Login/refresh/logout via JWT em cookies HttpOnly (nunca LocalStorage); RBAC
(`require_permission`) com permissões `<módulo>.<ação>`; troca de senha obrigatória no
primeiro acesso; rate limit de tentativas de login via Redis.

### Fase 4 — Backend Base
Clean Architecture (`api/ → use_cases/ → services/ → repositories/`) estabelecida como
convenção para todo módulo futuro; auditoria (`TenantAuditLog`) e logging estruturado
por requisição (`X-Request-ID`) reutilizáveis por qualquer módulo de negócio.

### Fase 5 — Frontend Base
Vue 3 + TypeScript + Vite + Tailwind + PrimeVue; layout com Sidebar/Header, tema
claro/escuro, tela de login. O botão "✨ Perguntar para IA" do Header já nasceu aqui
como placeholder — só ganhou função real na Fase 16.

### Fase 6 — CRM completo
Clientes, Fornecedores (cópia estrutural de Clientes), Categorias, Produtos e Serviços.

### Fase 7 — Estoque
Histórico de movimentações de estoque (entrada/saída/ajuste) dentro do módulo
`products/` (não um módulo próprio, para atualizar `products.stock` e gravar o
movimento na mesma transação).

### Fase 8 — Ordens de Serviço / Usuários
Primeiro fluxo operacional ponta-a-ponta: cria a Ordem, adiciona itens de produto/
serviço, `start`/`close`/`cancel` — `close` consome estoque automaticamente na mesma
transação. Módulo `users/` (somente leitura, para o seletor de técnico).

### Fase 9 — Vendas
Segundo fluxo operacional: cria a Venda, adiciona itens de produto, aplica desconto,
`complete` consome estoque automaticamente. Sem exclusão — só cancelamento.

### Fase 10 — Financeiro
Contas a Receber, Contas a Pagar e Fluxo de Caixa — `receive`/`pay` geram uma entrada
de fluxo de caixa automaticamente na mesma transação. Sem exclusão — só estorno.

### Fase 11 — Dashboard
Sem tabela própria — agrega em tempo real os dados que os módulos anteriores já
produzem em KPIs e dois gráficos (amCharts 5).

### Fase 12 — Storage (Anexos)
Conecta o MinIO (provisionado desde a Fase 1, nunca usado até então). Anexos genéricos
para Clientes, Produtos e Ordens de Serviço — tabela só guarda metadados, nunca o
arquivo em si. Exclusão remove do MinIO antes da linha do banco.

### Fase 13 — IA (AI Gateway)
`POST /ai/ask` conecta o Backend ao `ai-gateway/` (que já falava com o Gemini de
verdade, mas sem consumidor real) — contexto enxuto de empresa/usuário, cache de
resposta via Redis, estimativa de custo por token, histórico em `ai_conversations`.

### Fase 14 — MCP/Tools
*Function calling* real do Gemini: a IA pode decidir cadastrar/buscar um Cliente
(`CreateCustomer`/`SearchCustomers`/`GetCustomer`), sempre filtrado pelas permissões
reais do usuário, com o resultado auditado em `ai_actions`. Implementa o princípio MCP
dentro do Backend (Tool Registry + permissão + auditoria), não o protocolo MCP literal
(sem cliente MCP externo).

### Fase 15 — RAG (Base de Conhecimento)
Conecta o Backend ao Qdrant (uma Collection por tenant). `POST /knowledge` indexa de
verdade (chunking + embeddings reais do Gemini); `SearchKnowledge` deixa a IA buscar
semanticamente. Só texto puro — sem upload/OCR (pipeline de parsing multi-formato não
existe).

### Fase 16 — IA Integrada (Relatórios via IA + Chat Global)
Funde 3 docs ambiciosos e reduz o escopo a duas entregas reais: 3 novas Tools de
relatório reaproveitando os Use Cases já existentes do Dashboard, e o botão de IA do
Header (inerte desde a Fase 5) ligado a um chat flutuante disponível em qualquer tela.
**Automation Engine inteiro fica de fora** — nenhuma fatia é construível sem inventar
event bus/fila/scheduler/editor visual do zero.

### Fase 17 — Billing (Trial/Assinatura)
Conecta uma fundação que já existia no Banco Master desde o início do projeto mas
nunca tinha sido usada (`Tenant`/`Plan`/`Subscription`). Assinatura TRIAL real de 14
dias criada a cada novo tenant; leitura/cancelamento reais; acesso bloqueado de
verdade quando a assinatura expira/é cancelada. **Sem gateway de pagamento real**
(Asaas/Stripe — nenhuma credencial existe) — sem faturas, webhooks, múltiplos planos.

### Fase 18 — Painel Administrativo
Sistema de login totalmente separado para operadores da própria VeloAI
(`PlatformAdmin` no Banco Master, cookie/secret próprios, nunca reaproveita a sessão
de tenant). Tela somente leitura com todos os Tenants/Assinaturas e o Log de Auditoria
de cada um. Sem ação de escrita sobre outro tenant e sem Monitoramento real
(Prometheus/Grafana — infra que não existe).

### Fase 19 — Testes / Segurança / Refatoração
Corrigido um gap real de CI: `backend-ci.yml` nunca subia MinIO/Qdrant, então as
suítes de integração de Anexos e RAG sempre pulavam, até no próprio CI. Auditoria
manual de segurança no código das Fases 13-18 (isolamento de sessão, RBAC, SQL cru,
segredos, cookies, rate limit) sem nenhum problema real encontrado. **Performance/
Carga (k6/Locust) e Playwright E2E ficam de fora** — sem Docker/navegador disponíveis
para rodar algo que exigiria execução real para ter algum valor.

### Fase 20 — Release 1.0
Fechamento do Master Plan: este changelog, revisão final do README e bump de versão
para `1.0.0` em todos os serviços. **"Publicação" no sentido literal do
`docs/27-DEPLOYMENT.md`** (deploy em Docker/Kubernetes, ambientes de Homologation/
Production) **fica fora deste ambiente** — não há Docker nem conta de nuvem
disponíveis aqui; é o próximo passo natural fora deste repositório.

## Fora do escopo da v1.0 (ver README para a lista completa por módulo)

Automation Engine, Observabilidade real (OpenTelemetry/Prometheus/Grafana/Loki/Tempo/
Sentry), gateway de pagamento real (Asaas/Stripe/faturas/webhooks), MFA/SSO/Passkeys,
testes de carga/performance, Playwright E2E, e qualquer recurso avançado documentado
como deferred em cada seção "O que NÃO está nesta fase" do `README.md`.
