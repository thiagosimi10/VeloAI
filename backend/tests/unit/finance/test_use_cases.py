import uuid
from contextlib import asynccontextmanager
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from veloai_shared.exceptions import NotFoundError, ValidationError

from app.modules.finance.schemas.account_payable import (
    AccountPayableFilterParams,
    CreateAccountPayableRequest,
    UpdateAccountPayableRequest,
)
from app.modules.finance.schemas.account_receivable import (
    AccountReceivableFilterParams,
    CreateAccountReceivableRequest,
    UpdateAccountReceivableRequest,
)
from app.modules.finance.schemas.cash_flow import CashFlowFilterParams, CreateCashFlowEntryRequest
from app.modules.finance.use_cases.cancel_account_payable_use_case import (
    CancelAccountPayableUseCase,
)
from app.modules.finance.use_cases.cancel_account_receivable_use_case import (
    CancelAccountReceivableUseCase,
)
from app.modules.finance.use_cases.create_account_payable_use_case import (
    CreateAccountPayableUseCase,
)
from app.modules.finance.use_cases.create_account_receivable_use_case import (
    CreateAccountReceivableUseCase,
)
from app.modules.finance.use_cases.create_cash_flow_entry_use_case import (
    CreateCashFlowEntryUseCase,
)
from app.modules.finance.use_cases.get_account_receivable_use_case import (
    GetAccountReceivableUseCase,
)
from app.modules.finance.use_cases.list_account_receivables_use_case import (
    ListAccountReceivablesUseCase,
)
from app.modules.finance.use_cases.list_cash_flow_entries_use_case import (
    ListCashFlowEntriesUseCase,
)
from app.modules.finance.use_cases.pay_account_payable_use_case import PayAccountPayableUseCase
from app.modules.finance.use_cases.receive_account_receivable_use_case import (
    ReceiveAccountReceivableUseCase,
)
from app.modules.finance.use_cases.update_account_payable_use_case import (
    UpdateAccountPayableUseCase,
)
from app.modules.finance.use_cases.update_account_receivable_use_case import (
    UpdateAccountReceivableUseCase,
)


def _connection_manager_with_session(session: AsyncMock) -> MagicMock:
    @asynccontextmanager
    async def _session_context(*_args: object, **_kwargs: object):
        yield session

    manager = MagicMock()
    manager.session_for_tenant = MagicMock(side_effect=_session_context)
    return manager


def _build_receivable_mock(**overrides: object) -> MagicMock:
    receivable = MagicMock()
    receivable.id = overrides.get("id", uuid.uuid4())
    receivable.customer_id = overrides.get("customer_id", uuid.uuid4())
    receivable.due_date = overrides.get("due_date", date(2026, 8, 1))
    receivable.amount = overrides.get("amount", Decimal("980.00"))
    receivable.status = overrides.get("status", "pending")
    receivable.payment_date = overrides.get("payment_date")
    return receivable


def _build_payable_mock(**overrides: object) -> MagicMock:
    payable = MagicMock()
    payable.id = overrides.get("id", uuid.uuid4())
    payable.supplier_id = overrides.get("supplier_id", uuid.uuid4())
    payable.due_date = overrides.get("due_date", date(2026, 8, 1))
    payable.amount = overrides.get("amount", Decimal("320.00"))
    payable.status = overrides.get("status", "pending")
    payable.payment_date = overrides.get("payment_date")
    return payable


# --- Contas a Receber ---------------------------------------------------------------


async def test_create_account_receivable_rejects_nonexistent_customer() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CreateAccountReceivableUseCase(connection_manager=connection_manager)
    payload = CreateAccountReceivableRequest(
        customer_id=uuid.uuid4(), due_date=date(2026, 8, 1), amount=Decimal("100.00")
    )

    with patch(
        "app.modules.finance.use_cases.create_account_receivable_use_case.GetCustomerUseCase"
    ) as get_customer_cls:
        get_customer_cls.return_value.execute = AsyncMock(
            side_effect=NotFoundError("Cliente não encontrado.", code="CUSTOMER_NOT_FOUND")
        )

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                payload=payload,
            )


async def test_get_account_receivable_raises_not_found() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = GetAccountReceivableUseCase(connection_manager=connection_manager)

    with patch(
        "app.modules.finance.use_cases.get_account_receivable_use_case.AccountReceivableRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(), database_name="tenant_abc", receivable_id=uuid.uuid4()
            )


async def test_list_account_receivables_computes_pagination_meta() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = ListAccountReceivablesUseCase(connection_manager=connection_manager)
    receivable = _build_receivable_mock()

    with patch(
        "app.modules.finance.use_cases.list_account_receivables_use_case."
        "AccountReceivableRepository"
    ) as repo_cls:
        repo_cls.return_value.list = AsyncMock(return_value=([receivable], 25))

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            filters=AccountReceivableFilterParams(page=1, page_size=10),
        )

    assert result.meta.total == 25
    assert result.meta.pages == 3
    assert len(result.items) == 1


async def test_update_account_receivable_rejects_when_not_pending() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = UpdateAccountReceivableUseCase(connection_manager=connection_manager)
    receivable = _build_receivable_mock(status="received")

    with patch(
        "app.modules.finance.use_cases.update_account_receivable_use_case."
        "AccountReceivableRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=receivable)

        with pytest.raises(ValidationError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                receivable_id=receivable.id,
                payload=UpdateAccountReceivableRequest(amount=Decimal("50.00")),
            )


async def test_receive_account_receivable_rejects_invalid_transition() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = ReceiveAccountReceivableUseCase(connection_manager=connection_manager)
    receivable = _build_receivable_mock(status="cancelled")

    with patch(
        "app.modules.finance.use_cases.receive_account_receivable_use_case."
        "AccountReceivableRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=receivable)

        with pytest.raises(ValidationError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                receivable_id=receivable.id,
            )


async def test_receive_account_receivable_creates_cash_flow_entry() -> None:
    session = AsyncMock()
    connection_manager = _connection_manager_with_session(session)
    use_case = ReceiveAccountReceivableUseCase(connection_manager=connection_manager)
    receivable = _build_receivable_mock(status="pending", amount=Decimal("980.00"))

    with (
        patch(
            "app.modules.finance.use_cases.receive_account_receivable_use_case."
            "AccountReceivableRepository"
        ) as repo_cls,
        patch(
            "app.modules.finance.use_cases.receive_account_receivable_use_case.CashFlowRepository"
        ) as cash_flow_repo_cls,
        patch(
            "app.modules.finance.use_cases.receive_account_receivable_use_case.record_audit_log",
            AsyncMock(),
        ),
    ):
        def _apply_update(target: object, data: dict[str, object]) -> object:
            for field, value in data.items():
                setattr(target, field, value)
            return target

        repo_cls.return_value.get_by_id = AsyncMock(return_value=receivable)
        # Precisa mutar `receivable` de verdade (como o `update()` real faz via
        # `setattr`) para que a resposta reflita `status="received"` — um
        # `AsyncMock()` sem `side_effect` não alteraria o objeto.
        repo_cls.return_value.update = AsyncMock(side_effect=_apply_update)
        cash_flow_repo_cls.return_value.create = AsyncMock()

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            receivable_id=receivable.id,
        )

        cash_flow_repo_cls.return_value.create.assert_awaited_once()
        created_entry = cash_flow_repo_cls.return_value.create.call_args.args[0]
        assert created_entry.type == "in"
        assert created_entry.amount == Decimal("980.00")
        repo_cls.return_value.update.assert_awaited_once_with(
            receivable, {"status": "received", "payment_date": date.today()}
        )

    assert result.status == "received"


async def test_cancel_account_receivable_rejects_invalid_transition() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CancelAccountReceivableUseCase(connection_manager=connection_manager)
    receivable = _build_receivable_mock(status="received")

    with patch(
        "app.modules.finance.use_cases.cancel_account_receivable_use_case."
        "AccountReceivableRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=receivable)

        with pytest.raises(ValidationError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                receivable_id=receivable.id,
            )


# --- Contas a Pagar -------------------------------------------------------------------


async def test_create_account_payable_rejects_nonexistent_supplier() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CreateAccountPayableUseCase(connection_manager=connection_manager)
    payload = CreateAccountPayableRequest(
        supplier_id=uuid.uuid4(), due_date=date(2026, 8, 1), amount=Decimal("100.00")
    )

    with patch(
        "app.modules.finance.use_cases.create_account_payable_use_case.GetSupplierUseCase"
    ) as get_supplier_cls:
        get_supplier_cls.return_value.execute = AsyncMock(
            side_effect=NotFoundError("Fornecedor não encontrado.", code="SUPPLIER_NOT_FOUND")
        )

        with pytest.raises(NotFoundError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                payload=payload,
            )


async def test_update_account_payable_rejects_when_not_pending() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = UpdateAccountPayableUseCase(connection_manager=connection_manager)
    payable = _build_payable_mock(status="paid")

    with patch(
        "app.modules.finance.use_cases.update_account_payable_use_case.AccountPayableRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=payable)

        with pytest.raises(ValidationError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                payable_id=payable.id,
                payload=UpdateAccountPayableRequest(amount=Decimal("50.00")),
            )


async def test_pay_account_payable_creates_cash_flow_entry() -> None:
    session = AsyncMock()
    connection_manager = _connection_manager_with_session(session)
    use_case = PayAccountPayableUseCase(connection_manager=connection_manager)
    payable = _build_payable_mock(status="pending", amount=Decimal("320.00"))

    with (
        patch(
            "app.modules.finance.use_cases.pay_account_payable_use_case.AccountPayableRepository"
        ) as repo_cls,
        patch(
            "app.modules.finance.use_cases.pay_account_payable_use_case.CashFlowRepository"
        ) as cash_flow_repo_cls,
        patch(
            "app.modules.finance.use_cases.pay_account_payable_use_case.record_audit_log",
            AsyncMock(),
        ),
    ):
        def _apply_update(target: object, data: dict[str, object]) -> object:
            for field, value in data.items():
                setattr(target, field, value)
            return target

        repo_cls.return_value.get_by_id = AsyncMock(return_value=payable)
        # Precisa mutar `payable` de verdade (como o `update()` real faz via
        # `setattr`) para que a resposta reflita `status="paid"`.
        repo_cls.return_value.update = AsyncMock(side_effect=_apply_update)
        cash_flow_repo_cls.return_value.create = AsyncMock()

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            payable_id=payable.id,
        )

        created_entry = cash_flow_repo_cls.return_value.create.call_args.args[0]
        assert created_entry.type == "out"
        assert created_entry.amount == Decimal("320.00")

    assert result.status == "paid"


async def test_cancel_account_payable_rejects_invalid_transition() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CancelAccountPayableUseCase(connection_manager=connection_manager)
    payable = _build_payable_mock(status="paid")

    with patch(
        "app.modules.finance.use_cases.cancel_account_payable_use_case.AccountPayableRepository"
    ) as repo_cls:
        repo_cls.return_value.get_by_id = AsyncMock(return_value=payable)

        with pytest.raises(ValidationError):
            await use_case.execute(
                tenant_id=uuid.uuid4(),
                database_name="tenant_abc",
                actor_user_id=uuid.uuid4(),
                payable_id=payable.id,
            )


# --- Fluxo de Caixa -------------------------------------------------------------------


async def test_create_cash_flow_entry_defaults_date_to_today() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = CreateCashFlowEntryUseCase(connection_manager=connection_manager)
    payload = CreateCashFlowEntryRequest(
        type="in", category="Lançamento Avulso", amount=Decimal("50.00")
    )

    async def _fake_create(entry: object) -> object:
        from datetime import UTC, datetime

        # `created_at` usa `server_default=func.now()` — só é aplicado pelo
        # SQLAlchemy num `flush()` real (com a linha de volta do Postgres via
        # RETURNING), que este mock nunca executa; sem isso, `entry.created_at`
        # ficaria `None` e `CashFlowEntryResponse.model_validate` falharia.
        entry.id = uuid.uuid4()  # type: ignore[attr-defined]
        entry.created_at = datetime.now(UTC)  # type: ignore[attr-defined]
        return entry

    with (
        patch(
            "app.modules.finance.use_cases.create_cash_flow_entry_use_case.CashFlowRepository"
        ) as repo_cls,
        patch(
            "app.modules.finance.use_cases.create_cash_flow_entry_use_case.record_audit_log",
            AsyncMock(),
        ),
    ):
        repo_cls.return_value.create = AsyncMock(side_effect=_fake_create)

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            payload=payload,
        )

    assert result.date == date.today()


async def test_list_cash_flow_entries_computes_pagination_meta() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = ListCashFlowEntriesUseCase(connection_manager=connection_manager)
    entry = MagicMock()
    entry.id = uuid.uuid4()
    entry.type = "in"
    entry.category = "Recebimento"
    entry.description = None
    entry.amount = Decimal("980.00")
    entry.date = date.today()
    from datetime import UTC, datetime

    entry.created_at = datetime.now(UTC)

    with patch(
        "app.modules.finance.use_cases.list_cash_flow_entries_use_case.CashFlowRepository"
    ) as repo_cls:
        repo_cls.return_value.list = AsyncMock(return_value=([entry], 5))

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            filters=CashFlowFilterParams(page=1, page_size=20),
        )

    assert result.meta.total == 5
    assert len(result.items) == 1
