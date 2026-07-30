/** Compartilhado por toda importação em lote (Produtos, Clientes, Fornecedores,
 * Categorias) — mesmo formato do resultado em `app/core/import_result.py` no backend. */

export interface ImportRowNote {
  row: number
  message: string
}

export interface ImportResult {
  totalRows: number
  created: number
  errors: ImportRowNote[]
  warnings: ImportRowNote[]
}

interface RawImportRowNote {
  row: number
  message: string
}

export interface RawImportResult {
  total_rows: number
  created: number
  errors: RawImportRowNote[]
  warnings: RawImportRowNote[]
}

export function mapImportResult(raw: RawImportResult): ImportResult {
  return {
    totalRows: raw.total_rows,
    created: raw.created,
    errors: raw.errors,
    warnings: raw.warnings,
  }
}
