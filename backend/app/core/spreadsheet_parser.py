"""Parsing genérico (sem I/O de banco) de planilhas CSV/XLSX para qualquer importação
em lote — reaproveitado por Produtos, Clientes, Fornecedores e Categorias (cada módulo
só define seu próprio dicionário de apelidos de coluna, ver `product_import_parser.py`
como referência). CSV via `csv` da stdlib, XLSX via `openpyxl`.

Formato legado `.xls` (BIFF binário) não é suportado — `openpyxl` só lê o formato
moderno (`.xlsx`); pedir para a pessoa salvar como `.xlsx` ou `.csv` é mais simples e
honesto do que tentar suportar os dois."""

from __future__ import annotations

import csv
import io
import unicodedata

from openpyxl import load_workbook
from veloai_shared.exceptions import ValidationError


def normalize_header(text: str) -> str:
    """Minúsculo, sem acento, sem espaço/pontuação — 'Preço de Venda' e 'preco_venda'
    normalizam para a mesma chave ('precodevenda')."""

    decomposed = unicodedata.normalize("NFKD", text.strip().lower())
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    return "".join(char for char in without_accents if char.isalnum())


def _map_headers(raw_headers: list[str], header_aliases: dict[str, str]) -> dict[int, str]:
    """Índice da coluna → campo do destino, só para colunas reconhecidas (colunas
    desconhecidas na planilha são ignoradas, não geram erro)."""

    mapped: dict[int, str] = {}
    for index, raw_header in enumerate(raw_headers):
        field = header_aliases.get(normalize_header(raw_header or ""))
        if field:
            mapped[index] = field
    return mapped


def _parse_csv(data: bytes, header_aliases: dict[str, str]) -> list[dict[str, str]]:
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = data.decode("latin-1")

    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        return []

    header_map = _map_headers(rows[0], header_aliases)
    parsed_rows: list[dict[str, str]] = []
    for raw_row in rows[1:]:
        if not any(cell.strip() for cell in raw_row):
            continue  # linha em branco no meio da planilha — ignora, não é erro
        row: dict[str, str] = {}
        for index, field in header_map.items():
            if index < len(raw_row):
                row[field] = raw_row[index].strip()
        parsed_rows.append(row)
    return parsed_rows


def _parse_xlsx(data: bytes, header_aliases: dict[str, str]) -> list[dict[str, str]]:
    workbook = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    try:
        sheet = workbook.worksheets[0]
        rows_iter = sheet.iter_rows(values_only=True)
        try:
            raw_header_row = next(rows_iter)
        except StopIteration:
            return []

        header_map = _map_headers(
            [str(cell) if cell is not None else "" for cell in raw_header_row], header_aliases
        )

        parsed_rows: list[dict[str, str]] = []
        for raw_row in rows_iter:
            if raw_row is None or not any(cell is not None for cell in raw_row):
                continue
            row: dict[str, str] = {}
            for index, field in header_map.items():
                if index < len(raw_row) and raw_row[index] is not None:
                    row[field] = str(raw_row[index]).strip()
            parsed_rows.append(row)
        return parsed_rows
    finally:
        workbook.close()


def parse_rows(
    filename: str, data: bytes, header_aliases: dict[str, str]
) -> list[dict[str, str]]:
    """Devolve uma linha por dict, já com as chaves normalizadas para os campos do
    destino (definidos por `header_aliases`) — colunas da planilha que não batem com
    nenhum apelido conhecido são descartadas silenciosamente."""

    lower_name = filename.lower()
    if lower_name.endswith(".csv"):
        return _parse_csv(data, header_aliases)
    if lower_name.endswith(".xlsx"):
        return _parse_xlsx(data, header_aliases)
    if lower_name.endswith(".xls"):
        raise ValidationError(
            "Formato .xls (Excel antigo) não é suportado. Salve a planilha como "
            ".xlsx ou .csv e tente novamente.",
            code="UNSUPPORTED_FILE_FORMAT",
        )
    raise ValidationError(
        "Formato de arquivo não reconhecido. Envie um arquivo .csv ou .xlsx.",
        code="UNSUPPORTED_FILE_FORMAT",
    )


def read_raw_preview(filename: str, data: bytes) -> tuple[list[str], int]:
    """Lê só o cabeçalho tal como está escrito na planilha (sem mapear para nenhum
    campo específico) e conta as linhas de dados — usado pelo preview do anexo no chat
    com a IA (`AiUploadStore.preview`), que roda ANTES de saber se o arquivo é de
    Produtos, Clientes, Fornecedores ou Categorias (a IA decide isso pelo texto do
    pedido + esses cabeçalhos brutos, não o nosso parser específico de um módulo)."""

    lower_name = filename.lower()
    if lower_name.endswith(".csv"):
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = data.decode("latin-1")
        rows = list(csv.reader(io.StringIO(text)))
        if not rows:
            return [], 0
        headers = [cell.strip() for cell in rows[0] if cell.strip()]
        row_count = sum(1 for row in rows[1:] if any(cell.strip() for cell in row))
        return headers, row_count

    if lower_name.endswith(".xlsx"):
        workbook = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
        try:
            sheet = workbook.worksheets[0]
            rows_iter = sheet.iter_rows(values_only=True)
            try:
                raw_header_row = next(rows_iter)
            except StopIteration:
                return [], 0
            headers = [str(cell).strip() for cell in raw_header_row if cell is not None and str(cell).strip()]
            row_count = sum(
                1 for row in rows_iter if row is not None and any(cell is not None for cell in row)
            )
            return headers, row_count
        finally:
            workbook.close()

    raise ValidationError(
        "Formato de arquivo não reconhecido. Envie um arquivo .csv ou .xlsx.",
        code="UNSUPPORTED_FILE_FORMAT",
    )
