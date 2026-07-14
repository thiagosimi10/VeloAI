# 08-CLIENTES.md

> Projeto → VeloAI
> Documento → Módulo de Clientes
> Módulo → CRM
> Versão → 1.0.0

---

# Objetivo

O módulo de Clientes será responsável por centralizar todas as informações relacionadas aos clientes da empresa.

Não será apenas um cadastro.

Será o histórico completo do relacionamento entre empresa e cliente.

Todo o restante do sistema dependerá deste módulo.

---

# Objetivos do módulo

Permitir:

- Cadastro de clientes.
- Consulta.
- Alteração.
- Exclusão lógica.
- Histórico.
- Equipamentos.
- Ordens de Serviço.
- Compras.
- Financeiro.
- Anexos.
- Conversas com IA.

---

# Tipos de Cliente

Pessoa Física

Pessoa Jurídica

---

# Menu

```text
CRM

└── Clientes
```

---

# Layout

```text
+------------------------------------------------------+

Pesquisar cliente...

[Filtros]

+------------------------------------------------------+

Tabela

Nome

Documento

Telefone

Cidade

Última Compra

Última OS

Status

Ações

+------------------------------------------------------+

Botão

+ Novo Cliente
```

---

# Tela

Possuir:

- Pesquisa.
- Filtros.
- Ordenação.
- Paginação.
- Exportação.
- IA.

---

# Pesquisa

Pesquisar por:

- Nome
- CPF
- CNPJ
- Email
- Telefone
- WhatsApp
- Cidade

Pesquisa instantânea.

---

# Filtros

- Cidade
- Estado
- Status
- Tipo
- Última Compra
- Última OS
- Cliente Ativo
- Cliente Inativo

---

# Ordenação

- Nome
- Data Cadastro
- Última Compra
- Maior Valor
- Cidade

---

# Exportação

Permitir:

- Excel
- CSV
- PDF

---

# Cadastro

Campos obrigatórios

## Gerais

- Tipo
- Nome
- CPF/CNPJ
- IE
- IM
- Data Nascimento
- Sexo

---

## Contato

- Email
- Telefone
- Celular
- WhatsApp

---

## Endereço

- CEP
- Rua
- Número
- Complemento
- Bairro
- Cidade
- Estado
- País

Buscar CEP automaticamente.

---

## Financeiro

- Limite Crédito
- Forma Pagamento Preferida
- Condição Pagamento

---

## Comercial

- Origem
- Responsável
- Categoria
- Observações

---

## Status

- Ativo
- Inativo
- Bloqueado

---

# Abas

O cadastro possuirá abas.

## Dados Gerais

Cadastro.

---

## Histórico

Timeline completa.

Mostrar:

- Compras.
- Ordens.
- Pagamentos.
- Alterações.
- Login Portal.

---

## Equipamentos

Lista de equipamentos.

Campos:

- Marca
- Modelo
- Número Série
- Patrimônio
- Garantia
- Observações

---

## Ordens de Serviço

Tabela.

Mostrar:

- Número.
- Status.
- Técnico.
- Data.
- Valor.

---

## Financeiro

Mostrar:

- Contas Receber.
- Pagamentos.
- Pendências.
- Histórico.

---

## Anexos

Upload.

Tipos:

- PDF
- JPG
- PNG
- DOCX

---

## Observações

Editor Rich Text.

---

## IA

Histórico das conversas.

Mostrar:

- Pergunta.
- Resposta.
- Data.

---

# Timeline

Registrar automaticamente:

- Cadastro.
- Alteração.
- Compra.
- Venda.
- OS.
- Pagamento.
- Anexo.
- Nota.
- Login.

Nunca apagar histórico.

---

# Cards

No topo mostrar.

- Total Comprado.
- Total Ordens.
- Ticket Médio.
- Última Compra.
- Última Ordem.
- Pendências Financeiras.

---

# IA

Botão fixo.

```
✨ Perguntar para IA
```

Exemplos.

```
Cadastre um cliente chamado João Silva.

```

```
Atualize o telefone do João.

```

```
Mostre os clientes de Campinas.

```

```
Quem não compra há mais de seis meses?

```

```
Quais clientes possuem ordens em aberto?

```

```
Liste os clientes inadimplentes.

```

A IA deverá executar ações.

Não apenas responder.

---

# Tools MCP

Obrigatórias.

CreateCustomer

UpdateCustomer

DeleteCustomer

GetCustomer

SearchCustomer

MergeCustomers

CustomerHistory

CustomerFinancial

CustomerOrders

CustomerEquipment

CustomerDocuments

CustomerNotes

CustomerTimeline

---

# APIs

```
GET /customers

GET /customers/{id}

POST /customers

PUT /customers/{id}

DELETE /customers/{id}

GET /customers/search

GET /customers/history

GET /customers/orders

GET /customers/financial
```

---

# Banco

Tabela principal.

```
customers
```

Relacionamentos.

```
customers

↓

service_orders

↓

sales

↓

accounts_receivable

↓

customer_equipments

↓

attachments

↓

notes
```

---

# Permissões

```
customers.view

customers.create

customers.update

customers.delete

customers.export

customers.import

customers.ai
```

---

# Dashboard

Indicadores.

- Total Clientes.
- Novos Clientes.
- Clientes Ativos.
- Clientes Inativos.
- Clientes sem Compra.
- Ticket Médio.
- Receita por Cliente.

---

# Relatórios

Relatórios padrão.

Clientes por Cidade.

Clientes por Estado.

Clientes Inadimplentes.

Clientes sem Compra.

Clientes Mais Compram.

Clientes Novos.

Clientes por Origem.

Clientes por Responsável.

Todos poderão ser solicitados pela IA.

---

# Importação

Importar.

- Excel
- CSV

Mapeamento automático das colunas.

IA poderá corrigir inconsistências.

---

# Exportação

Excel.

CSV.

PDF.

---

# Auditoria

Registrar.

Cadastro.

Alteração.

Exclusão.

Importação.

Exportação.

Consulta sensível.

---

# Regras de Negócio

CPF e CNPJ não poderão ser duplicados.

Email poderá ser duplicado apenas mediante configuração.

Telefone deverá aceitar padrão internacional.

CEP preencherá endereço automaticamente.

Cliente bloqueado não poderá gerar venda.

Cliente bloqueado não poderá abrir Ordem de Serviço.

Todas as alterações deverão entrar na Timeline.

---

# Integrações Futuras

WhatsApp.

Google Maps.

ReceitaWS.

Portal Cliente.

Open Finance.

---

# Testes

Cobertura mínima.

90%.

Testar.

Cadastro.

Alteração.

Pesquisa.

Importação.

Exportação.

Permissões.

IA.

Tools.

APIs.

---

# Critérios de Aceite

✔ Cadastro completo.

✔ Pesquisa instantânea.

✔ IA funcional.

✔ Timeline funcionando.

✔ Equipamentos vinculados.

✔ Histórico completo.

✔ Exportação.

✔ Importação.

✔ Auditoria.

✔ Permissões.

✔ Testes.

---

# Objetivo Final

O módulo de Clientes deverá ser o centro do relacionamento entre empresa e consumidor, concentrando todas as informações comerciais, financeiras, operacionais e históricas em uma única tela, permitindo que tanto o usuário quanto a IA tenham uma visão completa do cliente e possam executar qualquer ação utilizando linguagem natural.

---
