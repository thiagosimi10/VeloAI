"""Constantes de permissão do módulo de Produtos, conforme 05-BANCO-DE-DADOS.md e
22-API-STANDARDS.md (padrão `<módulo>.<ação>`).

`STOCK_VIEW`/`STOCK_ADJUST` são do domínio "Estoque" (Fase 7 do Master Plan), mas o
código de movimentação vive neste módulo — ver `app/modules/README.md` — por isso as
constantes ficam aqui, com permissões próprias, separadas de `PRODUCTS_*` (permite dar a
alguém o direito de ajustar estoque sem poder editar o cadastro do produto)."""

from __future__ import annotations

PRODUCTS_VIEW = "products.view"
PRODUCTS_CREATE = "products.create"
PRODUCTS_UPDATE = "products.update"
PRODUCTS_DELETE = "products.delete"

STOCK_VIEW = "stock.view"
STOCK_ADJUST = "stock.adjust"
