"""Tool MCP: busca semanticamente na Base de Conhecimento, conforme
docs/20-MCP-TOOLS.md (`SearchKnowledge`). Reaproveita `SearchKnowledgeUseCase` já
existente."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel

from app.core.ai_gateway_client import get_ai_gateway_client
from app.core.ai_tools import AITool
from app.core.database import TenantConnectionManager
from app.core.qdrant_client import get_qdrant_client
from app.modules.knowledge.permissions import KNOWLEDGE_VIEW
from app.modules.knowledge.use_cases.search_knowledge_use_case import SearchKnowledgeUseCase


class SearchKnowledgeToolInput(BaseModel):
    query: str


class SearchKnowledgeTool(AITool):
    name = "SearchKnowledge"
    description = (
        "Busca semanticamente na base de conhecimento da empresa "
        "(políticas, FAQs, documentação interna)."
    )
    permission = KNOWLEDGE_VIEW
    service = "knowledge"
    input_model = SearchKnowledgeToolInput

    async def execute(
        self,
        *,
        connection_manager: TenantConnectionManager,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        tool_input = SearchKnowledgeToolInput.model_validate(arguments)
        use_case = SearchKnowledgeUseCase(
            connection_manager=connection_manager,
            ai_gateway_client=get_ai_gateway_client(),
            qdrant_client=get_qdrant_client(),
        )
        results = await use_case.execute(
            tenant_id=tenant_id, database_name=database_name, query=tool_input.query
        )
        return {"results": [result.model_dump(mode="json") for result in results]}
