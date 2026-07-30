"""Constante de permissão do módulo de Configurações da Empresa. Reaproveita
`system.admin` (já concedida ao papel Administrador de todo tenant no seed do
Provisioning Service) em vez de cadastrar uma permissão nova só para isto — editar os
dados cadastrais da própria empresa é, por natureza, uma ação de administração geral do
sistema, mesmo escopo do Painel Administrativo (`admin/permissions`, fora do tenant)."""

from __future__ import annotations

COMPANY_MANAGE = "system.admin"
