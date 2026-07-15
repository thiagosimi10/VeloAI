"""Constantes de permissão do módulo Financeiro, conforme 11-FINANCEIRO.md
("Permissões") e 22-API-STANDARDS.md (padrão `<módulo>.<ação>`). `receive`/`pay` são
permissões próprias — operações mais sensíveis que uma edição comum (mesmo padrão de
`service_orders.close`/`sales.complete`). Sem `finance.delete` — nenhum lançamento
financeiro é excluído, apenas cancelado (se `pending`) ou estornado (`cash_flow`, via
lançamento manual oposto)."""

from __future__ import annotations

FINANCE_VIEW = "finance.view"
FINANCE_CREATE = "finance.create"
FINANCE_UPDATE = "finance.update"
FINANCE_RECEIVE = "finance.receive"
FINANCE_PAY = "finance.pay"
FINANCE_CANCEL = "finance.cancel"
