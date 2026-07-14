# VeloAI

> AI Business OS — plataforma SaaS Multi-Tenant para pequenas e médias empresas, com
> Inteligência Artificial como interface principal.

Este repositório está na **fase de fundação** do projeto (ver `docs/34-MASTER-PLAN.md`,
Fases 1 a 5 parcialmente). Nenhum módulo de negócio (Clientes, Produtos, Ordens de
Serviço, Financeiro, Vendas) foi implementado ainda — o objetivo desta fase é ter toda a
infraestrutura, o esqueleto dos serviços e o provisionamento de tenants funcionando de
verdade antes de qualquer funcionalidade de negócio.

Toda a documentação oficial do produto está em [`docs/`](docs), começando por
[`docs/00-AI-CONSTITUTION.md`](docs/00-AI-CONSTITUTION.md) e
[`docs/34-MASTER-PLAN.md`](docs/34-MASTER-PLAN.md).

---

## Arquitetura desta fase

```
veloai/
  shared/          # pacote Python compartilhado (response envelope, exceptions,
                    # logging, health check, segurança) — usado por backend,
                    # provisioning e ai-gateway.
  backend/         # FastAPI — API principal (sem módulos de negócio ainda).
  provisioning/     # FastAPI — único serviço com privilégios administrativos de
                    # PostgreSQL. Cria bancos de tenant de verdade.
  ai-gateway/       # FastAPI — único ponto de comunicação com provedores de LLM
                    # (Gemini implementado; arquitetura pronta para outros).
  frontend/         # Vue 3 + TypeScript + Vite + Tailwind + PrimeVue.
  infra/            # Configurações de infraestrutura (nginx, scripts).
  .github/workflows/ # CI (lint, testes, build Docker, segurança).
  docker-compose.yml
```

Cada serviço Python segue Clean Architecture (`api/ → services/ → repositories/ →
models/`), conforme `docs/00-AI-CONSTITUTION.md` e `docs/16-BACKEND-ARCHITECTURE.md`.

---

## Subindo o ambiente

```bash
cp .env.example .env
docker compose up -d
```

Serviços expostos localmente:

| Serviço | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/docs |
| Provisioning | http://localhost:8001/docs |
| AI Gateway | http://localhost:8002/docs |
| MinIO Console | http://localhost:9001 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

Todo serviço FastAPI expõe `/health`, `/ready` e `/live`.

---

## Criando a primeira empresa (Tenant)

```bash
curl -X POST http://localhost:8001/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "legal_name": "Assistência Técnica Silva LTDA",
    "trade_name": "Assistência Silva",
    "document": "12345678000199",
    "admin_name": "Maria Souza",
    "admin_email": "maria@assistenciasilva.com"
  }'
```

Isso cria de verdade um banco PostgreSQL exclusivo (`tenant_<id>`), aplica as migrations
mínimas e cria o usuário administrador (senha temporária retornada uma única vez na
resposta, com `force_password_change=true`).

---

## Desenvolvimento local por serviço

### Backend / Provisioning / AI Gateway (Python 3.13)

```bash
cd <serviço>
pip install -r requirements-dev.txt
ruff check .
black --check .
mypy app
pytest
```

O pacote `shared/` é instalado em modo editável automaticamente (`-e ../shared` dentro de
`requirements.txt`).

### Frontend (Node 22)

```bash
cd frontend
npm install
npm run lint
npm run type-check
npm test
npm run build
```

---

## Testes

| Serviço | Cobertura mínima nesta fase |
|---|---|
| `shared/` | sem meta fixa (utilitário pequeno, buscar 100%) |
| `backend/` | 85% |
| `provisioning/` | 85% (inclui teste de integração real de criação de tenant) |
| `ai-gateway/` | 85% |
| `frontend/` | 80% |

A meta definitiva do projeto (`docs/00-AI-CONSTITUTION.md`) é 90-95%; os valores acima
são deliberadamente menores nesta fase por ainda não existir código de negócio — serão
elevados à medida que os módulos forem implementados.

---

## O que NÃO está nesta fase

- Autenticação (JWT/Refresh/RBAC completo) — Fase 3 do Master Plan.
- Qualquer módulo de negócio (Clientes, Produtos, OS, Financeiro, Vendas, Dashboard).
- MCP, RAG, Automation Engine, Billing real.
- RabbitMQ/Celery, Qdrant/pgvector, Nginx, Prometheus/Grafana/Loki/Tempo.

Essas peças serão adicionadas nas próximas fases, seguindo `docs/34-MASTER-PLAN.md`.
