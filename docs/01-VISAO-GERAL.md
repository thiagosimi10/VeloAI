# 01-VISAO-GERAL.md

> Projeto → VeloAI
> Produto → AI Business OS
> Versão → 1.0.0

---

# Visão Geral

O VeloAI é uma plataforma SaaS Multi-Tenant desenvolvida para centralizar toda a operação de pequenas e médias empresas em um único sistema.

O sistema une CRM, ERP, Financeiro, Estoque, Ordem de Serviço, Fiscal, Relatórios, Dashboards Inteligentes e Inteligência Artificial em uma única plataforma.

A IA não será um recurso adicional. Ela será parte da arquitetura do sistema e poderá executar praticamente qualquer ação disponível para o usuário, respeitando permissões e regras de negócio.

O objetivo é que o usuário consiga operar a empresa tanto pela interface gráfica quanto por linguagem natural.

---

# Missão

Permitir que pequenas empresas utilizem Inteligência Artificial para administrar seu negócio com a mesma eficiência de grandes empresas, reduzindo tempo operacional, automatizando tarefas repetitivas e facilitando a tomada de decisões.

---

# Visão

Ser a principal plataforma de gestão empresarial com Inteligência Artificial da América Latina.

---

# Valores

- Simplicidade acima da complexidade.
- IA como parte da operação.
- Segurança em primeiro lugar.
- Performance sempre.
- Código limpo.
- Arquitetura escalável.
- Experiência do usuário acima de tudo.
- Automação sempre que possível.
- Dados pertencem ao cliente.
- Evolução contínua.

---

# O que é o VeloAI

O VeloAI é um AI Business OS.

Isso significa que ele vai muito além de um CRM tradicional.

Ele centraliza toda a operação da empresa.

Principais módulos:

- Dashboard Inteligente
- CRM
- Clientes
- Leads
- Produtos
- Serviços
- Estoque
- Compras
- Vendas
- Orçamentos
- Ordens de Serviço
- Financeiro
- Contas a Pagar
- Contas a Receber
- Fluxo de Caixa
- Fiscal
- Agenda
- Relatórios
- IA
- Automações
- Configurações
- Usuários
- Empresas
- API Pública

---

# Público-Alvo

Empresas entre 1 e 100 colaboradores.

Principais segmentos:

- Assistência Técnica
- Oficinas
- Eletricistas
- Encanadores
- Empresas de Climatização
- Empresas de Segurança Eletrônica
- Prestadores de Serviço
- Lojas
- Comércio
- Representantes Comerciais
- Pequenas Indústrias
- Empresas de Manutenção
- Empresas de Instalação
- Empresas de Informática
- Consultorias

---

# Problemas que o VeloAI resolve

- Uso de vários sistemas diferentes.
- Falta de integração entre setores.
- Muito trabalho manual.
- Processos repetitivos.
- Falta de indicadores.
- Baixa produtividade.
- Dificuldade em controlar ordens de serviço.
- Controle financeiro descentralizado.
- Falta de informações para tomada de decisão.
- Sistemas antigos e pouco intuitivos.

---

# Diferenciais

## IA Nativa

Toda tela possui integração com Inteligência Artificial.

Não existe módulo sem IA.

---

## AI First

Toda funcionalidade nasce preparada para utilização pela IA.

Toda ação possui uma Tool.

Toda Tool possui um Service.

Toda ação pode ser executada por linguagem natural.

---

## Multi-Tenant

Cada empresa possui:

- Banco PostgreSQL exclusivo.
- Storage exclusivo.
- Vetores exclusivos.
- Configurações exclusivas.
- Usuários exclusivos.
- Dados totalmente isolados.

---

## Arquitetura Moderna

- FastAPI
- Vue 3
- TypeScript
- Docker
- PostgreSQL
- Redis
- RabbitMQ
- Celery
- Qdrant
- MinIO
- LangChain
- LangGraph
- MCP
- RAG

---

# IA Operacional

A IA poderá executar ações reais dentro da plataforma.

Exemplos:

Cadastrar clientes.

Cadastrar produtos.

Atualizar preços.

Criar serviços.

Criar ordens de serviço.

Gerar propostas.

Consultar indicadores.

Gerar gráficos.

Criar relatórios.

Lançar contas.

Pesquisar informações.

Atualizar estoque.

Gerar PDFs.

Responder dúvidas.

Executar automações.

Nunca será apenas um chatbot.

---

# Fluxo Geral

```text
Usuário
    ↓
Frontend Vue
    ↓
FastAPI
    ↓
Autenticação
    ↓
Planner Agent
    ↓
Executor Agent
    ↓
Tool
    ↓
Service
    ↓
Repository
    ↓
Banco PostgreSQL
```

---

# Objetivos do Produto

- Reduzir o tempo gasto em tarefas administrativas.
- Centralizar informações.
- Melhorar produtividade.
- Automatizar processos.
- Facilitar análises.
- Melhorar tomada de decisão.
- Reduzir erros operacionais.
- Aumentar controle financeiro.
- Aumentar controle operacional.
- Permitir gestão completa através de IA.

---

# Interface

A interface deverá transmitir sensação de produto premium.

Referências:

- Stripe
- Linear
- Notion
- Vercel
- ClickUp
- Raycast
- Arc Browser

Características:

- Minimalista.
- Moderna.
- Extremamente rápida.
- Responsiva.
- Dark Mode.
- Light Mode.
- Poucos cliques.
- Navegação intuitiva.

---

# Dashboard

O Dashboard será a principal tela do sistema.

Objetivos:

- Mostrar indicadores.
- Mostrar gráficos.
- Mostrar alertas.
- Mostrar insights gerados por IA.
- Mostrar recomendações.
- Mostrar atividades recentes.
- Mostrar próximos vencimentos.
- Mostrar ordens atrasadas.
- Mostrar estoque crítico.
- Mostrar previsão financeira.

Todos os gráficos utilizarão exclusivamente **amCharts 5**.

Todas as tabelas utilizarão **TanStack Table**.

---

# Inteligência Artificial

Provider inicial:

```env
AI_PROVIDER=google
AI_REPORT_MODEL=gemini-3.1-flash-lite
GEMINI_API_KEY=
```

Arquitetura preparada para:

- OpenAI
- Anthropic
- Ollama
- DeepSeek
- Grok
- Mistral
- Llama

A troca de provedor deverá ocorrer apenas por configuração.

---

# Modelo Comercial

Modelo → SaaS.

Cobrança → Mensal.

Plano inicial → R$129,00/mês.

Arquitetura preparada para múltiplos planos.

---

# Escalabilidade

O sistema deverá suportar:

- Milhares de empresas.
- Milhões de registros.
- Milhares de usuários simultâneos.
- Processamento distribuído.
- Workers independentes.
- Escalabilidade horizontal.

---

# Objetivo Final

O VeloAI deverá tornar-se a principal plataforma de gestão empresarial baseada em Inteligência Artificial da América Latina, oferecendo uma experiência moderna, simples e altamente automatizada, permitindo que empresas administrem praticamente toda sua operação conversando com uma IA.

---
