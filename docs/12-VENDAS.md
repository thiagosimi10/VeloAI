# 12-VENDAS.md

> Projeto → VeloAI
> Documento → Módulo de Vendas
> Módulo → Comercial
> Versão → 1.0.0

---

# Objetivo

O módulo de Vendas será responsável por controlar todo o processo comercial da empresa, desde a criação de um orçamento até a venda final, faturamento, recebimento e emissão futura de documentos fiscais.

Todo o fluxo deverá ser totalmente integrado ao CRM, Estoque, Financeiro, Fiscal, Dashboard e Inteligência Artificial.

O usuário deverá conseguir realizar uma venda completa apenas conversando com a IA.

---

# Objetivos

Permitir:

- Criar Orçamentos.
- Converter Orçamentos em Vendas.
- Venda Direta.
- Venda de Produtos.
- Venda de Serviços.
- Venda Mista.
- Aplicação de Descontos.
- Parcelamentos.
- Reserva de Estoque.
- Baixa Automática de Estoque.
- Geração de Contas a Receber.
- Emissão futura de Nota Fiscal.
- Assinatura Digital.
- Envio por E-mail.
- Envio por WhatsApp.

---

# Menu

```text
Comercial

├── Orçamentos
├── Vendas
├── Pedidos
├── Clientes
├── Metas
├── Comissões
└── Relatórios
```

---

# Fluxo Comercial

```text
Lead

↓

Cliente

↓

Orçamento

↓

Negociação

↓

Aprovação

↓

Venda

↓

Pagamento

↓

Entrega

↓

Nota Fiscal (Futuro)

↓

Pós-venda
```

---

# Tipos de Venda

- Produto.
- Serviço.
- Produto + Serviço.
- Balcão.
- Delivery.
- Venda Técnica.
- Venda Recorrente.

---

# Status

## Orçamento

- Rascunho.
- Enviado.
- Em Negociação.
- Aprovado.
- Rejeitado.
- Expirado.
- Cancelado.

---

## Venda

- Aberta.
- Aguardando Pagamento.
- Paga.
- Faturada.
- Entregue.
- Finalizada.
- Cancelada.

---

# Layout

```text
┌────────────────────────────────────────────────────────────┐
│ Cabeçalho                                                  │
├────────────────────────────────────────────────────────────┤
│ Cliente │ Vendedor │ Status │ Forma Pagamento              │
├────────────────────────────────────────────────────────────┤
│ Produtos                                                   │
├────────────────────────────────────────────────────────────┤
│ Serviços                                                   │
├────────────────────────────────────────────────────────────┤
│ Descontos │ Impostos │ Total                               │
├────────────────────────────────────────────────────────────┤
│ Parcelas │ Financeiro │ IA                                 │
└────────────────────────────────────────────────────────────┘
```

---

# Cabeçalho

Campos:

- Número.
- Cliente.
- Vendedor.
- Data.
- Status.
- Origem.
- Canal.
- Observações.

---

# Produtos

Cada item deverá possuir:

- Produto.
- Quantidade.
- Unidade.
- Preço.
- Desconto.
- Total.
- Estoque Disponível.
- Margem.

---

# Serviços

Cada item deverá possuir:

- Serviço.
- Quantidade.
- Valor.
- Desconto.
- Tempo Estimado.
- Total.

---

# Totais

Calcular automaticamente:

- Subtotal.
- Descontos.
- Acréscimos.
- Frete.
- Impostos.
- Total Geral.
- Lucro Estimado.
- Margem.

---

# Parcelamento

Permitir:

- Entrada.
- Parcelas.
- Datas personalizadas.
- Juros.
- Desconto à vista.

Cada parcela gerará um título financeiro independente.

---

# Formas de Pagamento

- PIX.
- Dinheiro.
- Cartão Crédito.
- Cartão Débito.
- Transferência.
- Boleto.
- Link de Pagamento.

Arquitetura preparada para integração automática.

---

# Reserva de Estoque

Ao criar orçamento.

Opcionalmente reservar produtos.

Ao converter em venda.

Confirmar reserva.

Ao cancelar.

Liberar estoque.

---

# Conversão

Fluxo.

```text
Orçamento

↓

Aprovado

↓

Venda

↓

Financeiro

↓

Estoque

↓

Dashboard
```

Conversão com um clique.

---

# Comissão

Preparado para cálculo automático.

Configurações:

- Percentual.
- Valor Fixo.
- Faixas.
- Por Produto.
- Por Serviço.
- Por Categoria.

---

# Entrega

Preparado para:

- Retirada.
- Entrega.
- Transportadora.
- Correios.

No futuro:

Código de rastreamento.

---

# Inteligência Artificial

Botão fixo.

```
✨ Assistente Comercial
```

---

## Exemplos

```
Crie um orçamento para João Silva.

Notebook Dell Latitude.

Mouse Logitech.

Desconto de 5%.

Pagamento em 3 vezes.
```

---

```
Converta este orçamento em venda.
```

---

```
Aplique 10% de desconto apenas nos serviços.
```

---

```
Quais vendas ainda não foram pagas?
```

---

```
Quanto vendemos este mês?
```

---

```
Quem é meu melhor vendedor?
```

---

```
Mostre os dez produtos mais vendidos no último trimestre.
```

---

A IA poderá:

- Criar.
- Alterar.
- Cancelar.
- Converter.
- Calcular.
- Gerar propostas.
- Explicar indicadores.
- Gerar gráficos.
- Gerar relatórios.

---

# MCP Tools

Obrigatórias.

CreateQuote.

UpdateQuote.

ApproveQuote.

RejectQuote.

ConvertQuoteToSale.

CreateSale.

UpdateSale.

CancelSale.

GeneratePayment.

ReserveStock.

ReleaseStock.

GeneratePDF.

GenerateQuote.

GenerateSalesReport.

SalesProjection.

TopSellingProducts.

TopCustomers.

TopSalespeople.

---

# APIs

```
GET /quotes

POST /quotes

PUT /quotes/{id}

POST /quotes/{id}/approve

POST /quotes/{id}/reject

POST /quotes/{id}/convert

GET /sales

POST /sales

PUT /sales/{id}

POST /sales/{id}/cancel

GET /sales/report

GET /sales/dashboard
```

---

# Dashboard

Indicadores.

- Faturamento Diário.
- Faturamento Mensal.
- Ticket Médio.
- Quantidade de Vendas.
- Conversão de Orçamentos.
- Produtos Mais Vendidos.
- Serviços Mais Vendidos.
- Top Clientes.
- Top Vendedores.
- Lucro por Venda.
- Receita por Categoria.

Todos os gráficos utilizarão amCharts 5.

---

# Relatórios

Orçamentos.

Conversão.

Vendas.

Produtos.

Serviços.

Comissões.

Clientes.

Categorias.

Margem.

Lucro.

Cancelamentos.

Todos poderão ser solicitados pela IA.

Exemplo.

```
Compare as vendas do primeiro semestre com o segundo semestre.
```

---

# Auditoria

Registrar.

Criação.

Alteração.

Aprovação.

Conversão.

Pagamento.

Cancelamento.

Exportação.

Importação.

---

# Regras de Negócio

Não permitir venda de produto sem estoque, salvo configuração da empresa.

Ao finalizar venda.

↓

Baixar estoque automaticamente.

↓

Atualizar Dashboard.

↓

Gerar Conta a Receber.

↓

Atualizar histórico do cliente.

↓

Atualizar ranking de produtos.

↓

Atualizar ranking do vendedor.

Cancelamento deverá estornar:

- Estoque.
- Financeiro.
- Comissões.

Nunca excluir vendas.

Sempre cancelar.

---

# Eventos

Disparar.

QuoteCreated.

QuoteApproved.

QuoteRejected.

QuoteConverted.

SaleCreated.

SalePaid.

SaleCancelled.

StockConsumed.

PaymentGenerated.

Todos poderão acionar:

- Dashboard.
- IA.
- Notificações.
- Emails.
- WhatsApp.
- Webhooks.

---

# Integrações Futuras

Mercado Pago.

Asaas.

Stripe.

PagSeguro.

Mercado Livre.

Shopee.

Amazon.

NFe.

NFC-e.

WhatsApp Business.

---

# Permissões

```
sales.view

sales.create

sales.update

sales.cancel

sales.approve

sales.discount

sales.export

sales.reports

sales.ai
```

---

# Testes

Cobertura mínima.

90%.

Testar:

Orçamentos.

Conversão.

Vendas.

Descontos.

Parcelamentos.

Estoque.

Financeiro.

IA.

Eventos.

Permissões.

---

# Critérios de Aceite

✔ Orçamentos.

✔ Conversão em Venda.

✔ Baixa automática de estoque.

✔ Integração com Financeiro.

✔ Dashboard.

✔ IA funcional.

✔ Relatórios.

✔ Auditoria.

✔ Eventos.

✔ Testes.

---

# Objetivo Final

O módulo de Vendas deverá permitir que toda a operação comercial da empresa seja executada de forma simples, rápida e integrada. Desde a criação de um orçamento até a conclusão da venda, todas as etapas deverão ser automatizadas, auditáveis e assistidas por Inteligência Artificial, permitindo que o empresário aumente suas vendas e reduza tarefas operacionais através de automações inteligentes.

---
