"""Controller do módulo Financeiro. Responsabilidade: receber requisição, validar
permissão via `require_permission` e delegar ao Use Case — nunca conter regra de
negócio (00-AI-CONSTITUTION.md). Sem `DELETE` em nenhuma rota — nenhum lançamento
financeiro é excluído (11-FINANCEIRO.md: "Nunca excluir lançamentos financeiros.
Sempre utilizar estorno.")."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from veloai_shared.responses import SuccessResponse

from app.core.database import TenantConnectionManager, get_tenant_connection_manager
from app.core.dependencies import CurrentUser, require_permission
from app.modules.finance.permissions import (
    FINANCE_CANCEL,
    FINANCE_CREATE,
    FINANCE_PAY,
    FINANCE_RECEIVE,
    FINANCE_UPDATE,
    FINANCE_VIEW,
)
from app.modules.finance.schemas.account_payable import (
    AccountPayableFilterParams,
    AccountPayableResponse,
    CreateAccountPayableRequest,
    UpdateAccountPayableRequest,
)
from app.modules.finance.schemas.account_receivable import (
    AccountReceivableFilterParams,
    AccountReceivableResponse,
    CreateAccountReceivableRequest,
    UpdateAccountReceivableRequest,
)
from app.modules.finance.schemas.cash_flow import (
    CashFlowEntryResponse,
    CashFlowFilterParams,
    CreateCashFlowEntryRequest,
)
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
from app.modules.finance.use_cases.get_account_payable_use_case import GetAccountPayableUseCase
from app.modules.finance.use_cases.get_account_receivable_use_case import (
    GetAccountReceivableUseCase,
)
from app.modules.finance.use_cases.list_account_payables_use_case import (
    ListAccountPayablesUseCase,
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

router = APIRouter(tags=["finance"])


# --- Contas a Receber --------------------------------------------------------------


@router.get("/accounts-receivable")
async def list_accounts_receivable(
    filters: AccountReceivableFilterParams = Depends(),
    current_user: CurrentUser = Depends(require_permission(FINANCE_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[AccountReceivableResponse]]:
    use_case = ListAccountReceivablesUseCase(connection_manager=connection_manager)
    result = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        filters=filters,
    )
    return SuccessResponse(
        message="Contas a Receber listadas com sucesso.", data=result.items, meta=result.meta
    )


@router.get("/accounts-receivable/{receivable_id}")
async def get_account_receivable(
    receivable_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(FINANCE_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[AccountReceivableResponse]:
    use_case = GetAccountReceivableUseCase(connection_manager=connection_manager)
    receivable = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        receivable_id=receivable_id,
    )
    return SuccessResponse(message="Conta a Receber encontrada.", data=receivable)


@router.post("/accounts-receivable", status_code=201)
async def create_account_receivable(
    payload: CreateAccountReceivableRequest,
    current_user: CurrentUser = Depends(require_permission(FINANCE_CREATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[AccountReceivableResponse]:
    use_case = CreateAccountReceivableUseCase(connection_manager=connection_manager)
    receivable = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        payload=payload,
    )
    return SuccessResponse(message="Conta a Receber criada com sucesso.", data=receivable)


@router.patch("/accounts-receivable/{receivable_id}")
async def update_account_receivable(
    receivable_id: uuid.UUID,
    payload: UpdateAccountReceivableRequest,
    current_user: CurrentUser = Depends(require_permission(FINANCE_UPDATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[AccountReceivableResponse]:
    use_case = UpdateAccountReceivableUseCase(connection_manager=connection_manager)
    receivable = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        receivable_id=receivable_id,
        payload=payload,
    )
    return SuccessResponse(message="Conta a Receber atualizada com sucesso.", data=receivable)


@router.post("/accounts-receivable/{receivable_id}/receive")
async def receive_account_receivable(
    receivable_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(FINANCE_RECEIVE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[AccountReceivableResponse]:
    use_case = ReceiveAccountReceivableUseCase(connection_manager=connection_manager)
    receivable = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        receivable_id=receivable_id,
    )
    return SuccessResponse(message="Conta a Receber recebida com sucesso.", data=receivable)


@router.post("/accounts-receivable/{receivable_id}/cancel")
async def cancel_account_receivable(
    receivable_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(FINANCE_CANCEL)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[AccountReceivableResponse]:
    use_case = CancelAccountReceivableUseCase(connection_manager=connection_manager)
    receivable = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        receivable_id=receivable_id,
    )
    return SuccessResponse(message="Conta a Receber cancelada com sucesso.", data=receivable)


# --- Contas a Pagar -----------------------------------------------------------------


@router.get("/accounts-payable")
async def list_accounts_payable(
    filters: AccountPayableFilterParams = Depends(),
    current_user: CurrentUser = Depends(require_permission(FINANCE_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[AccountPayableResponse]]:
    use_case = ListAccountPayablesUseCase(connection_manager=connection_manager)
    result = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        filters=filters,
    )
    return SuccessResponse(
        message="Contas a Pagar listadas com sucesso.", data=result.items, meta=result.meta
    )


@router.get("/accounts-payable/{payable_id}")
async def get_account_payable(
    payable_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(FINANCE_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[AccountPayableResponse]:
    use_case = GetAccountPayableUseCase(connection_manager=connection_manager)
    payable = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        payable_id=payable_id,
    )
    return SuccessResponse(message="Conta a Pagar encontrada.", data=payable)


@router.post("/accounts-payable", status_code=201)
async def create_account_payable(
    payload: CreateAccountPayableRequest,
    current_user: CurrentUser = Depends(require_permission(FINANCE_CREATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[AccountPayableResponse]:
    use_case = CreateAccountPayableUseCase(connection_manager=connection_manager)
    payable = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        payload=payload,
    )
    return SuccessResponse(message="Conta a Pagar criada com sucesso.", data=payable)


@router.patch("/accounts-payable/{payable_id}")
async def update_account_payable(
    payable_id: uuid.UUID,
    payload: UpdateAccountPayableRequest,
    current_user: CurrentUser = Depends(require_permission(FINANCE_UPDATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[AccountPayableResponse]:
    use_case = UpdateAccountPayableUseCase(connection_manager=connection_manager)
    payable = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        payable_id=payable_id,
        payload=payload,
    )
    return SuccessResponse(message="Conta a Pagar atualizada com sucesso.", data=payable)


@router.post("/accounts-payable/{payable_id}/pay")
async def pay_account_payable(
    payable_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(FINANCE_PAY)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[AccountPayableResponse]:
    use_case = PayAccountPayableUseCase(connection_manager=connection_manager)
    payable = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        payable_id=payable_id,
    )
    return SuccessResponse(message="Conta a Pagar paga com sucesso.", data=payable)


@router.post("/accounts-payable/{payable_id}/cancel")
async def cancel_account_payable(
    payable_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_permission(FINANCE_CANCEL)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[AccountPayableResponse]:
    use_case = CancelAccountPayableUseCase(connection_manager=connection_manager)
    payable = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        payable_id=payable_id,
    )
    return SuccessResponse(message="Conta a Pagar cancelada com sucesso.", data=payable)


# --- Fluxo de Caixa -------------------------------------------------------------------


@router.get("/cash-flow")
async def list_cash_flow_entries(
    filters: CashFlowFilterParams = Depends(),
    current_user: CurrentUser = Depends(require_permission(FINANCE_VIEW)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[list[CashFlowEntryResponse]]:
    use_case = ListCashFlowEntriesUseCase(connection_manager=connection_manager)
    result = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        filters=filters,
    )
    return SuccessResponse(
        message="Lançamentos de Fluxo de Caixa listados com sucesso.",
        data=result.items,
        meta=result.meta,
    )


@router.post("/cash-flow", status_code=201)
async def create_cash_flow_entry(
    payload: CreateCashFlowEntryRequest,
    current_user: CurrentUser = Depends(require_permission(FINANCE_CREATE)),
    connection_manager: TenantConnectionManager = Depends(get_tenant_connection_manager),
) -> SuccessResponse[CashFlowEntryResponse]:
    use_case = CreateCashFlowEntryUseCase(connection_manager=connection_manager)
    entry = await use_case.execute(
        tenant_id=current_user.tenant_id,
        database_name=current_user.database_name,
        actor_user_id=current_user.user_id,
        payload=payload,
    )
    return SuccessResponse(message="Lançamento registrado com sucesso.", data=entry)
