# 10-ORDEM-DE-SERVICO.md

> Projeto → VeloAI
> Documento → Módulo de Ordem de Serviço
> Módulo → Operacional
> Versão → 1.0.0

---

# Objetivo

O módulo de Ordem de Serviço (OS) será o coração operacional do VeloAI.

Ele deverá atender desde pequenos prestadores de serviço até empresas com dezenas de técnicos em campo.

A Ordem de Serviço será totalmente integrada aos módulos de Clientes, Produtos, Serviços, Agenda, Financeiro, Fiscal, Dashboard e Inteligência Artificial.

Todo o ciclo de vida de um atendimento deverá acontecer dentro deste módulo.

---

# Objetivos

Permitir:

- Abertura de OS.
- Orçamento.
- Aprovação.
- Agendamento.
- Execução.
- Consumo de materiais.
- Execução de serviços.
- Upload de fotos.
- Upload de vídeos.
- Assinatura digital.
- Encerramento.
- Geração de PDF.
- Emissão futura de Nota Fiscal.
- Geração automática de contas a receber.

---

# Tipos de Ordem de Serviço

- Manutenção Corretiva.
- Manutenção Preventiva.
- Instalação.
- Visita Técnica.
- Garantia.
- Orçamento.
- Retorno.
- Emergencial.
- Personalizada.

Cada empresa poderá criar novos tipos.

---

# Status

Fluxo padrão.

```text
Rascunho

↓

Aberta

↓

Aguardando Aprovação

↓

Aprovada

↓

Agendada

↓

Em Atendimento

↓

Aguardando Peças

↓

Pausada

↓

Concluída

↓

Faturada

↓

Cancelada
```

Todos os status serão configuráveis.

---

# Numeração

Formato padrão.

```
OS-2026-000001
```

Configurável por empresa.

---

# Layout

```text
┌───────────────────────────────────────────────┐
│ Cabeçalho                                     │
├───────────────────────────────────────────────┤
│ Cliente │ Equipamento │ Status │ Técnico      │
├───────────────────────────────────────────────┤
│ Problema Informado                            │
├───────────────────────────────────────────────┤
│ Diagnóstico                                   │
├───────────────────────────────────────────────┤
│ Serviços                                      │
├───────────────────────────────────────────────┤
│ Produtos                                      │
├───────────────────────────────────────────────┤
│ Fotos │ Vídeos │ Arquivos                     │
├───────────────────────────────────────────────┤
│ Histórico │ Timeline │ Auditoria              │
├───────────────────────────────────────────────┤
│ Financeiro │ IA │ Assinaturas                │
└───────────────────────────────────────────────┘
```

---

# Dados Gerais

Campos obrigatórios.

- Número.
- Tipo.
- Status.
- Prioridade.
- Cliente.
- Técnico Responsável.
- Data de Abertura.
- Previsão.
- Canal de Atendimento.
- Origem.

---

# Prioridade

- Baixa.
- Normal.
- Alta.
- Urgente.
- Emergencial.

---

# Cliente

Selecionar cliente existente.

Ou criar novo sem sair da tela.

---

# Equipamento

Campos.

- Categoria.
- Marca.
- Modelo.
- Número de Série.
- Patrimônio.
- Cor.
- Acessórios.
- Garantia.
- Data Compra.
- Observações.

Mesmo cliente poderá possuir diversos equipamentos.

---

# Problema

Texto livre.

Também poderá utilizar voz.

A IA poderá resumir automaticamente.

---

# Diagnóstico

Preenchido pelo técnico.

A IA poderá sugerir diagnóstico baseado em histórico semelhante.

---

# Solução

Descrição completa.

A IA poderá melhorar a escrita.

---

# Serviços

Adicionar serviços cadastrados.

Cada item possuirá.

- Serviço.
- Quantidade.
- Valor.
- Tempo estimado.
- Desconto.
- Total.

---

# Produtos

Adicionar produtos.

Ao adicionar:

Reservar estoque.

Ao concluir:

Baixar estoque automaticamente.

Ao cancelar:

Estornar reserva.

---

# Fotos

Upload múltiplo.

Permitir:

Antes.

Durante.

Depois.

As fotos poderão ser organizadas por etapa.

---

# Vídeos

Upload de vídeos curtos.

Preparado para armazenamento no MinIO.

---

# Anexos

Aceitar.

PDF.

DOCX.

XLSX.

ZIP.

Imagens.

---

# Assinatura

Assinatura digital do cliente.

Assinatura do técnico.

Assinatura incorporada ao PDF.

---

# Checklist

Cada tipo de OS poderá possuir checklist próprio.

Exemplo.

Instalação de Ar Condicionado.

- Tubulação conferida.
- Pressão medida.
- Vácuo realizado.
- Teste executado.
- Cliente orientado.

Todos os checklists serão configuráveis.

---

# Agenda

Integração total.

Ao marcar uma OS.

Criar evento automaticamente.

Ao alterar data.

Atualizar agenda.

---

# Financeiro

Ao concluir.

Opcionalmente:

Gerar Conta a Receber.

Gerar Boleto.

Gerar PIX.

Gerar Link de Pagamento.

Tudo configurável.

---

# Fiscal

Preparado para.

NFS-e.

NF-e.

NFC-e.

---

# PDF

Gerar automaticamente.

Conteúdo.

Logo.

Cliente.

Equipamento.

Fotos.

Serviços.

Produtos.

Assinaturas.

Observações.

QR Code.

Número da OS.

Layout moderno.

---

# Timeline

Registrar.

Abertura.

Alteração.

Mudança de Status.

Produtos.

Serviços.

Fotos.

Anexos.

Financeiro.

Assinaturas.

IA.

Nunca apagar histórico.

---

# IA

Toda tela possuirá um painel lateral.

Exemplos.

```
Abra uma OS para João Silva.

Notebook Dell Latitude.

Não liga.

Prioridade alta.

Agende para amanhã às 09:00.

Técnico Carlos.
```

Resultado.

A IA deverá:

Criar cliente caso não exista.

Cadastrar equipamento caso não exista.

Criar a OS.

Agendar.

Vincular técnico.

Reservar horário.

Responder com resumo da operação.

---

Outro exemplo.

```
Adicione um SSD Kingston de 1TB.

Mais uma formatação.

Aplique desconto de 10%.
```

A IA deverá alterar a OS existente.

---

Outro.

```
Finalize a OS.

Consumindo os produtos.

Gerando PDF.

Criando conta a receber para 30 dias.
```

Tudo automaticamente.

---

# MCP Tools

Obrigatórias.

CreateServiceOrder

UpdateServiceOrder

DeleteServiceOrder

SearchServiceOrder

AssignTechnician

ScheduleServiceOrder

AddService

RemoveService

AddProduct

RemoveProduct

ReserveStock

ReleaseStock

GeneratePDF

GenerateInvoice

GeneratePayment

UploadAttachment

UploadPhoto

UploadVideo

CloseServiceOrder

CancelServiceOrder

ReopenServiceOrder

GetTimeline

GetHistory

---

# APIs

```
GET /service-orders

GET /service-orders/{id}

POST /service-orders

PUT /service-orders/{id}

DELETE /service-orders/{id}

POST /service-orders/{id}/products

POST /service-orders/{id}/services

POST /service-orders/{id}/photos

POST /service-orders/{id}/attachments

POST /service-orders/{id}/close

POST /service-orders/{id}/cancel

GET /service-orders/report
```

---

# Dashboard

Indicadores.

- OS Abertas.
- Em Atendimento.
- Concluídas.
- Atrasadas.
- Tempo Médio.
- Ticket Médio.
- Técnicos Mais Produtivos.
- Receita por OS.
- OS por Categoria.
- OS por Técnico.

---

# Relatórios

OS por Cliente.

OS por Técnico.

OS por Status.

OS por Equipamento.

OS por Período.

OS Mais Lucrativas.

Produtos Consumidos.

Serviços Executados.

Tempo Médio de Atendimento.

Todos poderão ser gerados pela IA.

---

# Regras de Negócio

Número da OS nunca poderá ser alterado.

Toda mudança de status deverá gerar evento.

Não permitir concluir OS sem técnico responsável, salvo configuração da empresa.

Ao concluir a OS:

Consumir estoque automaticamente.

Atualizar dashboard.

Gerar eventos.

Gerar auditoria.

Atualizar histórico do cliente.

Atualizar histórico do equipamento.

Caso configurado:

Gerar conta a receber.

Caso configurado:

Preparar emissão de nota fiscal.

Cancelamento deverá estornar estoque reservado.

Nenhuma movimentação poderá ser apagada.

---

# Eventos

Disparar.

ServiceOrderCreated.

ServiceOrderUpdated.

ServiceOrderScheduled.

ServiceOrderStarted.

ServiceOrderPaused.

ServiceOrderFinished.

ServiceOrderCancelled.

ProductsConsumed.

InvoiceRequested.

PaymentCreated.

PDFGenerated.

Todos poderão acionar:

IA.

Notificações.

Emails.

WhatsApp.

Dashboard.

Webhooks.

---

# Automações

Exemplos.

Enviar WhatsApp ao abrir OS.

Enviar lembrete um dia antes.

Enviar mensagem ao concluir.

Enviar PDF automaticamente.

Solicitar avaliação do cliente.

Criar tarefa de retorno.

Criar manutenção preventiva futura.

---

# Permissões

```
service_orders.view

service_orders.create

service_orders.update

service_orders.delete

service_orders.close

service_orders.cancel

service_orders.schedule

service_orders.export

service_orders.ai
```

---

# Testes

Cobertura mínima.

90%.

Testar.

Cadastro.

Fluxo de Status.

Produtos.

Serviços.

Fotos.

Agenda.

PDF.

Financeiro.

IA.

Eventos.

Permissões.

---

# Critérios de Aceite

✔ Fluxo completo de OS.

✔ Agenda integrada.

✔ Estoque integrado.

✔ Financeiro integrado.

✔ IA funcional.

✔ PDF automático.

✔ Assinatura digital.

✔ Auditoria.

✔ Timeline.

✔ Eventos.

✔ Testes.

---

# Objetivo Final

O módulo de Ordem de Serviço deverá ser a principal ferramenta operacional do VeloAI, permitindo que empresas executem todo o ciclo de atendimento em um único ambiente, com total rastreabilidade, integração entre módulos e suporte completo da Inteligência Artificial. O usuário deverá conseguir abrir, atualizar, executar e finalizar uma Ordem de Serviço apenas conversando com a IA, enquanto o sistema realiza automaticamente todas as integrações necessárias com estoque, agenda, financeiro, relatórios e dashboard.

---
