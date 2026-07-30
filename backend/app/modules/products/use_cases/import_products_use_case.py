"""Caso de uso: importar produtos em lote a partir de um arquivo CSV/XLSX. Reaproveita
`CreateProductUseCase` linha a linha — herda de graça toda validação já existente (SKU/
código de barras únicos, categoria/fornecedor existentes) em vez de duplicar regra de
negócio. Uma linha com erro nunca aborta as demais.

Categoria/fornecedor citados na planilha que não existem no tenant NÃO são criados
automaticamente (evita duplicata por erro de digitação) — o produto é criado sem esse
vínculo e a linha aparece em `warnings`, não em `errors`."""

from __future__ import annotations

import uuid
from decimal import Decimal, InvalidOperation

from pydantic import ValidationError as PydanticValidationError
from veloai_shared.exceptions import AppException

from app.core.database import TenantConnectionManager
from app.core.import_result import ImportResult, ImportRowNote
from app.modules.categories.repositories.category_repository import CategoryRepository
from app.modules.products.schemas.product import CreateProductRequest
from app.modules.products.services.product_import_parser import (
    FIELD_LABELS,
    REQUIRED_FIELDS,
    parse_rows,
)
from app.modules.products.use_cases.create_product_use_case import CreateProductUseCase
from app.modules.suppliers.repositories.supplier_repository import SupplierRepository


class ImportProductsUseCase:
    def __init__(self, *, connection_manager: TenantConnectionManager) -> None:
        self._connections = connection_manager

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        filename: str,
        data: bytes,
    ) -> ImportResult:
        rows = parse_rows(filename, data)

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            categories = await CategoryRepository(session).list_all()
            suppliers = await SupplierRepository(session).list_all()
        category_by_name = {category.name.strip().lower(): category.id for category in categories}
        supplier_by_name = {supplier.name.strip().lower(): supplier.id for supplier in suppliers}

        create_use_case = CreateProductUseCase(connection_manager=self._connections)
        errors: list[ImportRowNote] = []
        warnings: list[ImportRowNote] = []
        created = 0

        for line_number, row in enumerate(rows, start=2):  # linha 1 da planilha é o cabeçalho
            try:
                payload, row_warning = self._build_request(row, category_by_name, supplier_by_name)
            except ValueError as exc:
                errors.append(ImportRowNote(row=line_number, message=str(exc)))
                continue

            try:
                await create_use_case.execute(
                    tenant_id=tenant_id,
                    database_name=database_name,
                    actor_user_id=actor_user_id,
                    payload=payload,
                )
                created += 1
                if row_warning:
                    warnings.append(ImportRowNote(row=line_number, message=row_warning))
            except AppException as exc:
                errors.append(ImportRowNote(row=line_number, message=exc.message))

        return ImportResult(
            total_rows=len(rows), created=created, errors=errors, warnings=warnings
        )

    def _build_request(
        self,
        row: dict[str, str],
        category_by_name: dict[str, uuid.UUID],
        supplier_by_name: dict[str, uuid.UUID],
    ) -> tuple[CreateProductRequest, str | None]:
        missing = [
            FIELD_LABELS[field] for field in REQUIRED_FIELDS if not row.get(field, "").strip()
        ]
        if missing:
            raise ValueError(f"Campo(s) obrigatório(s) ausente(s): {', '.join(missing)}.")

        warning_parts: list[str] = []

        category_id: uuid.UUID | None = None
        category_name = row.get("category_name", "").strip()
        if category_name:
            category_id = category_by_name.get(category_name.lower())
            if category_id is None:
                warning_parts.append(f'categoria "{category_name}" não encontrada')

        supplier_id: uuid.UUID | None = None
        supplier_name = row.get("supplier_name", "").strip()
        if supplier_name:
            supplier_id = supplier_by_name.get(supplier_name.lower())
            if supplier_id is None:
                warning_parts.append(f'fornecedor "{supplier_name}" não encontrado')

        try:
            cost_price = self._parse_decimal(row.get("cost_price"), default=Decimal("0"))
            sale_price = self._parse_decimal(row.get("sale_price"), default=None)
            weight = self._parse_decimal(row.get("weight"), default=None)
            stock = self._parse_int(row.get("stock"), default=0)
            minimum_stock = self._parse_int(row.get("minimum_stock"), default=None)
            maximum_stock = self._parse_int(row.get("maximum_stock"), default=None)
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"Valor numérico inválido: {exc}") from exc

        assert sale_price is not None  # "sale_price" já está em REQUIRED_FIELDS, checado acima

        try:
            payload = CreateProductRequest(
                category_id=category_id,
                supplier_id=supplier_id,
                sku=row["sku"].strip(),
                barcode=row.get("barcode", "").strip() or None,
                name=row["name"].strip(),
                description=row.get("description", "").strip() or None,
                cost_price=cost_price,
                sale_price=sale_price,
                stock=stock,
                minimum_stock=minimum_stock,
                maximum_stock=maximum_stock,
                unit=row.get("unit", "").strip() or "UN",
                weight=weight,
            )
        except PydanticValidationError as exc:
            raise ValueError(self._format_pydantic_error(exc)) from exc

        warning = "; ".join(warning_parts) if warning_parts else None
        return payload, warning

    @staticmethod
    def _parse_decimal(raw: str | None, *, default: Decimal | None) -> Decimal | None:
        text = (raw or "").strip()
        if not text:
            return default
        normalized = text.replace(".", "").replace(",", ".") if "," in text else text
        return Decimal(normalized)

    @classmethod
    def _parse_int(cls, raw: str | None, *, default: int | None) -> int | None:
        value = cls._parse_decimal(raw, default=None)
        return int(value) if value is not None else default

    @staticmethod
    def _format_pydantic_error(exc: PydanticValidationError) -> str:
        first = exc.errors()[0]
        field = str(first["loc"][-1]) if first["loc"] else ""
        return f"{field}: {first['msg']}"
