"""DTOs do módulo Dashboard — indicadores calculados a partir dos dados que os demais
módulos já produzem (Clientes, Produtos, Serviços, Ordens de Serviço, Vendas,
Financeiro). Sem tabela própria, conforme `app/modules/README.md`. Dashboard
personalizável por perfil, IA, WebSocket e exportação (ver 07-DASHBOARD.md) ficam para
uma iteração futura."""

from __future__ import annotations

import uuid
from decimal import Decimal

from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    total_customers: int
    total_products: int
    total_services: int
    orders_by_status: dict[str, int]
    sales_by_status: dict[str, int]
    revenue_this_month: Decimal
    revenue_last_month: Decimal
    revenue_change_percentage: Decimal | None
    average_ticket: Decimal
    accounts_receivable_pending_total: Decimal
    accounts_receivable_overdue_count: int
    accounts_payable_pending_total: Decimal
    accounts_payable_overdue_count: int
    cash_balance: Decimal
    critical_stock_count: int


class RevenueTimeSeriesPoint(BaseModel):
    period: str
    revenue: Decimal


class TopProductItem(BaseModel):
    product_id: uuid.UUID
    name: str
    quantity_sold: int


class NewCustomersTimeSeriesPoint(BaseModel):
    period: str
    count: int


class CashFlowTimeSeriesPoint(BaseModel):
    period: str
    cash_in: Decimal
    cash_out: Decimal


class CategoryProductCount(BaseModel):
    category_name: str
    product_count: int
