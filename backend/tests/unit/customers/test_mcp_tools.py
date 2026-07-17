import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from veloai_shared.responses import PaginationMeta

from app.modules.customers.mcp_tools.create_customer_tool import CreateCustomerTool
from app.modules.customers.mcp_tools.get_customer_tool import GetCustomerTool
from app.modules.customers.mcp_tools.search_customers_tool import SearchCustomersTool
from app.modules.customers.permissions import CUSTOMERS_CREATE, CUSTOMERS_VIEW
from app.modules.customers.schemas.customer import CustomerResponse
from app.modules.customers.use_cases.list_customers_use_case import ListCustomersResult


def _build_customer_response(**overrides: object) -> CustomerResponse:
    now = datetime.now(UTC)
    return CustomerResponse(
        id=overrides.get("id", uuid.uuid4()),
        code="C000001",
        type="PF",
        name="João Silva",
        document="12345678901",
        state_registration=None,
        municipal_registration=None,
        email=None,
        phone=None,
        mobile=None,
        whatsapp=None,
        zipcode=None,
        street=None,
        number=None,
        district=None,
        city=None,
        state=None,
        country="Brasil",
        notes=None,
        active=True,
        created_at=now,
        updated_at=now,
    )


def test_create_customer_tool_has_correct_permission_and_service() -> None:
    tool = CreateCustomerTool()

    assert tool.permission == CUSTOMERS_CREATE
    assert tool.service == "customers"
    assert tool.parameters_schema()["properties"]["name"]["type"] == "string"


async def test_create_customer_tool_executes_use_case_with_minimal_fields() -> None:
    connection_manager = MagicMock()
    tool = CreateCustomerTool()
    customer_response = _build_customer_response()

    with patch(
        "app.modules.customers.mcp_tools.create_customer_tool.CreateCustomerUseCase"
    ) as use_case_cls:
        use_case_cls.return_value.execute = AsyncMock(return_value=customer_response)

        result = await tool.execute(
            connection_manager=connection_manager,
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            arguments={"type": "PF", "name": "João Silva", "document": "12345678901"},
        )

    assert result["name"] == "João Silva"
    called_payload = use_case_cls.return_value.execute.call_args.kwargs["payload"]
    assert called_payload.type == "PF"
    assert called_payload.document == "12345678901"
    assert called_payload.country == "Brasil"


def test_search_customers_tool_has_correct_permission() -> None:
    tool = SearchCustomersTool()

    assert tool.permission == CUSTOMERS_VIEW
    assert tool.service == "customers"


async def test_search_customers_tool_executes_use_case_with_fixed_pagination() -> None:
    connection_manager = MagicMock()
    tool = SearchCustomersTool()
    customer_response = _build_customer_response()

    with patch(
        "app.modules.customers.mcp_tools.search_customers_tool.ListCustomersUseCase"
    ) as use_case_cls:
        use_case_cls.return_value.execute = AsyncMock(
            return_value=ListCustomersResult(
                items=[customer_response],
                meta=PaginationMeta(page=1, page_size=10, total=1, pages=1),
            )
        )

        result = await tool.execute(
            connection_manager=connection_manager,
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            arguments={"search": "João"},
        )

    assert result["total"] == 1
    assert len(result["items"]) == 1
    filters_used = use_case_cls.return_value.execute.call_args.kwargs["filters"]
    assert filters_used.page == 1
    assert filters_used.page_size == 10
    assert filters_used.search == "João"


def test_get_customer_tool_has_correct_permission() -> None:
    tool = GetCustomerTool()

    assert tool.permission == CUSTOMERS_VIEW
    assert tool.service == "customers"


async def test_get_customer_tool_executes_use_case() -> None:
    connection_manager = MagicMock()
    tool = GetCustomerTool()
    customer_id = uuid.uuid4()
    customer_response = _build_customer_response(id=customer_id)

    with patch(
        "app.modules.customers.mcp_tools.get_customer_tool.GetCustomerUseCase"
    ) as use_case_cls:
        use_case_cls.return_value.execute = AsyncMock(return_value=customer_response)

        result = await tool.execute(
            connection_manager=connection_manager,
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            arguments={"customer_id": str(customer_id)},
        )

    assert result["id"] == str(customer_id)


async def test_get_customer_tool_raises_value_error_for_invalid_uuid() -> None:
    connection_manager = MagicMock()
    tool = GetCustomerTool()

    with pytest.raises(ValueError):
        await tool.execute(
            connection_manager=connection_manager,
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            arguments={"customer_id": "not-a-uuid"},
        )
