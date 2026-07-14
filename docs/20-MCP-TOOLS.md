# 20-MCP-TOOLS.md

> Projeto → VeloAI
> Documento → Especificação das MCP Tools
> Módulo → Inteligência Artificial
> Versão → 1.0.0

---

# Objetivo

Toda interação entre a Inteligência Artificial e o VeloAI deverá ocorrer exclusivamente através de MCP (Model Context Protocol).

A IA nunca poderá acessar diretamente o banco de dados, executar SQL, chamar repositórios ou manipular entidades da aplicação.

Toda operação será realizada através de Tools registradas no MCP Server.

Cada Tool será responsável por uma única ação, possuirá validação própria, auditoria, controle de permissões e isolamento por Tenant.

---

# Filosofia

Fluxo obrigatório.

```text
Usuário

↓

LLM

↓

Planner Agent

↓

MCP Server

↓

Tool

↓

Backend

↓

Banco

↓

Resposta

↓

LLM

↓

Usuário
```

Nunca permitir.

LLM → Banco.

LLM → SQL.

LLM → Repository.

LLM → ORM.

Toda comunicação deverá passar pelo MCP.

---

# Arquitetura

```text
ai/

↓

planner

↓

executor

↓

mcp

↓

tool_registry

↓

tool_executor

↓

modules
```

Cada módulo registrará automaticamente suas próprias Tools.

---

# Estrutura de uma Tool

Toda Tool deverá possuir.

Nome.

Descrição.

Versão.

Categoria.

Permissões.

Schema de Entrada.

Schema de Saída.

Validações.

Auditoria.

Timeout.

Tratamento de Erros.

Documentação.

---

# Convenção de Nomes

Utilizar PascalCase.

Exemplos.

CreateCustomer.

UpdateCustomer.

DeleteCustomer.

SearchCustomers.

CreateProduct.

CreateSale.

CreateServiceOrder.

GenerateFinancialReport.

Nunca utilizar nomes genéricos.

---

# Categorias

CRM.

Produtos.

Estoque.

Serviços.

Ordens de Serviço.

Vendas.

Financeiro.

Agenda.

Usuários.

Empresas.

Relatórios.

Dashboard.

Notificações.

Automações.

Arquivos.

OCR.

IA.

Sistema.

---

# Estrutura de Entrada

Exemplo.

```json
{
  "customer_name": "João Silva",
  "phone": "(19)99999-9999",
  "email": "joao@email.com"
}
```

Toda entrada será validada com Pydantic.

---

# Estrutura de Saída

Padrão obrigatório.

```json
{
  "success": true,
  "message": "Cliente criado com sucesso.",
  "data": {},
  "errors": []
}
```

Nunca retornar estruturas diferentes.

---

# Contexto Obrigatório

Toda execução receberá automaticamente.

Tenant.

Usuário.

Empresa.

Idioma.

Timezone.

Permissões.

Request ID.

Conversation ID.

Nunca permitir que a IA informe esses dados manualmente.

---

# Registro das Tools

Criar um Tool Registry.

```text
Tool Registry

↓

Descobre módulos

↓

Carrega Tools

↓

Valida

↓

Registra

↓

Disponibiliza para IA
```

Nenhuma Tool deverá ser registrada manualmente.

---

# Descoberta Automática

Cada módulo possuirá.

```text
mcp_tools/
```

Exemplo.

```text
customers/

mcp_tools/

create_customer.py

update_customer.py

delete_customer.py

search_customer.py
```

O Registry carregará automaticamente.

---

# CRM Tools

CreateCustomer.

UpdateCustomer.

DeleteCustomer.

ArchiveCustomer.

SearchCustomers.

GetCustomer.

GetCustomerHistory.

AddCustomerNote.

UploadCustomerDocument.

MergeCustomers.

---

# Produtos

CreateProduct.

UpdateProduct.

DeleteProduct.

SearchProducts.

AdjustStock.

ReserveStock.

ReleaseStock.

TransferStock.

ImportProducts.

ExportProducts.

---

# Estoque

InventoryCount.

InventoryAdjustment.

GenerateInventoryReport.

StockMovement.

LowStockProducts.

ExpiredProducts.

---

# Ordens de Serviço

CreateServiceOrder.

UpdateServiceOrder.

AssignTechnician.

ScheduleServiceOrder.

AddProductToServiceOrder.

AddServiceToServiceOrder.

CloseServiceOrder.

CancelServiceOrder.

GenerateServiceOrderPDF.

---

# Comercial

CreateQuote.

ApproveQuote.

RejectQuote.

ConvertQuoteToSale.

CreateSale.

CancelSale.

GenerateProposal.

---

# Financeiro

CreateReceivable.

ReceivePayment.

CreatePayable.

PayBill.

GenerateCashFlow.

GenerateDRE.

GenerateFinancialProjection.

---

# Dashboard

GenerateDashboard.

GenerateChart.

GetKPIs.

GetAlerts.

GetInsights.

---

# Relatórios

GenerateSalesReport.

GenerateCRMReport.

GenerateStockReport.

GenerateFinancialReport.

GenerateExecutiveSummary.

ExportPDF.

ExportExcel.

ExportCSV.

---

# Agenda

CreateEvent.

UpdateEvent.

DeleteEvent.

ScheduleReminder.

ListEvents.

---

# Usuários

CreateUser.

UpdateUser.

DisableUser.

ResetPassword.

AssignRole.

RemoveRole.

---

# Empresa

UpdateCompany.

UpdateBranding.

UploadLogo.

UpdateSettings.

GetCompanyInformation.

---

# Arquivos

UploadFile.

DownloadFile.

DeleteFile.

MoveFile.

GenerateShareLink.

---

# OCR

ReadInvoice.

ReadReceipt.

ReadPDF.

ReadImage.

ExtractText.

DetectFields.

---

# IA

SearchKnowledge.

IndexDocument.

GenerateSummary.

GenerateSuggestions.

GenerateInsights.

AnalyzeConversation.

---

# Automações

CreateWorkflow.

UpdateWorkflow.

ExecuteWorkflow.

PauseWorkflow.

ResumeWorkflow.

DeleteWorkflow.

---

# Sistema

HealthCheck.

GetVersion.

GetConfiguration.

Ping.

---

# Segurança

Toda Tool deverá validar.

Tenant.

Permissões.

Usuário.

Empresa.

Plano.

Feature Flags.

Nunca confiar na IA.

---

# Timeout

Cada Tool deverá definir.

Tempo máximo.

Tentativas.

Retry.

Cancelamento.

Circuit Breaker.

---

# Logs

Registrar.

Tool.

Tempo.

Entrada.

Saída.

Usuário.

Tenant.

Resultado.

Erro.

---

# Auditoria

Toda Tool deverá gerar.

Quem executou.

Quando.

Qual entidade foi alterada.

Valor anterior.

Novo valor.

Request ID.

Conversation ID.

---

# Idempotência

Ferramentas críticas deverão aceitar.

Idempotency Key.

Evitando duplicações.

Principalmente.

Financeiro.

Vendas.

Ordens de Serviço.

Provisionamento.

---

# Erros

Padrão.

```json
{
  "success": false,
  "message": "Produto não encontrado.",
  "code": "PRODUCT_NOT_FOUND",
  "errors": []
}
```

Nunca lançar exceções diretamente para a IA.

---

# Versionamento

Toda Tool possuirá.

Version.

Deprecated.

Replacement.

Compatibilidade.

---

# Observabilidade

Registrar.

Latência.

Tokens.

Tempo de execução.

Uso.

Erros.

Timeouts.

Ferramentas mais utilizadas.

---

# Performance

Permitir.

Cache.

Execução assíncrona.

Batch.

Paginação.

Streaming.

---

# Testes

Cada Tool deverá possuir.

Testes Unitários.

Testes de Integração.

Testes de Permissão.

Testes de Tenant.

Testes de Auditoria.

Cobertura mínima.

95%.

---

# Exemplo Completo

Usuário.

```
Cadastre um cliente chamado João Silva.
```

Planner Agent.

↓

Seleciona.

```
CreateCustomer
```

Executor.

↓

Valida parâmetros.

↓

Executa Tool.

↓

Backend.

↓

Banco.

↓

Resposta.

```json
{
  "success": true,
  "message": "Cliente criado com sucesso.",
  "data": {
    "id": "uuid"
  }
}
```

↓

LLM.

↓

Usuário.

---

# Regras Obrigatórias

Toda Tool deverá possuir documentação.

Toda Tool deverá possuir testes.

Toda Tool deverá validar Tenant.

Toda Tool deverá validar permissões.

Toda Tool deverá registrar auditoria.

Toda Tool deverá possuir logs.

Toda Tool deverá utilizar Pydantic.

Toda Tool deverá possuir timeout.

Toda Tool deverá retornar estrutura padronizada.

Nenhuma Tool poderá acessar outro Tenant.

Nenhuma Tool poderá executar SQL diretamente.

Nenhuma Tool poderá ignorar regras de negócio.

---

# Roadmap

Adicionar.

Streaming Tools.

Parallel Tools.

Tool Chaining.

Tool Marketplace.

Ferramentas Externas.

MCP Remoto.

Agentes Distribuídos.

Observabilidade Avançada.

Execução Paralela Inteligente.

---

# Objetivo Final

A camada MCP será o único ponto de comunicação entre a Inteligência Artificial e o VeloAI. Todas as operações deverão ser executadas através de Tools especializadas, seguras, auditáveis e isoladas por Tenant. Essa arquitetura permitirá adicionar novos modelos de IA, novos agentes e novas funcionalidades sem alterar as regras de negócio da aplicação, garantindo escalabilidade, segurança e previsibilidade em todas as ações executadas pela IA.

---
