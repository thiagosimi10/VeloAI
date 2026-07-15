"""Modelos SQLAlchemy compartilhados do Banco Master e do template de banco de tenant.

Único lugar onde essas entidades são definidas — tanto o Provisioning Service (dono das
migrations Alembic) quanto o Backend (consultas em runtime) importam daqui, evitando
duplicação de código entre serviços (00-AI-CONSTITUTION.md, "Nunca gerar código
duplicado")."""
