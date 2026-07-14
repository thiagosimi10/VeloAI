# Módulos de negócio

Esta pasta está intencionalmente vazia nesta fase de fundação (ver
`docs/34-MASTER-PLAN.md`, Fases 6 em diante). Nenhum módulo de negócio (Clientes,
Produtos, Ordens de Serviço, Financeiro, Vendas...) foi criado ainda.

Quando um módulo for adicionado, ele deverá seguir exatamente a estrutura mínima definida
em `docs/00-AI-CONSTITUTION.md` e `docs/16-BACKEND-ARCHITECTURE.md`:

```text
modules/
  <nome_do_modulo>/
    api/            # Controllers — só recebem requisição, autenticam, chamam use_cases
    schemas/         # DTOs Pydantic (Create/Update/Response/Filter/Pagination)
    models/          # Entidades SQLAlchemy (sem lógica de negócio)
    repositories/    # Acesso ao banco — sem regra de negócio
    services/        # Regras de negócio, orquestração, eventos
    use_cases/       # Casos de uso expostos à API
    mcp_tools/       # Tools MCP expostas à IA para este módulo
    permissions/     # Constantes de permissão (ex.: customers.view)
    validators/
    exceptions/
    tests/
```

Nenhum módulo poderá acessar o `repository` de outro módulo diretamente — toda
comunicação entre módulos ocorre através de `services`.
