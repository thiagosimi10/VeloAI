"""Configuração de importação em lote de Categorias — apelidos de coluna reconhecidos
e campos obrigatórios. O parsing CSV/XLSX em si é genérico, ver
`app/core/spreadsheet_parser.py`."""

from __future__ import annotations

from app.core.spreadsheet_parser import parse_rows as _parse_rows

HEADER_ALIASES: dict[str, str] = {
    "nome": "name",
    "name": "name",
    "categoria": "name",
    "descricao": "description",
    "description": "description",
}

REQUIRED_FIELDS = ("name",)

FIELD_LABELS: dict[str, str] = {
    "name": "Nome",
    "description": "Descrição",
}


def parse_rows(filename: str, data: bytes) -> list[dict[str, str]]:
    return _parse_rows(filename, data, HEADER_ALIASES)
