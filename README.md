# VeloAI

> AI Business OS — plataforma SaaS Multi-Tenant para pequenas e médias empresas, com
> Inteligência Artificial como interface principal.

Este repositório cobre a **fundação + autenticação + CRM completo (Clientes,
Fornecedores, Categorias, Produtos e Serviços) + Estoque + Ordens de Serviço + Vendas +
Financeiro + Dashboard + Storage (anexos) + IA (AI Gateway)** do projeto (ver
`docs/34-MASTER-PLAN.md`, Fases 1 a 13 — Fases 6 a 13 concluídas). Infraestrutura,
provisionamento de tenants, autenticação, auditoria e logging estruturado já funcionam
de ponta a ponta, de
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
AI Gateway ganhou cache de resposta via Redis e estimativa de custo por token.

Toda a documentação oficial do produto está em [`docs/`](docs), começando por
[`docs/00-AI-CONSTITUTION.md`](docs/00-AI-CONSTITUTION.md) e
[`docs/34-MASTER-PLAN.md`](docs/34-MASTER-PLAN.md).

---

## Arquitetura desta fase

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
                    # /ai/conversations` lista o histórico paginado. `ai_actions`
                    # (Tools via MCP) fica para a Fase 14. Autentica no Postgres
                    # exclusivamente como a role `veloai_app`.
  provisioning/     # FastAPI — único serviço com privilégios administrativos de
                    # PostgreSQL. Cria bancos de tenant de verdade e concede os
                    # privilégios mínimos à role `veloai_app`.
  ai-gateway/       # FastAPI — único ponto de comunicação com provedores de LLM
                    # (Gemini implementado; arquitetura pronta para outros). Cache de
                    # resposta via Redis (Response Cache) e estimativa de custo por
                    # token (`GeminiProvider.estimate_cost`) desde a Fase 13.
  frontend/         # Vue 3 + TypeScript + Vite + Tailwind + PrimeVue. Sessão via
                    # cookies HttpOnly (nunca LocalStorage), com refresh automático.
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
| `backend/` | 85% (inclui testes de integração reais dos fluxos de autenticação, do CRUD de todo o CRM, do ajuste de estoque — entrada/saída/ajuste de inventário, estoque insuficiente tratado como 409 —, do ciclo completo de Ordens de Serviço — criar, adicionar itens de produto/serviço, iniciar, concluir sem técnico rejeitado, concluir consumindo estoque automaticamente, estoque insuficiente no fechamento tratado como 409, item bloqueado após conclusão, cancelamento —, do ciclo completo de Vendas — criar, adicionar item de produto herdando preço de catálogo, aplicar desconto recalculando o total, concluir consumindo estoque automaticamente, estoque insuficiente na conclusão tratado como 409, item/venda bloqueados após conclusão, cancelamento —, do ciclo completo Financeiro — criar/receber Conta a Receber com lançamento automático no Fluxo de Caixa, criar/pagar Conta a Pagar com lançamento automático, lançamento avulso, `is_overdue` calculado, edição bloqueada após recebida/paga/cancelada —, do Dashboard — resumo de KPIs refletindo dados criados (por delta, já que o tenant de teste é compartilhado), série histórica com o mês corrente, produtos mais vendidos — e de Anexos — upload/listagem/remoção nos três tipos de recurso suportados, upload rejeitado para recurso inexistente (404), suíte pulada automaticamente se o MinIO não estiver acessível —, e do fluxo de IA — `POST /ai/ask` grava em `ai_conversations` com o AI Gateway real substituído por um dependency override de resposta fixa, `GET /ai/conversations` reflete o histórico, acesso sem autenticação retorna 401 —, com verificação de auditoria) |
| `provisioning/` | 85% (inclui teste de integração real de criação de tenant) |
| `ai-gateway/` | 85% (inclui cache de resposta via Redis — hit/miss — e estimativa de custo) |
| `frontend/` | 80% |

A meta definitiva do projeto (`docs/00-AI-CONSTITUTION.md`) é 90-95%; os valores acima
são deliberadamente menores nesta fase por ainda não existir código de negócio — serão
elevados à medida que os módulos forem implementados.

---

## O que NÃO está nesta fase

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
  Alertas de estoque baixo (depende de sistema de eventos — Fase 14), Custos (custo
  médio ponderado), consumo automático de estoque por Compras (módulo ainda não existe
  — Ordens de Serviço e Vendas já consomem estoque automaticamente).
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
  tempo real, cache Redis, Assistente IA fixo e busca global (CTRL+K), insights
  automáticos por IA, Agenda (módulo inexistente), Caixa/Conciliação Bancária, Ranking
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
  Agent e todos os demais Agents (Executor/Report/CRM/Sales/OS/Financial/Inventory/
  Notification/OCR/Document/Automation) — nenhum pode chamar Tools sem MCP (Fase 14);
  MCP/Tools em si; RAG/embeddings/busca semântica (Fase 15, exige pgvector); memória de
  curto/longo prazo e conversas multi-turno (exigiria tabela/coluna não documentada);
  streaming (SSE/WebSocket); fallback entre múltiplos provedores (só existe Gemini);
  roteador inteligente de modelo; rate limit dedicado de IA por tenant/usuário/plano
  (existe rate limit genérico de login, não de IA); Prompt Builder completo com
  versionamento (o atual é fixo: empresa/usuário/papel/data); tabela `ai_actions`
  (depende de MCP); Dashboard de IA dedicado; guardrails de mascaramento automático de
  dados sensíveis; botão de IA em todas as telas (só há um painel no Dashboard); serviço
  `worker`/fila dedicado; Billing de IA real (o `estimated_cost` retornado é uma
  estimativa por tabela de preço fixa, não uma fatura).
- Qualquer módulo de negócio fora do CRM/Estoque/Ordens de Serviço/Vendas/Financeiro/
  Dashboard/Storage/IA — ver `docs/34-MASTER-PLAN.md`, Fase 14 em diante.
- MCP, RAG, Automation Engine, Billing real.
- RabbitMQ/Celery, Qdrant/pgvector, Nginx, Prometheus/Grafana/Loki/Tempo.
- MFA, SSO, Passkeys.

Essas peças serão adicionadas nas próximas fases, seguindo `docs/34-MASTER-PLAN.md`.
