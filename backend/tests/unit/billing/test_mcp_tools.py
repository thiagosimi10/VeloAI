import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from app.modules.billing.mcp_tools.get_subscription_status_tool import (
    GetSubscriptionStatusTool,
)
from app.modules.billing.permissions import BILLING_VIEW
from app.modules.billing.schemas.billing import SubscriptionResponse


def test_get_subscription_status_tool_has_correct_permission_and_service() -> None:
    tool = GetSubscriptionStatusTool()

    assert tool.permission == BILLING_VIEW
    assert tool.service == "billing"
    assert tool.parameters_schema()["properties"] == {}


async def test_get_subscription_status_tool_executes_use_case() -> None:
    connection_manager = MagicMock()
    tool = GetSubscriptionStatusTool()
    subscription = SubscriptionResponse(
        plan_name="VeloAI Professional",
        plan_price=Decimal("129.90"),
        status="TRIAL",
        trial_ends_at=datetime.now(UTC) + timedelta(days=5),
        current_period_ends_at=None,
        days_remaining=4,
    )

    with patch(
        "app.modules.billing.mcp_tools.get_subscription_status_tool.GetSubscriptionUseCase"
    ) as use_case_cls:
        use_case_cls.return_value.execute = AsyncMock(return_value=subscription)

        result = await tool.execute(
            connection_manager=connection_manager,
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            arguments={},
        )

    assert result["plan_name"] == "VeloAI Professional"
    assert result["status"] == "TRIAL"
    use_case_cls.return_value.execute.assert_awaited_once()
