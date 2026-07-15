"""Esquema aplicado a todo novo banco de tenant: autenticação (empresa, usuários, RBAC,
refresh tokens, histórico de login), os módulos de negócio do CRM (Clientes,
Fornecedores, Categorias, Produtos, Serviços), o histórico de estoque (`StockMovement`,
Fase 7), o núcleo operacional de Ordens de Serviço (Fase 8), o núcleo operacional de
Vendas (Fase 9), o núcleo operacional Financeiro (Fase 10), os anexos genéricos via
MinIO (`Attachment`, Fase 12) e o registro de uso de IA (`AiConversation`, Fase 13)."""

from veloai_shared.schema.tenant.account_payable import AccountPayable
from veloai_shared.schema.tenant.account_receivable import AccountReceivable
from veloai_shared.schema.tenant.ai_conversation import AiConversation
from veloai_shared.schema.tenant.attachment import Attachment
from veloai_shared.schema.tenant.audit_log import TenantAuditLog
from veloai_shared.schema.tenant.base import TenantBase
from veloai_shared.schema.tenant.cash_flow_entry import CashFlowEntry
from veloai_shared.schema.tenant.category import Category
from veloai_shared.schema.tenant.company import Company
from veloai_shared.schema.tenant.customer import Customer
from veloai_shared.schema.tenant.login_history import LoginHistory
from veloai_shared.schema.tenant.product import Product
from veloai_shared.schema.tenant.rbac import TenantPermission, TenantRole, TenantRolePermission
from veloai_shared.schema.tenant.refresh_token import RefreshToken
from veloai_shared.schema.tenant.sale import Sale
from veloai_shared.schema.tenant.sale_item import SaleItem
from veloai_shared.schema.tenant.service import Service
from veloai_shared.schema.tenant.service_order import ServiceOrder
from veloai_shared.schema.tenant.service_order_item import ServiceOrderItem
from veloai_shared.schema.tenant.stock_movement import StockMovement
from veloai_shared.schema.tenant.supplier import Supplier
from veloai_shared.schema.tenant.user import TenantUser

__all__ = [
    "TenantBase",
    "Company",
    "Customer",
    "Supplier",
    "Category",
    "Product",
    "Service",
    "StockMovement",
    "ServiceOrder",
    "ServiceOrderItem",
    "Sale",
    "SaleItem",
    "AccountReceivable",
    "AccountPayable",
    "CashFlowEntry",
    "Attachment",
    "AiConversation",
    "TenantUser",
    "TenantRole",
    "TenantPermission",
    "TenantRolePermission",
    "TenantAuditLog",
    "RefreshToken",
    "LoginHistory",
]
