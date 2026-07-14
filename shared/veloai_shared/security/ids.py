"""Geração de identificadores UUIDv7, conforme 05-BANCO-DE-DADOS.md e 18-DATABASE-01.md
("Utilizar UUID v7. Nunca utilizar Integer Auto Increment.").

Python 3.13 ainda não possui `uuid.uuid7()` nativo (previsto apenas para 3.14), por isso
utilizamos a biblioteca `uuid_utils`, convertendo sempre para `uuid.UUID` da stdlib para
manter compatibilidade com o tipo `Uuid` do SQLAlchemy."""

from __future__ import annotations

import uuid

import uuid_utils


def new_uuid7() -> uuid.UUID:
    """Retorna um novo UUIDv7 (ordenável por tempo de criação) como `uuid.UUID` padrão."""

    return uuid.UUID(str(uuid_utils.uuid7()))


def short_id(value: uuid.UUID) -> str:
    """Retorna os 12 primeiros caracteres hexadecimais de um UUID, usados para compor
    nomes de banco de dados de tenant (`tenant_<short_id>`)."""

    return value.hex[:12]
