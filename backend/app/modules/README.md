# Módulos do Backend

`auth/` (Fase 3 — Autenticação) e o CRM completo (`customers/`, `suppliers/`,
`categories/`, `products/`, `services/` — Fase 6) seguem a mesma convenção e servem de
referência para os módulos mais recentes (`users/`, `service_orders/` — Fase 8;
`sales/` — Fase 9; `finance/` — Fase 10; `dashboard/` — Fase 11, único que não segue a
convenção `repositories/` = dono de tabela, ver abaixo; `attachments/` — Fase 12; `ai/` —
Fase 13) e para os próximos (ver `docs/34-MASTER-PLAN.md`, Fase 14 em diante).
`suppliers/` é uma cópia estrutural exata de `customers/` — mesmos campos, mesmo fluxo —
conforme `docs/05-BANCO-DE-DADOS.md` ("Fornecedores: mesmo padrão dos clientes").
`categories/` é uma entidade enxuta (só nome/descrição, sem código sequencial).
`products/` e `services/` têm relações entre entidades (`category_id`/`supplier_id`);
`products/` também expõe um campo computado (margem):

```text
modules/
  auth/
    api/            # Controller — recebe requisição, delega ao use_case, gerencia cookies
    schemas/         # DTOs Pydantic (LoginRequest, MeResponse, ...)
    repositories/    # Acesso ao banco do tenant — sem regra de negócio
    services/        # token_service.py — emissão/decodificação de JWT
    use_cases/       # LoginUseCase, RefreshUseCase, LogoutUseCase, ChangePasswordUseCase, MeUseCase
  customers/
    api/             # Controller — valida permissão (require_permission) e delega
    schemas/         # CreateCustomerRequest, UpdateCustomerRequest, CustomerResponse, filtros
    repositories/    # CustomerRepository — CRUD + busca/paginação
    use_cases/       # ListCustomers, GetCustomer, CreateCustomer, UpdateCustomer, DeleteCustomer
    permissions.py   # Constantes: customers.view/create/update/delete
  suppliers/         # Mesma estrutura de customers/, trocando Customer -> Supplier
  categories/        # Estrutura igual, mas sem geração de código/documento (name+description)
  products/          # Estrutura igual + valida category_id/supplier_id chamando os
                      # use_cases (não os repositories) de categories/suppliers.
                      # Também contém o histórico de estoque (Fase 7 — ver abaixo) e
                      # expõe `services/stock_movement_service.py` (ver abaixo).
  services/          # Como customers/ (code sequencial "S000001") + valida category_id
                      # chamando GetCategoryUseCase, no mesmo padrão de products/
  users/              # Somente leitura nesta fase (list/get) — usado para popular o
                      # seletor de técnico em Ordens de Serviço; sem CRUD completo.
  service_orders/     # Fase 8 — o mais complexo até aqui: CRUD + itens (produto ou
                      # serviço) + transições de status (start/close/cancel). `close`
                      # consome estoque automaticamente reaproveitando
                      # `products/services/stock_movement_service.apply_stock_movement`
                      # (ver abaixo).
  sales/              # Fase 9 — mesmo padrão de service_orders/, mais enxuto porque
                      # 05-BANCO-DE-DADOS.md define `sales`/`sale_items` com bem menos
                      # campos: sem número sequencial, sem vendedor, itens sempre de
                      # produto (nunca serviço) e sem coluna `total` no item (calculado
                      # via `computed_field`, nunca persistido). Só 3 status
                      # (open/paid/cancelled — `complete`/`cancel`), sem `DELETE` (nunca
                      # se exclui uma venda, só se cancela). `complete` reaproveita o
                      # mesmo `apply_stock_movement` de `service_orders/` para consumir
                      # estoque na conclusão.
  finance/            # Fase 10 — três entidades no mesmo módulo: Contas a Receber,
                      # Contas a Pagar e Fluxo de Caixa (`accounts_receivable`/
                      # `accounts_payable`/`cash_flow`, todas com bem menos campos que
                      # 11-FINANCEIRO.md — sem juros/multa/desconto/parcial/categoria
                      # configurável/origem). `receive`/`pay` inserem uma linha em
                      # `cash_flow` automaticamente NA MESMA transação — isso não é uma
                      # integração cross-module (as três tabelas vivem no mesmo módulo),
                      # diferente do caso de `products/`/`service_orders/`/`sales/`.
                      # Geração automática de Conta a Receber a partir de Venda/OS
                      # concluída fica de fora — `accounts_receivable` não tem coluna de
                      # origem/referência para rastrear isso.
  dashboard/          # Fase 11 — não é dono de nenhuma tabela: `repositories/
                      # dashboard_repository.py` executa consultas agregadas
                      # (COUNT/SUM/GROUP BY) direto sobre os modelos SQLAlchemy
                      # compartilhados de Clientes, Produtos, Serviços, Ordens de
                      # Serviço, Vendas e Financeiro — nunca sobre os `repositories`
                      # desses módulos (ver "Nenhum módulo..." abaixo para o porquê
                      # isso não viola a regra). Só leitura, sem endpoint de escrita.
  attachments/        # Fase 12 (Storage) — sem base em 05-BANCO-DE-DADOS.md (decisão
                      # tomada com o usuário, ver `docs/34-MASTER-PLAN.md`). Tabela
                      # genérica/polimórfica (`resource_type`+`resource_id`) para
                      # anexar arquivos a Clientes, Produtos e Ordens de Serviço — os
                      # três tipos já citados em docs anteriores. Usa
                      # `app/core/storage.py` (cliente MinIO, cross-cutting) para o
                      # arquivo em si; a tabela só guarda metadados
                      # (`22-API-STANDARDS.md`: "Nunca armazenar arquivos no banco").
                      # Valida a existência do recurso reaproveitando
                      # `GetCustomerUseCase`/`GetProductUseCase`/`GetServiceOrderUseCase`.
                      # Exclusão remove do MinIO ANTES da linha do banco, nunca a ordem
                      # inversa (nunca deixa uma linha órfã apontando para um objeto já
                      # removido).
  ai/                 # Fase 13 — `POST /ai/ask` monta um "Prompt Builder" enxuto
                      # (nome da empresa + nome/papel do usuário + data de hoje) e
                      # delega ao `AIGatewayClient` (app/core/ai_gateway_client.py,
                      # cross-cutting) — o Backend nunca fala com uma LLM diretamente,
                      # só com o AI Gateway. Grava cada chamada em `ai_conversations`
                      # (tokens/modelo/tempo de execução) e reaproveita `GetUserUseCase`
                      # (users/) para o nome do usuário. `GET /ai/conversations` lista o
                      # histórico paginado. `ai_actions` (Tools via MCP) fica para a
                      # Fase 14.
```

Os modelos SQLAlchemy (`Customer`, `Supplier`, `Category`, `Product`, `Service`,
`StockMovement`, `ServiceOrder`, `ServiceOrderItem`, `Sale`, `SaleItem`,
`AccountReceivable`, `AccountPayable`, `CashFlowEntry`, `Attachment`) vivem em
`shared/veloai_shared/schema/tenant/`, não dentro do módulo — mesmo padrão de `auth/`
(`TenantUser`, `RefreshToken`, ...), pois o Provisioning também precisa deles para gerar
as migrations. `dashboard/` não acrescenta nenhum modelo novo — só lê os já existentes.

**Estoque (Fase 7) mora dentro de `products/`, não é um módulo próprio.** O ajuste de
estoque precisa atualizar `products.stock` e inserir a linha de histórico
(`stock_movements`) na mesma transação — como `stock` é uma coluna de `products`, isso só
é possível abrindo uma única sessão dentro do próprio módulo. A lógica de cálculo vive em
`products/services/stock_movement_service.py` (`apply_stock_movement`, recebe a sessão já
aberta pelo chamador, nunca abre a própria nem comita) — `products/use_cases/
adjust_product_stock_use_case.py` a usa para o endpoint dedicado de ajuste, e
`service_orders/use_cases/close_service_order_use_case.py` **e**
`sales/use_cases/complete_sale_use_case.py` a reaproveitam para consumir estoque de cada
item-produto **na mesma transação** do fechamento da OS/conclusão da Venda, sem duplicar
a conta e sem acessar `ProductRepository`/`StockMovementRepository` diretamente (o rule
de "nunca acessar repository de outro módulo" permite comunicação via `services/`, que é
exatamente essa camada). As permissões de estoque continuam separadas (`stock.view`/
`stock.adjust`, em `products/permissions.py`).

Os testes ficam centralizados em `backend/tests/{unit,integration}/<nome_do_modulo>/`
(não dentro de cada módulo) — ver `backend/tests/unit/auth/`, `backend/tests/unit/
customers/`, `backend/tests/unit/suppliers/`, `backend/tests/unit/categories/`,
`backend/tests/unit/products/` (inclui `test_stock_use_cases.py`),
`backend/tests/unit/services/`, `backend/tests/unit/users/`, `backend/tests/unit/
service_orders/`, `backend/tests/unit/sales/`, `backend/tests/unit/finance/`,
`backend/tests/unit/dashboard/`, `backend/tests/unit/attachments/`,
`backend/tests/unit/ai/`, `backend/tests/unit/core/test_ai_gateway_client.py` e
`backend/tests/integration/test_auth_flow.py`.

Cross-cutting reutilizável por qualquer módulo (nunca reimplementar):
- `app/core/dependencies.py` — `get_current_user`, `require_permission`.
- `app/core/audit.py` — `record_audit_log` (grava em `TenantAuditLog`).
- `app/core/middleware.py` — log estruturado por requisição (`X-Request-ID`).
- `app/core/storage.py` (Fase 12) — `get_storage_client()`/`StorageClient` (MinIO,
  `upload`/`delete`/`presigned_url`); qualquer módulo futuro que precise armazenar
  arquivos (ex.: imagem de Produto) pode reutilizá-lo diretamente, sem depender do
  módulo `attachments/`.

Nenhum módulo poderá acessar o `repository` de outro módulo diretamente — toda
comunicação entre módulos ocorre através de `services`/`use_cases`. Exemplos reais:
`products/use_cases/create_product_use_case.py` e
`services/use_cases/create_service_use_case.py` validam `category_id` (e, no caso de
Produtos, também `supplier_id`) chamando `GetCategoryUseCase`/`GetSupplierUseCase`;
`service_orders/use_cases/create_service_order_use_case.py` valida `customer_id`/
`technician_id` chamando `GetCustomerUseCase`/`GetUserUseCase`; nenhum desses acessa o
`repository` de outro módulo diretamente.

**Exceção deliberada: `dashboard/repositories/dashboard_repository.py`.** Essa regra
protege a lógica de negócio de **escrita** de cada módulo (mutações e invariantes) — o
Dashboard é somente-leitura e agrega dados de seis módulos diferentes; recriar
`GetCustomerUseCase`-como uma chamada por registro para depois somar em memória seria só
uma indireção sem benefício real. Por isso ele consulta os modelos SQLAlchemy
compartilhados diretamente, com `SELECT`s agregados (`COUNT`/`SUM`/`GROUP BY`) — a mesma
categoria de acesso de leitura que `GetCustomerUseCase`/`GetSupplierUseCase` já expõem
publicamente, só que em lote. Nenhum outro módulo deve replicar esse padrão para
mutações.

**Exceção pontual: `ai/use_cases/_helpers.py::get_company_display_name`.** `Company` não
tem módulo dono (não existe `company/`) — é um perfil único por tenant, sem CRUD próprio.
`ai/` faz um `SELECT` de leitura direto sobre o modelo, na mesma linha de raciocínio da
exceção do Dashboard acima (não há nenhum `repository` de outro módulo sendo contornado).
Para dados que **têm** módulo dono (o usuário autenticado), `ai/` reaproveita o
`GetUserUseCase` público de `users/`, sem exceção nenhuma.

Módulos de negócio futuros deverão acrescentar, quando fizer sentido:

```text
    mcp_tools/       # Tools MCP expostas à IA para este módulo (Fase 14)
    validators/
    exceptions/
```
