# 25-CI-CD.md

> Projeto → VeloAI
> Documento → Integração Contínua e Entrega Contínua
> Stack → GitHub Actions + Docker
> Versão → 1.0.0

---

# Objetivo

O processo de CI/CD do VeloAI deverá garantir que todo código enviado ao repositório seja validado automaticamente antes de qualquer merge.

Na primeira versão do projeto será implementado apenas CI (Continuous Integration).

Toda a arquitetura deverá permanecer preparada para futura implementação de CD (Continuous Deployment).

Nenhum código poderá ser incorporado à branch principal sem passar por todas as validações.

---

# Filosofia

Automatizar tudo.

Falhar rapidamente.

Nunca realizar validações manuais.

Garantir reprodutibilidade.

Toda alteração deverá ser testada.

---

# Branches

Principal.

```
main
```

Desenvolvimento.

```
develop
```

Features.

```
feature/nome-da-feature
```

Correções.

```
fix/nome-do-bug
```

Hotfix.

```
hotfix/nome
```

Release.

```
release/v1.0.0
```

---

# Fluxo

```text
Feature

↓

Commit

↓

Push

↓

GitHub Actions

↓

Lint

↓

Type Check

↓

Testes

↓

Coverage

↓

Build Docker

↓

Validação Alembic

↓

Validação OpenAPI

↓

Aprovação

↓

Merge
```

---

# Estratégia de Merge

Utilizar.

Pull Requests.

Code Review obrigatório.

Status Checks obrigatórios.

Merge Squash.

Nunca permitir Push direto na main.

---

# Commits

Padrão Conventional Commits.

Exemplos.

```
feat:

fix:

refactor:

docs:

test:

perf:

style:

build:

ci:

chore:
```

---

# GitHub Actions

Criar workflows separados.

```text
backend-ci.yml

frontend-ci.yml

docker-build.yml

security.yml

release.yml

dependency-check.yml
```

---

# Backend CI

Executar.

Instalar dependências.

Ruff.

Black.

MyPy.

Bandit.

Pytest.

Coverage.

Build.

---

# Frontend CI

Executar.

Install.

ESLint.

Type Check.

Vitest.

Playwright.

Build.

---

# Segurança

Executar.

Bandit.

Safety.

pip-audit.

npm audit.

Secret Scan.

Dependabot.

---

# Docker

Executar.

Docker Build Backend.

Docker Build Frontend.

Docker Build Provisioning.

Docker Compose Validation.

Dockerfile Lint.

---

# Banco

Executar.

Alembic Upgrade.

Alembic Downgrade.

Alembic Upgrade novamente.

Validar consistência.

---

# OpenAPI

Gerar documentação.

Validar.

Schemas.

Rotas.

Breaking Changes.

---

# Cobertura

Backend.

95%.

Frontend.

90%.

MCP.

95%.

RAG.

95%.

Provisioning.

95%.

Falhar Build abaixo destes valores.

---

# Artefatos

Gerar.

Coverage.

Logs.

OpenAPI.

Docker Images.

Test Reports.

Playwright Report.

---

# Versionamento

Semantic Versioning.

```
MAJOR.MINOR.PATCH
```

Exemplos.

```
1.0.0

1.1.0

1.1.1
```

---

# Releases

Criar automaticamente.

Release Notes.

Changelog.

Tag Git.

Docker Tag.

---

# Dependências

Atualização automática.

Dependabot.

Revisão obrigatória.

Nunca atualizar sem testes.

---

# Quality Gates

Obrigatórios.

Lint.

Type Check.

Coverage.

Security.

Docker Build.

OpenAPI.

Alembic.

Todos precisam passar.

---

# Secrets

Armazenar somente no GitHub Secrets.

Nunca utilizar.

.env no repositório.

Senhas.

Tokens.

API Keys.

Credenciais.

---

# Variáveis

Exemplo.

```
GEMINI_API_KEY

JWT_SECRET

DATABASE_URL

REDIS_URL

MINIO_SECRET

DOCKER_USERNAME

DOCKER_PASSWORD
```

---

# Ambientes

Development.

Testing.

Homologation.

Production.

Cada ambiente possuirá Secrets próprios.

---

# Cache

Utilizar cache para.

Python.

Node.

Docker Layers.

Playwright.

Pip.

NPM.

---

# Matrix Build

Executar.

Linux.

Python 3.13.

Preparado para futuras versões.

---

# Notificações

Enviar resultado para.

GitHub.

Discord.

Slack.

Microsoft Teams.

Email.

Configuração opcional.

---

# Falhas

Qualquer falha deverá interromper o Pipeline.

Nunca permitir Merge com erro.

---

# Pull Requests

Executar automaticamente.

Todos os testes.

Todos os Linters.

Build.

Coverage.

Security.

---

# Branch Protection

Obrigatório.

Code Review.

Status Checks.

Conversation Resolution.

Signed Commits opcional.

---

# Docker Images

Nome.

```
veloai-backend

veloai-frontend

veloai-provisioning

veloai-worker
```

Tag.

```
latest

develop

v1.0.0
```

---

# Qualidade

Executar.

Ruff.

Black.

MyPy.

Bandit.

ESLint.

Prettier.

Vitest.

Pytest.

Playwright.

---

# Relatórios

Gerar.

Coverage HTML.

Coverage XML.

JUnit.

OpenAPI.

Docker Build Logs.

---

# Monitoramento

Registrar.

Tempo.

Falhas.

Builds.

Cobertura.

Deploys futuros.

---

# Futuro CD

Preparar.

Deploy Docker.

Deploy Kubernetes.

Blue Green.

Canary.

Rollback.

Migrações.

Smoke Tests.

Health Checks.

---

# Estrutura

```text
.github/

workflows/

backend-ci.yml

frontend-ci.yml

docker-build.yml

security.yml

release.yml

dependency-check.yml
```

---

# Regras Obrigatórias

Todo Pull Request deverá executar todos os workflows.

Nenhum Merge poderá ocorrer com falhas.

Nenhuma imagem Docker poderá ser publicada sem sucesso no CI.

Toda alteração deverá possuir testes.

Toda Release deverá gerar Changelog.

Toda Migration deverá ser validada.

Toda documentação OpenAPI deverá ser gerada automaticamente.

---

# Roadmap

Adicionar.

Deploy Automático.

Terraform.

Kubernetes.

Helm.

ArgoCD.

GitOps.

Preview Environments.

Rollback Automático.

Canary Deploy.

Blue Green Deploy.

---

# Objetivo Final

O pipeline de CI/CD do VeloAI deverá automatizar completamente a validação da aplicação, garantindo qualidade, segurança e consistência desde o primeiro commit. A arquitetura deverá permitir evolução natural para Continuous Deployment sem necessidade de grandes mudanças, tornando o processo de entrega rápido, confiável e reproduzível.

---
