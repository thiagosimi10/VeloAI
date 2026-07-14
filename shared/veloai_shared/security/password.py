"""Hashing de senhas com Argon2id, conforme 29-SECURITY.md ("Senhas: Hash Argon2id, Salt
automático. Nunca armazenar senha em texto puro.")."""

from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_hasher = PasswordHasher()


def hash_password(plain_password: str) -> str:
    """Gera o hash Argon2id de uma senha em texto puro."""

    return _hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto puro corresponde ao hash armazenado."""

    try:
        return _hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False


def needs_rehash(hashed_password: str) -> bool:
    """Indica se o hash foi gerado com parâmetros desatualizados e deve ser regravado."""

    return _hasher.check_needs_rehash(hashed_password)
