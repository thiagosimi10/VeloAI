import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn().mockResolvedValue({ data: { data: [] } }), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
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

vi.mock('@amcharts/amcharts5', () => ({ Root: { new: vi.fn(() => createMockChartNode()) } }))
vi.mock('@amcharts/amcharts5/xy', () => ({
  XYChart: { new: vi.fn(() => createMockChartNode()) },
  CategoryAxis: { new: vi.fn(() => createMockChartNode()) },
  ValueAxis: { new: vi.fn(() => createMockChartNode()) },
  AxisRendererX: { new: vi.fn(() => ({})) },
  AxisRendererY: { new: vi.fn(() => ({})) },
  LineSeries: { new: vi.fn(() => createMockChartNode()) },
  ColumnSeries: { new: vi.fn(() => createMockChartNode()) },
}))
vi.mock('@amcharts/amcharts5/themes/Animated', () => ({ default: { new: vi.fn(() => ({})) } }))

import App from '@/App.vue'
import DashboardView from '@/views/DashboardView.vue'
import LoginView from '@/views/LoginView.vue'

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/login', name: 'login', component: LoginView, meta: { layout: 'auth' } },
      {
        path: '/dashboard',
        name: 'dashboard',
        component: DashboardView,
        meta: { layout: 'default' },
      },
      { path: '/customers', name: 'customers', component: { template: '<div />' } },
      { path: '/suppliers', name: 'suppliers', component: { template: '<div />' } },
      { path: '/categories', name: 'categories', component: { template: '<div />' } },
      { path: '/products', name: 'products', component: { template: '<div />' } },
      { path: '/services', name: 'services', component: { template: '<div />' } },
      { path: '/service-orders', name: 'service-orders', component: { template: '<div />' } },
      { path: '/sales', name: 'sales', component: { template: '<div />' } },
      { path: '/accounts-receivable', name: 'accounts-receivable', component: { template: '<div />' } },
      { path: '/accounts-payable', name: 'accounts-payable', component: { template: '<div />' } },
      { path: '/cash-flow', name: 'cash-flow', component: { template: '<div />' } },
    ],
  })
}

describe('App', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('uses AuthLayout (no sidebar) for routes marked as "auth"', async () => {
    const router = buildRouter()
    await router.push('/login')

    const wrapper = mount(App, { global: { plugins: [router, PrimeVue] } })

    expect(wrapper.find('[data-testid="app-sidebar"]').exists()).toBe(false)
    expect(wrapper.text()).toContain('Entrar no VeloAI')
  })

  it('uses DefaultLayout (with sidebar) for routes marked as "default"', async () => {
    const router = buildRouter()
    await router.push('/dashboard')

    const wrapper = mount(App, { global: { plugins: [router, PrimeVue] } })

    expect(wrapper.find('[data-testid="app-sidebar"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Dashboard')
  })
})
