"""Utilitários de segurança compartilhados: hashing de senha (Argon2id) e geração de
identificadores (UUIDv7), conforme 05-BANCO-DE-DADOS.md e 29-SECURITY.md."""

from veloai_shared.security.ids import new_uuid7
from veloai_shared.security.password import hash_password, needs_rehash, verify_password

__all__ = ["new_uuid7", "hash_password", "verify_password", "needs_rehash"]
