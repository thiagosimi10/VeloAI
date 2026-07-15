"""Utilitários internos compartilhados entre os use cases Financeiros. Diferente de
`service_orders`/`sales`, as respostas aqui mapeiam direto para colunas reais do
modelo SQLAlchemy (sem uma lista de itens embutida sem atributo correspondente) — não
há necessidade da defesa `to_response`/`hasattr` usada em `service_orders/use_cases/
_helpers.py` e `sales/use_cases/_helpers.py`."""

from __future__ import annotations

from typing import Any

from veloai_shared.exceptions import ValidationError
from veloai_shared.schema.tenant import AccountPayable, AccountReceivable

from app.modules.finance.schemas.account_payable import AccountPayableResponse
from app.modules.finance.schemas.account_receivable import AccountReceivableResponse

_RECEIVABLE_TRANSITIONS: dict[str, tuple[str, ...]] = {
    "pending": ("received", "cancelled"),
    "received": (),
    "cancelled": (),
}

_PAYABLE_TRANSITIONS: dict[str, tuple[str, ...]] = {
    "pending": ("paid", "cancelled"),
    "paid": (),
    "cancelled": (),
}


def ensure_receivable_transition_allowed(
    receivable: AccountReceivable, target_status: str
) -> None:
    allowed = _RECEIVABLE_TRANSITIONS.get(receivable.status, ())
    if target_status not in allowed:
        raise ValidationError(
            f"Não é possível mudar de '{receivable.status}' para '{target_status}'.",
            code="ACCOUNT_RECEIVABLE_INVALID_TRANSITION",
        )


def ensure_receivable_is_editable(receivable: AccountReceivable) -> None:
    if receivable.status != "pending":
        raise ValidationError(
            f"Não é possível alterar uma Conta a Receber '{receivable.status}'.",
            code="ACCOUNT_RECEIVABLE_NOT_EDITABLE",
        )


def ensure_payable_transition_allowed(payable: AccountPayable, target_status: str) -> None:
    allowed = _PAYABLE_TRANSITIONS.get(payable.status, ())
    if target_status not in allowed:
        raise ValidationError(
            f"Não é possível mudar de '{payable.status}' para '{target_status}'.",
            code="ACCOUNT_PAYABLE_INVALID_TRANSITION",
        )


def ensure_payable_is_editable(payable: AccountPayable) -> None:
    if payable.status != "pending":
        raise ValidationError(
            f"Não é possível alterar uma Conta a Pagar '{payable.status}'.",
            code="ACCOUNT_PAYABLE_NOT_EDITABLE",
        )


def serialize_receivable(receivable: AccountReceivable) -> dict[str, Any]:
    return AccountReceivableResponse.model_validate(receivable).model_dump(mode="json")


def serialize_payable(payable: AccountPayable) -> dict[str, Any]:
    return AccountPayableResponse.model_validate(payable).model_dump(mode="json")
