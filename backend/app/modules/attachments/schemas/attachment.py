"""DTOs de Anexos — 22-API-STANDARDS.md ("Upload") define que a resposta deve trazer
`file_id`/`url`/`size`; expomos esses três junto com os demais metadados. Só três tipos
de recurso suportados nesta fase (ver `app/modules/README.md`)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

AttachmentResourceType = Literal["customer", "product", "service_order"]


class AttachmentResponse(BaseModel):
    id: uuid.UUID
    resource_type: AttachmentResourceType
    resource_id: uuid.UUID
    original_filename: str
    content_type: str
    size_bytes: int
    url: str
    uploaded_by: uuid.UUID
    created_at: datetime


class AttachmentFilterParams(BaseModel):
    resource_type: AttachmentResourceType
    resource_id: uuid.UUID
