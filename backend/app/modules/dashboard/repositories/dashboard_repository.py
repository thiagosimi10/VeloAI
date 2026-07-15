"""Consultas agregadas somente-leitura para o Dashboard. Diferente dos demais
`repositories/` do projeto, este não é dono de nenhuma tabela — consulta diretamente os
modelos SQLAlchemy compartilhados de outros módulos (nunca seus `repositories`), o
mesmo tipo de acesso de leitura que `GetCustomerUseCase`/`GetSupplierUseCase` já expõem
publicamente, só que agregado em vez de registro-a-registro (ver
`app/modules/README.md`)."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from veloai_shared.schema.tenant import (
    AccountPayable,
    AccountReceivable,
    CashFlowEntry,
    Customer,
    Product,
    Sale,
    SaleItem,
    Service,
    ServiceOrder,
    ServiceOrderItem,
)


class DashboardRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def count_customers(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(Customer).where(Customer.deleted_at.is_(None))
        )
        return int(result.scalar_one())

    async def count_products(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(Product).where(Product.deleted_at.is_(None))
        )
        return int(result.scalar_one())

    async def count_services(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(Service).where(Service.deleted_at.is_(None))
        )
        return int(result.scalar_one())

    async def count_orders_by_status(self) -> dict[str, int]:
        result = await self._session.execute(
            select(ServiceOrder.status, func.count())
            .where(ServiceOrder.deleted_at.is_(None))
            .group_by(ServiceOrder.status)
        )
        return {status: int(count) for status, count in result.all()}

    async def sum_revenue_between(self, start: date, end: date) -> tuple[Decimal, int]:
        """Soma `sales.total` (pagas) + `service_orders.total` (concluídas) cujo
        recebimento/conclusão caiu no intervalo `[start, end)`, junto com a contagem de
        registros — usada tanto para a receita do período quanto para o ticket médio."""

        sales_result = await self._session.execute(
            select(func.coalesce(func.sum(Sale.total), Decimal("0.00")), func.count())
            .where(
                Sale.status == "paid",
                Sale.deleted_at.is_(None),
                func.date(Sale.created_at) >= start,
                func.date(Sale.created_at) < end,
            )
        )
        sales_total, sales_count = sales_result.one()

        orders_result = await self._session.execute(
            select(func.coalesce(func.sum(ServiceOrder.total), Decimal("0.00")), func.count())
            .where(
                ServiceOrder.status == "completed",
                ServiceOrder.deleted_at.is_(None),
                ServiceOrder.finished_at.is_not(None),
                func.date(ServiceOrder.finished_at) >= start,
                func.date(ServiceOrder.finished_at) < end,
            )
        )
        orders_total, orders_count = orders_result.one()

        return Decimal(sales_total) + Decimal(orders_total), int(sales_count) + int(orders_count)

    async def sum_accounts_receivable_pending(self) -> Decimal:
        result = await self._session.execute(
            select(func.coalesce(func.sum(AccountReceivable.amount), Decimal("0.00"))).where(
                AccountReceivable.status == "pending", AccountReceivable.deleted_at.is_(None)
            )
        )
        return Decimal(result.scalar_one())

    async def count_accounts_receivable_overdue(self) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(AccountReceivable)
            .where(
                AccountReceivable.status == "pending",
                AccountReceivable.deleted_at.is_(None),
                AccountReceivable.due_date < date.today(),
            )
        )
        return int(result.scalar_one())

    async def sum_accounts_payable_pending(self) -> Decimal:
        result = await self._session.execute(
            select(func.coalesce(func.sum(AccountPayable.amount), Decimal("0.00"))).where(
                AccountPayable.status == "pending", AccountPayable.deleted_at.is_(None)
            )
        )
        return Decimal(result.scalar_one())

    async def count_accounts_payable_overdue(self) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(AccountPayable)
            .where(
                AccountPayable.status == "pending",
                AccountPayable.deleted_at.is_(None),
                AccountPayable.due_date < date.today(),
            )
        )
        return int(result.scalar_one())

    async def sum_cash_balance(self) -> Decimal:
        result = await self._session.execute(
            select(
                func.coalesce(
                    func.sum(case((CashFlowEntry.type == "in", CashFlowEntry.amount), else_=0)),
                    Decimal("0.00"),
                )
                - func.coalesce(
                    func.sum(case((CashFlowEntry.type == "out", CashFlowEntry.amount), else_=0)),
                    Decimal("0.00"),
                )
            )
        )
        return Decimal(result.scalar_one())

    async def count_critical_stock(self) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(Product)
            .where(
                Product.deleted_at.is_(None),
                Product.minimum_stock.is_not(None),
                Product.stock <= Product.minimum_stock,
            )
        )
        return int(result.scalar_one())

    async def top_products_by_quantity(self, limit: int) -> list[tuple[uuid.UUID, str, int]]:
        """Soma a quantidade vendida de cada produto em `sale_items` +
        `service_order_items` (só os itens com `product_id`, nunca os de serviço) —
        nunca substitui uma fonte pela outra, sempre soma as duas."""

        sale_quantities = (
            select(SaleItem.product_id.label("product_id"), SaleItem.quantity.label("quantity"))
        )
        order_quantities = select(
            ServiceOrderItem.product_id.label("product_id"),
            ServiceOrderItem.quantity.label("quantity"),
        ).where(ServiceOrderItem.product_id.is_not(None))

        combined = sale_quantities.union_all(order_quantities).subquery()

        result = await self._session.execute(
            select(
                Product.id,
                Product.name,
                func.sum(combined.c.quantity).label("quantity_sold"),
            )
            .join(combined, combined.c.product_id == Product.id)
            .group_by(Product.id, Product.name)
            .order_by(func.sum(combined.c.quantity).desc())
            .limit(limit)
        )
        return [(row.id, row.name, int(row.quantity_sold)) for row in result.all()]
