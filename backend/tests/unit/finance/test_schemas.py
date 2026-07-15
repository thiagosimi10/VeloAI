import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.finance.schemas.account_payable import AccountPayableResponse
from app.modules.finance.schemas.account_receivable import (
    AccountReceivableResponse,
    CreateAccountReceivableRequest,
)
from app.modules.finance.schemas.cash_flow import CreateCashFlowEntryRequest


def test_create_account_receivable_rejects_zero_amount() -> None:
    with pytest.raises(ValidationError):
        CreateAccountReceivableRequest(
            customer_id=uuid.uuid4(), due_date=date(2026, 8, 1), amount=Decimal("0.00")
        )


def test_account_receivable_response_is_overdue_when_pending_and_past_due() -> None:
    response = AccountReceivableResponse(
        id=uuid.uuid4(),
        customer_id=uuid.uuid4(),
        due_date=date.today() - timedelta(days=1),
        amount=Decimal("100.00"),
        status="pending",
        payment_date=None,
    )

    assert response.is_overdue is True


def test_account_receivable_response_is_not_overdue_when_received() -> None:
    response = AccountReceivableResponse(
        id=uuid.uuid4(),
        customer_id=uuid.uuid4(),
        due_date=date.today() - timedelta(days=1),
        amount=Decimal("100.00"),
        status="received",
        payment_date=date.today(),
    )

    assert response.is_overdue is False


def test_account_payable_response_is_not_overdue_when_due_date_in_future() -> None:
    response = AccountPayableResponse(
        id=uuid.uuid4(),
        supplier_id=uuid.uuid4(),
        due_date=date.today() + timedelta(days=1),
        amount=Decimal("100.00"),
        status="pending",
        payment_date=None,
    )

    assert response.is_overdue is False


def test_create_cash_flow_entry_rejects_invalid_type() -> None:
    with pytest.raises(ValidationError):
        CreateCashFlowEntryRequest(type="invalid", category="Recebimento", amount=Decimal("10.00"))
