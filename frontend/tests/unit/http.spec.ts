import MockAdapter from 'axios-mock-adapter'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'

import { http } from '@/services/http'

describe('http interceptor', () => {
  let mock: MockAdapter

  beforeEach(() => {
    mock = new MockAdapter(http)
  })

  afterEach(() => {
    mock.restore()
  })

  it('passes through successful responses unchanged', async () => {
    mock.onGet('/ok').reply(200, { success: true, data: { hello: 'world' } })

    const response = await http.get('/ok')

    expect(response.data.data.hello).toBe('world')
  })

  it('refreshes the session and retries the original request once on a 401', async () => {
    let attempt = 0
    mock.onGet('/protected').reply(() => {
      attempt += 1
      return attempt === 1 ? [401, { message: 'expired' }] : [200, { data: { ok: true } }]
    })
    mock.onPost('/api/v1/auth/refresh').reply(200, { data: {} })

    const response = await http.get('/protected')

    expect(response.data.data.ok).toBe(true)
    expect(attempt).toBe(2)
  })

  it('does not retry more than once for the same request', async () => {
    mock.onGet('/always-401').reply(401, { message: 'expired' })
    mock.onPost('/api/v1/auth/refresh').reply(200, { data: {} })

    await expect(http.get('/always-401')).rejects.toMatchObject({
      response: { status: 401 },
    })
  })

  it('rejects immediately when the refresh call itself fails', async () => {
    mock.onGet('/protected').reply(401, { message: 'expired' })
    mock.onPost('/api/v1/auth/refresh').reply(401, { message: 'refresh expired' })

    await expect(http.get('/protected')).rejects.toMatchObject({
      response: { status: 401 },
    })
  })

  it('never attempts to refresh for the login endpoint itself', async () => {
    mock.onPost('/api/v1/auth/login').reply(401, { message: 'invalid credentials' })

    await expect(http.post('/api/v1/auth/login', {})).rejects.toMatchObject({
      response: { status: 401 },
    })
    expect(mock.history.post?.filter((request) => request.url === '/api/v1/auth/refresh')).toHaveLength(
      0,
    )
  })

  it('rejects non-401 errors without attempting a refresh', async () => {
    mock.onGet('/server-error').reply(500, { message: 'boom' })

    await expect(http.get('/server-error')).rejects.toMatchObject({
      response: { status: 500 },
    })
  })
})
