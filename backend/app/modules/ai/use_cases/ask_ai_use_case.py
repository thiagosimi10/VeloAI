"""Caso de uso: perguntar algo ao assistente de IA. Monta o contexto de
empresa/usuário, delega a geração ao AI Gateway (único ponto de contato com a LLM) e
grava o uso em `ai_conversations`, conforme 28-AI-GATEWAY.md."""

from __future__ import annotations

import time
import uuid
from decimal import Decimal

from veloai_shared.schema.tenant import AiConversation

from app.core.ai_gateway_client import AIGatewayClient
from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.ai.repositories.ai_conversation_repository import AiConversationRepository
from app.modules.ai.schemas.ai import AskAIResponse
from app.modules.ai.use_cases._helpers import build_system_prompt, get_company_display_name
from app.modules.users.use_cases.get_user_use_case import GetUserUseCase


class AskAIUseCase:
    def __init__(
        self, *, connection_manager: TenantConnectionManager, ai_gateway_client: AIGatewayClient
    ) -> None:
        self._connections = connection_manager
        self._ai_gateway = ai_gateway_client

    async def execute(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        role: str,
        prompt: str,
    ) -> AskAIResponse:
        user = await GetUserUseCase(connection_manager=self._connections).execute(
            tenant_id=tenant_id, database_name=database_name, user_id=actor_user_id
        )
        user_name = (
            f"{user.first_name} {user.last_name}".strip() if user.last_name else user.first_name
        )

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            company_name = await get_company_display_name(session)

        system_prompt = build_system_prompt(
            company_name=company_name, user_name=user_name, role=role
        )

        started_at = time.perf_counter()
        result = await self._ai_gateway.generate(prompt, system_prompt=system_prompt)
        execution_time = Decimal(str(round(time.perf_counter() - started_at, 3)))

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            conversation = AiConversation(
                user_id=actor_user_id,
                prompt=prompt,
                response=result.text,
                tokens=result.input_tokens + result.output_tokens,
                model=result.model,
                execution_time=execution_time,
            )
            await AiConversationRepository(session).create(conversation)
            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="AI_ASK",
                resource="ai_conversations",
                after={"id": str(conversation.id), "model": conversation.model},
            )
            await session.commit()

        return AskAIResponse(
            response=result.text,
            model=result.model,
            tokens=conversation.tokens,
            execution_time=execution_time,
            cached=result.cached,
            estimated_cost=result.estimated_cost,
        )
