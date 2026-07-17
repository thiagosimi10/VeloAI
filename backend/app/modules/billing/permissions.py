"""Constantes de permissão do módulo Billing, conforme 31-BILLING.md e
22-API-STANDARDS.md (padrão `<módulo>.<ação>`). São permissões de RBAC normais,
checadas contra a role do usuário no banco do tenant — mesmo mecanismo de sempre —
ainda que os dados de Assinatura em si vivam no Banco Master."""

from __future__ import annotations

BILLING_VIEW = "billing.view"
BILLING_MANAGE = "billing.manage"
