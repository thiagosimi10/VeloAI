"""Base de Conhecimento do tenant (RAG — Fase 15), conforme docs/21-RAG.md — sem
tabela dedicada em 05-BANCO-DE-DADOS.md, criada com o usuário (mesmo critério já usado
para `Attachment` na Fase 12). Guarda só os metadados/texto de origem: os chunks e
embeddings vivem no Qdrant (`veloai_shared.qdrant.collection_name_for_tenant`), nunca
duplicados aqui — mesma separação já usada em Anexos (MinIO guarda o arquivo, Postgres
guarda metadados)."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from veloai_shared.schema.tenant.base import TenantBase, TimestampMixin, UUIDPrimaryKeyMixin


class KnowledgeDocument(TenantBase, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "knowledge_documents"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
