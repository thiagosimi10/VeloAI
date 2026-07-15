"""Anexos genéricos do tenant, conforme a Fase 12 do Master Plan ("Storage") — sem
tabela dedicada em 05-BANCO-DE-DADOS.md, criada com o usuário para permitir anexar
arquivos (MinIO) a Clientes, Produtos e Ordens de Serviço, conforme já pedido em
08-CLIENTES.md/09-PRODUTOS.md/10-ORDEM-DE-SERVICO.md. Polimórfica (`resource_type` +
`resource_id`) em vez de uma FK por tipo de recurso — evita crescer com uma migration a
cada novo tipo suportado. Sem soft delete: remover um anexo é uma exclusão real (arquivo
+ linha), mesmo padrão de `ServiceOrderItem`/`SaleItem` — não é, em si, um registro
histórico a preservar."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.tenant.base import TenantBase, UUIDPrimaryKeyMixin


class Attachment(TenantBase, UUIDPrimaryKeyMixin):
    __tablename__ = "attachments"
    __table_args__ = (
        Index("ix_attachments_resource", "resource_type", "resource_id"),
    )

    resource_type: Mapped[str] = mapped_column(String(30), nullable=False)
    resource_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    uploaded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
