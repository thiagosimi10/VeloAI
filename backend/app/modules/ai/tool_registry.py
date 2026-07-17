"""Registro de Tools disponíveis para a IA, conforme docs/20-MCP-TOOLS.md ("Registro
das Tools"). Lista explícita — sem descoberta automática via filesystem, que não se
justifica ainda para 8 Tools (adicionar a próxima é só escrever uma classe + acrescentar
aqui). Vive no módulo `ai/` (não em `app/core/`) porque é quem consome as Tools; cada
Tool em si mora no `mcp_tools/` do seu próprio módulo."""

from __future__ import annotations

from app.core.ai_tools import AITool
from app.modules.billing.mcp_tools.get_subscription_status_tool import (
    GetSubscriptionStatusTool,
)
from app.modules.customers.mcp_tools.create_customer_tool import CreateCustomerTool
from app.modules.customers.mcp_tools.get_customer_tool import GetCustomerTool
from app.modules.customers.mcp_tools.search_customers_tool import SearchCustomersTool
from app.modules.dashboard.mcp_tools.get_dashboard_summary_tool import GetDashboardSummaryTool
from app.modules.dashboard.mcp_tools.get_revenue_timeseries_tool import (
    GetRevenueTimeseriesTool,
)
from app.modules.dashboard.mcp_tools.get_top_selling_products_tool import (
    GetTopSellingProductsTool,
)
from app.modules.knowledge.mcp_tools.search_knowledge_tool import SearchKnowledgeTool

ALL_TOOLS: list[AITool] = [
    CreateCustomerTool(),
    SearchCustomersTool(),
    GetCustomerTool(),
    SearchKnowledgeTool(),
    GetDashboardSummaryTool(),
    GetRevenueTimeseriesTool(),
    GetTopSellingProductsTool(),
    GetSubscriptionStatusTool(),
]


def get_tools_for_permissions(permissions: list[str]) -> list[AITool]:
    """Nunca expõe à IA uma Tool que o usuário autenticado não tem permissão de
    executar (docs/20-MCP-TOOLS.md, "Nunca confiar na IA")."""

    return [tool for tool in ALL_TOOLS if tool.permission in permissions]


def find_tool(name: str, *, permissions: list[str]) -> AITool | None:
    """Revalida a permissão na hora de resolver a Tool escolhida pela IA — defesa em
    profundidade, mesmo já tendo filtrado a lista enviada ao Gemini."""

    for tool in get_tools_for_permissions(permissions):
        if tool.name == name:
            return tool
    return None
