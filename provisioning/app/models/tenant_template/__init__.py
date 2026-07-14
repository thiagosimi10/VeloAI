"""Esquema mínimo aplicado a todo novo banco de tenant. Contém apenas o necessário para
o Provisioning Service criar um usuário administrador logável — nenhuma tabela de
negócio (customers/products/orders) foi criada nesta fase de fundação."""

from app.models.tenant_template.audit_log import TenantAuditLog
from app.models.tenant_template.base import TenantBase
from app.models.tenant_template.company import Company
from app.models.tenant_template.rbac import TenantPermission, TenantRole, TenantRolePermission
from app.models.tenant_template.user import TenantUser

__all__ = [
    "TenantBase",
    "Company",
    "TenantUser",
    "TenantRole",
    "TenantPermission",
    "TenantRolePermission",
    "TenantAuditLog",
]
