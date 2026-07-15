"""Modelos do Banco Master (`veloai_master`). Nunca armazenam dados operacionais de
negócio — apenas o registro de empresas, planos, assinaturas, auditoria da plataforma e
o índice de roteamento de login, conforme 04-MULTI-TENANCY.md e o apêndice
18-DATABASE-02 (Multi Tenancy)."""

from veloai_shared.schema.master.audit_log import AuditLog
from veloai_shared.schema.master.base import MasterBase
from veloai_shared.schema.master.plan import Plan
from veloai_shared.schema.master.rbac import Permission, Role
from veloai_shared.schema.master.subscription import Subscription, SubscriptionStatus
from veloai_shared.schema.master.tenant_registry import Tenant, TenantStatus
from veloai_shared.schema.master.tenant_user_index import TenantUserIndex

__all__ = [
    "MasterBase",
    "Tenant",
    "TenantStatus",
    "Plan",
    "Subscription",
    "SubscriptionStatus",
    "Role",
    "Permission",
    "AuditLog",
    "TenantUserIndex",
]
