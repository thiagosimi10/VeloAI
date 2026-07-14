# 07-DASHBOARD.md

> Projeto → VeloAI
> Documento → Dashboard
> Tela → Home
> Versão → 1.0.0

---

# Objetivo

O Dashboard será a principal tela do VeloAI.

O usuário deverá conseguir entender a situação completa da empresa em menos de 30 segundos.

A IA será parte do Dashboard.

Não será apenas uma tela com gráficos.

Será um painel inteligente.

---

# Tecnologias

Gráficos → amCharts 5

Tabelas → TanStack Table

Atualização → WebSocket

Cache → Redis

IA → Gemini 3.1 Flash Lite

---

# Layout

```text
┌────────────────────────────────────────────────────────────┐
│ Menu Lateral              Header                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Assistente IA                                               │
│                                                            │
├────────────────────────────────────────────────────────────┤
│ KPIs                                                      │
├────────────────────────────────────────────────────────────┤
│ Receita │ Fluxo Caixa │ OS │ Estoque                      │
├────────────────────────────────────────────────────────────┤
│ Receita Mensal           │ Vendas por Categoria           │
├──────────────────────────┼────────────────────────────────│
│ Fluxo de Caixa           │ Produtos Mais Vendidos         │
├──────────────────────────┼────────────────────────────────│
│ Agenda                   │ Ordens em Aberto              │
├──────────────────────────┼────────────────────────────────│
│ Contas a Receber         │ Contas a Pagar                │
├──────────────────────────┼────────────────────────────────│
│ Atividades Recentes      │ Alertas IA                    │
└────────────────────────────────────────────────────────────┘
```

---

# Header

Itens:

- Logo da Empresa.
- Nome da Empresa.
- Pesquisa Global.
- Botão IA.
- Notificações.
- Perfil.
- Tema Claro/Escuro.

---

# Pesquisa Global

Pesquisar:

- Clientes.
- Produtos.
- Serviços.
- Ordens.
- Vendas.
- Financeiro.
- Usuários.

Resultados instantâneos.

Atalho:

```
CTRL + K
```

---

# Assistente IA

Sempre visível.

Não será um popup.

Será um componente fixo no topo.

Placeholder:

```
O que você deseja fazer hoje?
```

Exemplos:

```
Cadastre um cliente.

Abra uma ordem de serviço.

Quanto vendi em maio?

Qual produto mais vendeu?

Quais contas vencem hoje?

Mostre minhas ordens atrasadas.

Qual técnico mais faturou?
```

A IA poderá:

- Executar ações.
- Consultar dados.
- Criar gráficos.
- Criar relatórios.
- Gerar PDFs.
- Explicar indicadores.

---

# KPIs

Primeira linha.

Cards:

- Receita Hoje.
- Receita Mês.
- Receita Ano.
- Lucro.
- Ticket Médio.
- Total Clientes.
- Total Produtos.
- Total Ordens.
- Total Serviços.
- Contas a Receber.
- Contas a Pagar.
- Fluxo de Caixa.
- Estoque Crítico.
- Ordens Atrasadas.

Cada KPI deverá mostrar:

- Valor.
- Comparação.
- Percentual.
- Tendência.
- Ícone.

---

# Receita

Gráfico:

Line Chart.

Períodos:

- Hoje.
- Semana.
- Mês.
- Ano.
- Personalizado.

Mostrar:

- Receita.
- Meta.
- Comparação.

---

# Fluxo de Caixa

Gráfico:

Area Chart.

Mostrar:

- Entradas.
- Saídas.
- Saldo.

---

# Produtos

Gráfico:

Bar Chart.

Mostrar:

- Mais vendidos.
- Menos vendidos.
- Maior lucro.
- Menor lucro.

Filtros:

- Semana.
- Mês.
- Ano.

---

# Categorias

Gráfico:

Donut Chart.

Mostrar:

Participação das categorias.

---

# Ordens

Widgets:

- Em Aberto.
- Em Andamento.
- Concluídas.
- Atrasadas.
- Canceladas.

Ao clicar abrir listagem.

---

# Agenda

Mostrar:

- Hoje.
- Amanhã.
- Próximos 7 dias.

Permitir:

- Arrastar.
- Editar.
- Concluir.

---

# Financeiro

Widgets:

Contas a Receber.

Contas a Pagar.

Fluxo Diário.

Receita.

Despesa.

Lucro.

---

# Estoque

Widgets:

- Produtos abaixo do mínimo.
- Produtos sem estoque.
- Produtos mais vendidos.
- Produtos parados.
- Produtos próximos do vencimento.

---

# Ranking

Mostrar:

Top Clientes.

Top Produtos.

Top Técnicos.

Top Serviços.

Top Vendedores.

---

# Atividades

Timeline.

Mostrar:

- Login.
- Cadastro.
- Venda.
- Ordem.
- Produto.
- Financeiro.

---

# Alertas

Mostrar automaticamente:

- Contas vencidas.
- Estoque baixo.
- OS atrasadas.
- Clientes sem compra.
- Produtos sem movimentação.

---

# IA Insights

A IA deverá analisar automaticamente.

Exemplo:

```
Seu faturamento aumentou 14%.

O estoque possui 8 produtos abaixo do mínimo.

Seu melhor cliente representa 38% da receita.

Existem 4 contas vencidas.

As vendas cresceram em relação ao mês anterior.

O lucro caiu 6%.

O ticket médio aumentou.
```

Esses insights deverão aparecer automaticamente.

---

# Relatórios Inteligentes

Botão:

```
Gerar Relatório
```

Exemplos:

```
Resumo Financeiro.

Resumo Comercial.

Resumo Operacional.

Resumo Mensal.

Resumo Semanal.
```

A IA criará:

- Texto.
- Gráficos.
- PDFs.

---

# Atualização

Atualização automática.

Sem refresh.

Utilizar WebSocket.

---

# Personalização

Usuário poderá:

Mover widgets.

Ocultar widgets.

Adicionar widgets.

Redimensionar widgets.

Salvar Layout.

Criar múltiplos dashboards.

---

# Dashboard por Perfil

Administrador.

Gerente.

Financeiro.

Técnico.

Vendedor.

Cada perfil visualizará informações diferentes.

---

# Exportação

Exportar Dashboard:

- PDF.
- PNG.
- Excel.

---

# Tema

Obrigatório:

Dark Mode.

Light Mode.

---

# Performance

Utilizar:

Redis.

Cache.

Lazy Loading.

Paginação.

Consultas assíncronas.

Background Jobs.

---

# Permissões

Cada Widget deverá possuir permissão própria.

Exemplo:

```
dashboard.finance

dashboard.orders

dashboard.products

dashboard.stock

dashboard.ai
```

---

# IA

Toda informação exibida poderá ser consultada.

Exemplo:

```
Por que meu lucro caiu?

↓

IA analisa dados.

↓

Explica.

↓

Mostra gráfico.

↓

Sugere ações.
```

Outro exemplo:

```
Como aumentar meu faturamento?

↓

IA analisa histórico.

↓

Analisa estoque.

↓

Analisa clientes.

↓

Gera recomendações.
```

---

# Objetivo Final

O Dashboard deverá substituir reuniões de acompanhamento, permitindo que o empresário visualize em poucos segundos a saúde financeira, operacional e comercial da empresa, além de receber recomendações automáticas geradas pela Inteligência Artificial.

O Dashboard será o principal diferencial competitivo do VeloAI e deverá ser uma referência em experiência do usuário para sistemas de gestão empresarial.

---
