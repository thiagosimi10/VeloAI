# 09-PRODUTOS.md

> Projeto → VeloAI
> Documento → Módulo de Produtos
> Módulo → Estoque / Comercial
> Versão → 1.0.0

---

# Objetivo

O módulo de Produtos será responsável por gerenciar todo o catálogo de produtos da empresa.

Não será apenas um cadastro.

Será o centro de controle do estoque, compras, vendas, ordens de serviço e financeiro.

Qualquer movimentação envolvendo um produto deverá passar por este módulo.

---

# Objetivos

Permitir:

- Cadastro completo.
- Controle de estoque.
- Controle de custo.
- Controle de preço.
- Controle de margem.
- Controle de fornecedores.
- Controle de categorias.
- Controle de movimentações.
- Importação.
- Exportação.
- Integração com IA.

---

# Menu

```text
Cadastros

└── Produtos
```

---

# Layout

```text
+--------------------------------------------------------------+

Pesquisar produto...

[Filtros]

+--------------------------------------------------------------+

Tabela

Imagem

SKU

Código Barras

Produto

Categoria

Fornecedor

Estoque

Preço Custo

Preço Venda

Margem

Status

Ações

+--------------------------------------------------------------+

+ Novo Produto
```

---

# Tela

Possuir:

- Pesquisa instantânea.
- Filtros avançados.
- Ordenação.
- Paginação.
- Exportação.
- Importação.
- IA.
- Ações rápidas.

---

# Pesquisa

Pesquisar por:

- Nome.
- SKU.
- Código de Barras.
- Código Interno.
- Categoria.
- Fornecedor.
- Marca.

---

# Filtros

- Categoria.
- Marca.
- Fornecedor.
- Estoque.
- Ativo.
- Inativo.
- Promoção.
- Sem Estoque.
- Abaixo do Estoque Mínimo.

---

# Cadastro

## Informações Gerais

- Nome.
- Descrição.
- SKU.
- Código Interno.
- Código de Barras.
- Categoria.
- Marca.
- Modelo.
- Unidade.

---

## Valores

- Preço de Custo.
- Preço de Venda.
- Lucro.
- Margem.
- Desconto Máximo.

Margem deverá ser calculada automaticamente.

---

## Estoque

- Estoque Atual.
- Estoque Inicial.
- Estoque Mínimo.
- Estoque Máximo.
- Localização.
- Reservado.

---

## Fiscal

- NCM.
- CFOP.
- CST.
- CEST.
- Origem.
- Alíquota.

Preparado para emissão futura de NF-e.

---

## Fornecedor

- Fornecedor Principal.
- Código do Fornecedor.
- Última Compra.

---

## Dimensões

- Peso.
- Altura.
- Largura.
- Comprimento.

---

## Imagens

Upload múltiplo.

Imagem principal.

Galeria.

Drag and Drop.

---

## Arquivos

Permitir anexar:

- Manual.
- Catálogo.
- Garantia.
- Datasheet.

---

## Observações

Editor Rich Text.

---

# Abas

Dados Gerais.

Estoque.

Preços.

Fiscal.

Fornecedores.

Movimentações.

Compras.

Vendas.

Ordens de Serviço.

Anexos.

Histórico.

IA.

---

# Cards

Mostrar:

- Estoque Atual.
- Valor em Estoque.
- Total Vendido.
- Total Comprado.
- Lucro.
- Giro.
- Última Venda.
- Última Compra.

---

# Movimentações

Registrar automaticamente:

- Entrada.
- Saída.
- Ajuste.
- Inventário.
- Reserva.
- Cancelamento.
- Transferência.

Nunca apagar histórico.

---

# IA

Botão:

```
✨ Perguntar para IA
```

Exemplos.

```
Cadastre um produto chamado SSD Kingston 1TB.

```

```
Preço de custo R$ 320.

Preço de venda R$ 490.

Fornecedor Tech Distribuidora.

Categoria Armazenamento.

Estoque inicial 20 unidades.
```

A IA deverá preencher toda a tela.

---

Outro exemplo.

```
Aumente em 8% o preço de todos os SSDs.
```

---

Outro.

```
Produtos com estoque abaixo de cinco unidades.
```

---

Outro.

```
Produtos que não vendem há mais de seis meses.
```

---

Outro.

```
Crie uma promoção de 10% para todos os notebooks Dell.
```

---

# MCP Tools

Obrigatórias.

CreateProduct

UpdateProduct

DeleteProduct

SearchProduct

UpdatePrice

UpdateStock

ImportProducts

ExportProducts

ReserveProduct

ReleaseReservation

ProductHistory

ProductDashboard

---

# APIs

```
GET /products

GET /products/{id}

POST /products

PUT /products/{id}

DELETE /products/{id}

GET /products/search

POST /products/import

GET /products/export

POST /products/stock

GET /products/history
```

---

# Banco

Tabelas.

```
products

categories

suppliers

stock_movements

product_images

product_documents

product_prices
```

---

# Dashboard

Indicadores.

- Total Produtos.
- Produtos Ativos.
- Produtos Sem Estoque.
- Estoque Crítico.
- Valor Total em Estoque.
- Produtos Mais Vendidos.
- Produtos Menos Vendidos.
- Produtos Sem Giro.
- Lucro por Produto.

---

# Relatórios

Produtos Mais Vendidos.

Produtos Mais Lucrativos.

Produtos Sem Estoque.

Produtos Abaixo do Mínimo.

Produtos Parados.

Inventário.

Movimentações.

Compras.

Margem.

Todos deverão poder ser gerados pela IA.

---

# Importação

Permitir importar:

- Excel.
- CSV.

A IA deverá identificar:

- Colunas.
- Erros.
- Produtos duplicados.
- Categorias inexistentes.
- Fornecedores inexistentes.

Podendo sugerir correções antes da importação.

---

# Exportação

Excel.

CSV.

PDF.

---

# Auditoria

Registrar:

Cadastro.

Alteração.

Mudança de preço.

Mudança de estoque.

Importação.

Exportação.

Exclusão.

---

# Regras de Negócio

SKU único.

Código de Barras único quando informado.

Não permitir estoque negativo, salvo configuração da empresa.

Movimentações nunca poderão ser apagadas.

Alteração manual de estoque deverá registrar motivo.

Preço de venda não poderá ser inferior ao custo sem permissão específica.

Toda venda reduzirá estoque automaticamente.

Toda compra aumentará estoque automaticamente.

Toda Ordem de Serviço consumirá estoque automaticamente ao ser finalizada.

Cancelamentos deverão estornar movimentações.

---

# Eventos

Disparar eventos:

ProductCreated.

ProductUpdated.

StockUpdated.

PriceUpdated.

LowStockDetected.

OutOfStockDetected.

ProductDeleted.

Esses eventos poderão acionar:

- IA.
- Notificações.
- Dashboard.
- Webhooks.
- Integrações.

---

# Integrações Futuras

Mercado Livre.

Shopee.

Amazon.

Bling.

Tiny.

Google Shopping.

Leitor de Código de Barras.

Balanças.

---

# Testes

Cobertura mínima.

90%.

Testar:

Cadastro.

Pesquisa.

Preço.

Margem.

Movimentação.

Importação.

Exportação.

Permissões.

IA.

Tools.

Eventos.

---

# Critérios de Aceite

✔ Cadastro completo.

✔ Controle de estoque.

✔ Controle de preços.

✔ Histórico de movimentações.

✔ IA funcional.

✔ Importação.

✔ Exportação.

✔ Auditoria.

✔ Eventos.

✔ Dashboard.

✔ Testes.

---

# Objetivo Final

O módulo de Produtos deverá ser o núcleo do controle de estoque e comercial do VeloAI, fornecendo informações precisas sobre disponibilidade, custos, margens, vendas e movimentações, além de permitir que todas essas operações sejam realizadas tanto pela interface gráfica quanto por comandos em linguagem natural através da Inteligência Artificial.

---

# Status

✅ Documento concluído.

**ACABAMOS O 09-PRODUTOS.md**