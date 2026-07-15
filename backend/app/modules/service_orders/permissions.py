"""Constantes de permissão do módulo de Ordens de Serviço, conforme
10-ORDEM-DE-SERVICO.md ("Permissões") e 22-API-STANDARDS.md (padrão
`<módulo>.<ação>`). `close`/`cancel` são permissões próprias — operações mais
sensíveis que uma edição comum (mesmo padrão de `stock.adjust` separado de
`products.update`)."""

from __future__ import annotations

SERVICE_ORDERS_VIEW = "service_orders.view"
SERVICE_ORDERS_CREATE = "service_orders.create"
SERVICE_ORDERS_UPDATE = "service_orders.update"
SERVICE_ORDERS_DELETE = "service_orders.delete"
SERVICE_ORDERS_CLOSE = "service_orders.close"
SERVICE_ORDERS_CANCEL = "service_orders.cancel"
