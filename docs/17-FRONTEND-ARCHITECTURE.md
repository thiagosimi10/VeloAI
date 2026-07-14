# 17-FRONTEND-ARCHITECTURE.md

> Projeto → VeloAI
> Documento → Arquitetura Frontend
> Stack → Vue 3 + TypeScript
> Versão → 1.0.0

---

# Objetivo

O Frontend do VeloAI deverá ser moderno, extremamente rápido, responsivo e totalmente orientado à experiência do usuário.

O sistema será desenvolvido inicialmente para Web, porém toda a arquitetura deverá ser preparada para compartilhamento de lógica com futuras aplicações Mobile.

A interface deverá transmitir a sensação de um produto premium, mesmo sendo destinado a pequenas e médias empresas.

O principal objetivo é que o usuário consiga executar qualquer tarefa com o menor número possível de cliques e, sempre que desejar, simplesmente converse com a IA para realizar a ação.

---

# Stack

Framework.

Vue 3

Linguagem.

TypeScript

Build.

Vite

Gerenciamento de Estado.

Pinia

Rotas.

Vue Router

Requisições HTTP.

Axios

Validação.

Vee Validate

Schema Validation.

Zod

Componentes.

PrimeVue

Ícones.

Lucide Icons

Tabelas.

TanStack Table

Gráficos.

amCharts 5

Editor Rich Text.

TipTap

Datas.

Day.js

Upload.

Vue FilePond

Drag and Drop.

VueUse

Tema.

Dark / Light Mode

CSS.

Tailwind CSS

---

# Identidade Visual

Nome.

VeloAI

Conceito.

Sistema moderno.

Minimalista.

Elegante.

Tecnológico.

Foco em produtividade.

---

# Cores

Cor Primária.

Roxo.

Cor Secundária.

Violeta.

Cor de Apoio.

Branco.

Cinza.

Grafite.

Verde para sucesso.

Vermelho para erros.

Amarelo para alertas.

Nunca utilizar excesso de cores.

---

# Layout

```text
┌──────────────────────────────────────────────┐
│ Header                                       │
├──────────────┬───────────────────────────────┤
│ Sidebar      │ Conteúdo                      │
│              │                               │
│              │                               │
│              │                               │
├──────────────┴───────────────────────────────┤
│ Chat IA Flutuante                            │
└──────────────────────────────────────────────┘
```

---

# Sidebar

Sempre fixa.

Colapsável.

Ícones.

Busca.

Favoritos.

Módulos.

Perfil.

Empresa.

Notificações.

---

# Header

Logo.

Busca Global.

Empresa Atual.

Usuário.

Alertas.

Mensagens.

IA.

Tema.

Perfil.

---

# Dashboard

Primeira tela do sistema.

Mostrar.

KPIs.

Gráficos.

Atividades Recentes.

Agenda.

Financeiro.

Ordens de Serviço.

Vendas.

Produtos.

Alertas.

Insights da IA.

Todos os gráficos deverão utilizar amCharts 5.

---

# Busca Global

Atalho.

CTRL + K.

Pesquisar.

Clientes.

Produtos.

OS.

Vendas.

Usuários.

Relatórios.

Configurações.

A IA também participará da busca.

---

# IA Global

Botão fixo.

```
✨ Perguntar para IA
```

Sempre disponível.

Nunca depender da tela atual.

A IA poderá:

Criar.

Editar.

Pesquisar.

Excluir.

Gerar relatórios.

Executar automações.

Responder dúvidas.

---

# Componentes

Criar Design System próprio.

Componentes.

Button.

Card.

Modal.

Drawer.

Dialog.

Input.

Textarea.

Select.

Autocomplete.

Badge.

Avatar.

Tabs.

Timeline.

Stepper.

Calendar.

File Upload.

Chart.

DataTable.

Skeleton.

Loading.

Toast.

Confirm Dialog.

Empty State.

Error State.

---

# DataTables

Utilizar TanStack Table.

Recursos obrigatórios.

Paginação.

Ordenação.

Filtros.

Busca.

Colunas configuráveis.

Exportação.

Seleção múltipla.

Ações rápidas.

Scroll virtual.

Persistência das preferências do usuário.

---

# Formulários

Todos deverão possuir.

Validação instantânea.

Máscaras.

Autocomplete.

Upload.

Salvamento automático quando aplicável.

Feedback visual.

Mensagens amigáveis.

---

# Responsividade

Desktop.

Notebook.

Tablet.

Mobile.

Nunca utilizar layout fixo.

---

# Tema

Light.

Dark.

Modo automático.

Persistir preferência do usuário.

---

# Dashboard Inteligente

Widgets.

Arrastar.

Redimensionar.

Salvar posição.

Ocultar.

Duplicar.

Criar widgets personalizados.

---

# Notificações

Central única.

Alertas.

Mensagens.

Financeiro.

OS.

Vendas.

IA.

Sistema.

Filtros.

Marcar como lida.

---

# Uploads

Drag and Drop.

Preview.

Upload múltiplo.

Barra de progresso.

Cancelamento.

Retry.

---

# Performance

Lazy Loading.

Code Splitting.

Dynamic Imports.

Cache.

Virtual Scroll.

Memoização.

Prefetch.

---

# Organização

```text
src/

assets/

components/

layouts/

views/

modules/

stores/

router/

services/

composables/

types/

utils/

plugins/

styles/

ai/

tests/
```

---

# Estrutura dos Módulos

```text
customers/

products/

sales/

finance/

service-orders/

reports/

dashboard/

automation/

settings/
```

Cada módulo será independente.

---

# Comunicação

Frontend nunca acessará banco.

Sempre consumir APIs REST.

Toda IA utilizará Backend.

Nunca chamar LLM diretamente.

---

# Estados

Pinia.

Separar.

Auth Store.

Company Store.

User Store.

Theme Store.

Notification Store.

Dashboard Store.

AI Store.

---

# UX

Sempre mostrar.

Loading.

Feedback.

Progresso.

Erros.

Sucesso.

Nunca deixar o usuário sem resposta.

---

# Atalhos

CTRL + K.

Busca.

CTRL + S.

Salvar.

CTRL + /.

Abrir IA.

ESC.

Fechar Modais.

---

# Acessibilidade

WCAG.

ARIA.

Contraste.

Navegação por teclado.

Labels.

Screen Readers.

---

# Internacionalização

Preparar.

Português.

Inglês.

Espanhol.

Utilizar i18n.

---

# Segurança

Nunca armazenar JWT em LocalStorage.

Utilizar Cookies HttpOnly.

Sanitizar HTML.

Escapar conteúdo.

Nunca confiar em validações do Frontend.

---

# Erros

Tela amigável.

Código.

Mensagem.

Botão para tentar novamente.

Botão para relatar erro.

---

# Observabilidade

Capturar.

Erros.

Performance.

Tempo de carregamento.

Eventos de navegação.

Falhas de API.

Integração com Sentry.

---

# Testes

Vitest.

Vue Testing Library.

Playwright.

Cobertura mínima.

80%.

Testar.

Componentes.

Páginas.

Stores.

Rotas.

Permissões.

Integração com API.

---

# CI

Executar.

ESLint.

Type Check.

Build.

Testes.

Coverage.

---

# Convenções

Composition API.

`<script setup>`.

TypeScript obrigatório.

Componentes pequenos.

Reutilização máxima.

Nunca duplicar lógica.

---

# Proibições

Nunca colocar regra de negócio.

Nunca acessar banco.

Nunca chamar IA diretamente.

Nunca utilizar `any` sem justificativa.

Nunca criar componentes gigantes.

Nunca misturar estilos globais com componentes.

---

# Roadmap

Preparado para.

PWA.

Aplicativo Mobile.

Electron.

Desktop.

Offline Mode.

Push Notifications.

Command Palette.

Widgets personalizáveis.

---

# Objetivo Final

O Frontend do VeloAI deverá oferecer uma experiência moderna, rápida e intuitiva, permitindo que qualquer usuário opere o sistema com facilidade. A interface deverá combinar Design System próprio, dashboards ricos com amCharts 5, tabelas avançadas utilizando TanStack Table, excelente performance e integração total com a plataforma de Inteligência Artificial, tornando a navegação opcional e permitindo que grande parte das ações seja executada apenas por linguagem natural.

---
