"""Router raiz da versão 1 da API (`/api/v1`), conforme 22-API-STANDARDS.md.

Módulos registrados: Autenticação (Fase 3), CRM completo — Clientes, Fornecedores,
Categorias, Produtos e Serviços (Fase 6) —, Usuários (leitura, Fase 8), Ordens de
Serviço (Fase 8), Vendas (Fase 9), Financeiro (Fase 10), Dashboard (Fase 11), Anexos
(Fase 12) e IA (Fase 13). Os próximos módulos se registram aqui sem exigir mudanças na
inicialização da aplicação."""

from __future__ import annotations

from fastapi import APIRouter

from app.modules.ai.api.router import router as ai_router
from app.modules.attachments.api.router import router as attachments_router
from app.modules.auth.api.router import router as auth_router
from app.modules.categories.api.router import router as categories_router
from app.modules.customers.api.router import router as customers_router
from app.modules.dashboard.api.router import router as dashboard_router
from app.modules.finance.api.router import router as finance_router
from app.modules.products.api.router import router as products_router
from app.modules.sales.api.router import router as sales_router
from app.modules.service_orders.api.router import router as service_orders_router
from app.modules.services.api.router import router as services_router
from app.modules.suppliers.api.router import router as suppliers_router
from app.modules.users.api.router import router as users_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(customers_router)
api_v1_router.include_router(suppliers_router)
api_v1_router.include_router(categories_router)
api_v1_router.include_router(products_router)
api_v1_router.include_router(services_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(service_orders_router)
api_v1_router.include_router(sales_router)
api_v1_router.include_router(finance_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(attachments_router)
api_v1_router.include_router(ai_router)
