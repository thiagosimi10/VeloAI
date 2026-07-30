"""Tipos compartilhados por toda importação em lote (Produtos, Clientes, Fornecedores,
Categorias) — o formato do resultado é idêntico em todo módulo, só a lógica de
validação de cada linha muda (ver `import_products_use_case.py` como referência)."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(frozen=True)
class ImportRowNote:
    row: int
    message: str


@dataclass(frozen=True)
class ImportResult:
    total_rows: int
    created: int
    errors: list[ImportRowNote]
    warnings: list[ImportRowNote]


class ImportRowNoteResponse(BaseModel):
    row: int
    message: str


class ImportResultResponse(BaseModel):
    total_rows: int
    created: int
    errors: list[ImportRowNoteResponse]
    warnings: list[ImportRowNoteResponse]


def to_import_result_response(result: ImportResult) -> ImportResultResponse:
    return ImportResultResponse(
        total_rows=result.total_rows,
        created=result.created,
        errors=[{"row": note.row, "message": note.message} for note in result.errors],
        warnings=[{"row": note.row, "message": note.message} for note in result.warnings],
    )
