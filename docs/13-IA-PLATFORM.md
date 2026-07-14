# 13-IA-PLATFORM.md

> Projeto → VeloAI
> Documento → Plataforma de Inteligência Artificial
> Módulo → IA
> Versão → 1.0.0

---

# Objetivo

A Inteligência Artificial será o principal diferencial do VeloAI.

Ela não será apenas um chat.

Ela será uma camada de execução inteligente presente em absolutamente todas as telas do sistema.

O usuário nunca precisará saber onde determinada funcionalidade está localizada.

Bastará dizer o que deseja fazer.

A IA entenderá a intenção, localizará a Tool correta, executará a ação e retornará o resultado.

O VeloAI será um sistema AI First.

A interface gráfica será apenas uma das formas de interação.

---

# Filosofia

Nunca perguntar:

"Em qual tela você deseja fazer isso?"

Sempre entender a intenção.

Sempre executar.

Sempre utilizar Tools.

Nunca inventar dados.

Nunca responder utilizando conhecimento próprio quando a informação existir no banco.

---

# Modelo Inicial

Primeiro modelo utilizado.

```env
AI_REPORT_MODEL=gemini-3.1-flash-lite

GEMINI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
```

Toda comunicação deverá passar pela camada de IA.

No futuro será possível trocar o modelo apenas alterando as variáveis de ambiente.

---

# Modelos Futuros

Arquitetura preparada para:

Gemini.

OpenAI.

Claude.

DeepSeek.

Llama.

Qwen.

Mistral.

Azure OpenAI.

Amazon Bedrock.

Ollama.

Modelos locais.

---

# Arquitetura

```text
Usuário

↓

Frontend Vue

↓

Backend FastAPI

↓

AI Gateway

↓

Planner Agent

↓

Executor Agent

↓

MCP Server

↓

Tools

↓

Sistema

↓

Resposta

↓

Usuário
```

Nenhuma Tool será chamada diretamente pelo Frontend.

---

# AI Gateway

Responsável por:

Autenticação.

Rate Limit.

Controle de Tokens.

Logs.

Contexto.

Seleção do Modelo.

Observabilidade.

Cache.

Auditoria.

---

# Agentes

A plataforma possuirá agentes especializados.

Cada agente possuirá uma única responsabilidade.

---

## Planner Agent

Responsável por interpretar a intenção do usuário.

Exemplo.

```
Abra uma OS para João.

```

Resultado.

Determinar.

Criar cliente.

Cadastrar equipamento.

Criar OS.

Agendar técnico.

Gerar resposta.

Nunca executar diretamente.

---

## Executor Agent

Executar Tools.

Validar parâmetros.

Executar regras.

Retornar resultados.

---

## Report Agent

Responsável por:

Relatórios.

Gráficos.

Insights.

Comparações.

KPIs.

Previsões.

Sempre utilizar amCharts para visualizações.

---

## CRM Agent

Especialista em:

Clientes.

Contatos.

Equipamentos.

Histórico.

---

## Sales Agent

Especialista em:

Orçamentos.

Vendas.

Conversões.

Comissões.

---

## Service Order Agent

Especialista em:

OS.

Agenda.

Técnicos.

Produtos.

Serviços.

---

## Financial Agent

Especialista em:

Receitas.

Despesas.

Fluxo.

Indicadores.

Projeções.

---

## Inventory Agent

Especialista em:

Produtos.

Categorias.

Compras.

Estoque.

Movimentações.

---

## Notification Agent

Responsável por:

Emails.

WhatsApp.

Push.

Alertas.

---

## OCR Agent

Responsável por:

PDF.

Imagem.

Nota Fiscal.

Comprovantes.

Documentos.

Extração automática de dados.

---

## Document Agent

Responsável por:

PDF.

Relatórios.

Propostas.

Orçamentos.

Ordens de Serviço.

Contratos.

---

## Automation Agent

Responsável por:

Execução de rotinas.

Agendamentos.

Workflows.

Eventos.

---

# MCP

Toda comunicação ocorrerá através de MCP.

Nunca acessar banco diretamente.

Nunca gerar SQL.

Nunca montar queries pela IA.

A IA apenas chamará Tools.

---

# Organização das Tools

CRM.

Products.

Sales.

Finance.

Service Orders.

Users.

Company.

Reports.

Dashboard.

Notifications.

Automation.

Documents.

OCR.

Storage.

Search.

Settings.

Audit.

Permissions.

---

# Exemplo de execução

Usuário.

```
Cadastre um cliente chamado João da Silva.
```

↓

Planner.

↓

Seleciona Tool.

```
CreateCustomer
```

↓

Executor.

↓

Validação.

↓

Backend.

↓

Banco.

↓

Resposta.

↓

Usuário.

---

# Outro exemplo

Usuário.

```
Quanto faturei em maio?
```

↓

Planner.

↓

Seleciona.

FinancialReport.

↓

Report Agent.

↓

amCharts.

↓

Resposta.

---

# Context Engineering

Toda conversa possuirá contexto.

Empresa.

Usuário.

Permissões.

Idioma.

Tenant.

Tela atual.

Módulo.

Histórico recente.

Preferências.

Nunca enviar informações desnecessárias para o modelo.

---

# Memória

## Curto Prazo

Histórico da conversa atual.

---

## Longo Prazo

Preferências do usuário.

Forma de responder.

Idioma.

Configurações.

Sempre respeitando LGPD.

---

# RAG

Cada Tenant possuirá sua própria base.

Nunca compartilhar documentos.

Nunca compartilhar embeddings.

Nunca compartilhar contexto.

---

# Fontes do RAG

PDF.

Word.

Excel.

Manuais.

Procedimentos.

FAQ.

Notas Técnicas.

Contratos.

Políticas.

Documentação interna.

---

# Banco Vetorial

Arquitetura preparada para.

PostgreSQL + pgvector.

No futuro.

Qdrant.

Pinecone.

Weaviate.

Milvus.

---

# Fluxo do RAG

```text
Pergunta

↓

Busca Vetorial

↓

Recuperação

↓

Contexto

↓

LLM

↓

Resposta
```

---

# Segurança

Toda Tool deverá validar.

Tenant.

Permissões.

Usuário.

Perfil.

Empresa.

Nunca confiar apenas na IA.

Toda validação ocorrerá no Backend.

---

# Prompt do Sistema

Sempre informar.

Empresa.

Usuário.

Idioma.

Módulo.

Permissões.

Tenant.

Data Atual.

Nunca informar dados de outros clientes.

---

# Guardrails

Nunca responder dados inexistentes.

Nunca inventar valores.

Nunca executar ação sem permissão.

Nunca acessar outro Tenant.

Nunca ignorar regras de negócio.

Sempre validar parâmetros antes de executar Tools.

---

# Logs

Registrar.

Prompt.

Modelo.

Tokens.

Tempo.

Ferramentas utilizadas.

Resultado.

Erro.

Usuário.

Tenant.

---

# Observabilidade

Métricas.

Tempo médio.

Latência.

Tokens.

Custo.

Ferramentas utilizadas.

Falhas.

Taxa de sucesso.

---

# Cache

Perguntas repetidas.

Relatórios.

Consultas.

KPIs.

Configurações.

Utilizar Redis.

---

# Rate Limit

Controlar.

Usuário.

Empresa.

Modelo.

Ferramentas.

Evitar abuso.

---

# IA em Todas as Telas

Obrigatório.

Dashboard.

Clientes.

Produtos.

Estoque.

Vendas.

Financeiro.

Ordens de Serviço.

Usuários.

Empresa.

Relatórios.

Configurações.

Sempre haverá um botão.

```
✨ Perguntar para IA
```

---

# Exemplos

```
Cadastre um cliente.

```

```
Abra uma Ordem de Serviço.

```

```
Crie um produto.

```

```
Aumente o preço em 8%.

```

```
Recebi um PIX.

```

```
Mostre minhas vendas.

```

```
Quais clientes estão inadimplentes?

```

```
Crie um relatório em PDF.

```

Tudo executado automaticamente.

---

# IA Proativa

A IA poderá sugerir.

Produtos sem estoque.

Clientes sem compra.

Fluxo negativo.

Despesas elevadas.

Lucro baixo.

Ordens atrasadas.

Serviços recorrentes.

Possibilidades de venda.

Nunca executar automaticamente.

Sempre solicitar confirmação quando houver impacto nos dados.

---

# Futuro

Adicionar.

Agentes especializados.

Voice Assistant.

Chat por WhatsApp.

Chat por Telegram.

Aplicativo Mobile.

Integração com E-mail.

Integração com Google Calendar.

Integração com Outlook.

Modo Offline.

Modelos Locais.

Multi Model Routing.

---

# Objetivo Final

A Plataforma de Inteligência Artificial do VeloAI deverá transformar completamente a forma como pequenas empresas utilizam um sistema de gestão. Em vez de navegar por menus complexos, o usuário poderá simplesmente conversar com o sistema utilizando linguagem natural. A IA será responsável por interpretar intenções, selecionar os agentes corretos, executar Tools via MCP, consultar informações através de RAG e retornar respostas confiáveis, auditáveis e contextualizadas, sempre respeitando permissões, isolamento entre tenants e regras de negócio. Toda a arquitetura deverá ser modular para permitir a evolução contínua da plataforma e a adoção de novos modelos de linguagem sem alterações significativas no restante do sistema.

---
