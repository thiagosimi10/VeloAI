"""Router raiz da versão 1 da API (`/api/v1`), conforme 22-API-STANDARDS.md.

Nesta fase de fundação nenhum módulo de negócio foi criado ainda — este router existe
apenas para que os próximos módulos (customers/, products/, ...) possam se registrar aqui
sem exigir mudanças na inicialização da aplicação."""

from __future__ import annotations

from fastapi import APIRouter

api_v1_router = APIRouter()
