"""Tool MCP: importa categorias em lote a partir de um arquivo CSV/XLSX anexado pelo
usuário na conversa (`POST /ai/uploads`, guardado transitoriamente no Redis por
`AiUploadStore`), conforme docs/20-MCP-TOOLS.md. Reaproveita `ImportCategoriesUseCase`
— mesma lógica usada pelo botão "Importar" na tela de categorias, nunca duplicada
aqui."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel
from veloai_shared.exceptions import ValidationError

from app.core.ai_tools import AITool
from app.core.ai_uploads import get_ai_upload_store
from app.core.database import TenantConnectionManager
from app.modules.categories.permissions import CATEGORIES_CREATE
from app.modules.categories.use_cases.import_categories_use_case import ImportCategoriesUseCase


class ImportCategoriesFromFileToolInput(BaseModel):
    upload_id: str


class ImportCategoriesFromFileTool(AITool):
    name = "ImportCategoriesFromFile"
    description = (
        "Importa categorias em lote a partir de um arquivo CSV/XLSX que o usuário "
        "anexou na conversa. Use quando o usuário pedir para importar categorias e "
        "houver um arquivo anexado (indicado no contexto da mensagem com um upload_id)."
    )
    permission = CATEGORIES_CREATE
    service = "categories"
    input_model = ImportCategoriesFromFileToolInput

    async def execute(
        self,
        *,
        connection_manager: TenantConnectionManager,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        tool_input = ImportCategoriesFromFileToolInput.model_validate(arguments)

        ai_uploads = get_ai_upload_store()
        stored = await ai_uploads.pop(tenant_id=str(tenant_id), upload_id=tool_input.upload_id)
        if stored is None:
            raise ValidationError(
                "Arquivo não encontrado ou expirado. Peça para a pessoa anexar novamente.",
                code="AI_UPLOAD_NOT_FOUND",
            )
        filename, data = stored

        use_case = ImportCategoriesUseCase(connection_manager=connection_manager)
        result = await use_case.execute(
            tenant_id=tenant_id,
            database_name=database_name,
            actor_user_id=actor_user_id,
            filename=filename,
            data=data,
        )

        return {
            "total_rows": result.total_rows,
            "created": result.created,
            "errors": [{"row": note.row, "message": note.message} for note in result.errors],
            "warnings": [{"row": note.row, "message": note.message} for note in result.warnings],
        }
