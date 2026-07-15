import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
}))

// DashboardView.vue importa @amcharts/amcharts5 no topo do módulo — como este arquivo
// reseta os módulos a cada teste (`vi.resetModules()`), navegar para /dashboard força
// o Vue Router a resolver o componente lazy e recarregar a biblioteca real do zero em
// cada teste, o que estourava o timeout padrão do Vitest (5s). Mockar aqui evita a
// recarga pesada sem precisar simular o comportamento interno do gráfico (esta suíte
// nunca monta o componente, só resolve a rota).
vi.mock('@amcharts/amcharts5', () => ({ Root: { new: vi.fn() } }))
vi.mock('@amcharts/amcharts5/xy', () => ({
  XYChart: { new: vi.fn() },
  CategoryAxis: { new: vi.fn() },
  ValueAxis: { new: vi.fn() },
  AxisRendererX: { new: vi.fn() },
  AxisRendererY: { new: vi.fn() },
  LineSeries: { new: vi.fn() },
  ColumnSeries: { new: vi.fn() },
}))
vi.mock('@amcharts/amcharts5/themes/Animated', () => ({ default: { new: vi.fn() } }))

import { http } from '@/services/http'

const FAKE_USER = {
  id: 'user-1',
  email: 'maria@empresa.test',
  first_name: 'Maria',
  last_name: 'Souza',
  role: 'Administrador',
  permissions: ['system.admin'],
  must_change_password: false,
}

describe('router', () => {
  beforeEach(() => {
    // Cada teste precisa de uma instância nova do router (com histórico limpo) — sem
    // isso, navegar para uma rota igual à do teste anterior é tratado como no-op pelo
    // Vue Router e os guards não seriam reexecutados.
    vi.resetModules()
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
  })

  it('redirects to /login when navigating to a protected route while unauthenticated', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('unauthenticated'))

    const router = (await import('@/router')).default
    await router.push('/dashboard')

    expect(router.currentRoute.value.name).toBe('login')
    expect(router.currentRoute.value.query.redirect).toBe('/dashboard')
  })

  it('allows navigating to /dashboard when the session is restored via /auth/me', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: FAKE_USER } })

    const router = (await import('@/router')).default
    await router.push('/dashboard')

    expect(router.currentRoute.value.name).toBe('dashboard')
  })

  it('redirects to /change-password when the user must change their password', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: { ...FAKE_USER, must_change_password: true } },
    })

    const router = (await import('@/router')).default
    await router.push('/dashboard')

    expect(router.currentRoute.value.name).toBe('change-password')
  })

  it('redirects an already authenticated user away from /login', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: FAKE_USER } })

    const router = (await import('@/router')).default
    await router.push('/login')

    expect(router.currentRoute.value.name).toBe('dashboard')
  })

  it('renders the not-found view for unknown paths', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('unauthenticated'))

    const router = (await import('@/router')).default
    await router.push('/rota-que-nao-existe')

    expect(router.currentRoute.value.name).toBe('not-found')
  })
})
