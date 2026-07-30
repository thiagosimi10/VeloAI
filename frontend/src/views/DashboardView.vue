<script setup lang="ts">
import * as am5 from '@amcharts/amcharts5'
import am5themes_Animated from '@amcharts/amcharts5/themes/Animated'
import * as am5percent from '@amcharts/amcharts5/percent'
import * as am5xy from '@amcharts/amcharts5/xy'
import {
  AlertTriangle,
  ArrowDownCircle,
  ArrowUpCircle,
  ClipboardList,
  Package,
  Receipt,
  TrendingUp,
  Users,
  Wallet,
  Wrench,
} from 'lucide-vue-next'
import Message from 'primevue/message'
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useDashboardStore } from '@/stores/dashboard'

const store = useDashboardStore()
const router = useRouter()

const revenueChartDiv = ref<HTMLDivElement | null>(null)
const dailyRevenueChartDiv = ref<HTMLDivElement | null>(null)
const topProductsChartDiv = ref<HTMLDivElement | null>(null)
const serviceStatusChartDiv = ref<HTMLDivElement | null>(null)
const salesStatusChartDiv = ref<HTMLDivElement | null>(null)
const newCustomersChartDiv = ref<HTMLDivElement | null>(null)
const cashFlowChartDiv = ref<HTMLDivElement | null>(null)
const productsByCategoryChartDiv = ref<HTMLDivElement | null>(null)
let revenueRoot: am5.Root | null = null
let dailyRevenueRoot: am5.Root | null = null
let topProductsRoot: am5.Root | null = null
let serviceStatusRoot: am5.Root | null = null
let salesStatusRoot: am5.Root | null = null
let newCustomersRoot: am5.Root | null = null
let cashFlowRoot: am5.Root | null = null
let productsByCategoryRoot: am5.Root | null = null

function formatCurrency(value: number): string {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function formatDayLabel(period: string): string {
  const [, month, day] = period.split('-')
  return `${day}/${month}`
}

function formatPercentage(value: number | null): string {
  if (value === null) return '—'
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

function ordersOpenCount(): number {
  const byStatus = store.summary?.ordersByStatus ?? {}
  return (byStatus.open ?? 0) + (byStatus.in_progress ?? 0)
}

const SERVICE_STATUS_META: Record<string, { label: string; color: number }> = {
  open: { label: 'Aberta', color: 0x3b82f6 },
  in_progress: { label: 'Em Atendimento', color: 0xf59e0b },
  completed: { label: 'Concluída', color: 0x22c55e },
  cancelled: { label: 'Cancelada', color: 0x9ca3af },
}

const serviceStatusBreakdown = computed(() => {
  const byStatus = store.summary?.ordersByStatus ?? {}
  return Object.entries(SERVICE_STATUS_META)
    .map(([key, meta]) => ({ key, label: meta.label, color: meta.color, value: byStatus[key] ?? 0 }))
    .filter((item) => item.value > 0)
})

const hasServiceOrders = computed(() =>
  serviceStatusBreakdown.value.some((item) => item.value > 0),
)

const SALES_STATUS_META: Record<string, { label: string; color: number }> = {
  open: { label: 'Aberta', color: 0x3b82f6 },
  paid: { label: 'Paga', color: 0x22c55e },
  cancelled: { label: 'Cancelada', color: 0xef4444 },
}

const salesStatusBreakdown = computed(() => {
  const byStatus = store.summary?.salesByStatus ?? {}
  return Object.entries(SALES_STATUS_META)
    .map(([key, meta]) => ({ key, label: meta.label, color: meta.color, value: byStatus[key] ?? 0 }))
    .filter((item) => item.value > 0)
})

const hasSales = computed(() => salesStatusBreakdown.value.some((item) => item.value > 0))

const CATEGORY_PALETTE = [0x6d28d9, 0x3b82f6, 0x22c55e, 0xf59e0b, 0xec4899, 0x9ca3af]
const MAX_CATEGORY_SLICES = 5

const productsByCategoryBreakdown = computed(() => {
  const items = [...store.productsByCategory].sort((a, b) => b.productCount - a.productCount)
  const top = items.slice(0, MAX_CATEGORY_SLICES)
  const rest = items.slice(MAX_CATEGORY_SLICES)
  const restTotal = rest.reduce((sum, item) => sum + item.productCount, 0)

  const breakdown = top.map((item, index) => ({
    key: item.categoryName,
    label: item.categoryName,
    color: CATEGORY_PALETTE[index % CATEGORY_PALETTE.length] ?? 0x6d28d9,
    value: item.productCount,
  }))
  if (restTotal > 0) {
    breakdown.push({ key: '__others__', label: 'Outras', color: 0x9ca3af, value: restTotal })
  }
  return breakdown
})

const hasProducts = computed(() =>
  productsByCategoryBreakdown.value.some((item) => item.value > 0),
)

function renderDonutChart(container: HTMLDivElement, data: { label: string; value: number; color: number }[]): am5.Root {
  const root = am5.Root.new(container)
  root.setThemes([am5themes_Animated.new(root)])
  root._logo?.dispose()

  const chart = root.container.children.push(
    am5percent.PieChart.new(root, { layout: root.verticalLayout, innerRadius: am5.percent(65) }),
  )

  const series = chart.series.push(
    am5percent.PieSeries.new(root, { valueField: 'value', categoryField: 'label' }),
  )
  series.labels.template.set('forceHidden', true)
  series.ticks.template.set('forceHidden', true)
  series.slices.template.set('templateField', 'sliceSettings')
  series.slices.template.setAll({ strokeWidth: 2, stroke: am5.color(0xffffff) })

  series.data.setAll(
    data.map((item) => ({
      label: item.label,
      value: item.value,
      sliceSettings: { fill: am5.color(item.color) },
    })),
  )
  series.appear(800, 100)

  return root
}

function renderRevenueChart(): void {
  if (!revenueChartDiv.value) return
  revenueRoot?.dispose()

  const root = am5.Root.new(revenueChartDiv.value)
  root.setThemes([am5themes_Animated.new(root)])
  root._logo?.dispose()

  const chart = root.container.children.push(
    am5xy.XYChart.new(root, { panX: false, panY: false, wheelX: 'none', wheelY: 'none' }),
  )

  const xAxis = chart.xAxes.push(
    am5xy.CategoryAxis.new(root, {
      categoryField: 'period',
      renderer: am5xy.AxisRendererX.new(root, { minGridDistance: 40 }),
    }),
  )
  xAxis.get('renderer').grid.template.set('visible', false)

  const yAxis = chart.yAxes.push(
    am5xy.ValueAxis.new(root, { renderer: am5xy.AxisRendererY.new(root, {}) }),
  )
  yAxis.get('renderer').grid.template.setAll({ strokeDasharray: [3, 3] })

  const series = chart.series.push(
    am5xy.LineSeries.new(root, {
      name: 'Receita',
      xAxis,
      yAxis,
      valueYField: 'revenue',
      categoryXField: 'period',
      stroke: am5.color(0x6d28d9),
      fill: am5.color(0x6d28d9),
      tooltip: am5.Tooltip.new(root, { labelText: '{valueY}' }),
    }),
  )
  series.strokes.template.setAll({ strokeWidth: 3 })
  series.fills.template.setAll({ visible: true, fillOpacity: 1 })
  series.fills.template.set(
    'fillGradient',
    am5.LinearGradient.new(root, { stops: [{ opacity: 0.35 }, { opacity: 0 }], rotation: 90 }),
  )

  series.bullets.push(() =>
    am5.Bullet.new(root, {
      sprite: am5.Circle.new(root, {
        radius: 4,
        fill: am5.color(0x6d28d9),
        stroke: am5.color(0xffffff),
        strokeWidth: 2,
      }),
    }),
  )

  const data = store.revenueTimeseries
  xAxis.data.setAll(data)
  series.data.setAll(data)
  series.appear(800)
  chart.appear(800, 100)

  revenueRoot = root
}

function renderDailyRevenueChart(): void {
  if (!dailyRevenueChartDiv.value) return
  dailyRevenueRoot?.dispose()

  const root = am5.Root.new(dailyRevenueChartDiv.value)
  root.setThemes([am5themes_Animated.new(root)])
  root._logo?.dispose()

  const chart = root.container.children.push(
    am5xy.XYChart.new(root, { panX: false, panY: false, wheelX: 'none', wheelY: 'none' }),
  )

  const xAxis = chart.xAxes.push(
    am5xy.CategoryAxis.new(root, {
      categoryField: 'period',
      renderer: am5xy.AxisRendererX.new(root, { minGridDistance: 40 }),
    }),
  )
  xAxis.get('renderer').grid.template.set('visible', false)
  xAxis.get('renderer').labels.template.setAll({ rotation: -45, centerY: am5.p50, centerX: am5.p100 })

  const yAxis = chart.yAxes.push(
    am5xy.ValueAxis.new(root, { renderer: am5xy.AxisRendererY.new(root, {}) }),
  )
  yAxis.get('renderer').grid.template.setAll({ strokeDasharray: [3, 3] })

  const series = chart.series.push(
    am5xy.LineSeries.new(root, {
      name: 'Receita',
      xAxis,
      yAxis,
      valueYField: 'revenue',
      categoryXField: 'period',
      stroke: am5.color(0x22c55e),
      fill: am5.color(0x22c55e),
      tooltip: am5.Tooltip.new(root, { labelText: '{valueY}' }),
    }),
  )
  series.strokes.template.setAll({ strokeWidth: 3 })
  series.fills.template.setAll({ visible: true, fillOpacity: 1 })
  series.fills.template.set(
    'fillGradient',
    am5.LinearGradient.new(root, { stops: [{ opacity: 0.35 }, { opacity: 0 }], rotation: 90 }),
  )

  series.bullets.push(() =>
    am5.Bullet.new(root, {
      sprite: am5.Circle.new(root, {
        radius: 3,
        fill: am5.color(0x22c55e),
        stroke: am5.color(0xffffff),
        strokeWidth: 2,
      }),
    }),
  )

  const data = store.dailyRevenueTimeseries.map((point) => ({
    period: formatDayLabel(point.period),
    revenue: point.revenue,
  }))
  xAxis.data.setAll(data)
  series.data.setAll(data)
  series.appear(800)
  chart.appear(800, 100)

  dailyRevenueRoot = root
}

function renderTopProductsChart(): void {
  if (!topProductsChartDiv.value) return
  topProductsRoot?.dispose()

  const root = am5.Root.new(topProductsChartDiv.value)
  root.setThemes([am5themes_Animated.new(root)])
  root._logo?.dispose()

  const chart = root.container.children.push(
    am5xy.XYChart.new(root, { panX: false, panY: false, wheelX: 'none', wheelY: 'none' }),
  )

  const yAxis = chart.yAxes.push(
    am5xy.CategoryAxis.new(root, {
      categoryField: 'name',
      renderer: am5xy.AxisRendererY.new(root, { minGridDistance: 20 }),
    }),
  )
  yAxis.get('renderer').grid.template.set('visible', false)

  const xAxis = chart.xAxes.push(
    am5xy.ValueAxis.new(root, { renderer: am5xy.AxisRendererX.new(root, {}), min: 0 }),
  )
  xAxis.get('renderer').grid.template.setAll({ strokeDasharray: [3, 3] })

  const palette = [0x6d28d9, 0x3b82f6, 0x22c55e, 0xf59e0b, 0xec4899, 0x14b8a6]

  const series = chart.series.push(
    am5xy.ColumnSeries.new(root, {
      name: 'Quantidade Vendida',
      xAxis,
      yAxis,
      valueXField: 'quantitySold',
      categoryYField: 'name',
      tooltip: am5.Tooltip.new(root, { labelText: '{valueX}' }),
    }),
  )
  series.columns.template.setAll({ cornerRadiusTR: 6, cornerRadiusBR: 6, strokeOpacity: 0, height: am5.percent(60) })
  series.columns.template.adapters.add('fill', (_fill, target) => {
    const dataItem = target.dataItem
    const index = dataItem ? series.dataItems.indexOf(dataItem) : 0
    return am5.color(palette[index % palette.length] ?? 0x6d28d9)
  })

  const data = store.topProducts
  yAxis.data.setAll(data)
  series.data.setAll(data)
  series.appear(800)
  chart.appear(800, 100)

  topProductsRoot = root
}

function renderServiceStatusChart(): void {
  if (!serviceStatusChartDiv.value || !hasServiceOrders.value) return
  serviceStatusRoot?.dispose()
  serviceStatusRoot = renderDonutChart(serviceStatusChartDiv.value, serviceStatusBreakdown.value)
}

function renderSalesStatusChart(): void {
  if (!salesStatusChartDiv.value || !hasSales.value) return
  salesStatusRoot?.dispose()
  salesStatusRoot = renderDonutChart(salesStatusChartDiv.value, salesStatusBreakdown.value)
}

function renderProductsByCategoryChart(): void {
  if (!productsByCategoryChartDiv.value || !hasProducts.value) return
  productsByCategoryRoot?.dispose()
  productsByCategoryRoot = renderDonutChart(
    productsByCategoryChartDiv.value,
    productsByCategoryBreakdown.value,
  )
}

function renderNewCustomersChart(): void {
  if (!newCustomersChartDiv.value) return
  newCustomersRoot?.dispose()

  const root = am5.Root.new(newCustomersChartDiv.value)
  root.setThemes([am5themes_Animated.new(root)])
  root._logo?.dispose()

  const chart = root.container.children.push(
    am5xy.XYChart.new(root, { panX: false, panY: false, wheelX: 'none', wheelY: 'none' }),
  )

  const xAxis = chart.xAxes.push(
    am5xy.CategoryAxis.new(root, {
      categoryField: 'period',
      renderer: am5xy.AxisRendererX.new(root, { minGridDistance: 40 }),
    }),
  )
  xAxis.get('renderer').grid.template.set('visible', false)

  const yAxis = chart.yAxes.push(
    am5xy.ValueAxis.new(root, { renderer: am5xy.AxisRendererY.new(root, {}), min: 0 }),
  )
  yAxis.get('renderer').grid.template.setAll({ strokeDasharray: [3, 3] })

  const series = chart.series.push(
    am5xy.ColumnSeries.new(root, {
      name: 'Novos Clientes',
      xAxis,
      yAxis,
      valueYField: 'count',
      categoryXField: 'period',
      fill: am5.color(0x6d28d9),
      tooltip: am5.Tooltip.new(root, { labelText: '{valueY}' }),
    }),
  )
  series.columns.template.setAll({
    cornerRadiusTL: 6,
    cornerRadiusTR: 6,
    strokeOpacity: 0,
    width: am5.percent(50),
  })

  const data = store.newCustomersTimeseries
  xAxis.data.setAll(data)
  series.data.setAll(data)
  series.appear(800)
  chart.appear(800, 100)

  newCustomersRoot = root
}

function renderCashFlowChart(): void {
  if (!cashFlowChartDiv.value) return
  cashFlowRoot?.dispose()

  const root = am5.Root.new(cashFlowChartDiv.value)
  root.setThemes([am5themes_Animated.new(root)])
  root._logo?.dispose()

  const chart = root.container.children.push(
    am5xy.XYChart.new(root, { panX: false, panY: false, wheelX: 'none', wheelY: 'none' }),
  )

  const xAxis = chart.xAxes.push(
    am5xy.CategoryAxis.new(root, {
      categoryField: 'period',
      renderer: am5xy.AxisRendererX.new(root, { minGridDistance: 40 }),
    }),
  )
  xAxis.get('renderer').grid.template.set('visible', false)

  const yAxis = chart.yAxes.push(
    am5xy.ValueAxis.new(root, { renderer: am5xy.AxisRendererY.new(root, {}) }),
  )
  yAxis.get('renderer').grid.template.setAll({ strokeDasharray: [3, 3] })

  const inSeries = chart.series.push(
    am5xy.ColumnSeries.new(root, {
      name: 'Entradas',
      xAxis,
      yAxis,
      valueYField: 'cashIn',
      categoryXField: 'period',
      fill: am5.color(0x22c55e),
      tooltip: am5.Tooltip.new(root, { labelText: '{name}: {valueY}' }),
    }),
  )
  inSeries.columns.template.setAll({ strokeOpacity: 0 })

  const outSeries = chart.series.push(
    am5xy.ColumnSeries.new(root, {
      name: 'Saídas',
      xAxis,
      yAxis,
      valueYField: 'cashOut',
      categoryXField: 'period',
      fill: am5.color(0xef4444),
      tooltip: am5.Tooltip.new(root, { labelText: '{name}: {valueY}' }),
    }),
  )
  outSeries.columns.template.setAll({ strokeOpacity: 0 })

  const data = store.cashFlowTimeseries.map((point) => ({
    period: formatDayLabel(point.period),
    cashIn: point.cashIn,
    cashOut: point.cashOut,
  }))
  xAxis.data.setAll(data)
  inSeries.data.setAll(data)
  outSeries.data.setAll(data)
  inSeries.appear(800)
  outSeries.appear(800)
  chart.appear(800, 100)

  cashFlowRoot = root
}

async function renderAllCharts(): Promise<void> {
  await nextTick()
  renderRevenueChart()
  renderDailyRevenueChart()
  renderTopProductsChart()
  renderServiceStatusChart()
  renderSalesStatusChart()
  renderNewCustomersChart()
  renderCashFlowChart()
  renderProductsByCategoryChart()
}

onMounted(async () => {
  await Promise.all([
    store.fetchSummary(),
    store.fetchRevenueTimeseries(),
    store.fetchDailyRevenueTimeseries(),
    store.fetchTopProducts(),
    store.fetchNewCustomersTimeseries(),
    store.fetchCashFlowTimeseries(),
    store.fetchProductsByCategory(),
  ])
  await renderAllCharts()
})

onBeforeUnmount(() => {
  revenueRoot?.dispose()
  dailyRevenueRoot?.dispose()
  topProductsRoot?.dispose()
  serviceStatusRoot?.dispose()
  salesStatusRoot?.dispose()
  newCustomersRoot?.dispose()
  cashFlowRoot?.dispose()
  productsByCategoryRoot?.dispose()
})
</script>

<template>
  <div class="space-y-5">
    <h1 class="text-xl font-semibold text-text-primary dark:text-white">Dashboard</h1>

    <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>

    <div
      v-if="store.isLoading && !store.summary"
      class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5"
    >
      <div
        v-for="n in 5"
        :key="n"
        class="rounded-xl border border-black/5 bg-surface-light p-4 shadow-sm dark:border-white/10 dark:bg-surface-dark"
      >
        <div class="h-3 w-16 animate-pulse rounded bg-black/5 dark:bg-white/10" />
        <div class="mt-2 h-5 w-12 animate-pulse rounded bg-black/5 dark:bg-white/10" />
      </div>
    </div>

    <div v-if="store.summary" class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
      <div
        class="rounded-xl border border-black/5 bg-surface-light p-4 shadow-sm transition-shadow hover:shadow-md dark:border-white/10 dark:bg-surface-dark"
      >
        <div class="flex items-center justify-between">
          <p class="text-xs font-medium text-text-secondary">Clientes</p>
          <span class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Users :size="16" />
          </span>
        </div>
        <p class="mt-2 text-xl font-bold text-text-primary dark:text-white">
          {{ store.summary.totalCustomers }}
        </p>
      </div>
      <div
        class="rounded-xl border border-black/5 bg-surface-light p-4 shadow-sm transition-shadow hover:shadow-md dark:border-white/10 dark:bg-surface-dark"
      >
        <div class="flex items-center justify-between">
          <p class="text-xs font-medium text-text-secondary">Produtos</p>
          <span class="flex h-8 w-8 items-center justify-center rounded-lg bg-info/10 text-info">
            <Package :size="16" />
          </span>
        </div>
        <p class="mt-2 text-xl font-bold text-text-primary dark:text-white">
          {{ store.summary.totalProducts }}
        </p>
      </div>
      <div
        class="rounded-xl border border-black/5 bg-surface-light p-4 shadow-sm transition-shadow hover:shadow-md dark:border-white/10 dark:bg-surface-dark"
      >
        <div class="flex items-center justify-between">
          <p class="text-xs font-medium text-text-secondary">Serviços</p>
          <span class="flex h-8 w-8 items-center justify-center rounded-lg bg-warning/10 text-warning">
            <Wrench :size="16" />
          </span>
        </div>
        <p class="mt-2 text-xl font-bold text-text-primary dark:text-white">
          {{ store.summary.totalServices }}
        </p>
      </div>
      <div
        class="rounded-xl border border-black/5 bg-surface-light p-4 shadow-sm transition-shadow hover:shadow-md dark:border-white/10 dark:bg-surface-dark"
      >
        <div class="flex items-center justify-between">
          <p class="text-xs font-medium text-text-secondary">Ordens Abertas</p>
          <span class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <ClipboardList :size="16" />
          </span>
        </div>
        <p class="mt-2 text-xl font-bold text-text-primary dark:text-white">
          {{ ordersOpenCount() }}
        </p>
      </div>
      <div
        class="rounded-xl border border-black/5 bg-surface-light p-4 shadow-sm transition-shadow hover:shadow-md dark:border-white/10 dark:bg-surface-dark"
      >
        <div class="flex items-center justify-between">
          <p class="text-xs font-medium text-text-secondary">Ticket Médio</p>
          <span class="flex h-8 w-8 items-center justify-center rounded-lg bg-success/10 text-success">
            <Receipt :size="16" />
          </span>
        </div>
        <p class="mt-2 text-xl font-bold text-text-primary dark:text-white">
          {{ formatCurrency(store.summary.averageTicket) }}
        </p>
      </div>
      <div
        class="rounded-xl border border-black/5 bg-surface-light p-4 shadow-sm transition-shadow hover:shadow-md dark:border-white/10 dark:bg-surface-dark"
      >
        <div class="flex items-center justify-between">
          <p class="text-xs font-medium text-text-secondary">Receita do Mês</p>
          <span class="flex h-8 w-8 items-center justify-center rounded-lg bg-success/10 text-success">
            <TrendingUp :size="16" />
          </span>
        </div>
        <p class="mt-2 text-xl font-bold text-text-primary dark:text-white">
          {{ formatCurrency(store.summary.revenueThisMonth) }}
        </p>
        <p
          class="text-xs"
          :class="
            (store.summary.revenueChangePercentage ?? 0) >= 0 ? 'text-success' : 'text-danger'
          "
        >
          {{ formatPercentage(store.summary.revenueChangePercentage) }} vs. mês anterior
        </p>
      </div>
      <div
        class="rounded-xl border border-black/5 bg-surface-light p-4 shadow-sm transition-shadow hover:shadow-md dark:border-white/10 dark:bg-surface-dark"
      >
        <div class="flex items-center justify-between">
          <p class="text-xs font-medium text-text-secondary">Saldo de Caixa</p>
          <span class="flex h-8 w-8 items-center justify-center rounded-lg bg-info/10 text-info">
            <Wallet :size="16" />
          </span>
        </div>
        <p class="mt-2 text-xl font-bold text-text-primary dark:text-white">
          {{ formatCurrency(store.summary.cashBalance) }}
        </p>
      </div>
      <button
        type="button"
        data-testid="receivable-kpi-card"
        class="rounded-xl border border-black/5 bg-surface-light p-4 text-left shadow-sm transition-shadow hover:shadow-md dark:border-white/10 dark:bg-surface-dark"
        @click="router.push({ name: 'accounts-receivable' })"
      >
        <div class="flex items-center justify-between">
          <p class="text-xs font-medium text-text-secondary">Contas a Receber</p>
          <span class="flex h-8 w-8 items-center justify-center rounded-lg bg-success/10 text-success">
            <ArrowDownCircle :size="16" />
          </span>
        </div>
        <p class="mt-2 text-xl font-bold text-text-primary dark:text-white">
          {{ formatCurrency(store.summary.accountsReceivablePendingTotal) }}
        </p>
        <p class="text-xs text-text-secondary">
          {{ store.summary.accountsReceivableOverdueCount }} vencida(s)
        </p>
      </button>
      <button
        type="button"
        data-testid="payable-kpi-card"
        class="rounded-xl border border-black/5 bg-surface-light p-4 text-left shadow-sm transition-shadow hover:shadow-md dark:border-white/10 dark:bg-surface-dark"
        @click="router.push({ name: 'accounts-payable' })"
      >
        <div class="flex items-center justify-between">
          <p class="text-xs font-medium text-text-secondary">Contas a Pagar</p>
          <span class="flex h-8 w-8 items-center justify-center rounded-lg bg-danger/10 text-danger">
            <ArrowUpCircle :size="16" />
          </span>
        </div>
        <p class="mt-2 text-xl font-bold text-text-primary dark:text-white">
          {{ formatCurrency(store.summary.accountsPayablePendingTotal) }}
        </p>
        <p class="text-xs text-text-secondary">
          {{ store.summary.accountsPayableOverdueCount }} vencida(s)
        </p>
      </button>
      <button
        type="button"
        data-testid="critical-stock-kpi-card"
        class="rounded-xl border border-black/5 bg-surface-light p-4 text-left shadow-sm transition-shadow hover:shadow-md dark:border-white/10 dark:bg-surface-dark"
        @click="router.push({ name: 'products' })"
      >
        <div class="flex items-center justify-between">
          <p class="text-xs font-medium text-text-secondary">Estoque Crítico</p>
          <span class="flex h-8 w-8 items-center justify-center rounded-lg bg-warning/10 text-warning">
            <AlertTriangle :size="16" />
          </span>
        </div>
        <p class="mt-2 text-xl font-bold text-text-primary dark:text-white">
          {{ store.summary.criticalStockCount }}
        </p>
      </button>
    </div>

    <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <div
        class="rounded-xl border border-black/5 bg-surface-light p-4 shadow-sm dark:border-white/10 dark:bg-surface-dark"
      >
        <h2 class="mb-2 text-sm font-semibold text-text-primary dark:text-white">
          Receita Mensal
        </h2>
        <div ref="revenueChartDiv" data-testid="revenue-chart" class="h-64 w-full"></div>
      </div>
      <div
        class="rounded-xl border border-black/5 bg-surface-light p-4 shadow-sm dark:border-white/10 dark:bg-surface-dark"
      >
        <h2 class="mb-2 text-sm font-semibold text-text-primary dark:text-white">
          Receita Diária
        </h2>
        <div ref="dailyRevenueChartDiv" data-testid="daily-revenue-chart" class="h-64 w-full"></div>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <div
        class="rounded-xl border border-black/5 bg-surface-light p-4 shadow-sm dark:border-white/10 dark:bg-surface-dark"
      >
        <h2 class="mb-2 text-sm font-semibold text-text-primary dark:text-white">
          Ordens de Serviço por Status
        </h2>
        <div
          v-if="hasServiceOrders"
          ref="serviceStatusChartDiv"
          data-testid="service-status-chart"
          class="h-48 w-full"
        ></div>
        <p v-else class="flex h-48 items-center justify-center text-center text-sm text-text-secondary">
          Nenhuma ordem de serviço registrada ainda.
        </p>
        <ul v-if="hasServiceOrders" class="mt-2 space-y-1.5">
          <li
            v-for="item in serviceStatusBreakdown"
            :key="item.key"
            class="flex items-center justify-between text-xs text-text-secondary"
          >
            <span class="flex items-center gap-2">
              <span
                class="h-2 w-2 rounded-full"
                :style="{ backgroundColor: '#' + item.color.toString(16).padStart(6, '0') }"
              />
              {{ item.label }}
            </span>
            <span class="font-medium text-text-primary dark:text-white">{{ item.value }}</span>
          </li>
        </ul>
      </div>
      <div
        class="rounded-xl border border-black/5 bg-surface-light p-4 shadow-sm dark:border-white/10 dark:bg-surface-dark"
      >
        <h2 class="mb-2 text-sm font-semibold text-text-primary dark:text-white">
          Vendas por Status
        </h2>
        <div
          v-if="hasSales"
          ref="salesStatusChartDiv"
          data-testid="sales-status-chart"
          class="h-48 w-full"
        ></div>
        <p v-else class="flex h-48 items-center justify-center text-center text-sm text-text-secondary">
          Nenhuma venda registrada ainda.
        </p>
        <ul v-if="hasSales" class="mt-2 space-y-1.5">
          <li
            v-for="item in salesStatusBreakdown"
            :key="item.key"
            class="flex items-center justify-between text-xs text-text-secondary"
          >
            <span class="flex items-center gap-2">
              <span
                class="h-2 w-2 rounded-full"
                :style="{ backgroundColor: '#' + item.color.toString(16).padStart(6, '0') }"
              />
              {{ item.label }}
            </span>
            <span class="font-medium text-text-primary dark:text-white">{{ item.value }}</span>
          </li>
        </ul>
      </div>
      <div
        class="rounded-xl border border-black/5 bg-surface-light p-4 shadow-sm dark:border-white/10 dark:bg-surface-dark"
      >
        <h2 class="mb-2 text-sm font-semibold text-text-primary dark:text-white">
          Produtos por Categoria
        </h2>
        <div
          v-if="hasProducts"
          ref="productsByCategoryChartDiv"
          data-testid="products-by-category-chart"
          class="h-48 w-full"
        ></div>
        <p v-else class="flex h-48 items-center justify-center text-center text-sm text-text-secondary">
          Nenhum produto cadastrado ainda.
        </p>
        <ul v-if="hasProducts" class="mt-2 space-y-1.5">
          <li
            v-for="item in productsByCategoryBreakdown"
            :key="item.key"
            class="flex items-center justify-between text-xs text-text-secondary"
          >
            <span class="flex items-center gap-2 truncate">
              <span
                class="h-2 w-2 shrink-0 rounded-full"
                :style="{ backgroundColor: '#' + item.color.toString(16).padStart(6, '0') }"
              />
              <span class="truncate">{{ item.label }}</span>
            </span>
            <span class="font-medium text-text-primary dark:text-white">{{ item.value }}</span>
          </li>
        </ul>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <div
        class="rounded-xl border border-black/5 bg-surface-light p-4 shadow-sm dark:border-white/10 dark:bg-surface-dark"
      >
        <h2 class="mb-2 text-sm font-semibold text-text-primary dark:text-white">
          Novos Clientes
        </h2>
        <div ref="newCustomersChartDiv" data-testid="new-customers-chart" class="h-64 w-full"></div>
      </div>
      <div
        class="rounded-xl border border-black/5 bg-surface-light p-4 shadow-sm dark:border-white/10 dark:bg-surface-dark"
      >
        <h2 class="mb-2 text-sm font-semibold text-text-primary dark:text-white">
          Fluxo de Caixa (30 dias)
        </h2>
        <div ref="cashFlowChartDiv" data-testid="cash-flow-chart" class="h-64 w-full"></div>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4">
      <div
        class="rounded-xl border border-black/5 bg-surface-light p-4 shadow-sm dark:border-white/10 dark:bg-surface-dark"
      >
        <h2 class="mb-2 text-sm font-semibold text-text-primary dark:text-white">
          Produtos Mais Vendidos
        </h2>
        <div ref="topProductsChartDiv" data-testid="top-products-chart" class="h-64 w-full"></div>
      </div>
    </div>
  </div>
</template>
