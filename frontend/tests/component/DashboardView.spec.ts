import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import DashboardView from '@/views/DashboardView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

function createMockChartNode(): Record<string, unknown> {
  const node: Record<string, unknown> = {
    setThemes: vi.fn(),
    appear: vi.fn(),
    dispose: vi.fn(),
    data: { setAll: vi.fn() },
    container: { children: { push: vi.fn(() => createMockChartNode()) } },
    xAxes: { push: vi.fn(() => createMockChartNode()) },
    yAxes: { push: vi.fn(() => createMockChartNode()) },
    series: { push: vi.fn(() => createMockChartNode()) },
  }
  return node
}

vi.mock('@amcharts/amcharts5', () => ({
  Root: { new: vi.fn(() => createMockChartNode()) },
}))

vi.mock('@amcharts/amcharts5/xy', () => ({
  XYChart: { new: vi.fn(() => createMockChartNode()) },
  CategoryAxis: { new: vi.fn(() => createMockChartNode()) },
  ValueAxis: { new: vi.fn(() => createMockChartNode()) },
  AxisRendererX: { new: vi.fn(() => ({})) },
  AxisRendererY: { new: vi.fn(() => ({})) },
  LineSeries: { new: vi.fn(() => createMockChartNode()) },
  ColumnSeries: { new: vi.fn(() => createMockChartNode()) },
}))

vi.mock('@amcharts/amcharts5/themes/Animated', () => ({
  default: { new: vi.fn(() => ({})) },
}))

import { http } from '@/services/http'

const RAW_SUMMARY = {
  total_customers: 10,
  total_products: 20,
  total_services: 5,
  orders_by_status: { open: 2, in_progress: 1, completed: 8, cancelled: 1 },
  revenue_this_month: '1100.00',
  revenue_last_month: '1000.00',
  revenue_change_percentage: '10.00',
  average_ticket: '275.00',
  accounts_receivable_pending_total: '500.00',
  accounts_receivable_overdue_count: 1,
  accounts_payable_pending_total: '200.00',
  accounts_payable_overdue_count: 0,
  cash_balance: '3000.00',
  critical_stock_count: 2,
}

function mockAllFetches(): void {
  vi.mocked(http.get).mockImplementation((url: string) => {
    if (url === '/api/v1/dashboard/summary') {
      return Promise.resolve({ data: { data: RAW_SUMMARY } }) as never
    }
    if (url === '/api/v1/dashboard/revenue-timeseries') {
      return Promise.resolve({
        data: { data: [{ period: '2026-07', revenue: '1100.00' }] },
      }) as never
    }
    if (url === '/api/v1/dashboard/top-products') {
      return Promise.resolve({
        data: { data: [{ product_id: 'product-1', name: 'SSD Kingston 1TB', quantity_sold: 15 }] },
      }) as never
    }
    throw new Error(`unexpected GET ${url}`)
  })
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/dashboard', name: 'dashboard', component: DashboardView },
      { path: '/accounts-receivable', name: 'accounts-receivable', component: { template: '<div />' } },
      { path: '/accounts-payable', name: 'accounts-payable', component: { template: '<div />' } },
      { path: '/products', name: 'products', component: { template: '<div />' } },
    ],
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('DashboardView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
  })

  it('renders the KPI cards with the values returned by the store', async () => {
    mockAllFetches()
    const router = buildRouter()
    router.push('/dashboard')
    await router.isReady()

    const wrapper = mount(DashboardView, {
      global: { plugins: [router] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('10')
    expect(wrapper.text()).toContain('R$')
    expect(wrapper.text()).toContain('+10.00% vs. mês anterior')
    expect(wrapper.text()).toContain('1 vencida(s)')
  })

  it('navigates to accounts-receivable when the receivable KPI card is clicked', async () => {
    mockAllFetches()
    const router = buildRouter()
    router.push('/dashboard')
    await router.isReady()

    const wrapper = mount(DashboardView, {
      global: { plugins: [router] },
    })
    await flushPromises()

    await wrapper.find('[data-testid="receivable-kpi-card"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('accounts-receivable')
  })

  it('navigates to products when the critical stock KPI card is clicked', async () => {
    mockAllFetches()
    const router = buildRouter()
    router.push('/dashboard')
    await router.isReady()

    const wrapper = mount(DashboardView, {
      global: { plugins: [router] },
    })
    await flushPromises()

    await wrapper.find('[data-testid="critical-stock-kpi-card"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('products')
  })

  it('shows an error message when the summary request fails', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/dashboard/summary') {
        return Promise.reject(new Error('failed')) as never
      }
      return Promise.resolve({ data: { data: [] } }) as never
    })
    const router = buildRouter()
    router.push('/dashboard')
    await router.isReady()

    const wrapper = mount(DashboardView, {
      global: { plugins: [router] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Não foi possível concluir a operação')
  })
})
