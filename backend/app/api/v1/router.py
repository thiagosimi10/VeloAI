"""Router raiz da versão 1 da API (`/api/v1`), conforme 22-API-STANDARDS.md.

Módulos registrados: Autenticação (Fase 3), CRM completo — Clientes, Fornecedores,
Categorias, Produtos e Serviços (Fase 6) —, Usuários (leitura, Fase 8), Ordens de
Serviço (Fase 8), Vendas (Fase 9), Financeiro (Fase 10), Dashboard (Fase 11), Anexos
(Fase 12), IA (Fase 13), Base de Conhecimento/RAG (Fase 15), Billing (Fase 17) e Admin/
Painel Administrativo (Fase 18). Os próximos módulos se registram aqui sem exigir
mudanças na inicialização da aplicação.

Todo módulo de negócio, exceto `auth_router`/`billing_router`/`admin_router`, é
registrado com `dependencies=[Depends(require_active_subscription)]` — um tenant com
assinatura expirada/cancelada/suspensa (31-BILLING.md) é bloqueado em qualquer rota de
negócio, mas continua conseguindo logar/deslogar e enxergar/cancelar a própria
assinatura. `admin_router` nunca leva esse gate — um Platform Admin não pertence a
nenhum tenant, não tem assinatura para verificar."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.dependencies import require_active_subscription
from app.modules.admin.api.router import router as admin_router
from app.modules.ai.api.router import router as ai_router
from app.modules.attachments.api.router import router as attachments_router
from app.modules.auth.api.router import router as auth_router
from app.modules.billing.api.router import router as billing_router
from app.modules.categories.api.router import router as categories_router
from app.modules.customers.api.router import router as customers_router
from app.modules.dashboard.api.router import router as dashboard_router
from app.modules.finance.api.router import router as finance_router
from app.modules.knowledge.api.router import router as knowledge_router
from app.modules.products.api.router import router as products_router
from app.modules.sales.api.router import router as sales_router
from app.modules.service_orders.api.router import router as service_orders_router
from app.modules.services.api.router import router as services_router
from app.modules.suppliers.api.router import router as suppliers_router
from app.modules.users.api.router import router as users_router

_subscription_gate = [Depends(require_active_subscription)]

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(billing_router)
api_v1_router.include_router(admin_router)
api_v1_router.include_router(customers_router, dependencies=_subscription_gate)
api_v1_router.include_router(suppliers_router, dependencies=_subscription_gate)
api_v1_router.include_router(categories_router, dependencies=_subscription_gate)
api_v1_router.include_router(products_router, dependencies=_subscription_gate)
api_v1_router.include_router(services_router, dependencies=_subscription_gate)
api_v1_router.include_router(users_router, dependencies=_subscription_gate)
api_v1_router.include_router(service_orders_router, dependencies=_subscription_gate)
api_v1_router.include_router(sales_router, dependencies=_subscription_gate)
api_v1_router.include_router(finance_router, dependencies=_subscription_gate)
api_v1_router.include_router(dashboard_router, dependencies=_subscription_gate)
api_v1_router.include_router(attachments_router, dependencies=_subscription_gate)
api_v1_router.include_router(ai_router, dependencies=_subscription_gate)
api_v1_router.include_router(knowledge_router, dependencies=_subscription_gate)
