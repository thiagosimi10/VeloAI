import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.ai_gateway_client import AIGatewayResult
from app.modules.ai.schemas.ai import AiConversationFilterParams
from app.modules.ai.use_cases.ask_ai_use_case import AskAIUseCase
from app.modules.ai.use_cases.list_ai_conversations_use_case import ListAiConversationsUseCase
from app.modules.users.schemas.user import UserResponse


def _connection_manager_with_session(session: AsyncMock) -> MagicMock:
    @asynccontextmanager
    async def _session_context(*_args: object, **_kwargs: object):
        yield session

    manager = MagicMock()
    manager.session_for_tenant = MagicMock(side_effect=_session_context)
    return manager


def _build_ai_gateway_client(**overrides: object) -> MagicMock:
    result = AIGatewayResult(
        text=overrides.get("text", "Você vendeu R$ 12.340,00 em maio."),
        model=overrides.get("model", "gemini-3.1-flash-lite"),
        input_tokens=overrides.get("input_tokens", 40),
        output_tokens=overrides.get("output_tokens", 20),
        cached=overrides.get("cached", False),
        estimated_cost=overrides.get("estimated_cost", Decimal("0.0000120")),
    )
    client = MagicMock()
    client.generate = AsyncMock(return_value=result)
    return client


def _build_user_response() -> UserResponse:
    return UserResponse(
        id=uuid.uuid4(), first_name="Ana", last_name="Souza", email="ana@empresa.test", active=True
    )


async def test_ask_ai_returns_response_from_ai_gateway() -> None:
    session = AsyncMock()
    connection_manager = _connection_manager_with_session(session)
    ai_gateway_client = _build_ai_gateway_client()
    use_case = AskAIUseCase(
        connection_manager=connection_manager, ai_gateway_client=ai_gateway_client
    )

    with (
        patch(
            "app.modules.ai.use_cases.ask_ai_use_case.GetUserUseCase"
        ) as get_user_use_case_cls,
        patch(
            "app.modules.ai.use_cases.ask_ai_use_case.get_company_display_name",
            AsyncMock(return_value="Oficina do João"),
        ),
        patch(
            "app.modules.ai.use_cases.ask_ai_use_case.AiConversationRepository"
        ) as repo_cls,
        patch("app.modules.ai.use_cases.ask_ai_use_case.record_audit_log", AsyncMock()),
    ):
        get_user_use_case_cls.return_value.execute = AsyncMock(return_value=_build_user_response())
        repo_cls.return_value.create = AsyncMock()

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            role="Administrador",
            prompt="Quanto vendi em maio?",
        )

    assert result.response == "Você vendeu R$ 12.340,00 em maio."
    assert result.model == "gemini-3.1-flash-lite"
    assert result.tokens == 60
    assert result.cached is False
    assert result.estimated_cost == Decimal("0.0000120")

    system_prompt = ai_gateway_client.generate.call_args.kwargs["system_prompt"]
    assert "Oficina do João" in system_prompt
    assert "Ana Souza" in system_prompt
    assert "Administrador" in system_prompt


async def test_ask_ai_persists_conversation_with_summed_tokens() -> None:
    session = AsyncMock()
    connection_manager = _connection_manager_with_session(session)
    ai_gateway_client = _build_ai_gateway_client(input_tokens=5, output_tokens=3)
    use_case = AskAIUseCase(
        connection_manager=connection_manager, ai_gateway_client=ai_gateway_client
    )

    saved_conversations: list[object] = []

    async def _fake_create(conversation: object) -> object:
        conversation.id = uuid.uuid4()  # type: ignore[attr-defined]
        conversation.created_at = datetime.now(UTC)  # type: ignore[attr-defined]
        saved_conversations.append(conversation)
        return conversation

    with (
        patch(
            "app.modules.ai.use_cases.ask_ai_use_case.GetUserUseCase"
        ) as get_user_use_case_cls,
        patch(
            "app.modules.ai.use_cases.ask_ai_use_case.get_company_display_name",
            AsyncMock(return_value="Oficina do João"),
        ),
        patch(
            "app.modules.ai.use_cases.ask_ai_use_case.AiConversationRepository"
        ) as repo_cls,
        patch("app.modules.ai.use_cases.ask_ai_use_case.record_audit_log", AsyncMock()),
    ):
        get_user_use_case_cls.return_value.execute = AsyncMock(return_value=_build_user_response())
        repo_cls.return_value.create = AsyncMock(side_effect=_fake_create)

        await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            role="Administrador",
            prompt="Quanto vendi em maio?",
        )

    assert len(saved_conversations) == 1
    conversation = saved_conversations[0]
    assert conversation.tokens == 8
    assert conversation.model == "gemini-3.1-flash-lite"
    assert conversation.prompt == "Quanto vendi em maio?"


async def test_list_ai_conversations_returns_paginated_items() -> None:
    connection_manager = _connection_manager_with_session(AsyncMock())
    use_case = ListAiConversationsUseCase(connection_manager=connection_manager)

    conversation = MagicMock()
    conversation.id = uuid.uuid4()
    conversation.prompt = "Quanto vendi em maio?"
    conversation.response = "Você vendeu R$ 12.340,00 em maio."
    conversation.tokens = 60
    conversation.model = "gemini-3.1-flash-lite"
    conversation.execution_time = Decimal("1.234")
    conversation.created_at = datetime.now(UTC)

    with patch(
        "app.modules.ai.use_cases.list_ai_conversations_use_case.AiConversationRepository"
    ) as repo_cls:
        repo_cls.return_value.list_by_tenant = AsyncMock(return_value=([conversation], 1))

        result = await use_case.execute(
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            filters=AiConversationFilterParams(page=1, page_size=20),
        )

    assert len(result.items) == 1
    assert result.items[0].prompt == "Quanto vendi em maio?"
    assert result.meta.total == 1
    assert result.meta.pages == 1
