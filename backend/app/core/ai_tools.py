"""Interface comum a toda Tool exposta à IA, conforme docs/20-MCP-TOOLS.md ("Estrutura
de uma Tool") e docs/00-AI-CONSTITUTION.md ("A IA nunca poderá... Alterar dados sem
utilizar Tools."). Cross-cutting (mesmo nível de `app/core/audit.py`) — qualquer módulo
que queira expor uma ação para a IA implementa esta interface em seu próprio
`mcp_tools/`, sem depender do módulo `ai/`.

Cada Tool reaproveita o Use Case público já existente do seu módulo — nunca duplica
regra de negócio, nunca acessa um `repository` diretamente."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from app.core.database import TenantConnectionManager


class AITool(ABC):
    name: str
    description: str
    permission: str
    service: str
    input_model: type[BaseModel]

    def parameters_schema(self) -> dict[str, Any]:
        return self.input_model.model_json_schema()

    @abstractmethod
    async def execute(
        self,
        *,
        connection_manager: TenantConnectionManager,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """Valida `arguments` com `self.input_model` e executa o Use Case do próprio
        módulo, retornando um dict serializável em JSON. Pode levantar `AppException`
        (validação, não encontrado, conflito) — quem chama (`AskAIUseCase`, fazendo o
        papel de Executor) é responsável por capturar e nunca deixar a exceção crua
        chegar até a IA (conforme 20-MCP-TOOLS.md, "Nunca lançar exceções diretamente
        para a IA")."""
