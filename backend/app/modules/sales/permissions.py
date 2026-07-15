"""Constantes de permissão do módulo de Vendas, conforme 12-VENDAS.md ("Permissões") e
22-API-STANDARDS.md (padrão `<módulo>.<ação>`). `complete`/`cancel` são permissões
próprias — operações mais sensíveis que uma edição comum (mesmo padrão de
`service_orders.close`/`stock.adjust`). Sem `sales.delete` — vendas nunca são excluídas,
apenas canceladas."""

from __future__ import annotations

SALES_VIEW = "sales.view"
SALES_CREATE = "sales.create"
SALES_UPDATE = "sales.update"
SALES_COMPLETE = "sales.complete"
SALES_CANCEL = "sales.cancel"
