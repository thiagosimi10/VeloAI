import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from app.modules.knowledge.mcp_tools.search_knowledge_tool import SearchKnowledgeTool
from app.modules.knowledge.permissions import KNOWLEDGE_VIEW
from app.modules.knowledge.schemas.knowledge import KnowledgeSearchResult


def test_search_knowledge_tool_has_correct_permission_and_service() -> None:
    tool = SearchKnowledgeTool()

    assert tool.permission == KNOWLEDGE_VIEW
    assert tool.service == "knowledge"
    assert tool.parameters_schema()["properties"]["query"]["type"] == "string"


async def test_search_knowledge_tool_executes_use_case() -> None:
    connection_manager = MagicMock()
    tool = SearchKnowledgeTool()

    with (
        patch("app.modules.knowledge.mcp_tools.search_knowledge_tool.get_ai_gateway_client"),
        patch("app.modules.knowledge.mcp_tools.search_knowledge_tool.get_qdrant_client"),
        patch(
            "app.modules.knowledge.mcp_tools.search_knowledge_tool.SearchKnowledgeUseCase"
        ) as use_case_cls,
    ):
        use_case_cls.return_value.execute = AsyncMock(
            return_value=[
                KnowledgeSearchResult(
                    title="Política de Garantia", content="90 dias de garantia.", score=0.9
                )
            ]
        )

        result = await tool.execute(
            connection_manager=connection_manager,
            tenant_id=uuid.uuid4(),
            database_name="tenant_abc",
            actor_user_id=uuid.uuid4(),
            arguments={"query": "qual a garantia?"},
        )

    assert result["results"] == [
        {"title": "Política de Garantia", "content": "90 dias de garantia.", "score": 0.9}
    ]
    use_case_cls.return_value.execute.assert_awaited_once()
    assert use_case_cls.return_value.execute.call_args.kwargs["query"] == "qual a garantia?"
