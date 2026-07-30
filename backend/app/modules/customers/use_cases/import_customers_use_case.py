"""Caso de uso: importar clientes em lote a partir de um arquivo CSV/XLSX. Reaproveita
`CreateCustomerUseCase` linha a linha — herda de graça toda validação já existente
(documento único) em vez de duplicar regra de negócio. Uma linha com erro nunca aborta
as demais.

Se a coluna "tipo" (PF/PJ) não vier preenchida, o tipo é inferido pelo tamanho do
documento normalizado (11 dígitos = CPF/PF, 14 = CNPJ/PJ)."""

from __future__ import annotations

import uuid

from pydantic import ValidationError as PydanticValidationError
from veloai_shared.exceptions import AppException
from veloai_shared.validators import normalize_document

from app.core.database import TenantConnectionManager
from app.core.import_result import ImportResult, ImportRowNote
from app.modules.customers.schemas.customer import CreateCustomerRequest
from app.modules.customers.services.customer_import_parser import (
    FIELD_LABELS,
    REQUIRED_FIELDS,
    parse_rows,
)
from app.modules.customers.use_cases.create_customer_use_case import CreateCustomerUseCase

_PF_ALIASES = {"pf", "pessoa fisica", "pessoa física", "fisica", "física", "individual"}
_PJ_ALIASES = {"pj", "pessoa juridica", "pessoa jurídica", "juridica", "jurídica", "empresa"}


class ImportCustomersUseCase:
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

        create_use_case = CreateCustomerUseCase(connection_manager=self._connections)
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

    def _build_request(self, row: dict[str, str]) -> CreateCustomerRequest:
        missing = [
            FIELD_LABELS[field] for field in REQUIRED_FIELDS if not row.get(field, "").strip()
        ]
        if missing:
            raise ValueError(f"Campo(s) obrigatório(s) ausente(s): {', '.join(missing)}.")

        document = normalize_document(row["document"].strip())
        customer_type = self._infer_type(row.get("type", ""), document)

        try:
            return CreateCustomerRequest(
                type=customer_type,
                name=row["name"].strip(),
                document=document,
                email=row.get("email", "").strip() or None,
                phone=row.get("phone", "").strip() or None,
                mobile=row.get("mobile", "").strip() or None,
                whatsapp=row.get("whatsapp", "").strip() or None,
                zipcode=row.get("zipcode", "").strip() or None,
                street=row.get("street", "").strip() or None,
                number=row.get("number", "").strip() or None,
                district=row.get("district", "").strip() or None,
                city=row.get("city", "").strip() or None,
                state=row.get("state", "").strip() or None,
                country=row.get("country", "").strip() or "Brasil",
                notes=row.get("notes", "").strip() or None,
            )
        except PydanticValidationError as exc:
            raise ValueError(self._format_pydantic_error(exc)) from exc

    @staticmethod
    def _infer_type(raw_type: str, normalized_document: str) -> str:
        normalized = raw_type.strip().lower()
        if normalized in _PF_ALIASES:
            return "PF"
        if normalized in _PJ_ALIASES:
            return "PJ"
        return "PF" if len(normalized_document) <= 11 else "PJ"

    @staticmethod
    def _format_pydantic_error(exc: PydanticValidationError) -> str:
        first = exc.errors()[0]
        field = str(first["loc"][-1]) if first["loc"] else ""
        return f"{field}: {first['msg']}"
