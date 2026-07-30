"""Configuração de importação em lote de Produtos — apelidos de coluna reconhecidos e
campos obrigatórios. O parsing CSV/XLSX em si é genérico, ver
`app/core/spreadsheet_parser.py` (reaproveitado também por Clientes, Fornecedores e
Categorias)."""

from __future__ import annotations

from app.core.spreadsheet_parser import parse_rows as _parse_rows

# Cada chave é o nome normalizado (via `normalize_header`) de um possível cabeçalho na
# planilha; o valor é o campo correspondente em `CreateProductRequest`.
HEADER_ALIASES: dict[str, str] = {
    "sku": "sku",
    "codigo": "sku",
    "cod": "sku",
    "nome": "name",
    "produto": "name",
    "name": "name",
    "descricao": "description",
    "description": "description",
    "categoria": "category_name",
    "category": "category_name",
    "fornecedor": "supplier_name",
    "supplier": "supplier_name",
    "precodecusto": "cost_price",
    "precocusto": "cost_price",
    "custo": "cost_price",
    "costprice": "cost_price",
    "precodevenda": "sale_price",
    "precovenda": "sale_price",
    "preco": "sale_price",
    "valor": "sale_price",
    "price": "sale_price",
    "saleprice": "sale_price",
    "estoque": "stock",
    "quantidade": "stock",
    "qtd": "stock",
    "stock": "stock",
    "estoqueminimo": "minimum_stock",
    "minimumstock": "minimum_stock",
    "estoquemaximo": "maximum_stock",
    "maximumstock": "maximum_stock",
    "unidade": "unit",
    "unit": "unit",
    "codigodebarras": "barcode",
    "codigobarras": "barcode",
    "ean": "barcode",
    "barcode": "barcode",
    "peso": "weight",
    "weight": "weight",
}

REQUIRED_FIELDS = ("sku", "name", "sale_price")

# Nome de exibição de cada campo reconhecido — usado tanto nas mensagens de erro da
# importação (`import_products_use_case.py`) quanto no preview mostrado ao anexar um
# arquivo no chat com a IA (`ai/api/router.py`).
FIELD_LABELS: dict[str, str] = {
    "sku": "SKU",
    "name": "Nome",
    "description": "Descrição",
    "category_name": "Categoria",
    "supplier_name": "Fornecedor",
    "cost_price": "Preço de custo",
    "sale_price": "Preço de venda",
    "stock": "Estoque",
    "minimum_stock": "Estoque mínimo",
    "maximum_stock": "Estoque máximo",
    "unit": "Unidade",
    "barcode": "Código de barras",
    "weight": "Peso",
}


def parse_rows(filename: str, data: bytes) -> list[dict[str, str]]:
    return _parse_rows(filename, data, HEADER_ALIASES)
