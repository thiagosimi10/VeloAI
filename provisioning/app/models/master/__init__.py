"""Modelos do Banco Master (`veloai_master`). Nunca armazenam dados operacionais de
negócio — apenas o registro de empresas, planos, assinaturas e auditoria da plataforma,
conforme 04-MULTI-TENANCY.md e 18-DATABASE-02 (apêndice de Multi Tenancy)."""

from app.models.master.audit_log import AuditLog
from app.models.master.base import MasterBase
from app.models.master.plan import Plan
from app.models.master.rbac import Permission, Role
from app.models.master.subscription import Subscription
from app.models.master.tenant_registry import Tenant, TenantStatus

__all__ = [
    "MasterBase",
    "Tenant",
    "TenantStatus",
    "Plan",
    "Subscription",
    "Role",
    "Permission",
    "AuditLog",
]
