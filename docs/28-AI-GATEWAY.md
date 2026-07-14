# 28-AI-GATEWAY.md

> Projeto → VeloAI
> Documento → AI Gateway
> Módulo → Inteligência Artificial
> Versão → 1.0.0

---

# Objetivo

O AI Gateway será um microserviço independente responsável por toda comunicação entre o VeloAI e qualquer modelo de Inteligência Artificial.

Nenhum outro serviço do sistema poderá chamar diretamente uma LLM.

Toda requisição obrigatoriamente passará pelo AI Gateway.

O objetivo é desacoplar completamente o Backend das LLMs, permitindo adicionar, remover ou substituir modelos sem alterar a aplicação.

---

# Filosofia

Backend nunca conversa com LLM.

Frontend nunca conversa com LLM.

Workers nunca conversam com LLM.

Provisioning nunca conversa com LLM.

Todos os serviços utilizam exclusivamente o AI Gateway.

---

# Arquitetura

```text
                        Frontend
                            │
                            ▼
                      Backend API
                            │
                            ▼
                       AI Gateway
                            │
      ┌─────────────────────┼─────────────────────┐
      │                     │                     │
      ▼                     ▼                     ▼
  Gemini API          OpenAI API           Anthropic API
      │                     │                     │
      ▼                     ▼                     ▼
 Gemini Models         GPT Models          Claude Models
      │
      ├───────────────┐
      ▼               ▼
 DeepSeek API      Ollama
                      │
                      ▼
                Modelos Locais
```

---

# Responsabilidades

Receber requisições.

Selecionar modelo.

Montar prompts.

Aplicar contexto.

Consultar RAG.

Executar MCP.

Executar Agents.

Executar Planner.

Executar memória.

Executar Cache.

Executar Fallback.

Executar Retry.

Registrar auditoria.

Registrar métricas.

Calcular custo.

Controlar Rate Limit.

Controlar Tokens.

---

# Modelos Suportados

Gemini.

OpenAI.

Claude.

DeepSeek.

Llama.

Mistral.

Qwen.

Ollama.

OpenRouter.

Amazon Bedrock.

Azure OpenAI.

Vertex AI.

---

# Modelo Inicial

Modelo Principal.

```
gemini-3.1-flash-lite
```

Variável.

```
AI_REPORT_MODEL=gemini-3.1-flash-lite
```

API Key.

```
GEMINI_API_KEY
```

---

# Futuramente

Adicionar.

Gemini Pro.

Claude Sonnet.

Claude Opus.

GPT-5.

GPT-5 Mini.

DeepSeek.

Modelos locais.

Sem alterar Backend.

---

# Estrutura

```text
ai_gateway/

api/

routers/

services/

providers/

planner/

agents/

memory/

rag/

mcp/

prompts/

cache/

metrics/

billing/

security/

tests/
```

---

# Providers

Cada LLM possuirá um Provider.

```text
providers/

gemini.py

openai.py

claude.py

deepseek.py

ollama.py

bedrock.py
```

Todos implementarão a mesma interface.

---

# Interface

Cada Provider deverá possuir.

Generate.

Streaming.

Embeddings.

Health Check.

Estimate Cost.

List Models.

Count Tokens.

---

# Seleção de Modelo

O AI Gateway decidirá automaticamente.

Exemplo.

Relatórios.

↓

Gemini Flash Lite.

Análise Complexa.

↓

Claude.

Código.

↓

GPT.

OCR.

↓

Gemini.

Embeddings.

↓

Gemini Embedding.

---

# Roteador Inteligente

Criar.

Model Router.

Critérios.

Preço.

Velocidade.

Precisão.

Disponibilidade.

Tokens.

Plano do Cliente.

---

# Fallback

Fluxo.

```text
Gemini

↓

Erro

↓

Claude

↓

Erro

↓

GPT

↓

Erro

↓

DeepSeek

↓

Resposta
```

Nunca falhar imediatamente.

---

# Prompt Builder

Todo Prompt será criado pelo Gateway.

Nunca pelo Backend.

Separar.

System Prompt.

Developer Prompt.

Context Prompt.

Memory Prompt.

User Prompt.

---

# Prompt Versioning

Cada Prompt possuirá.

Versão.

Histórico.

Autor.

Data.

Rollback.

---

# Planner Agent

Responsável por decidir.

Consultar MCP.

Consultar RAG.

Responder diretamente.

Executar múltiplas Tools.

Executar múltiplos Agents.

---

# Agents

Criar inicialmente.

Planner Agent.

Executor Agent.

Report Agent.

Sales Agent.

CRM Agent.

Finance Agent.

OS Agent.

Dashboard Agent.

Automation Agent.

Document Agent.

---

# Memory

Implementar.

Short Memory.

Working Memory.

Long Memory.

Semantic Memory.

Conversation Memory.

---

# Cache

Criar.

Prompt Cache.

Embedding Cache.

Response Cache.

Tool Cache.

Context Cache.

TTL configurável.

---

# Tokens

Controlar.

Entrada.

Saída.

Total.

Limites.

Custo.

Por Tenant.

Por Usuário.

---

# Billing

Registrar.

Modelo.

Tokens.

Valor.

Empresa.

Usuário.

Data.

Tempo.

---

# Rate Limit

Limitar.

Por Tenant.

Por Usuário.

Por Plano.

Por Minuto.

Por Hora.

Por Dia.

---

# Segurança

Nunca registrar.

Senhas.

JWT.

Credenciais.

Cartões.

Dados sensíveis.

Mascarar automaticamente.

---

# MCP

Toda execução de Tool ocorrerá.

```text
Planner

↓

MCP

↓

Tool

↓

Backend

↓

Banco
```

Nunca acessar banco diretamente.

---

# RAG

Toda consulta seguirá.

```text
Pergunta

↓

Embedding

↓

Busca

↓

Ranking

↓

Contexto

↓

Prompt

↓

LLM
```

---

# Streaming

Permitir.

Server Sent Events.

WebSocket.

Chunks.

Cancelamento.

Reconexão.

---

# APIs

```
POST /chat

POST /generate

POST /stream

POST /embeddings

POST /agents

POST /planner

POST /tools

GET /models

GET /health

GET /metrics
```

---

# Observabilidade

Registrar.

Modelo.

Tempo.

Prompt.

Tokens.

Tenant.

Usuário.

Custo.

Fallback.

Retry.

Ferramentas.

---

# Métricas

Tempo Médio.

Tokens.

Custo.

Modelo.

Ferramentas.

Cache Hit.

Cache Miss.

Fallback.

Erro.

Timeout.

---

# Dashboard IA

Criar Dashboard exclusivo.

Mostrar.

Consumo.

Tokens.

Custo.

Modelos.

Ferramentas.

Top Tenants.

Top Usuários.

Tempo Médio.

Falhas.

---

# Auditoria

Registrar.

Quem perguntou.

Modelo.

Prompt.

Ferramentas.

Documentos.

Resultado.

Tempo.

---

# Testes

Cobertura mínima.

95%.

Testar.

Providers.

Fallback.

Planner.

Agents.

Cache.

Streaming.

Rate Limit.

Billing.

Segurança.

---

# Docker

Serviço independente.

```yaml
ai-gateway

redis

worker
```

---

# Escalabilidade

Permitir.

Múltiplas instâncias.

Balanceamento.

Fila.

Cache distribuído.

Escalonamento horizontal.

---

# Roadmap

Adicionar.

Model Context Protocol Remoto.

Agent2Agent.

Computer Use.

Voice Agents.

Vision Agents.

Realtime API.

Memory Persistente.

Aprendizado Contínuo.

Auto Prompt Optimization.

A/B Testing de Modelos.

Fine Tuning.

Knowledge Graph.

GraphRAG.

---

# Regras Obrigatórias

Nenhuma LLM poderá ser chamada diretamente.

Todo Prompt deverá passar pelo Prompt Builder.

Toda Tool deverá utilizar MCP.

Toda busca deverá utilizar RAG quando necessário.

Todo consumo deverá ser registrado.

Todo custo deverá ser calculado.

Todo Prompt deverá possuir versão.

Todo modelo deverá implementar a interface oficial.

Todo erro deverá gerar fallback quando possível.

Todo acesso deverá respeitar o isolamento entre Tenants.

---

# Objetivo Final

O AI Gateway será o núcleo da Inteligência Artificial do VeloAI. Ele será responsável por orquestrar modelos, agentes, memória, RAG, MCP, cache, billing, observabilidade e segurança em um único ponto centralizado. Essa arquitetura eliminará o acoplamento com fornecedores específicos de IA, permitirá evolução contínua da plataforma e garantirá escalabilidade para suportar milhares de empresas utilizando diferentes modelos de linguagem de forma transparente.

---
