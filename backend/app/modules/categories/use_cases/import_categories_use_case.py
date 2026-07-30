"""Caso de uso: importar categorias em lote a partir de um arquivo CSV/XLSX.
Reaproveita `CreateCategoryUseCase` linha a linha — herda de graça a validação de nome
único em vez de duplicar regra de negócio. Uma linha com erro nunca aborta as demais."""

from __future__ import annotations

import uuid

from pydantic import ValidationError as PydanticValidationError
from veloai_shared.exceptions import AppException

from app.core.database import TenantConnectionManager
from app.core.import_result import ImportResult, ImportRowNote
from app.modules.categories.schemas.category import CreateCategoryRequest
from app.modules.categories.services.category_import_parser import (
    FIELD_LABELS,
    REQUIRED_FIELDS,
    parse_rows,
)
from app.modules.categories.use_cases.create_category_use_case import CreateCategoryUseCase


class ImportCategoriesUseCase:
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

        create_use_case = CreateCategoryUseCase(connection_manager=self._connections)
        errors: list[ImportRowNote] = []
        warnings: list[ImportRowNote] = []
        created = 0

        for line_number, row in enumerate(rows, start=2):  # linha 1 da planilha é o cabeçalho
            try:
                payload = self._build_request(row)
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
            except AppException as exc:
                errors.append(ImportRowNote(row=line_number, message=exc.message))

        return ImportResult(
            total_rows=len(rows), created=created, errors=errors, warnings=warnings
        )

    def _build_request(self, row: dict[str, str]) -> CreateCategoryRequest:
        missing = [
            FIELD_LABELS[field] for field in REQUIRED_FIELDS if not row.get(field, "").strip()
        ]
        if missing:
            raise ValueError(f"Campo(s) obrigatório(s) ausente(s): {', '.join(missing)}.")

        try:
            return CreateCategoryRequest(
                name=row["name"].strip(),
                description=row.get("description", "").strip() or None,
            )
        except PydanticValidationError as exc:
            raise ValueError(self._format_pydantic_error(exc)) from exc

    @staticmethod
    def _format_pydantic_error(exc: PydanticValidationError) -> str:
        first = exc.errors()[0]
        field = str(first["loc"][-1]) if first["loc"] else ""
        return f"{field}: {first['msg']}"
