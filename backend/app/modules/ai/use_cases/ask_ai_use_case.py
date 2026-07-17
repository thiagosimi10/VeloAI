"""Caso de uso: perguntar algo ao assistente de IA. Monta o contexto de
empresa/usuário, filtra as Tools que o usuário tem permissão de usar e delega ao AI
Gateway (único ponto de contato com a LLM). Se a IA decidir chamar uma Tool (function
calling do Gemini), esta classe faz o papel de Executor (docs/00-AI-CONSTITUTION.md,
"Fluxo obrigatório da IA"): resolve a Tool no Registry, revalida permissão, executa e
grava o resultado em `ai_actions`. Sempre grava em `ai_conversations`, conforme
28-AI-GATEWAY.md/20-MCP-TOOLS.md."""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from pydantic import ValidationError
from veloai_shared.exceptions import AppException
from veloai_shared.schema.tenant import AiAction, AiConversation

from app.core.ai_gateway_client import (
    AIGatewayClient,
    AIGatewayResult,
    FunctionCall,
    ToolDeclaration,
)
from app.core.audit import record_audit_log
from app.core.database import TenantConnectionManager
from app.modules.ai.repositories.ai_action_repository import AiActionRepository
from app.modules.ai.repositories.ai_conversation_repository import AiConversationRepository
from app.modules.ai.schemas.ai import AskAIResponse
from app.modules.ai.tool_registry import find_tool, get_tools_for_permissions
from app.modules.ai.use_cases._helpers import build_system_prompt, get_company_display_name
from app.modules.auth.repositories.user_repository import TenantUserRepository
from app.modules.users.use_cases.get_user_use_case import GetUserUseCase


@dataclass(frozen=True)
class _AnswerOutcome:
    final_text: str
    tool_used: str | None
    service: str | None
    execution: dict[str, Any] | None
    success: bool | None
    input_tokens: int
    output_tokens: int
    model: str
    cached: bool
    estimated_cost: Decimal


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
            permissions = await TenantUserRepository(session).get_role_permissions_by_name(role)

        system_prompt = build_system_prompt(
            company_name=company_name, user_name=user_name, role=role
        )
        tool_declarations = [
            ToolDeclaration(
                name=tool.name, description=tool.description, parameters=tool.parameters_schema()
            )
            for tool in get_tools_for_permissions(permissions)
        ]

        started_at = time.perf_counter()
        first_result = await self._ai_gateway.generate(
            prompt, system_prompt=system_prompt, tools=tool_declarations or None
        )

        function_call = first_result.function_call
        if function_call is not None:
            outcome = await self._run_tool_call(
                tenant_id=tenant_id,
                database_name=database_name,
                actor_user_id=actor_user_id,
                permissions=permissions,
                system_prompt=system_prompt,
                original_prompt=prompt,
                function_call=function_call,
                first_result=first_result,
            )
        else:
            outcome = _AnswerOutcome(
                final_text=first_result.text or "",
                tool_used=None,
                service=None,
                execution=None,
                success=None,
                input_tokens=first_result.input_tokens,
                output_tokens=first_result.output_tokens,
                model=first_result.model,
                cached=first_result.cached,
                estimated_cost=first_result.estimated_cost,
            )

        execution_time = Decimal(str(round(time.perf_counter() - started_at, 3)))

        async with self._connections.session_for_tenant(tenant_id, database_name) as session:
            conversation = AiConversation(
                user_id=actor_user_id,
                prompt=prompt,
                response=outcome.final_text,
                tokens=outcome.input_tokens + outcome.output_tokens,
                model=outcome.model,
                execution_time=execution_time,
            )
            await AiConversationRepository(session).create(conversation)

            if outcome.tool_used is not None:
                await AiActionRepository(session).create(
                    AiAction(
                        conversation_id=conversation.id,
                        tool=outcome.tool_used,
                        service=outcome.service or "unknown",
                        execution=outcome.execution,
                        success=bool(outcome.success),
                    )
                )

            await record_audit_log(
                session,
                user_id=actor_user_id,
                action="AI_ASK",
                resource="ai_conversations",
                after={
                    "id": str(conversation.id),
                    "model": conversation.model,
                    "tool_used": outcome.tool_used,
                },
            )
            await session.commit()

        return AskAIResponse(
            response=outcome.final_text,
            model=outcome.model,
            tokens=conversation.tokens,
            execution_time=execution_time,
            cached=outcome.cached,
            estimated_cost=outcome.estimated_cost,
            tool_used=outcome.tool_used,
        )

    async def _run_tool_call(
        self,
        *,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        permissions: list[str],
        system_prompt: str,
        original_prompt: str,
        function_call: FunctionCall,
        first_result: AIGatewayResult,
    ) -> _AnswerOutcome:
        tool = find_tool(function_call.name, permissions=permissions)

        if tool is None:
            service = "unknown"
            success = False
            tool_outcome: dict[str, Any] = {"error": "Ferramenta não permitida ou inexistente."}
        else:
            service = tool.service
            try:
                tool_data = await tool.execute(
                    connection_manager=self._connections,
                    tenant_id=tenant_id,
                    database_name=database_name,
                    actor_user_id=actor_user_id,
                    arguments=function_call.arguments,
                )
                success = True
                tool_outcome = {"result": tool_data}
            except (AppException, ValidationError, ValueError) as exc:
                success = False
                tool_outcome = {"error": str(exc)}

        follow_up_prompt = (
            f'O usuário perguntou: "{original_prompt}"\n\n'
            f"Você decidiu executar a ferramenta '{function_call.name}' com os "
            f"parâmetros {json.dumps(function_call.arguments, ensure_ascii=False)}. "
            f"{'O resultado foi' if success else 'A execução falhou com o erro'}: "
            f"{json.dumps(tool_outcome, ensure_ascii=False, default=str)}.\n\n"
            "Elabore uma resposta final, clara e natural, em português do Brasil, "
            "para o usuário, baseada nesse resultado. Nunca invente dados que não "
            "estejam no resultado."
        )
        second_result = await self._ai_gateway.generate(
            follow_up_prompt, system_prompt=system_prompt
        )

        return _AnswerOutcome(
            final_text=second_result.text or "",
            tool_used=function_call.name,
            service=service,
            execution={"arguments": function_call.arguments, **tool_outcome},
            success=success,
            input_tokens=first_result.input_tokens + second_result.input_tokens,
            output_tokens=first_result.output_tokens + second_result.output_tokens,
            model=second_result.model,
            cached=second_result.cached,
            estimated_cost=first_result.estimated_cost + second_result.estimated_cost,
        )
