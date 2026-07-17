# VeloAI

> AI Business OS — plataforma SaaS Multi-Tenant para pequenas e médias empresas, com
> Inteligência Artificial como interface principal.

**Release `1.0.0`** — Fases 1 a 20 do [`docs/34-MASTER-PLAN.md`](docs/34-MASTER-PLAN.md)
concluídas. Para o resumo fase a fase (o que foi construído e o que ficou de fora, e
por quê), ver o [`CHANGELOG.md`](CHANGELOG.md).

Este repositório cobre a fundação + autenticação + CRM completo (Clientes,
Fornecedores, Categorias, Produtos e Serviços) + Estoque + Ordens de Serviço + Vendas +
Financeiro + Dashboard + Storage (anexos) + IA (AI Gateway) + MCP/Tools + RAG +
Relatórios via IA + Chat Global + Billing (Trial/Assinatura) + Painel Administrativo,
com CI real cobrindo Anexos/RAG/Provisioning e uma auditoria de segurança já
realizada. Infraestrutura, provisionamento de tenants, autenticação, auditoria e
logging estruturado funcionam de ponta a ponta.

Toda a documentação oficial do produto está em [`docs/`](docs), começando por
[`docs/00-AI-CONSTITUTION.md`](docs/00-AI-CONSTITUTION.md) e
[`docs/34-MASTER-PLAN.md`](docs/34-MASTER-PLAN.md).

---

## Arquitetura

```
veloai/
  shared/             # Pacote Python compartilhado: response envelope, exceptions,
                       # logging, segurança (Argon2, UUIDv7, JWT) e os modelos
                       # SQLAlchemy do Banco Master e do template de tenant.
  backend/             # FastAPI — API principal.
  provisioning/        # FastAPI — único serviço com privilégios administrativos de PostgreSQL.
  ai-gateway/          # FastAPI — único ponto de comunicação com provedores de LLM.
  frontend/            # Vue 3 + TypeScript + Vite + Tailwind + PrimeVue.
  infra/               # postgres/init (cria a role `veloai_app` no primeiro boot), scripts.
  .github/workflows/    # CI (lint, testes, build Docker, segurança).
  docker-compose.yml
```

Cada serviço Python segue Clean Architecture (`api/ → use_cases/ → services/ →
repositories/ → models/`), conforme `docs/00-AI-CONSTITUTION.md` e
`docs/16-BACKEND-ARCHITECTURE.md`. Módulos de negócio nunca acessam o repository de
outro módulo diretamente.

### Módulos do backend

| Módulo | Fase | Descrição |
|---|---|---|
| `auth/` | 1-3 | Login/refresh/logout, troca de senha, RBAC (`require_permission`), auditoria e logging estruturado — reutilizados por todo módulo de negócio. |
| `customers/`, `suppliers/`, `categories/`, `products/`, `services/` | 6 | CRM completo. `suppliers/` é cópia estrutural de `customers/`. O histórico de movimentações de estoque mora dentro de `products/` (não é módulo próprio) para atualizar `products.stock` e gravar o movimento na mesma transação. |
| `users/` | 8 | Somente leitura (id/nome/email), usado para o seletor de técnico responsável. |
| `service_orders/` | 8 | Primeiro fluxo operacional ponta-a-ponta: cria a OS, adiciona itens de produto/serviço; `close` baixa o estoque automaticamente na mesma transação. |
| `sales/` | 9 | Cria a Venda, adiciona itens de produto, aplica desconto; `complete` baixa estoque do mesmo jeito que `service_orders/`. Sem exclusão — só cancelamento. |
| `finance/` | 10 | Contas a Receber, Contas a Pagar e Fluxo de Caixa; `receive`/`pay` geram uma entrada de caixa automaticamente na mesma transação. Sem exclusão — só estorno. |
| `dashboard/` | 11 | Sem tabela própria — agrega em tempo real os dados dos módulos anteriores em KPIs e dois gráficos (amCharts 5). |
| `attachments/` | 12 | Conecta o MinIO. Tabela genérica (`resource_type`+`resource_id`) para Clientes, Produtos e Ordens de Serviço; só guarda metadados, nunca o arquivo em si. |
| `ai/` | 13 | `POST /ai/ask` monta o contexto de empresa/usuário e delega ao AI Gateway (`app/core/ai_gateway_client.py`) — o Backend nunca fala com uma LLM diretamente. Grava cada chamada em `ai_conversations`. |
| MCP/Tools | 14 | `tool_registry.py` filtra as Tools pelas permissões reais do usuário e as declara ao Gemini (function calling); a IA nunca altera dados sem passar por uma Tool auditada em `ai_actions`. |
| `knowledge/` (RAG) | 15 | Base de Conhecimento em texto puro. `POST /knowledge` indexa (chunking + embeddings reais do Gemini) e faz upsert no Qdrant — uma Collection por tenant. `SearchKnowledge` deixa a IA buscar semanticamente. |
| Relatórios + Chat Global | 16 | 3 Tools em `dashboard/mcp_tools/` reaproveitando os Use Cases já existentes do Dashboard, e o botão "✨ Perguntar para IA" do Header ligado a um `AiChatModal.vue` flutuante disponível em qualquer tela. |
| `billing/` | 17 | Primeiro módulo do Backend que opera no Banco Master, não no banco do tenant. `require_active_subscription` bloqueia com 403 `SUBSCRIPTION_INACTIVE` qualquer rota de negócio quando a assinatura expira/é cancelada. |
| `admin/` | 18 | Painel usado pela equipe da VeloAI, nunca por um tenant — login totalmente separado (`PlatformAdmin`, cookie/secret próprios). Somente leitura: lista de Tenants/Assinaturas e Log de Auditoria de cada um. |

### Outros serviços

- **`provisioning/`** — cria bancos de tenant de verdade e concede os privilégios
  mínimos à role `veloai_app`; cria a Collection Qdrant e a Assinatura TRIAL (14 dias)
  de cada tenant. `scripts/seed_master.py` roda a cada subida do container e garante o
  Plano ativo e o primeiro operador do Painel Administrativo.
- **`ai-gateway/`** — cache de resposta via Redis, estimativa de custo por token,
  `/generate` com suporte a function calling (Gemini) e `/embeddings` (`text-embedding-004`).
- **`frontend/`** — sessão via cookies HttpOnly (nunca LocalStorage) com refresh
  automático; assistente de IA global (`AiChatModal.vue`); Painel Administrativo com
  layout e guard de rota isolados (`stores/adminAuth.ts`, nunca `stores/auth.ts`).

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
# → retorna a senha temporária do admin (force_password_change: true)

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

# 5. Criar um Cliente
curl -X POST http://localhost:8000/api/v1/customers \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"type": "PF", "name": "João Silva", "document": "123.456.789-01", "email": "joao@cliente.com"}'

# 6. Listar/buscar clientes (paginado)
curl "http://localhost:8000/api/v1/customers?search=joao&page=1" -b cookies.txt

# 7. Criar um Fornecedor
curl -X POST http://localhost:8000/api/v1/suppliers \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"type": "PJ", "name": "Tech Distribuidora LTDA", "document": "12.345.678/0001-99"}'

# 8. Listar/buscar fornecedores (paginado)
curl "http://localhost:8000/api/v1/suppliers?search=tech&page=1" -b cookies.txt

# 9. Criar uma Categoria
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
# → a resposta inclui "margin"/"margin_percentage", calculados na hora

# 11. Listar produtos filtrando por categoria
curl "http://localhost:8000/api/v1/products?category_id=<id-da-categoria>" -b cookies.txt

# 12. Criar um Serviço vinculado à categoria
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

# 14. Registrar uma entrada de estoque no produto criado acima
curl -X POST http://localhost:8000/api/v1/products/<id-do-produto>/stock-movements \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"movement": "in", "quantity": 10, "reason": "Compra de reposição"}'
# → GET /products/{id} já reflete o novo "stock" (mesma transação)

# 15. Consultar o histórico de movimentações do produto (mais recente primeiro)
curl "http://localhost:8000/api/v1/products/<id-do-produto>/stock-movements" -b cookies.txt

# 16. Criar uma Ordem de Serviço (number é gerado automaticamente: OS-<ano>-<sequência>)
curl -X POST http://localhost:8000/api/v1/service-orders \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "customer_id": "<id-do-cliente>",
    "equipment": "Notebook Dell",
    "problem": "Não liga"
  }'

# 17. Adicionar um item de produto à OS (product_id OU service_id, nunca os dois)
curl -X POST http://localhost:8000/api/v1/service-orders/<id-da-os>/items \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"product_id": "<id-do-produto>", "quantity": 1}'

# 18. Consultar a OS (itens embutidos e total recalculado)
curl http://localhost:8000/api/v1/service-orders/<id-da-os> -b cookies.txt

# 19. Iniciar o atendimento (open → in_progress)
curl -X POST http://localhost:8000/api/v1/service-orders/<id-da-os>/start -b cookies.txt

# 20. Concluir a OS informando o técnico responsável — baixa o estoque de cada item
#     de produto automaticamente na mesma transação
curl -X POST http://localhost:8000/api/v1/service-orders/<id-da-os>/close \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"technician_id": "<id-do-tecnico>", "solution": "Placa-mãe trocada"}'

# 21. Criar uma Venda
curl -X POST http://localhost:8000/api/v1/sales \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"customer_id": "<id-do-cliente>", "payment_method": "pix"}'

# 22. Adicionar um item de produto à Venda
curl -X POST http://localhost:8000/api/v1/sales/<id-da-venda>/items \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"product_id": "<id-do-produto>", "quantity": 2}'

# 23. Aplicar um desconto (total recalculado: soma dos itens - desconto)
curl -X PATCH http://localhost:8000/api/v1/sales/<id-da-venda> \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"discount": "80.00"}'

# 24. Concluir a Venda — baixa o estoque automaticamente na mesma transação
curl -X POST http://localhost:8000/api/v1/sales/<id-da-venda>/complete -b cookies.txt

# 25. Criar uma Conta a Receber
curl -X POST http://localhost:8000/api/v1/accounts-receivable \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"customer_id": "<id-do-cliente>", "due_date": "2026-08-15", "amount": "980.00"}'
# → a resposta inclui "is_overdue", calculado na hora

# 26. Receber a Conta a Receber — grava "payment_date" e insere uma entrada de
#     entrada ("in") no Fluxo de Caixa, na mesma transação
curl -X POST http://localhost:8000/api/v1/accounts-receivable/<id-da-conta>/receive \
  -b cookies.txt

# 27. Criar e pagar uma Conta a Pagar — mesmo mecanismo, saída ("out") no Fluxo de Caixa
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

# 30. Resumo do Dashboard — KPIs agregados, calculados na hora
curl "http://localhost:8000/api/v1/dashboard/summary" -b cookies.txt
# → inclui "revenue_change_percentage" e "average_ticket"

# 31. Série histórica de receita (últimos 6 meses) — gráfico de linha do Dashboard
curl "http://localhost:8000/api/v1/dashboard/revenue-timeseries" -b cookies.txt

# 32. Produtos mais vendidos — gráfico de barras do Dashboard
curl "http://localhost:8000/api/v1/dashboard/top-products?limit=5" -b cookies.txt

# 33. Anexar um arquivo à Ordem de Serviço (multipart/form-data; resource_type também
#     aceita "customer"/"product")
curl -X POST http://localhost:8000/api/v1/attachments \
  -b cookies.txt \
  -F "resource_type=service_order" \
  -F "resource_id=<id-da-os>" \
  -F "file=@/caminho/para/foto.jpg"
# → a resposta inclui "url" (link pré-assinado do MinIO, válido por 1 hora)

# 34. Listar os anexos da OS
curl "http://localhost:8000/api/v1/attachments?resource_type=service_order&resource_id=<id-da-os>" \
  -b cookies.txt

# 35. Remover um anexo (apaga do MinIO e do banco)
curl -X DELETE http://localhost:8000/api/v1/attachments/<id-do-anexo> -b cookies.txt

# 36. Perguntar algo ao assistente de IA
curl -X POST http://localhost:8000/api/v1/ai/ask \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"prompt": "Quanto vendi este mês?"}'
# → a resposta inclui "cached" e "estimated_cost" (estimativa, não fatura real)

# 37. Consultar o histórico de uso de IA do tenant (mais recente primeiro)
curl "http://localhost:8000/api/v1/ai/conversations" -b cookies.txt

# 38. Pedir para a IA executar uma ação de verdade — o Gemini decide chamar a Tool
#     CreateCustomer (function calling real) e o resultado é auditado em ai_actions
curl -X POST http://localhost:8000/api/v1/ai/ask \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"prompt": "Cadastre um cliente chamado Ana Costa, CPF 321.301.765-92."}'
# → "tool_used": "CreateCustomer" quando uma Tool foi executada (null em conversas de texto)

# 39. Cadastrar um item na Base de Conhecimento — indexa de verdade (chunking +
#     embeddings reais + upsert no Qdrant, tudo na mesma requisição)
curl -X POST http://localhost:8000/api/v1/knowledge \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "title": "Política de Garantia",
    "content": "Todo produto tem garantia de 90 dias contra defeitos de fabricação."
  }'

# 40. Listar a Base de Conhecimento (paginado)
curl "http://localhost:8000/api/v1/knowledge" -b cookies.txt

# 41. Perguntar algo que só a Base de Conhecimento sabe responder
curl -X POST http://localhost:8000/api/v1/ai/ask \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"prompt": "Qual é a política de garantia da minha empresa?"}'
# → "tool_used": "SearchKnowledge"

# 42. Remover um item da Base de Conhecimento (apaga do Qdrant e do banco)
curl -X DELETE http://localhost:8000/api/v1/knowledge/<id-do-documento> -b cookies.txt

# 43. Perguntar algo analítico ao assistente
curl -X POST http://localhost:8000/api/v1/ai/ask \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"prompt": "Qual foi meu faturamento este mês e qual a variação em relação ao mês passado?"}'
# → "tool_used": "GetDashboardSummary"

# 44. Perguntar pelos produtos mais vendidos
curl -X POST http://localhost:8000/api/v1/ai/ask \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"prompt": "Quais os 3 produtos que mais venderam?"}'
# → "tool_used": "GetTopSellingProducts"

# 45. Ver a própria Assinatura (Trial de 14 dias criada no provisionamento, item 1)
curl "http://localhost:8000/api/v1/billing/subscription" -b cookies.txt
# → plan_name/plan_price/status/trial_ends_at/days_remaining

# 46. Perguntar à IA sobre a própria assinatura
curl -X POST http://localhost:8000/api/v1/ai/ask \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"prompt": "Qual o meu plano e quando ele vence?"}'
# → "tool_used": "GetSubscriptionStatus"

# 47. Cancelar a própria Assinatura — depois disso, qualquer rota de negócio responde
#     403 SUBSCRIPTION_INACTIVE; login e /billing continuam acessíveis
curl -X POST http://localhost:8000/api/v1/billing/cancel -b cookies.txt

# 48. Login no Painel Administrativo — sessão separada da de tenant (cookie jar
#     próprio). O primeiro operador vem do bootstrap de scripts/seed_master.py
curl -i -X POST http://localhost:8000/api/v1/admin/auth/login \
  -H "Content-Type: application/json" \
  -c admin_cookies.txt \
  -d '{"email": "admin@veloai.internal", "password": "<senha-do-bootstrap>"}'

# 49. Listar todos os Tenants e o resumo executivo (contagens + MRR estimado)
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

| Serviço | Cobertura mínima | Destaques |
|---|---|---|
| `shared/` | sem meta fixa | Utilitário pequeno — buscar 100%. |
| `backend/` | 85% | Testes de integração reais (Postgres/Redis/MinIO/Qdrant) dos fluxos completos de Auth, CRM, Estoque, Ordens de Serviço, Vendas, Financeiro, Dashboard, Anexos, IA/MCP (round-trip de function calling auditado), RAG, Billing e Painel Administrativo — incluindo os casos de borda de cada um (estoque insuficiente → 409, edição bloqueada após conclusão/cancelamento, isolamento entre sessão de tenant e de admin). |
| `provisioning/` | 85% | Criação de tenant, com Collection Qdrant e Assinatura TRIAL verificadas de verdade. |
| `ai-gateway/` | 85% | Cache de resposta via Redis (hit/miss), estimativa de custo, function calling e `/embeddings` reais. |
| `frontend/` | 80% | — |

A meta definitiva do projeto (`docs/00-AI-CONSTITUTION.md`) é 90-95%. Os valores acima
(`--cov-fail-under` em cada `pyproject.toml`) permanecem deliberadamente nos números
originais desde a fundação do projeto — elevá-los às cegas, sem um interpretador Python
neste ambiente para confirmar a cobertura real atual, arriscaria quebrar o CI na
próxima execução (ver Fase 19 do `CHANGELOG.md`).

---

## O que NÃO está nesta versão (v1.0)

- **Usuários** — CRUD completo (listar, criar outros usuários pela tela); nesta versão só há leitura, para o seletor de técnico.
- **Clientes/Fornecedores** (`docs/08-CLIENTES.md`) — equipamentos, notas em rich text, timeline, importação/exportação CSV/Excel. Anexos via MinIO já funcionam no backend, mas sem tela de detalhe para exibi-los.
- **Produtos** (`docs/09-PRODUTOS.md`) — campos fiscais (NCM/CFOP/CST/CEST), imagens/galeria, dashboard/relatórios próprios, import/export, MCP Tools, eventos de domínio, marca/modelo, múltiplos fornecedores, promoções.
- **Estoque** — Reservas, Transferências, estorno de movimentações, Inventário formal, Alertas de estoque baixo (depende de um sistema de eventos), custo médio ponderado, consumo automático por Compras (módulo inexistente).
- **Ordens de Serviço** (`docs/10-ORDEM-DE-SERVICO.md`) — Agenda, Fiscal (NF-e/NFS-e/NFC-e), assinatura digital, checklist configurável, geração de PDF, orçamento/aprovação, tipos de OS customizáveis, cadastro de equipamento como entidade própria (hoje é texto livre), reserva de estoque ao adicionar item, numeração por ano, CRUD completo de Usuários, MCP Tools, eventos/webhooks, dashboard/relatórios próprios.
- **Vendas** (`docs/12-VENDAS.md`) — Orçamentos, Venda de Serviços/Venda Mista (`sale_items` não tem `service_id`), parcelamento/juros, gateway de pagamento real, comissões/ranking de vendedor, reserva de estoque, numeração sequencial, geração automática de Conta a Receber, nota fiscal, frete, MCP Tools, eventos/webhooks.
- **Financeiro** (`docs/11-FINANCEIRO.md`) — geração automática de Conta a Receber a partir de Venda/OS, Dashboard Financeiro, Categorias/Centros de Custo configuráveis, Caixa (abertura/fechamento/sangria), Conciliação Bancária, parcelamento/recorrência, juros/multa/recebimento parcial, DRE/projeções, MCP Tools, eventos/webhooks.
- **Dashboard** (`docs/07-DASHBOARD.md`) — WebSocket/tempo real, cache Redis, busca global (CTRL+K), insights proativos por IA, Agenda, Caixa, ranking completo (vendedor/técnico), "Ordens Atrasadas", timeline, alertas automáticos, personalização de layout, exportação (PDF/PNG/Excel), permissão por widget.
- **Storage** — OCR, assinatura digital, galeria com preview/crop, versionamento de arquivo, quota por tenant, vírus scan, thumbnails, bucket dedicado por tenant (isolamento hoje é por prefixo de chave), anexos em Vendas/Financeiro, anexos em Clientes/Produtos pela UI (o backend já suporta; só a tela de OS tem o componente integrado).
- **IA** (`docs/28-AI-GATEWAY.md`, `docs/13-IA-PLATFORM.md`) — Planner/Executor Agent como camadas separadas, memória multi-turno, streaming (SSE/WebSocket), múltiplos provedores de LLM, roteador de modelo, rate limit dedicado de IA, Prompt Builder versionado, Dashboard de IA, guardrails de mascaramento, Agentes especializados por domínio, chat por WhatsApp/Telegram/Voice, fila/worker dedicado, billing de IA real (o custo retornado é uma estimativa).
- **MCP/Tools** (`docs/20-MCP-TOOLS.md`) — protocolo MCP literal (JSON-RPC/stdio/SSE — nenhum cliente MCP externo consome o VeloAI ainda), descoberta automática de Tools via filesystem (lista explícita, 7 Tools nesta fase), Tools fora de Clientes/Conhecimento/Dashboard, múltiplas Tools por resposta, idempotency key, timeout/retry/circuit breaker, Tool Marketplace, Workflow/Automation Engine, versionamento de Tool.
- **Relatórios** (`docs/15-RELATORIOS-INTELIGENTES.md`) — as demais Tools documentadas (`GenerateFinancialReport`, `ComparePeriods`, `GenerateForecast`, etc.), exportação PDF/Excel/CSV, relatórios agendados, previsão/ML, dashboards personalizáveis.
- **RAG** (`docs/21-RAG.md`) — upload de arquivo e parsing/OCR (PDF/DOCX/XLSX/imagem — hoje é só texto puro colado), versionamento/reindexação incremental, re-ranking, busca híbrida (BM25 + vetorial), cache dedicado de busca/embedding, processamento assíncrono via fila, os demais endpoints/Tools do doc (só criar/listar/excluir e `SearchKnowledge` existem).
- **Billing** (`docs/31-BILLING.md`) — gateway de pagamento real (nenhuma credencial existe neste ambiente), PIX/Boleto/Cartão, faturas, webhooks, reativação/troca de plano (só existe 1 Plano ativo), suspensão escalonada por dias, ARR/Churn/LTV/CAC reais, Tool de IA para cancelar a própria assinatura (só existe leitura), planos Enterprise/White Label.
- **Painel Administrativo** — qualquer ação de escrita sobre outro tenant, refresh token/sessão persistida para operadores, papéis/permissões administrativas granulares, 2FA/MFA, Monitoramento real (Prometheus/Grafana/Loki/Tempo/Sentry — infra inexistente).
- **Testes** (`docs/24-TESTING.md`) — testes de carga/performance (k6/Locust) e Playwright E2E (sem Docker/navegador headless neste ambiente), elevar `--cov-fail-under` para as metas de 95%/90% do doc, Storybook Tests, Visual Regression, MSW.
- **Automation Engine** (editor visual, event bus, scheduler, filas, integrações externas — `docs/14-AUTOMATION-ENGINE.md`).
- RabbitMQ/Celery, Nginx, Prometheus/Grafana/Loki/Tempo, MFA/SSO/Passkeys.
- Qualquer módulo fora do CRM/Estoque/OS/Vendas/Financeiro/Dashboard/Storage/IA/MCP/RAG/Relatórios/Chat Global/Billing/Admin — fica para a Versão 1.1+ do `docs/32-ROADMAP.md`.

As 20 Fases de `docs/34-MASTER-PLAN.md` estão concluídas (ver `CHANGELOG.md`). Essas
peças ficam para a Versão 1.1+ de `docs/32-ROADMAP.md`, ou para quando a
infraestrutura que falta (gateway de pagamento, stack de observabilidade, ambiente
Docker/CI real) estiver disponível.
