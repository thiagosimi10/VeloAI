"""Utilitários de segurança compartilhados: hashing de senha (Argon2id), geração de
identificadores (UUIDv7) e tokens JWT, conforme 05-BANCO-DE-DADOS.md, 29-SECURITY.md e
02-ARQUITETURA.md."""

from veloai_shared.security.ids import new_uuid7
from veloai_shared.security.jwt import (
    TokenError,
    TokenExpiredError,
    TokenInvalidError,
    create_token,
    decode_token,
)
from veloai_shared.security.password import hash_password, needs_rehash, verify_password

__all__ = [
    "new_uuid7",
    "hash_password",
    "verify_password",
    "needs_rehash",
    "create_token",
    "decode_token",
    "TokenError",
    "TokenExpiredError",
    "TokenInvalidError",
]
