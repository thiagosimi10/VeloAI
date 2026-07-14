# 31-BILLING.md

> Projeto → VeloAI
> Documento → Billing, Assinaturas e Monetização
> Produto → SaaS Multi Tenant
> Versão → 1.0.0

---

# Objetivo

Definir toda a arquitetura de cobrança, assinaturas, planos, limites, upgrades, cancelamentos e monetização do VeloAI.

O Billing será um módulo independente do CRM.

Toda empresa cadastrada possuirá uma assinatura.

Sem assinatura válida a empresa não poderá utilizar o sistema.

---

# Filosofia

Cobrança automática.

Renovação automática.

Baixa inadimplência.

Escalabilidade.

Integração via API.

Toda cobrança auditável.

---

# Modelo de Negócio

SaaS.

Assinatura Mensal.

Renovação Automática.

Sem Fidelidade.

Cancelamento quando desejar.

---

# Valor Inicial

Plano.

```text
VeloAI Professional
```

Valor.

```text
R$ 129,90 / mês
```

---

# Trial

Todos os novos clientes receberão.

14 dias gratuitos.

Sem cobrança antecipada.

Sem necessidade de cartão de crédito no cadastro inicial.

Ao final do Trial será necessário contratar um plano para continuar utilizando a plataforma.

---

# Gateway de Pagamento

Arquitetura preparada para múltiplos provedores.

Inicialmente.

Asaas.

Futuramente.

Stripe.

Mercado Pago.

Iugu.

Pagar.me.

PagSeguro.

---

# Provider Pattern

Criar.

```text
billing/

providers/

asaas.py

stripe.py

mercadopago.py

base_provider.py
```

Todos deverão implementar a mesma interface.

---

# Métodos de Pagamento

PIX.

Boleto.

Cartão de Crédito.

Cartão de Débito quando suportado.

Link de Pagamento.

Assinatura Recorrente.

---

# Fluxo de Cadastro

```text
Empresa

↓

Trial iniciado

↓

Banco criado

↓

Usuário Administrador criado

↓

Sistema liberado

↓

14 dias

↓

Pagamento

↓

Assinatura Ativa
```

---

# Estados da Assinatura

TRIAL.

ACTIVE.

PENDING_PAYMENT.

OVERDUE.

SUSPENDED.

CANCELED.

EXPIRED.

---

# Fluxo

```text
Trial

↓

Pagamento

↓

Ativa

↓

Falha

↓

Inadimplente

↓

Suspensa

↓

Pagamento

↓

Reativada
```

---

# Suspensão

Após vencimento.

5 dias.

↓

Lembrete.

↓

10 dias.

↓

Novo aviso.

↓

15 dias.

↓

Sistema somente leitura.

↓

20 dias.

↓

Conta suspensa.

↓

60 dias.

↓

Arquivamento.

↓

180 dias.

↓

Exclusão definitiva mediante política da empresa e LGPD.

---

# Plano Inicial

VeloAI Professional.

Inclui.

Usuários ilimitados.

Clientes ilimitados.

Produtos ilimitados.

Ordens de Serviço ilimitadas.

Vendas ilimitadas.

Financeiro completo.

Dashboard IA.

Relatórios IA.

Chat IA.

RAG.

MCP.

Uploads.

Emissão de documentos.

API.

---

# Limites

Inicialmente.

Sem limite de usuários.

Sem limite de produtos.

Sem limite de clientes.

Sem limite de documentos.

Sem limite de vendas.

Sem limite de Ordens de Serviço.

---

# Limite de IA

Controle interno.

Tokens.

Custo.

Tempo.

Uso.

Não limitar inicialmente.

Monitorar consumo por Tenant.

Preparar para futuras políticas.

---

# Billing Dashboard

Exibir.

Plano.

Valor.

Próximo vencimento.

Situação.

Histórico.

Faturas.

Pagamentos.

Consumo IA.

---

# Tela Financeira da Assinatura

Mostrar.

Plano atual.

Dias restantes do Trial.

Situação.

Cobranças.

PIX.

Boletos.

Cartão.

Atualizar pagamento.

Cancelar assinatura.

---

# Faturas

Armazenar.

Número.

Valor.

Data.

Status.

PDF.

Link.

Pagamento.

Webhook.

---

# Webhooks

Receber.

Pagamento aprovado.

Pagamento recusado.

Cancelamento.

Chargeback.

Estorno.

Atualização de assinatura.

---

# API Billing

Criar.

```
POST /billing/create

POST /billing/cancel

POST /billing/reactivate

POST /billing/change-plan

POST /billing/webhook

GET /billing/invoices

GET /billing/subscription

GET /billing/history
```

---

# Auditoria

Registrar.

Plano.

Valor.

Mudanças.

Pagamento.

Falha.

Webhook.

Usuário.

Empresa.

---

# IA

A IA poderá responder.

Qual meu plano.

Quando vence.

Quanto paguei.

Mostrar minhas faturas.

Gerar segunda via.

Alterar forma de pagamento.

Cancelar assinatura.

Sempre utilizando MCP.

---

# Dashboard Executivo

Mostrar.

MRR.

ARR.

Clientes Ativos.

Trial.

Cancelamentos.

Receita.

Churn.

Ticket Médio.

LTV.

CAC futuramente.

---

# Métricas

MRR.

ARR.

Churn.

ARPU.

LTV.

Receita Diária.

Receita Mensal.

Receita Anual.

Trial Conversion.

---

# Segurança

Nunca armazenar.

Cartões.

CVV.

Dados bancários.

Toda cobrança será realizada pelo Gateway de Pagamento.

---

# Backup

Salvar.

Faturas.

Eventos.

Webhooks.

Histórico.

Logs.

---

# Multi Tenant

Cada empresa visualizará apenas.

Seu plano.

Suas faturas.

Seu histórico.

Seu consumo.

---

# Admin Master

Painel administrativo poderá visualizar.

Todas as empresas.

Receita.

Pagamentos.

Trials.

Inadimplentes.

Cancelamentos.

---

# Futuro

Adicionar.

Plano Enterprise.

Plano White Label.

Plano Franquia.

Plano Revenda.

Marketplace.

Cobrança por uso de IA.

Cobrança por Storage.

Cobrança por API.

---

# Regras Obrigatórias

Nenhum Tenant poderá utilizar o sistema após suspensão definitiva.

Todo pagamento deverá ser auditado.

Todo webhook deverá ser validado.

Toda assinatura deverá possuir histórico.

Toda alteração deverá gerar evento.

Nenhum dado financeiro sensível será armazenado pelo VeloAI.

Toda cobrança deverá ser idempotente.

---

# Objetivo Final

O módulo de Billing deverá ser totalmente desacoplado do restante da aplicação, permitindo crescimento da plataforma, troca de gateways de pagamento, criação de novos planos e futura monetização baseada em consumo de IA, armazenamento ou integrações, mantendo simplicidade para o cliente e flexibilidade para evolução do negócio.

---
