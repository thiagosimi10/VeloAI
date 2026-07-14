# 06-MODULOS.md

> Projeto → VeloAI
> Documento → Módulos do Sistema
> Versão → 1.0.0

---

# Objetivo

Definir todos os módulos oficiais do VeloAI.

Todo módulo deverá possuir:

- Interface Web.
- API REST.
- Integração com IA.
- Tools MCP.
- Permissões.
- Auditoria.
- Testes.
- Documentação.

Nenhum módulo será desenvolvido sem seguir este padrão.

---

# Estrutura Geral

```text
Dashboard

CRM

Cadastros

Operacional

Financeiro

Fiscal

Relatórios

IA

Configurações

Integrações
```

---

# Dashboard

Objetivo:

Centralizar todas as informações importantes da empresa.

Responsabilidades:

- KPIs.
- Gráficos.
- Alertas.
- Insights da IA.
- Agenda.
- Atividades recentes.
- Ordens abertas.
- Fluxo financeiro.
- Produtos mais vendidos.
- Produtos sem estoque.
- Contas vencidas.
- Vendas do mês.
- Ranking de clientes.
- Ranking de vendedores.
- Metas.

Possuir IA integrada.

Exemplo:

> Como foi meu faturamento este mês?

---

# CRM

Responsável por relacionamento com clientes.

Submódulos:

- Clientes.
- Histórico.
- Anotações.
- Arquivos.
- Contatos.
- Endereços.
- Equipamentos.
- Histórico financeiro.
- Histórico de compras.
- Histórico de serviços.

IA:

> Mostre os clientes que estão há mais de 90 dias sem comprar.

---

# Empresas

Responsável pelas configurações da empresa.

Funcionalidades:

- Dados da empresa.
- Logo.
- Cores.
- Horário.
- Endereço.
- CNPJ.
- Certificado Digital.
- Configurações fiscais.
- Configurações financeiras.
- Configurações da IA.

Logo utilizada automaticamente:

- PDFs.
- Relatórios.
- OS.
- Orçamentos.

---

# Usuários

Responsável por:

- Cadastro.
- Permissões.
- Perfis.
- Foto.
- Login.
- MFA (futuro).

IA:

> Crie um usuário chamado Carlos como Técnico.

---

# Clientes

Responsável por:

- Cadastro.
- Consulta.
- Histórico.
- Equipamentos.
- Anexos.
- Localização.
- Observações.

IA:

> Cadastre um cliente chamado João Silva...

---

# Fornecedores

Responsável por:

- Cadastro.
- Produtos fornecidos.
- Histórico.
- Contas a pagar.

---

# Produtos

Responsável por:

- Cadastro.
- Categorias.
- Código.
- Código de barras.
- SKU.
- Estoque.
- Preço.
- Fotos.
- Fornecedor.

IA:

> Cadastre um notebook Dell Latitude por R$ 5.200 com estoque inicial de 10 unidades.

---

# Categorias

Responsável por:

- Organização dos produtos.
- Organização dos serviços.

---

# Serviços

Responsável por:

- Cadastro.
- Tempo estimado.
- Valor.
- Categoria.

IA:

> Crie um serviço chamado Formatação de Computador no valor de R$ 180.

---

# Estoque

Responsável por:

- Entradas.
- Saídas.
- Ajustes.
- Inventário.
- Reservas.
- Histórico.
- Alertas.

IA:

> Diminua 3 unidades do produto X.

---

# Compras

Responsável por:

- Pedidos.
- Entrada de mercadorias.
- Fornecedores.
- Custos.

---

# Vendas

Responsável por:

- PDV.
- Pedido.
- Orçamento.
- Conversão.
- Pagamentos.

IA:

> Gere uma venda para João contendo dois notebooks.

---

# Ordem de Serviço

Principal módulo do sistema.

Responsável por:

- Abertura.
- Diagnóstico.
- Execução.
- Materiais.
- Serviços.
- Técnicos.
- Assinatura.
- Fotos.
- PDF.
- Encerramento.

IA:

> Abra uma OS para Maria referente a um notebook Dell que não liga. Informe problema, cliente, equipamento e prioridade alta.

A IA deverá criar toda a OS automaticamente.

---

# Agenda

Responsável por:

- Compromissos.
- Visitas.
- Instalações.
- Serviços.
- Calendário.

---

# Financeiro

Submódulos:

- Contas a Pagar.
- Contas a Receber.
- Fluxo de Caixa.
- Receitas.
- Despesas.
- Centros de Custo.

IA:

> Lance uma conta de energia de R$ 430 para vencer dia 20.

---

# Fiscal

Responsável por:

- NFS-e.
- NFe.
- NFC-e.
- XML.
- DANFE.

Preparado para integração futura.

---

# Relatórios

Todos os relatórios serão dinâmicos.

Nunca existirão apenas relatórios fixos.

Exemplos:

> Qual cliente mais comprou este ano?

> Qual produto vendeu mais em maio?

> Quanto faturei na última semana?

> Qual técnico fecha mais ordens?

A IA será responsável por interpretar a solicitação, selecionar as Tools necessárias, consultar os dados e montar tabelas, gráficos (amCharts) e análises.

---

# Dashboard Inteligente

O Dashboard deverá apresentar automaticamente:

- Receita do dia.
- Receita do mês.
- Receita anual.
- Ticket médio.
- Produtos mais vendidos.
- Clientes mais ativos.
- Contas vencidas.
- Contas a vencer.
- Ordens abertas.
- Ordens atrasadas.
- Estoque baixo.
- Lucro estimado.
- Margem.
- Crescimento.
- Comparação entre períodos.
- Alertas da IA.

---

# Notificações

Tipos:

- Sistema.
- Financeiro.
- Estoque.
- Ordem.
- IA.
- Integrações.

Preparado para:

- Email.
- Push.
- WhatsApp.

---

# Configurações

Submódulos:

- Empresa.
- Usuários.
- Perfis.
- Permissões.
- IA.
- Integrações.
- Impressão.
- Fiscal.
- Financeiro.
- Aparência.
- Logo.
- Tema.

---

# Integrações

Preparado para:

- Mercado Pago.
- Asaas.
- Stripe.
- WhatsApp.
- Google Calendar.
- Google Drive.
- Outlook.
- NFS-e.
- NFe.
- NFC-e.

---

# Inteligência Artificial

A IA será um módulo próprio.

Responsável por:

- Chat.
- Agentes.
- Memória.
- Histórico.
- Ferramentas.
- RAG.
- MCP.
- OCR.
- Relatórios.
- Insights.
- Automações.

---

# Automações

Fluxos automáticos.

Exemplos:

- Enviar WhatsApp após finalizar OS.
- Avisar cliente sobre vencimento.
- Atualizar estoque após venda.
- Gerar contas automaticamente.
- Criar tarefas.
- Enviar emails.
- Executar IA em horários programados.

No futuro será criado um construtor visual semelhante ao n8n.

---

# API Pública

Disponibilizar APIs para integração.

Recursos:

- OAuth.
- API Keys.
- Webhooks.
- Rate Limit.
- Documentação OpenAPI.

---

# Portal do Cliente (Futuro)

Permitir ao cliente:

- Consultar OS.
- Consultar boletos.
- Consultar notas.
- Baixar PDFs.
- Conversar com IA.
- Aprovar orçamentos.

---

# Aplicativo Mobile (Futuro)

Aplicação em Flutter.

Mesmo Backend.

Mesma API.

Mesmo banco.

Mesmo sistema de autenticação.

---

# Objetivo Final

Cada módulo deverá funcionar de forma independente, porém integrado aos demais através de Services, Eventos e IA, permitindo que o usuário utilize o sistema tanto pela interface tradicional quanto por linguagem natural.

Todos os módulos deverão possuir documentação específica com regras de negócio, APIs, permissões, telas, integrações e comportamento da IA.

---
