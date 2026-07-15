"""Constante de permissão do módulo Dashboard, conforme 07-DASHBOARD.md
("Permissões") e 22-API-STANDARDS.md (padrão `<módulo>.<ação>`). O doc lista uma
permissão por widget (`dashboard.finance`, `dashboard.orders`, ...) — nesta fase existe
um único papel (Administrador) e nenhum benefício real em granularizar, então todos os
endpoints usam esta única permissão."""

from __future__ import annotations

DASHBOARD_VIEW = "dashboard.view"
