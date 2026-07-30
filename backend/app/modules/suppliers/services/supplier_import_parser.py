"""Configuração de importação em lote de Fornecedores — apelidos de coluna
reconhecidos e campos obrigatórios. O parsing CSV/XLSX em si é genérico, ver
`app/core/spreadsheet_parser.py`."""

from __future__ import annotations

from app.core.spreadsheet_parser import parse_rows as _parse_rows

HEADER_ALIASES: dict[str, str] = {
    "tipo": "type",
    "type": "type",
    "nome": "name",
    "name": "name",
    "fornecedor": "name",
    "documento": "document",
    "cpf": "document",
    "cnpj": "document",
    "cpfcnpj": "document",
    "cnpjcpf": "document",
    "email": "email",
    "emails": "email",
    "telefone": "phone",
    "fone": "phone",
    "phone": "phone",
    "celular": "mobile",
    "mobile": "mobile",
    "whatsapp": "whatsapp",
    "cep": "zipcode",
    "zipcode": "zipcode",
    "endereco": "street",
    "rua": "street",
    "street": "street",
    "numero": "number",
    "number": "number",
    "bairro": "district",
    "district": "district",
    "cidade": "city",
    "city": "city",
    "estado": "state",
    "uf": "state",
    "state": "state",
    "pais": "country",
    "country": "country",
    "observacoes": "notes",
    "obs": "notes",
    "notes": "notes",
}

REQUIRED_FIELDS = ("name", "document")

FIELD_LABELS: dict[str, str] = {
    "type": "Tipo",
    "name": "Nome",
    "document": "CPF/CNPJ",
    "email": "E-mail",
    "phone": "Telefone",
    "mobile": "Celular",
    "whatsapp": "WhatsApp",
    "zipcode": "CEP",
    "street": "Endereço",
    "number": "Número",
    "district": "Bairro",
    "city": "Cidade",
    "state": "Estado",
    "country": "País",
    "notes": "Observações",
}


def parse_rows(filename: str, data: bytes) -> list[dict[str, str]]:
    return _parse_rows(filename, data, HEADER_ALIASES)
