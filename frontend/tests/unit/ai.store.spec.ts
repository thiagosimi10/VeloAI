import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'
import { useAiStore } from '@/stores/ai'

const RAW_ASK_AI_RESPONSE = {
  response: 'Você vendeu R$ 12.340,00 em maio.',
  model: 'gemini-3.1-flash-lite',
  tokens: 60,
  execution_time: '1.234',
  cached: false,
  estimated_cost: '0.0000120',
}

describe('ai store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.post).mockReset()
  })

  it('askAI sends the prompt and maps the response', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_ASK_AI_RESPONSE } })
    const store = useAiStore()

    const result = await store.askAI('Quanto vendi em maio?')

    expect(http.post).toHaveBeenCalledWith('/api/v1/ai/ask', { prompt: 'Quanto vendi em maio?' })
    expect(result?.response).toBe('Você vendeu R$ 12.340,00 em maio.')
    expect(result?.tokens).toBe(60)
    expect(store.lastResult?.model).toBe('gemini-3.1-flash-lite')
  })

  it('askAI returns null and sets error on failure', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(new Error('failed'))
    const store = useAiStore()

    const result = await store.askAI('Quanto vendi em maio?')

    expect(result).toBeNull()
    expect(store.error).not.toBeNull()
  })

  it('toggles isLoading while the request is in flight', async () => {
    let resolveRequest: (value: unknown) => void = () => {}
    vi.mocked(http.post).mockReturnValueOnce(
      new Promise((resolve) => {
        resolveRequest = resolve
      }) as never,
    )
    const store = useAiStore()

    const pending = store.askAI('Quanto vendi em maio?')
    expect(store.isLoading).toBe(true)

    resolveRequest({ data: { data: RAW_ASK_AI_RESPONSE } })
    await pending

    expect(store.isLoading).toBe(false)
  })
})
