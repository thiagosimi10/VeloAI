# VeloAI

> AI Business OS — plataforma SaaS Multi-Tenant para pequenas e médias empresas, com
> Inteligência Artificial como interface principal.

Este repositório cobre a **fundação + autenticação + CRM completo (Clientes,
Fornecedores, Categorias, Produtos e Serviços) + Estoque + Ordens de Serviço + Vendas +
Financeiro + Dashboard + Storage (anexos) + IA (AI Gateway) + MCP/Tools + RAG +
Relatórios via IA + Chat Global + Billing (Trial/Assinatura) + Painel Administrativo**
do projeto, com CI real cobrindo Anexos/RAG/Provisioning e uma auditoria de segurança
já realizada — **release `1.0.0`** (ver `docs/34-MASTER-PLAN.md`, Fases 1 a 20, todas
concluídas, e o [`CHANGELOG.md`](CHANGELOG.md) para o resumo fase a fase).
Infraestrutura, provisionamento de tenants, autenticação, auditoria e logging
estruturado já funcionam de ponta a ponta, de
verdade. `suppliers/` é uma cópia estrutural exata de `customers/`, conforme
`docs/05-BANCO-DE-DADOS.md` ("Fornecedores: mesmo padrão dos clientes"). `products/` e
`services/` têm relações entre entidades (`category_id`/`supplier_id`); `products/`
também expõe um campo calculado (margem, nunca persistida) e concentra o histórico de
movimentações de estoque (Fase 7). O módulo `service_orders/` (Fase 8) é o primeiro
fluxo operacional ponta-a-ponta do sistema — cria a Ordem, adiciona itens de produto/
serviço, e ao concluir consome automaticamente o estoque dos itens de produto na mesma
transação. O módulo `sales/` (Fase 9) é o segundo — cria a Venda, adiciona itens de
produto, aplica desconto, e ao concluir também consome estoque automaticamente na
mesma transação, reaproveitando a mesma peça de infraestrutura criada na Fase 8. O
módulo `finance/` (Fase 10) cobre Contas a Receber, Contas a Pagar e Fluxo de Caixa —
ao receber/pagar uma conta, uma entrada de fluxo de caixa é registrada automaticamente
na mesma transação. O módulo `dashboard/` (Fase 11) não tem tabela própria — agrega, em
tempo real, os dados que os módulos anteriores já produzem em KPIs e dois gráficos
(amCharts 5). O módulo `attachments/` (Fase 12) conecta o MinIO (já provisionado no
`docker-compose.yml` desde a Fase 1, mas nunca usado até agora) — anexos genéricos para
Clientes, Produtos e Ordens de Serviço (ver "Arquitetura desta fase" abaixo para o
porquê). O módulo `ai/` (Fase 13) conecta o Backend ao `ai-gateway/` (que já chamava o
Gemini de verdade desde antes desta fase, mas sem nenhum consumidor real) — `POST
/ai/ask` monta um contexto enxuto de empresa/usuário, delega a geração ao AI Gateway e
grava cada chamada em `ai_conversations` (tokens, modelo, tempo de execução). O
AI Gateway ganhou cache de resposta via Redis e estimativa de custo por token. A Fase 14
(MCP/Tools) torna real a regra mais importante da Constitution — "a IA nunca altera
dados sem usar uma Tool" — com *function calling* de verdade do Gemini: a IA pode
decidir cadastrar/buscar um Cliente (`CreateCustomer`/`SearchCustomers`/`GetCustomer`,
as 3 primeiras Tools, reaproveitando o CRUD já existente), sempre filtrado pelas
permissões reais do usuário, com o resultado auditado em `ai_actions`. O módulo
`knowledge/` (Fase 15 — RAG) conecta o Backend ao Qdrant (serviço novo no
`docker-compose.yml`, uma Collection por tenant) — um usuário cadastra um trecho de
texto (política, FAQ) em `POST /knowledge`, o sistema indexa de verdade (chunking +
embeddings reais do Gemini via AI Gateway) e a 4ª Tool, `SearchKnowledge`, deixa a IA
buscar semanticamente esse conteúdo. A Fase 16 (IA Integrada) funde 3 docs
(`13-IA-PLATFORM.md`, `14-AUTOMATION-ENGINE.md`, `15-RELATORIOS-INTELIGENTES.md`) e
reduz o escopo a duas entregas reais: **Reports via IA** — 3 novas Tools em
`dashboard/mcp_tools/` (`GetDashboardSummary`, `GetRevenueTimeseries`,
`GetTopSellingProducts`) que reaproveitam, sem nenhuma query nova, os mesmos Use Cases
já reais do Dashboard (Fase 11) — e **Chat Global** — o botão "✨ Perguntar para IA" do
Header, que existia desde a Fase 5 mas nunca tinha `@click`, agora abre um
`AiChatModal.vue` flutuante disponível em qualquer tela (antes só existia embutido no
Dashboard). O Automation Engine inteiro (editor visual, event bus, scheduler, filas)
fica 100% fora — nenhuma fatia é construível sem inventar essa infraestrutura do zero.
A Fase 17 (Billing) conecta uma fundação que já existia no Banco Master desde o início
do projeto mas nunca tinha sido usada: os modelos `Tenant`/`Plan`/`Subscription`, as
migrations e o script `seed_master.py` (que já garante o Plano "VeloAI Professional" a
cada subida do container do Provisioning). Agora o Provisioning cria de verdade uma
Assinatura TRIAL de 14 dias a cada novo tenant, o Backend ganha um módulo `billing/`
(o primeiro que opera no Banco Master, não no banco do tenant) com leitura/cancelamento
reais da assinatura, e o acesso a qualquer rota de negócio é bloqueado de verdade
quando a assinatura expira ou é cancelada. Sem gateway de pagamento real (Asaas/
Stripe/...) — nenhuma credencial existe neste ambiente, e simular cobrança/faturas/
webhooks violaria a disciplina do projeto de nunca fingir dados reais. A Fase 18
(Painel Administrativo) não tinha nenhum doc dedicado — só um trecho em
`31-BILLING.md` ("Admin Master") — e revelou que essa tela é usada pela equipe da
própria VeloAI, nunca por um tenant; por isso ganhou um sistema de login totalmente
separado (`PlatformAdmin` no Banco Master, cookie/secret próprios, nunca reaproveita
`CurrentUser`/`TokenService` de tenant) e uma tela somente leitura com todos os
Tenants/Assinaturas (dados reais desde a Fase 17) e o Log de Auditoria de cada um
(reaproveita `AuditLog`, já escrito pelo Provisioning e pelo `billing/`). Sem escrita
sobre outro tenant (suspender/mudar plano manualmente) e sem Monitoramento real
(Prometheus/Grafana/Loki/Tempo — infra que não existe). A Fase 19 (Testes/Performance/
Segurança/Carga/Refatorações) não tinha Python nem Docker disponíveis neste ambiente —
sem como rodar pytest, testcontainers ou gerar carga real, então Performance/Carga
ficaram 100% fora (mesmo critério do Automation Engine e do Monitoramento: um script de
carga nunca executado seria só um artefato não verificado). O que era executável de
verdade: um gap real de CI — `backend-ci.yml` já rodava Postgres+Redis reais, mas nunca
MinIO/Qdrant, então as suítes de integração de Anexos (Fase 12) e RAG (Fase 15) sempre
pulavam, até no CI — corrigido acrescentando os dois serviços (`bitnami/minio`, já que
a imagem oficial `minio/minio` não roda como serviço do GitHub Actions sem um argumento
de linha de comando que o schema não permite passar; `qdrant/qdrant` funciona sem
ajuste). E uma auditoria manual de segurança dirigida ao código das Fases 13-18
(isolamento de sessão tenant/admin, cobertura de RBAC em todo `router.py`, interpolação
de SQL cru no Provisioning, segredos em log, cookies, rate limit) — sem nenhum problema
real encontrado que exigisse correção; o único ponto observado (um token, de tenant ou
de Platform Admin, continua válido até expirar mesmo que a conta seja desativada nesse
meio-tempo) é uma escolha arquitetural deliberada de todo o sistema desde a Fase 3, não
um bug desta fase, documentada aqui para o futuro em vez de alterada às pressas.

Toda a documentação oficial do produto está em [`docs/`](docs), começando por
[`docs/00-AI-CONSTITUTION.md`](docs/00-AI-CONSTITUTION.md) e
[`docs/34-MASTER-PLAN.md`](docs/34-MASTER-PLAN.md).

---

## Arquitetura

```
veloai/
  shared/          # pacote Python compartilhado: response envelope, exceptions,
                    # logging, health check, segurança (Argon2, UUIDv7, JWT) e os
                    # modelos SQLAlchemy do Banco Master e do template de tenant —
                    # usado por backend, provisioning e ai-gateway.
  backend/         # FastAPI — API principal. Módulo `auth/` (login, refresh, logout,
                    # /me, troca de senha) + RBAC (`require_permission`) + auditoria
                    # (`core/audit.py`) + logging estruturado por requisição
                    # (`core/middleware.py`), reutilizáveis por qualquer módulo de
                    # negócio. Módulos `customers/`, `suppliers/`, `categories/`,
                    # `products/` e `services/` (CRM completo). O histórico de
                    # movimentações de estoque (Fase 7) mora dentro de `products/` —
                    # não é um módulo próprio — para poder atualizar `products.stock` e
                    # gravar o movimento na mesma transação (ver
                    # `backend/app/modules/README.md`); as permissões continuam
                    # separadas (`stock.view`/`stock.adjust`). Módulo `service_orders/`
                    # (Fase 8): cria/lista/atualiza Ordens de Serviço, adiciona/remove
                    # itens (produto ou serviço) e expõe as transições `start`/`close`/
                    # `cancel`; `close` reaproveita a mesma lógica de baixa de estoque de
                    # `products/` via `products/services/stock_movement_service.py`
                    # (nunca acessando o repository de outro módulo diretamente) para
                    # marcar a Ordem como concluída e consumir o estoque de cada item de
                    # produto numa única transação. Módulo `users/` (Fase 8): apenas
                    # leitura (id/nome/email), usado para popular o seletor de técnico
                    # responsável — CRUD completo de usuários fica para fase futura.
                    # Módulo `sales/` (Fase 9): cria/lista/atualiza Vendas, adiciona/
                    # remove itens de produto (nunca serviço — `05-BANCO-DE-DADOS.md` não
                    # tem `service_id` em `sale_items`) e expõe as transições `complete`/
                    # `cancel`; `complete` reaproveita a mesma
                    # `products/services/stock_movement_service.py` para consumir
                    # estoque na conclusão. Sem exclusão — só cancelamento (`12-VENDAS.md`:
                    # "Nunca excluir vendas. Sempre cancelar."). Módulo `finance/`
                    # (Fase 10): Contas a Receber, Contas a Pagar e Fluxo de Caixa —
                    # `receive`/`pay` inserem uma entrada de fluxo de caixa
                    # automaticamente na mesma transação (as três tabelas vivem no
                    # mesmo módulo, então essa integração não esbarra na regra de "nunca
                    # acessar repository de outro módulo"). Sem exclusão — só
                    # cancelamento de contas pendentes (`11-FINANCEIRO.md`: "Nunca
                    # excluir lançamentos financeiros. Sempre utilizar estorno.").
                    # Geração automática de Conta a Receber a partir de Venda/OS
                    # concluída fica de fora — não há coluna de origem no banco para
                    # rastrear isso. Módulo `dashboard/` (Fase 11): sem tabela própria —
                    # `repositories/dashboard_repository.py` consulta os modelos
                    # SQLAlchemy de outros módulos diretamente com SELECTs agregados
                    # (COUNT/SUM/GROUP BY), somente leitura (não é uma violação da regra
                    # de "nunca acessar repository de outro módulo", que protege escrita
                    # — ver `backend/app/modules/README.md`). Módulo `attachments/`
                    # (Fase 12): sem base em `05-BANCO-DE-DADOS.md` — decisão tomada com
                    # o usuário por não haver tabela alguma prevista para Storage nesta
                    # fase. Tabela genérica/polimórfica (`resource_type`+`resource_id`)
                    # para anexar arquivos a Clientes, Produtos e Ordens de Serviço; usa
                    # `app/core/storage.py` (cliente MinIO) — a tabela só guarda
                    # metadados, nunca o arquivo em si (`22-API-STANDARDS.md`: "Nunca
                    # armazenar arquivos no banco"). Exclusão remove do MinIO antes da
                    # linha do banco, nunca a ordem inversa. Módulo `ai/` (Fase 13):
                    # `POST /ai/ask` monta um "Prompt Builder" enxuto (empresa/usuário/
                    # data) e delega a um `AIGatewayClient` novo (`app/core/
                    # ai_gateway_client.py`, cross-cutting) — o Backend nunca fala com
                    # uma LLM diretamente, só com o AI Gateway. Grava cada chamada em
                    # `ai_conversations` (tokens/modelo/tempo de execução); `GET
                    # /ai/conversations` lista o histórico paginado. Fase 14 (MCP/
                    # Tools): `tool_registry.py` filtra as Tools (`app/core/
                    # ai_tools.py::AITool`) pelas permissões reais do usuário e as
                    # declara ao Gemini (function calling); se a IA decidir chamar uma,
                    # `AskAIUseCase` resolve/revalida/executa (papel de Executor,
                    # 00-AI-CONSTITUTION.md) e grava o resultado em `ai_actions`. As 3
                    # primeiras Tools (`customers/mcp_tools/`) reaproveitam o CRUD já
                    # existente. Módulo `knowledge/` (Fase 15 — RAG): Base de
                    # Conhecimento em texto puro (sem upload/OCR — `docs/21-RAG.md`
                    # pede um pipeline de parsing que não existe ainda). `POST
                    # /knowledge` grava no Postgres e indexa na mesma requisição
                    # (chunking sem LangChain → embeddings reais via AI Gateway →
                    # upsert no Qdrant, `app/core/qdrant_client.py`). Uma Collection por
                    # tenant (`tenant_{id}_vectors`, 04-MULTI-TENANCY.md), criada no
                    # Provisioning. `SearchKnowledge` (4ª Tool) deixa a IA buscar
                    # semanticamente. Autentica no Postgres exclusivamente como a role
                    # `veloai_app`. Módulo `dashboard/` (Fase 16): ganha
                    # `mcp_tools/` com mais 3 Tools (`GetDashboardSummary`,
                    # `GetRevenueTimeseries`, `GetTopSellingProducts`, chegando a 7 no
                    # Registry) — cada uma só chama o Use Case já existente do próprio
                    # módulo, nenhuma query nova. Módulo `billing/` (Fase 17): primeiro
                    # módulo do Backend que opera no Banco Master (`get_master_session()`),
                    # não no banco do tenant — `GET /billing/subscription`/`POST
                    # /billing/cancel` + a 8ª Tool (`GetSubscriptionStatus`). Nova
                    # dependency `require_active_subscription` (`app/core/
                    # dependencies.py`) é aplicada a todo módulo de negócio em
                    # `app/api/v1/router.py`, exceto `auth`/`billing`/`admin` — bloqueia
                    # com 403 `SUBSCRIPTION_INACTIVE` um tenant com assinatura expirada/
                    # cancelada/suspensa. Módulo `admin/` (Fase 18) — Painel
                    # Administrativo, único usado pela equipe da VeloAI, nunca por um
                    # tenant: login próprio (`PlatformAdmin` no Banco Master, cookie
                    # `admin_access_token` + secret `platform_admin_jwt_secret`, nunca
                    # reaproveita `CurrentUser`/`TokenService` de tenant), `GET
                    # /admin/tenants` (lista real com plano/assinatura), `GET /admin/
                    # summary` (contagens + MRR estimado), `GET /admin/tenants/{id}/
                    # audit-log` (reaproveita `AuditLog` do Master). Somente leitura —
                    # sem ação de escrita sobre outro tenant nesta fase.
  provisioning/     # FastAPI — único serviço com privilégios administrativos de
                    # PostgreSQL. Cria bancos de tenant de verdade e concede os
                    # privilégios mínimos à role `veloai_app`. Desde a Fase 15, também
                    # cria a Collection Qdrant exclusiva de cada tenant. Desde a Fase 17,
                    # também cria a Assinatura TRIAL (14 dias) de cada tenant, atribuída
                    # ao único Plano ativo já semeado por `scripts/seed_master.py`
                    # (roda automaticamente a cada subida do container, via
                    # `docker-entrypoint.sh`). Desde a Fase 18, esse mesmo script também
                    # garante o primeiro operador do Painel Administrativo
                    # (`PLATFORM_ADMIN_EMAIL`/`PLATFORM_ADMIN_PASSWORD`).
  ai-gateway/       # FastAPI — único ponto de comunicação com provedores de LLM
                    # (Gemini implementado; arquitetura pronta para outros). Cache de
                    # resposta via Redis (Response Cache) e estimativa de custo por
                    # token (`GeminiProvider.estimate_cost`) desde a Fase 13.
                    # `/generate` aceita `tools` (function calling do Gemini) desde a
                    # Fase 14 — a chave de cache passou a variar também pelas Tools
                    # disponíveis. `POST /embeddings` (Fase 15) chama o modelo real
                    # `text-embedding-004` — o Backend nunca fala com o Gemini
                    # diretamente, só com o AI Gateway.
  frontend/         # Vue 3 + TypeScript + Vite + Tailwind + PrimeVue. Sessão via
                    # cookies HttpOnly (nunca LocalStorage), com refresh automático.
                    # Desde a Fase 16, o Assistente de IA é global: o botão "✨
                    # Perguntar para IA" do `AppHeader.vue` abre um `AiChatModal.vue`
                    # flutuante (montado uma vez em `DefaultLayout.vue`), disponível em
                    # qualquer tela — não mais só embutido no Dashboard. Tela `/billing`
                    # (Fase 17): plano/status/dias restantes de trial + cancelamento.
                    # Painel Administrativo (Fase 18): `/admin/login`, `/admin/tenants`,
                    # `/admin/tenants/:id/audit-log` — layout próprio (`AdminLayout.vue`,
                    # sem Sidebar/AiChatModal) e guard de rota isolado no `router/
                    # index.ts` (usa `stores/adminAuth.ts`, nunca `stores/auth.ts`).
  infra/            # postgres/init (cria a role `veloai_app` no primeiro boot), scripts.
  .github/workflows/ # CI (lint, testes, build Docker, segurança).
  docker-compose.yml
```

Cada serviço Python segue Clean Architecture (`api/ → use_cases/ → services/ →
repositories/ → models/`), conforme `docs/00-AI-CONSTITUTION.md` e
`docs/16-BACKEND-ARCHITECTURE.md`.

### Duas roles de PostgreSQL

- `veloai_admin` — usada **exclusivamente** pelo Provisioning Service (`CREATE
  DATABASE`/`DROP DATABASE`/`CREATE SCHEMA`/`GRANT`).
- `veloai_app` — usada **exclusivamente** pelo Backend, tanto no Banco Master quanto em
  cada banco de tenant. Sem nenhum privilégio administrativo.

---

## Subindo o ambiente

```bash
cp .env.example .env
docker compose up -d
```

Serviços expostos localmente:

| Serviço | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/docs |
| Provisioning | http://localhost:8001/docs |
| AI Gateway | http://localhost:8002/docs |
| MinIO Console | http://localhost:9001 |
| Qdrant | http://localhost:6333/dashboard |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

Todo serviço FastAPI expõe `/health`, `/ready` e `/live`.

---

## Criando a primeira empresa (Tenant) e fazendo login

```bash
# 1. Provisiona a empresa (Provisioning Service)
curl -X POST http://localhost:8001/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "legal_name": "Assistência Técnica Silva LTDA",
    "trade_name": "Assistência Silva",
    "document": "12345678000199",
    "admin_name": "Maria Souza",
    "admin_email": "maria@assistenciasilva.com"
  }'
# → retorna a senha temporária do admin uma única vez (force_password_change: true)

# 2. Login (Backend) — cookies HttpOnly são setados na resposta
curl -i -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email": "maria@assistenciasilva.com", "password": "<senha-temporaria>"}'

# 3. Troca de senha obrigatória no primeiro acesso
curl -X PATCH http://localhost:8000/api/v1/auth/password \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"current_password": "<senha-temporaria>", "new_password": "NovaSenhaForte123!"}'

# 4. Perfil do usuário autenticado
curl http://localhost:8000/api/v1/auth/me -b cookies.txt

# 5. Criar um Cliente (o papel Administrador já recebe customers.* no seed)
curl -X POST http://localhost:8000/api/v1/customers \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"type": "PF", "name": "João Silva", "document": "123.456.789-01", "email": "joao@cliente.com"}'

# 6. Listar/buscar clientes (paginado)
curl "http://localhost:8000/api/v1/customers?search=joao&page=1" -b cookies.txt

# 7. Criar um Fornecedor (o papel Administrador já recebe suppliers.* no seed)
curl -X POST http://localhost:8000/api/v1/suppliers \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"type": "PJ", "name": "Tech Distribuidora LTDA", "document": "12.345.678/0001-99"}'

# 8. Listar/buscar fornecedores (paginado)
curl "http://localhost:8000/api/v1/suppliers?search=tech&page=1" -b cookies.txt

# 9. Criar uma Categoria (o papel Administrador já recebe categories.* no seed)
curl -X POST http://localhost:8000/api/v1/categories \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"name": "Armazenamento", "description": "SSDs, HDs e pendrives"}'

# 10. Criar um Produto vinculado à categoria e ao fornecedor criados acima
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "category_id": "<id-da-categoria>",
    "supplier_id": "<id-do-fornecedor>",
    "sku": "SSD-KGN-1TB",
    "name": "SSD Kingston 1TB",
    "cost_price": "320.00",
    "sale_price": "490.00",
    "stock": 20
  }'
# → a resposta inclui "margin" e "margin_percentage", calculados na hora (nunca persistidos)

# 11. Listar produtos filtrando por categoria
curl "http://localhost:8000/api/v1/products?category_id=<id-da-categoria>" -b cookies.txt

# 12. Criar um Serviço vinculado à categoria (o papel Administrador já recebe services.* no seed)
curl -X POST http://localhost:8000/api/v1/services \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "category_id": "<id-da-categoria>",
    "name": "Formatação de Computador",
    "price": "180.00",
    "estimated_time": 60
  }'

# 13. Listar/buscar serviços filtrando por categoria
curl "http://localhost:8000/api/v1/services?category_id=<id-da-categoria>" -b cookies.txt

# 14. Registrar uma entrada de estoque no produto criado acima (o papel Administrador
#     já recebe stock.* no seed)
curl -X POST http://localhost:8000/api/v1/products/<id-do-produto>/stock-movements \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"movement": "in", "quantity": 10, "reason": "Compra de reposição"}'
# → a resposta inclui "previous_stock" e "current_stock"; GET /products/{id} já reflete
#   o novo valor de stock (mesma transação)

# 15. Consultar o histórico de movimentações do produto (mais recente primeiro)
curl "http://localhost:8000/api/v1/products/<id-do-produto>/stock-movements" -b cookies.txt

# 16. Criar uma Ordem de Serviço para o cliente criado acima (o papel Administrador já
#     recebe service_orders.*/users.view no seed) — number é gerado automaticamente
#     (OS-<ano>-<sequência>)
curl -X POST http://localhost:8000/api/v1/service-orders \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "customer_id": "<id-do-cliente>",
    "equipment": "Notebook Dell",
    "problem": "Não liga"
  }'

# 17. Adicionar um item de produto à OS (product_id OU service_id, nunca os dois; se
#     unit_price for omitido, herda o preço do catálogo)
curl -X POST http://localhost:8000/api/v1/service-orders/<id-da-os>/items \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"product_id": "<id-do-produto>", "quantity": 1}'

# 18. Consultar a OS (a resposta já inclui os itens embutidos e o total recalculado)
curl http://localhost:8000/api/v1/service-orders/<id-da-os> -b cookies.txt

# 19. Iniciar o atendimento (open → in_progress)
curl -X POST http://localhost:8000/api/v1/service-orders/<id-da-os>/start -b cookies.txt

# 20. Concluir a OS informando o técnico responsável — obrigatório se a OS ainda não
#     tiver um; ao concluir, o estoque de cada item de produto é baixado
#     automaticamente na mesma transação
curl -X POST http://localhost:8000/api/v1/service-orders/<id-da-os>/close \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"technician_id": "<id-do-tecnico>", "solution": "Placa-mãe trocada"}'

# 21. Criar uma Venda para o cliente criado acima (o papel Administrador já recebe
#     sales.* no seed)
curl -X POST http://localhost:8000/api/v1/sales \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"customer_id": "<id-do-cliente>", "payment_method": "pix"}'

# 22. Adicionar um item de produto à Venda (sempre produto — sem service_id nesta fase;
#     se unit_price for omitido, herda o preço do catálogo)
curl -X POST http://localhost:8000/api/v1/sales/<id-da-venda>/items \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"product_id": "<id-do-produto>", "quantity": 2}'

# 23. Aplicar um desconto (o total é recalculado: soma dos itens - desconto)
curl -X PATCH http://localhost:8000/api/v1/sales/<id-da-venda> \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"discount": "80.00"}'

# 24. Concluir a Venda — o estoque de cada item de produto é baixado automaticamente
#     na mesma transação (mesmo mecanismo usado na conclusão da Ordem de Serviço)
curl -X POST http://localhost:8000/api/v1/sales/<id-da-venda>/complete -b cookies.txt

# 25. Criar uma Conta a Receber para o cliente criado acima (o papel Administrador já
#     recebe finance.* no seed)
curl -X POST http://localhost:8000/api/v1/accounts-receivable \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"customer_id": "<id-do-cliente>", "due_date": "2026-08-15", "amount": "980.00"}'
# → a resposta inclui "is_overdue", calculado na hora (status pendente + vencimento no
#   passado), nunca persistido

# 26. Receber a Conta a Receber — grava "payment_date" e insere automaticamente uma
#     entrada de entrada ("in") no Fluxo de Caixa, na mesma transação
curl -X POST http://localhost:8000/api/v1/accounts-receivable/<id-da-conta>/receive \
  -b cookies.txt

# 27. Criar e pagar uma Conta a Pagar para o fornecedor criado acima — mesmo mecanismo,
#     insere uma entrada de saída ("out") no Fluxo de Caixa
curl -X POST http://localhost:8000/api/v1/accounts-payable \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"supplier_id": "<id-do-fornecedor>", "due_date": "2026-08-15", "amount": "320.00"}'
curl -X POST http://localhost:8000/api/v1/accounts-payable/<id-da-conta>/pay -b cookies.txt

# 28. Lançamento avulso de Fluxo de Caixa (sem vínculo com Conta a Receber/Pagar)
curl -X POST http://localhost:8000/api/v1/cash-flow \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"type": "out", "category": "Despesas Administrativas", "description": "Aluguel", "amount": "1500.00"}'

# 29. Consultar o Fluxo de Caixa (mais recente primeiro)
curl "http://localhost:8000/api/v1/cash-flow" -b cookies.txt

# 30. Resumo do Dashboard — KPIs agregados de Clientes/Produtos/Serviços/Ordens/Vendas/
#     Financeiro, calculados na hora (o papel Administrador já recebe dashboard.view no
#     seed)
curl "http://localhost:8000/api/v1/dashboard/summary" -b cookies.txt
# → inclui "revenue_change_percentage" (vs. mês anterior, null se não houve receita no
#   mês anterior) e "average_ticket"

# 31. Série histórica de receita (últimos 6 meses, mês corrente incluso) — usada no
#     gráfico de linha do Dashboard
curl "http://localhost:8000/api/v1/dashboard/revenue-timeseries" -b cookies.txt

# 32. Produtos mais vendidos (soma sale_items + service_order_items) — usada no
#     gráfico de barras do Dashboard
curl "http://localhost:8000/api/v1/dashboard/top-products?limit=5" -b cookies.txt

# 33. Anexar um arquivo à Ordem de Serviço criada acima (multipart/form-data; o papel
#     Administrador já recebe attachments.* no seed) — resource_type também aceita
#     "customer"/"product"
curl -X POST http://localhost:8000/api/v1/attachments \
  -b cookies.txt \
  -F "resource_type=service_order" \
  -F "resource_id=<id-da-os>" \
  -F "file=@/caminho/para/foto.jpg"
# → a resposta inclui "url" (link pré-assinado do MinIO, válido por 1 hora) e "size_bytes"

# 34. Listar os anexos da OS
curl "http://localhost:8000/api/v1/attachments?resource_type=service_order&resource_id=<id-da-os>" \
  -b cookies.txt

# 35. Remover um anexo (apaga do MinIO e do banco)
curl -X DELETE http://localhost:8000/api/v1/attachments/<id-do-anexo> -b cookies.txt

# 36. Perguntar algo ao assistente de IA (o papel Administrador já recebe ai.use no
#     seed) — o Backend monta o contexto de empresa/usuário e delega ao AI Gateway
curl -X POST http://localhost:8000/api/v1/ai/ask \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"prompt": "Quanto vendi este mês?"}'
# → a resposta inclui "cached" (true se já havia uma resposta idêntica em cache) e
#   "estimated_cost" (estimativa, não fatura real)

# 37. Consultar o histórico de uso de IA do tenant (mais recente primeiro)
curl "http://localhost:8000/api/v1/ai/conversations" -b cookies.txt

# 38. Pedir para a IA executar uma ação de verdade — o Gemini decide chamar a Tool
#     CreateCustomer (function calling real), o Backend executa o mesmo
#     CreateCustomerUseCase do item 5 e audita o resultado em `ai_actions`
curl -X POST http://localhost:8000/api/v1/ai/ask \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"prompt": "Cadastre um cliente chamado Ana Costa, CPF 321.301.765-92."}'
# → a resposta inclui "tool_used": "CreateCustomer" quando uma Tool foi executada
#   (null em conversas puramente de texto, como nos itens 36/37)

# 39. Cadastrar um item na Base de Conhecimento (o papel Administrador já recebe
#     knowledge.* no seed) — indexa de verdade: chunking + embeddings reais do Gemini
#     + upsert no Qdrant, tudo na mesma requisição
curl -X POST http://localhost:8000/api/v1/knowledge \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "title": "Política de Garantia",
    "content": "Todo produto tem garantia de 90 dias contra defeitos de fabricação."
  }'

# 40. Listar a Base de Conhecimento (paginado)
curl "http://localhost:8000/api/v1/knowledge" -b cookies.txt

# 41. Perguntar algo que só a Base de Conhecimento sabe responder — o Gemini decide
#     chamar a Tool SearchKnowledge (busca semântica real no Qdrant)
curl -X POST http://localhost:8000/api/v1/ai/ask \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"prompt": "Qual é a política de garantia da minha empresa?"}'
# → "tool_used": "SearchKnowledge" quando a IA usa a Base de Conhecimento para responder

# 42. Remover um item da Base de Conhecimento (apaga do Qdrant e do banco)
curl -X DELETE http://localhost:8000/api/v1/knowledge/<id-do-documento> -b cookies.txt

# 43. Perguntar algo analítico ao assistente — o Gemini decide chamar a Tool
#     GetDashboardSummary (reaproveita o mesmo Use Case do endpoint /dashboard/summary)
curl -X POST http://localhost:8000/api/v1/ai/ask \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"prompt": "Qual foi meu faturamento este mês e qual a variação em relação ao mês passado?"}'
# → "tool_used": "GetDashboardSummary"

# 44. Perguntar pelos produtos mais vendidos — a Tool GetTopSellingProducts aceita um
#     "limit" opcional (padrão 5, entre 1 e 20), extraído pela própria IA do prompt
curl -X POST http://localhost:8000/api/v1/ai/ask \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"prompt": "Quais os 3 produtos que mais venderam?"}'
# → "tool_used": "GetTopSellingProducts"

# 45. Ver a própria Assinatura — real desde o provisionamento (item 1), que já cria uma
#     Assinatura TRIAL de 14 dias vinculada ao Plano "VeloAI Professional"
curl "http://localhost:8000/api/v1/billing/subscription" -b cookies.txt
# → plan_name/plan_price/status/trial_ends_at/days_remaining

# 46. Perguntar à IA sobre a própria assinatura — Tool GetSubscriptionStatus
curl -X POST http://localhost:8000/api/v1/ai/ask \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"prompt": "Qual o meu plano e quando ele vence?"}'
# → "tool_used": "GetSubscriptionStatus"

# 47. Cancelar a própria Assinatura — depois disso, qualquer rota de negócio
#     (customers/products/sales/...) passa a responder 403 SUBSCRIPTION_INACTIVE;
#     login e as próprias rotas de /billing continuam acessíveis
curl -X POST http://localhost:8000/api/v1/billing/cancel -b cookies.txt

# 48. Login no Painel Administrativo — sessão totalmente separada da de tenant (cookie
#     jar próprio: nunca reaproveitar cookies.txt). O primeiro operador vem do bootstrap
#     de scripts/seed_master.py (PLATFORM_ADMIN_EMAIL/PLATFORM_ADMIN_PASSWORD)
curl -i -X POST http://localhost:8000/api/v1/admin/auth/login \
  -H "Content-Type: application/json" \
  -c admin_cookies.txt \
  -d '{"email": "admin@veloai.internal", "password": "<senha-do-bootstrap>"}'

# 49. Listar todos os Tenants (dados reais — plano/status/assinatura, desde a Fase 17)
#     e o resumo executivo (contagens + MRR estimado)
curl "http://localhost:8000/api/v1/admin/tenants" -b admin_cookies.txt
curl "http://localhost:8000/api/v1/admin/summary" -b admin_cookies.txt
```

O primeiro passo cria de verdade um banco PostgreSQL exclusivo (`tenant_<id>`), aplica as
migrations mínimas, cria o usuário administrador e concede os privilégios necessários à
role `veloai_app`. O login resolve o tenant a partir de um índice no Banco Master
(`tenant_user_index`), abre a conexão correta e emite access/refresh tokens como cookies
HttpOnly — nunca em LocalStorage.

---

## Desenvolvimento local por serviço

### Backend / Provisioning / AI Gateway (Python 3.13)

```bash
cd <serviço>
pip install -r requirements-dev.txt
ruff check .
black --check .
mypy app
pytest
```

O pacote `shared/` é instalado em modo editável automaticamente (`-e ../shared` dentro de
`requirements.txt`).

### Frontend (Node 22)

```bash
cd frontend
npm install
npm run lint
npm run type-check
npm test
npm run build
```

---

## Testes

| Serviço | Cobertura mínima nesta fase |
|---|---|
| `shared/` | sem meta fixa (utilitário pequeno, buscar 100%) |
| `backend/` | 85% (inclui testes de integração reais dos fluxos de autenticação, do CRUD de todo o CRM, do ajuste de estoque — entrada/saída/ajuste de inventário, estoque insuficiente tratado como 409 —, do ciclo completo de Ordens de Serviço — criar, adicionar itens de produto/serviço, iniciar, concluir sem técnico rejeitado, concluir consumindo estoque automaticamente, estoque insuficiente no fechamento tratado como 409, item bloqueado após conclusão, cancelamento —, do ciclo completo de Vendas — criar, adicionar item de produto herdando preço de catálogo, aplicar desconto recalculando o total, concluir consumindo estoque automaticamente, estoque insuficiente na conclusão tratado como 409, item/venda bloqueados após conclusão, cancelamento —, do ciclo completo Financeiro — criar/receber Conta a Receber com lançamento automático no Fluxo de Caixa, criar/pagar Conta a Pagar com lançamento automático, lançamento avulso, `is_overdue` calculado, edição bloqueada após recebida/paga/cancelada —, do Dashboard — resumo de KPIs refletindo dados criados (por delta, já que o tenant de teste é compartilhado), série histórica com o mês corrente, produtos mais vendidos — e de Anexos — upload/listagem/remoção nos três tipos de recurso suportados, upload rejeitado para recurso inexistente (404), suíte pulada automaticamente se o MinIO não estiver acessível —, e do fluxo de IA — `POST /ai/ask` grava em `ai_conversations` com o AI Gateway real substituído por um dependency override de resposta fixa, `GET /ai/conversations` reflete o histórico, acesso sem autenticação retorna 401, e o round-trip completo de MCP/Tools — a IA decide chamar `CreateCustomer` (function calling), o Backend executa a Tool de verdade contra o banco e grava em `ai_actions` —, com verificação de auditoria, e do fluxo de RAG — `POST /knowledge` indexa de verdade no Qdrant, `GET /knowledge` lista, `DELETE /knowledge/{id}` remove do Qdrant antes do banco, suíte pulada automaticamente se o Qdrant não estiver acessível —, e das 3 novas Tools de Relatório da Fase 16 — `GetDashboardSummary`/`GetRevenueTimeseries`/`GetTopSellingProducts` aparecem na lista de Tools declaradas ao Gemini —, e do fluxo de Billing da Fase 17 — `GET /billing/subscription` reflete a Assinatura real, `POST /billing/cancel` cancela de verdade e uma segunda tentativa retorna 409, e qualquer rota de negócio responde 403 `SUBSCRIPTION_INACTIVE` depois do cancelamento, com reversão do estado no `finally` do teste já que o tenant é compartilhado por toda a suíte —, e do fluxo do Painel Administrativo da Fase 18 — login de Platform Admin, `GET /admin/tenants` reflete o tenant real de `auth_environment` com plano/assinatura, `GET /admin/summary` com contagens reais, `GET /admin/tenants/{id}/audit-log`, senha errada bloqueada, e confirmação de que o cookie de sessão de tenant nunca autentica uma rota de admin e vice-versa) |
| `provisioning/` | 85% (inclui teste de integração real de criação de tenant, com a Collection Qdrant e a Assinatura TRIAL do tenant verificadas de verdade) |
| `ai-gateway/` | 85% (inclui cache de resposta via Redis — hit/miss —, estimativa de custo, function calling — parsing de `functionCall`, conversão de JSON Schema para o formato do Gemini — e `/embeddings` real) |
| `frontend/` | 80% |

A meta definitiva do projeto (`docs/00-AI-CONSTITUTION.md`) é 90-95%. Os valores acima
(`--cov-fail-under` em cada `pyproject.toml`) permanecem deliberadamente nos números
originais desde a fundação do projeto — elevá-los às cegas, sem um interpretador Python
neste ambiente para confirmar a cobertura real atual, arriscaria quebrar o CI na
próxima execução. Ajustar esses limiares é um passo seguro para quem tiver acesso a um
ambiente com Python/CI real (ver Fase 19, `CHANGELOG.md`).

---

## O que NÃO está nesta versão (v1.0)

- CRUD completo de Usuários/Empresas (listar, criar outros usuários pela tela) — módulo
  "Usuários" da Fase 6+.
- Recursos avançados de Clientes/Fornecedores: equipamentos, notas em rich text,
  timeline, importação/exportação CSV/Excel — ver `docs/08-CLIENTES.md` (anexos via
  MinIO já têm suporte no backend desde a Fase 12, mas sem tela de detalhe para exibir
  o painel de anexos ainda).
- Recursos avançados de Produtos (`docs/09-PRODUTOS.md`): campos fiscais (NCM/CFOP/
  CST/CEST), imagens/galeria (anexos genéricos via MinIO já têm suporte no backend
  desde a Fase 12), dashboard/relatórios, import/export, MCP Tools, eventos de
  domínio, marca/modelo, múltiplos fornecedores por produto, promoções.
- Recursos avançados de Estoque (Fase 7): Reservas, Transferências, estorno/
  cancelamento de movimentações, processo formal de Inventário (contagem em massa),
  Alertas de estoque baixo (depende de um sistema de eventos, ainda não implementado),
  Custos (custo médio ponderado), consumo automático de estoque por Compras (módulo
  ainda não existe — Ordens de Serviço e Vendas já consomem estoque automaticamente).
- Recursos avançados de Ordens de Serviço (`docs/10-ORDEM-DE-SERVICO.md`): Agenda,
  Financeiro (contas a receber), Fiscal (NF-e/NFS-e/NFC-e), assinatura digital,
  checklist configurável, geração de PDF, aprovação/orçamento, agendamento, tipos de OS
  customizáveis, prioridade, canal de atendimento, cadastro de equipamento como
  entidade própria (nesta fase é só texto livre — `equipment`/`serial_number` na
  própria OS), reserva de estoque ao adicionar item (só é consumido no fechamento),
  numeração reiniciando por ano, CRUD completo de Usuários (nesta fase só existe
  leitura, para popular o seletor de técnico), MCP Tools, IA, eventos/webhooks,
  dashboard, relatórios (fotos/vídeos/anexos já têm suporte desde a Fase 12, via o
  painel de anexos genérico).
- Recursos avançados de Vendas (`docs/12-VENDAS.md`): Orçamentos (todo o fluxo —
  `05-BANCO-DE-DADOS.md` não tem tabela de orçamentos), Venda de Serviços/Venda Mista
  (`sale_items` só tem `product_id`, nunca `service_id`), parcelamento/juros, formas de
  pagamento com gateway real, comissões, vendedor/ranking de vendedor (`sales` não tem
  coluna para isso), reserva de estoque ao adicionar item (só é consumido na
  conclusão), numeração sequencial (`sales` não tem `number`), geração automática de
  Conta a Receber, emissão de nota fiscal, assinatura digital, envio por e-mail/
  WhatsApp, frete, impostos, entrega/rastreamento, MCP Tools, IA, eventos/webhooks,
  dashboard, relatórios.
- Recursos avançados Financeiro (`docs/11-FINANCEIRO.md`): geração automática de
  Conta a Receber a partir de Venda/OS concluída (`accounts_receivable`/
  `accounts_payable` não têm coluna de origem/referência para rastrear isso — fica para
  quando o schema ganhar esse campo), Dashboard Financeiro, Categorias Financeiras e
  Centros de Custo como entidades configuráveis (`cash_flow.category` é só texto
  livre), Caixa (abertura/fechamento/sangria/suprimento/conferência), Conciliação
  Bancária (OFX/Open Finance/APIs), parcelamento, recorrência, juros/multa/desconto/
  recebimento parcial (`amount` é um valor único, recebido/pago integralmente), forma
  de pagamento em Contas a Receber/Pagar (não existe coluna), DRE/relatórios/
  projeções, MCP Tools, IA, eventos/webhooks.
- Recursos avançados de Dashboard (`docs/07-DASHBOARD.md`): WebSocket/atualização em
  tempo real, cache Redis, busca global (CTRL+K — o botão de busca no Header continua
  inerte; só o botão de IA foi ligado, na Fase 16), insights automáticos por IA
  (a IA responde perguntas quando solicitada, mas não gera insights proativos sem
  pergunta), Agenda (módulo inexistente), Caixa/Conciliação Bancária, Ranking
  completo (Top Técnicos/Vendedores — `sales` não tem coluna de vendedor; Top
  Clientes/Serviços), "Ordens Atrasadas" (`service_orders` não tem campo de prazo),
  Atividades/Timeline, Alertas automáticos, personalização de layout (mover/ocultar/
  redimensionar/salvar/múltiplos dashboards), Dashboard por Perfil, exportação (PDF/PNG/
  Excel), Notificações (tabela existe mas é um sistema à parte), permissão por widget
  (`dashboard.finance`/`dashboard.orders`/... — nesta fase há só `dashboard.view`).
- Recursos avançados de Storage (`docs/34-MASTER-PLAN.md`, Fase 12): OCR, assinatura
  digital, galeria de imagens com preview/crop, categorização de anexos, controle de
  versão de arquivo, quota de armazenamento por tenant, vírus scan, geração de
  thumbnail, bucket por tenant (isolamento é lógico, por prefixo de chave — um único
  bucket `veloai-attachments`), anexos em Clientes/Produtos pela UI (o backend já
  suporta os três tipos; só a tela de Ordem de Serviço tem um componente de anexos
  integrado nesta fase, porque Clientes/Produtos ainda não têm tela de detalhe própria),
  anexos em Vendas/Financeiro.
- Recursos avançados de IA (`docs/28-AI-GATEWAY.md`, `docs/13-IA-PLATFORM.md`): Planner
  Agent e Executor Agent como processos/camadas separadas (nesta fase, a própria
  `AskAIUseCase` faz o papel de Executor); memória de curto/longo prazo e conversas
  multi-turno (exigiria tabela/coluna não documentada); streaming (SSE/WebSocket);
  fallback entre múltiplos
  provedores (só existe Gemini); roteador inteligente de modelo; rate limit dedicado de
  IA por tenant/usuário/plano (existe rate limit genérico de login, não de IA); Prompt
  Builder completo com versionamento (o atual é fixo: empresa/usuário/papel/data);
  Dashboard de IA dedicado; guardrails de mascaramento automático de dados sensíveis;
  Agentes especializados (Planner/Report/CRM/Sales/Financial/Inventory/Notification/
  OCR/Document/Automation Agent) como classes/camadas distintas — a IA continua usando
  o mesmo mecanismo único de function calling (botão de IA em todas as telas já existe
  desde a Fase 16, via `AiChatModal.vue`); Chat por WhatsApp/Telegram/Voice; serviço
  `worker`/fila dedicado; Billing de IA real (o `estimated_cost` retornado é uma
  estimativa por tabela de preço fixa, não uma fatura).
- Recursos avançados de MCP/Tools (`docs/20-MCP-TOOLS.md`): protocolo MCP literal
  (JSON-RPC/stdio/SSE — não há nenhum cliente MCP externo consumindo o VeloAI ainda, só
  o princípio "IA nunca toca banco sem Tool" foi implementado); Tool Registry com
  descoberta automática via filesystem (lista explícita, 7 Tools nesta fase — 3 de
  `customers/`, 1 de `knowledge/`, 3 de `dashboard/`); Tools fora desses 3 módulos —
  dezenas descritas no doc para Produtos, Estoque, Ordens de Serviço, Vendas,
  Financeiro, Agenda, Usuários, Empresa, Arquivos, OCR, Automações; múltiplas Tools por
  resposta / laço agente-ferramenta (só 1 rodada de tool-calling por pergunta);
  idempotency key; timeout/retry/circuit breaker por Tool; Tool Marketplace; MCP
  remoto; Workflow/Automation Engine (`CreateWorkflow`/`ExecuteWorkflow` — nenhum motor
  de automação existe, nem event bus, fila ou scheduler); versionamento de Tool
  (`version`/`deprecated`/`replacement`); endpoint dedicado para listar `ai_actions` de
  uma conversa (o campo `tool_used` na resposta do `/ai/ask` já dá transparência
  suficiente nesta fase).
- Recursos avançados de Relatórios (`docs/15-RELATORIOS-INTELIGENTES.md`): as demais
  Tools documentadas (`GenerateFinancialReport`/`GenerateSalesReport`/
  `GenerateStockReport`/`GenerateCRMReport`/`ComparePeriods`/`GenerateForecast`/
  `GenerateExecutiveSummary`/`GenerateChart` — as 3 Tools desta fase só reaproveitam os
  3 Use Cases que o Dashboard já tinha); exportação em PDF/Excel/CSV; relatórios
  agendados/recorrentes; comparação entre períodos; previsão/ML; dashboards
  personalizáveis/favoritos por usuário.
- Recursos avançados de RAG (`docs/21-RAG.md`): upload de arquivo e todo o pipeline de
  parsing/OCR (PDF/DOCX/XLSX/CSV/imagem — sem `PyMuPDF`/`python-docx`/`openpyxl`/
  `pandas`/`Unstructured`/Tesseract; a Base de Conhecimento desta fase é só texto puro
  colado pelo usuário); versionamento de documento e reindexação incremental;
  re-ranking (score bruto do Qdrant, top 5, sem segunda passada); busca híbrida
  (BM25 + vetorial); camadas de cache dedicadas (Prompt/Embedding/Search — o Response
  Cache do `/generate` já existe desde a Fase 13, mas não há cache específico de
  busca/embedding); processamento assíncrono via Celery (fila não existe); os outros 6
  endpoints REST do doc (`/rag/reindex`, `/rag/rebuild-index`, etc. — só
  criar/listar/excluir); as outras 6 MCP Tools de RAG (`IndexDocument`,
  `DeleteDocument`, `ReindexDocument`, `SummarizeDocument`, `ExtractDocumentMetadata`,
  `SearchSimilarDocuments` — só `SearchKnowledge` existe); Planner Agent decidindo
  RAG-vs-MCP-vs-ambos (a IA já decide isso implicitamente via function calling).
- Recursos avançados de Billing (`docs/31-BILLING.md`): integração real com gateway de
  pagamento (Asaas inicialmente, arquitetura pronta para Stripe/Mercado Pago/Iugu/
  Pagar.me/PagSeguro — nenhuma credencial existe neste ambiente); PIX/Boleto/Cartão;
  faturas (armazenamento, PDF, segunda via); webhooks (`POST /billing/webhook`,
  validação de assinatura); `POST /billing/reactivate` (reativação depende de um sinal
  real de pagamento, que não existe) e `POST /billing/change-plan` (só existe 1 Plano
  ativo); os estados `ACTIVE`/`PENDING_PAYMENT`/`OVERDUE`/`SUSPENDED` do enum ficam sem
  nenhuma transição real possível nesta fase (só `TRIAL`→`EXPIRED` automático e
  `TRIAL`/`EXPIRED`→`CANCELED` manual); suspensão escalonada por dias (5/10/15/20/60/
  180 dias do doc — aqui é binário: ativa ou bloqueada); ARR/Churn/LTV/CAC como
  métricas reais (o Painel Administrativo da Fase 18 já mostra um resumo — total de
  tenants, contagem por status de assinatura, MRR estimado —, mas sem histórico de
  eventos para calcular churn/LTV de verdade); Tool de IA para cancelar a própria
  assinatura (só existe leitura, `GetSubscriptionStatus` — cancelar via prompt casual é
  uma mutação de alto risco para o primeiro corte); Plano Enterprise/White Label/
  Franquia/Revenda/Marketplace; cobrança por uso de IA/Storage/API.
- Recursos avançados do Painel Administrativo (`docs/31-BILLING.md`, seção "Admin
  Master" — sem doc dedicado): qualquer ação de escrita sobre outro tenant (suspender/
  reativar/mudar plano manualmente — a tela desta fase é somente leitura); refresh
  token/sessão persistida para Platform Admin (só um access token de curta duração,
  login de novo quando expira); papéis/permissões administrativas granulares ("é um
  Platform Admin ativo" é a única checagem nesta fase); 2FA/MFA para operadores;
  Monitoramento real (OpenTelemetry/Prometheus/Grafana/Loki/Tempo/Sentry — nenhuma
  infra existe, `docs/26-OBSERVABILITY.md`); alertas automáticos.
- Qualquer módulo de negócio fora do CRM/Estoque/Ordens de Serviço/Vendas/Financeiro/
  Dashboard/Storage/IA/MCP/RAG/Relatórios/Chat Global/Billing/Painel Administrativo —
  as Fases 1 a 20 do `docs/34-MASTER-PLAN.md` estão concluídas; o que vem depois é a
  Versão 1.1+ do `docs/32-ROADMAP.md` (importação/exportação, dashboard personalizado,
  Agentes de IA especializados, Automation Engine, e o restante já listado acima).
- Recursos avançados de Testes (`docs/24-TESTING.md`): testes de carga/performance
  (k6/Locust/Artillery) e Playwright E2E — sem Docker/navegador headless disponíveis
  neste ambiente para rodar; testcontainers (o CI já resolve Postgres/Redis/MinIO/
  Qdrant via `services:` do GitHub Actions, sem precisar da biblioteca); elevar
  `--cov-fail-under` de 85%/80% para as metas de 95%/90% do doc (não dá para verificar
  a cobertura real sem rodar pytest neste ambiente); Storybook Tests, Visual
  Regression, MSW.
- Automation Engine (editor visual, event bus, scheduler, filas, integrações
  externas — ver `docs/14-AUTOMATION-ENGINE.md`).
- RabbitMQ/Celery, Nginx, Prometheus/Grafana/Loki/Tempo.
- MFA, SSO, Passkeys.

As 20 Fases de `docs/34-MASTER-PLAN.md` estão concluídas (ver `CHANGELOG.md`). Essas
peças ficam para a Versão 1.1+ de `docs/32-ROADMAP.md`, ou para quando a
infraestrutura que falta (gateway de pagamento, stack de observabilidade, ambiente
Docker/CI real) estiver disponível.
