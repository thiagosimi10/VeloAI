"""Validadores reutilizáveis entre serviços, conforme 00-AI-CONSTITUTION.md ("Nunca
gerar código duplicado"). Usado por schemas Pydantic via `field_validator`."""

from __future__ import annotations

import re


def normalize_document(value: str) -> str:
    """Remove máscara de um CPF/CNPJ e valida o número de dígitos.

    Levanta `ValueError` (capturado pelo Pydantic como erro de validação) quando o
    resultado não tem 11 dígitos (CPF) nem 14 (CNPJ)."""

    digits = re.sub(r"\D", "", value)
    if len(digits) not in (11, 14):
        raise ValueError("Documento deve ser um CPF (11 dígitos) ou CNPJ (14 dígitos).")
    return digits
