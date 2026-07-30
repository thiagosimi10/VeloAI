"""Tool MCP: importa produtos em lote a partir de um arquivo CSV/XLSX anexado pelo
usuário na conversa (`POST /ai/uploads`, guardado transitoriamente no Redis por
`AiUploadStore`), conforme docs/20-MCP-TOOLS.md. Reaproveita `ImportProductsUseCase` —
mesma lógica usada pelo botão "Importar" na tela de produtos, nunca duplicada aqui."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel
from veloai_shared.exceptions import ValidationError

from app.core.ai_tools import AITool
from app.core.ai_uploads import get_ai_upload_store
from app.core.database import TenantConnectionManager
from app.modules.products.permissions import PRODUCTS_CREATE
from app.modules.products.use_cases.import_products_use_case import ImportProductsUseCase


class ImportProductsFromFileToolInput(BaseModel):
    upload_id: str


class ImportProductsFromFileTool(AITool):
    name = "ImportProductsFromFile"
    description = (
        "Importa produtos em lote a partir de um arquivo CSV/XLSX que o usuário "
        "anexou na conversa. Use quando o usuário pedir para importar produtos e "
        "houver um arquivo anexado (indicado no contexto da mensagem com um upload_id)."
    )
    permission = PRODUCTS_CREATE
    service = "products"
    input_model = ImportProductsFromFileToolInput

    async def execute(
        self,
        *,
        connection_manager: TenantConnectionManager,
        tenant_id: uuid.UUID,
        database_name: str,
        actor_user_id: uuid.UUID,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        tool_input = ImportProductsFromFileToolInput.model_validate(arguments)

        ai_uploads = get_ai_upload_store()
        stored = await ai_uploads.pop(tenant_id=str(tenant_id), upload_id=tool_input.upload_id)
        if stored is None:
            raise ValidationError(
                "Arquivo não encontrado ou expirado. Peça para a pessoa anexar novamente.",
                code="AI_UPLOAD_NOT_FOUND",
            )
        filename, data = stored

        use_case = ImportProductsUseCase(connection_manager=connection_manager)
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
