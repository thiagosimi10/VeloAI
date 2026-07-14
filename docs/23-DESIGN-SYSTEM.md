# 23-DESIGN-SYSTEM.md

> Projeto → VeloAI
> Documento → Design System Oficial
> Stack → Vue 3 + Tailwind CSS + PrimeVue
> Versão → 1.0.0

---

# Objetivo

O Design System do VeloAI deverá garantir consistência visual, reutilização de componentes, excelente experiência do usuário e facilidade de manutenção.

Todo componente desenvolvido deverá seguir este documento.

Nenhuma tela poderá criar componentes próprios sem antes verificar se já existe um componente equivalente no Design System.

---

# Filosofia

O VeloAI deverá transmitir.

Modernidade.

Velocidade.

Tecnologia.

Confiança.

Organização.

Produtividade.

Simplicidade.

A interface deverá parecer um software premium.

---

# Inspirações

Linear.

Notion.

Stripe Dashboard.

Vercel.

ClickUp.

Slack.

HubSpot.

Raycast.

Supabase.

Cron.

---

# Identidade

Nome.

VeloAI.

Logo.

Minimalista.

Ícone simples.

Boa leitura em tamanhos pequenos.

Preparada para Light e Dark Mode.

---

# Paleta de Cores

Primária.

Roxo.

```text
#6D28D9
```

Hover.

```text
#7C3AED
```

Active.

```text
#5B21B6
```

Background.

```text
#F8FAFC
```

Dark Background.

```text
#0F172A
```

Surface.

```text
#FFFFFF
```

Dark Surface.

```text
#1E293B
```

Texto Principal.

```text
#111827
```

Texto Secundário.

```text
#6B7280
```

Sucesso.

```text
#22C55E
```

Erro.

```text
#EF4444
```

Alerta.

```text
#F59E0B
```

Informação.

```text
#3B82F6
```

---

# Tipografia

Fonte Principal.

Inter.

Fonte Monoespaçada.

JetBrains Mono.

---

# Escala

Título Principal.

36px.

Título.

30px.

Subtítulo.

24px.

H4.

20px.

Texto.

16px.

Texto Pequeno.

14px.

Legenda.

12px.

---

# Espaçamento

Base.

4px.

Escala.

4.

8.

12.

16.

20.

24.

32.

40.

48.

64.

96.

Nunca utilizar valores aleatórios.

---

# Bordas

Radius.

6px.

10px.

14px.

20px.

Cards.

14px.

Botões.

10px.

Inputs.

10px.

---

# Sombras

Utilizar sombras leves.

Nunca exagerar.

Cards.

Dropdowns.

Modais.

Menus.

---

# Ícones

Lucide Icons.

Mesmo tamanho.

Mesmo estilo.

Nunca misturar bibliotecas.

---

# Grid

12 colunas.

Responsivo.

Gap padrão.

24px.

---

# Breakpoints

Mobile.

0.

Tablet.

768.

Notebook.

1024.

Desktop.

1280.

Large Desktop.

1536.

---

# Layout Principal

```text
┌──────────────────────────────────────────────┐
│ Header                                       │
├──────────────┬───────────────────────────────┤
│ Sidebar      │ Conteúdo                      │
│              │                               │
│              │                               │
│              │                               │
├──────────────┴───────────────────────────────┤
│ Assistente IA                               │
└──────────────────────────────────────────────┘
```

---

# Sidebar

Largura.

280px.

Modo recolhido.

72px.

Itens.

Ícone.

Texto.

Badge.

Atalho.

Busca.

Favoritos.

---

# Header

Logo.

Busca.

Empresa.

Usuário.

Tema.

Notificações.

IA.

Perfil.

---

# Cards

Padding.

24px.

Radius.

14px.

Sombra leve.

Título.

Conteúdo.

Ações.

---

# Botões

Variantes.

Primary.

Secondary.

Success.

Danger.

Warning.

Ghost.

Outline.

Link.

Estados.

Hover.

Focus.

Loading.

Disabled.

---

# Inputs

Text.

Textarea.

Number.

Money.

Phone.

CPF.

CNPJ.

Email.

Password.

Date.

Time.

Color.

Upload.

Autocomplete.

Todos com validação visual.

---

# Selects

Pesquisa.

Scroll virtual.

Multi seleção.

Agrupamento.

Atalhos.

---

# Modais

Centralizados.

Responsivos.

Fechamento por ESC.

Fechamento por clique externo configurável.

---

# Drawer

Utilizar para.

Configurações.

Detalhes.

Histórico.

IA.

Filtros.

---

# DataTables

Utilizar.

TanStack Table.

Recursos.

Paginação.

Ordenação.

Filtros.

Busca.

Virtual Scroll.

Exportação.

Persistência.

Redimensionamento de colunas.

Colunas configuráveis.

---

# Gráficos

Utilizar exclusivamente.

amCharts 5.

Tipos.

Line.

Area.

Column.

Pie.

Donut.

Radar.

Gauge.

Heatmap.

Treemap.

Timeline.

Stock Chart.

Sempre responsivos.

---

# Dashboard

Widgets.

Arrastar.

Redimensionar.

Salvar posição.

Criar novos widgets.

Ocultar.

Duplicar.

---

# KPIs

Exibir.

Valor.

Ícone.

Comparação.

Percentual.

Tendência.

Mini gráfico.

---

# Feedback

Toast.

Alert.

Snackbar.

Progress.

Loading.

Skeleton.

Empty State.

Error State.

Success State.

---

# IA

Botão flutuante.

Sempre visível.

Atalho.

CTRL + /

Permitir.

Conversar.

Executar comandos.

Analisar tela.

Gerar relatórios.

Criar registros.

---

# Formulários

Stepper.

Wizard.

Auto Save.

Validação instantânea.

Campos obrigatórios destacados.

Máscaras.

Autocomplete.

---

# Animações

Suaves.

Curtas.

150ms.

250ms.

Nunca exagerar.

---

# Responsividade

Todas as telas deverão funcionar.

Desktop.

Notebook.

Tablet.

Mobile.

Sem barras horizontais.

---

# Tema

Light.

Dark.

Automático.

Persistência por usuário.

---

# Acessibilidade

WCAG AA.

ARIA.

Contraste.

Teclado.

Screen Reader.

Focus visível.

---

# Componentes

Criar biblioteca própria.

```text
Button

Input

Card

Modal

Drawer

Dialog

Avatar

Badge

Breadcrumb

Calendar

Chart

Checkbox

Color Picker

Combobox

Command Palette

Confirm Dialog

DataTable

Date Picker

Dropdown

Editor

Empty State

File Upload

Form

Icon

Image

Input OTP

Loading

Logo

Menu

Notification

Pagination

Popover

Progress

Radio

Search

Select

Sidebar

Skeleton

Slider

Spinner

Statistic Card

Stepper

Switch

Table

Tabs

Tag

Textarea

Timeline

Toast

Tooltip

Tree

TreeTable

Upload
```

---

# UX

Máximo.

3 cliques para qualquer ação comum.

Sempre informar.

Loading.

Erro.

Sucesso.

Nunca deixar a interface sem feedback.

---

# Performance

Code Splitting.

Lazy Loading.

Virtual Scroll.

Memoização.

Cache.

Prefetch.

---

# Convenções

Utilizar.

Composition API.

TypeScript.

Tailwind.

PrimeVue.

Lucide.

amCharts.

TanStack Table.

---

# Proibições

Nunca utilizar Bootstrap.

Nunca utilizar jQuery.

Nunca utilizar CSS Inline.

Nunca utilizar cores aleatórias.

Nunca criar componentes duplicados.

Nunca misturar bibliotecas de ícones.

Nunca utilizar gráficos diferentes de amCharts.

---

# Testes

Visual Regression.

Playwright.

Storybook.

Snapshots.

Acessibilidade.

Responsividade.

---

# Storybook

Todos os componentes deverão possuir.

Documentação.

Exemplos.

Estados.

Propriedades.

Eventos.

Variações.

Nenhum componente poderá ser utilizado sem documentação.

---

# Tokens de Design

Criar Design Tokens para.

Cores.

Fontes.

Espaçamentos.

Sombras.

Radius.

Ícones.

Animações.

Z-index.

Breakpoints.

Todos centralizados e reutilizáveis.

---

# Objetivo Final

O Design System do VeloAI deverá servir como a base visual de toda a plataforma, garantindo uma experiência consistente, moderna e altamente produtiva. Todos os módulos, dashboards, formulários, relatórios e componentes deverão seguir rigorosamente este padrão, permitindo evolução contínua da interface sem perda de identidade visual ou qualidade da experiência do usuário.

---
