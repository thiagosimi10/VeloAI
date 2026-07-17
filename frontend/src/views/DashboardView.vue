<script setup lang="ts">
import * as am5 from '@amcharts/amcharts5'
import am5themes_Animated from '@amcharts/amcharts5/themes/Animated'
import * as am5xy from '@amcharts/amcharts5/xy'
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useDashboardStore } from '@/stores/dashboard'

const store = useDashboardStore()
const router = useRouter()

const revenueChartDiv = ref<HTMLDivElement | null>(null)
const topProductsChartDiv = ref<HTMLDivElement | null>(null)
let revenueRoot: am5.Root | null = null
let topProductsRoot: am5.Root | null = null

function formatCurrency(value: number): string {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
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

function renderRevenueChart(): void {
  if (!revenueChartDiv.value) return
  revenueRoot?.dispose()

  const root = am5.Root.new(revenueChartDiv.value)
  root.setThemes([am5themes_Animated.new(root)])

  const chart = root.container.children.push(
    am5xy.XYChart.new(root, { panX: false, panY: false, wheelX: 'none', wheelY: 'none' }),
  )

  const xAxis = chart.xAxes.push(
    am5xy.CategoryAxis.new(root, {
      categoryField: 'period',
      renderer: am5xy.AxisRendererX.new(root, {}),
    }),
  )
  const yAxis = chart.yAxes.push(
    am5xy.ValueAxis.new(root, { renderer: am5xy.AxisRendererY.new(root, {}) }),
  )

  const series = chart.series.push(
    am5xy.LineSeries.new(root, {
      name: 'Receita',
      xAxis,
      yAxis,
      valueYField: 'revenue',
      categoryXField: 'period',
    }),
  )

  const data = store.revenueTimeseries
  xAxis.data.setAll(data)
  series.data.setAll(data)
  series.appear(600)
  chart.appear(600, 100)

  revenueRoot = root
}

function renderTopProductsChart(): void {
  if (!topProductsChartDiv.value) return
  topProductsRoot?.dispose()

  const root = am5.Root.new(topProductsChartDiv.value)
  root.setThemes([am5themes_Animated.new(root)])

  const chart = root.container.children.push(
    am5xy.XYChart.new(root, { panX: false, panY: false, wheelX: 'none', wheelY: 'none' }),
  )

  const yAxis = chart.yAxes.push(
    am5xy.CategoryAxis.new(root, {
      categoryField: 'name',
      renderer: am5xy.AxisRendererY.new(root, {}),
    }),
  )
  const xAxis = chart.xAxes.push(
    am5xy.ValueAxis.new(root, { renderer: am5xy.AxisRendererX.new(root, {}) }),
  )

  const series = chart.series.push(
    am5xy.ColumnSeries.new(root, {
      name: 'Quantidade Vendida',
      xAxis,
      yAxis,
      valueXField: 'quantitySold',
      categoryYField: 'name',
    }),
  )

  const data = store.topProducts
  yAxis.data.setAll(data)
  series.data.setAll(data)
  series.appear(600)
  chart.appear(600, 100)

  topProductsRoot = root
}

onMounted(async () => {
  await Promise.all([
    store.fetchSummary(),
    store.fetchRevenueTimeseries(),
    store.fetchTopProducts(),
  ])
  renderRevenueChart()
  renderTopProductsChart()
})

onBeforeUnmount(() => {
  revenueRoot?.dispose()
  topProductsRoot?.dispose()
})
</script>

<template>
  <div class="space-y-5">
    <h1 class="text-xl font-semibold text-text-primary dark:text-white">Dashboard</h1>

    <p v-if="store.error" class="text-sm text-danger">{{ store.error }}</p>

    <div v-if="store.summary" class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
      <div class="rounded-lg border border-black/10 p-4 dark:border-white/10">
        <p class="text-xs text-text-secondary">Clientes</p>
        <p class="text-lg font-semibold text-text-primary dark:text-white">
          {{ store.summary.totalCustomers }}
        </p>
      </div>
      <div class="rounded-lg border border-black/10 p-4 dark:border-white/10">
        <p class="text-xs text-text-secondary">Produtos</p>
        <p class="text-lg font-semibold text-text-primary dark:text-white">
          {{ store.summary.totalProducts }}
        </p>
      </div>
      <div class="rounded-lg border border-black/10 p-4 dark:border-white/10">
        <p class="text-xs text-text-secondary">Serviços</p>
        <p class="text-lg font-semibold text-text-primary dark:text-white">
          {{ store.summary.totalServices }}
        </p>
      </div>
      <div class="rounded-lg border border-black/10 p-4 dark:border-white/10">
        <p class="text-xs text-text-secondary">Ordens Abertas</p>
        <p class="text-lg font-semibold text-text-primary dark:text-white">
          {{ ordersOpenCount() }}
        </p>
      </div>
      <div class="rounded-lg border border-black/10 p-4 dark:border-white/10">
        <p class="text-xs text-text-secondary">Ticket Médio</p>
        <p class="text-lg font-semibold text-text-primary dark:text-white">
          {{ formatCurrency(store.summary.averageTicket) }}
        </p>
      </div>
      <div class="rounded-lg border border-black/10 p-4 dark:border-white/10">
        <p class="text-xs text-text-secondary">Receita do Mês</p>
        <p class="text-lg font-semibold text-text-primary dark:text-white">
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
      <div class="rounded-lg border border-black/10 p-4 dark:border-white/10">
        <p class="text-xs text-text-secondary">Saldo de Caixa</p>
        <p class="text-lg font-semibold text-text-primary dark:text-white">
          {{ formatCurrency(store.summary.cashBalance) }}
        </p>
      </div>
      <button
        type="button"
        data-testid="receivable-kpi-card"
        class="rounded-lg border border-black/10 p-4 text-left dark:border-white/10"
        @click="router.push({ name: 'accounts-receivable' })"
      >
        <p class="text-xs text-text-secondary">Contas a Receber</p>
        <p class="text-lg font-semibold text-text-primary dark:text-white">
          {{ formatCurrency(store.summary.accountsReceivablePendingTotal) }}
        </p>
        <p class="text-xs text-text-secondary">
          {{ store.summary.accountsReceivableOverdueCount }} vencida(s)
        </p>
      </button>
      <button
        type="button"
        data-testid="payable-kpi-card"
        class="rounded-lg border border-black/10 p-4 text-left dark:border-white/10"
        @click="router.push({ name: 'accounts-payable' })"
      >
        <p class="text-xs text-text-secondary">Contas a Pagar</p>
        <p class="text-lg font-semibold text-text-primary dark:text-white">
          {{ formatCurrency(store.summary.accountsPayablePendingTotal) }}
        </p>
        <p class="text-xs text-text-secondary">
          {{ store.summary.accountsPayableOverdueCount }} vencida(s)
        </p>
      </button>
      <button
        type="button"
        data-testid="critical-stock-kpi-card"
        class="rounded-lg border border-black/10 p-4 text-left dark:border-white/10"
        @click="router.push({ name: 'products' })"
      >
        <p class="text-xs text-text-secondary">Estoque Crítico</p>
        <p class="text-lg font-semibold text-text-primary dark:text-white">
          {{ store.summary.criticalStockCount }}
        </p>
      </button>
    </div>

    <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <div class="rounded-lg border border-black/10 p-4 dark:border-white/10">
        <h2 class="mb-2 text-sm font-semibold text-text-primary dark:text-white">
          Receita Mensal
        </h2>
        <div ref="revenueChartDiv" data-testid="revenue-chart" class="h-64 w-full"></div>
      </div>
      <div class="rounded-lg border border-black/10 p-4 dark:border-white/10">
        <h2 class="mb-2 text-sm font-semibold text-text-primary dark:text-white">
          Produtos Mais Vendidos
        </h2>
        <div ref="topProductsChartDiv" data-testid="top-products-chart" class="h-64 w-full"></div>
      </div>
    </div>
  </div>
</template>
