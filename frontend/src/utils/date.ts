/**
 * Conversão entre `Date` (usado pelo PrimeVue DatePicker) e strings `YYYY-MM-DD`
 * (formato que a API espera/retorna) — sempre a partir dos componentes locais de
 * ano/mês/dia, nunca via `toISOString()`, que usa UTC e pode deslocar o dia conforme o
 * fuso horário do navegador.
 */

export function dateToIsoString(value: Date | null): string {
  if (!value) {
    return ''
  }
  const year = value.getFullYear()
  const month = String(value.getMonth() + 1).padStart(2, '0')
  const day = String(value.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function isoStringToDate(value: string): Date | null {
  if (!value) {
    return null
  }
  return new Date(`${value}T00:00:00`)
}
