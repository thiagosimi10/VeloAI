import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'
import { type ImportResult, type RawImportResult, mapImportResult } from '@/types/import'

export interface Product {
  id: string
  categoryId: string | null
  supplierId: string | null
  sku: string
  barcode: string | null
  name: string
  description: string | null
  costPrice: number
  salePrice: number
  stock: number
  minimumStock: number | null
  maximumStock: number | null
  unit: string
  weight: number | null
  active: boolean
  margin: number
  marginPercentage: number | null
  createdAt: string
  updatedAt: string
}

export interface ProductFormPayload {
  categoryId?: string | null
  supplierId?: string | null
  sku?: string
  barcode?: string | null
  name: string
  description?: string | null
  costPrice: number
  salePrice: number
  stock?: number
  minimumStock?: number | null
  maximumStock?: number | null
  unit?: string
  weight?: number | null
}

interface RawProduct {
  id: string
  category_id: string | null
  supplier_id: string | null
  sku: string
  barcode: string | null
  name: string
  description: string | null
  cost_price: string
  sale_price: string
  stock: number
  minimum_stock: number | null
  maximum_stock: number | null
  unit: string
  weight: string | null
  active: boolean
  margin: string
  margin_percentage: string | null
  created_at: string
  updated_at: string
}

interface PaginationMeta {
  page: number
  page_size: number
  total: number
  pages: number
}

interface ProductsState {
  items: Product[]
  meta: PaginationMeta
  search: string
  categoryId: string | null
  supplierId: string | null
  page: number
  isLoading: boolean
  error: string | null
}

function toNumber(value: string | null): number | null {
  return value === null ? null : Number(value)
}

function mapProduct(raw: RawProduct): Product {
  return {
    id: raw.id,
    categoryId: raw.category_id,
    supplierId: raw.supplier_id,
    sku: raw.sku,
    barcode: raw.barcode,
    name: raw.name,
    description: raw.description,
    costPrice: Number(raw.cost_price),
    salePrice: Number(raw.sale_price),
    stock: raw.stock,
    minimumStock: raw.minimum_stock,
    maximumStock: raw.maximum_stock,
    unit: raw.unit,
    weight: toNumber(raw.weight),
    active: raw.active,
    margin: Number(raw.margin),
    marginPercentage: toNumber(raw.margin_percentage),
    createdAt: raw.created_at,
    updatedAt: raw.updated_at,
  }
}

function toRawPayload(payload: ProductFormPayload): Record<string, unknown> {
  return {
    category_id: payload.categoryId || null,
    supplier_id: payload.supplierId || null,
    sku: payload.sku,
    barcode: payload.barcode || null,
    name: payload.name,
    description: payload.description || null,
    cost_price: payload.costPrice,
    sale_price: payload.salePrice,
    stock: payload.stock,
    minimum_stock: payload.minimumStock,
    maximum_stock: payload.maximumStock,
    unit: payload.unit,
    weight: payload.weight,
  }
}

function extractErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const message = (error.response?.data as { message?: unknown } | undefined)?.message
    if (typeof message === 'string') {
      return message
    }
  }
  return 'Não foi possível concluir a operação. Tente novamente.'
}

export const useProductsStore = defineStore('products', {
  state: (): ProductsState => ({
    items: [],
    meta: { page: 1, page_size: 20, total: 0, pages: 0 },
    search: '',
    categoryId: null,
    supplierId: null,
    page: 1,
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchProducts(): Promise<void> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.get<{ data: RawProduct[]; meta: PaginationMeta }>(
          '/api/v1/products',
          {
            params: {
              search: this.search || undefined,
              category_id: this.categoryId || undefined,
              supplier_id: this.supplierId || undefined,
              page: this.page,
            },
          },
        )
        this.items = response.data.data.map(mapProduct)
        this.meta = response.data.meta
      } catch (error) {
        this.error = extractErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },

    setSearch(value: string): void {
      this.search = value
      this.page = 1
    },

    setCategoryFilter(value: string | null): void {
      this.categoryId = value
      this.page = 1
    },

    setPage(value: number): void {
      this.page = value
    },

    async getProduct(id: string): Promise<Product | null> {
      try {
        const response = await http.get<{ data: RawProduct }>(`/api/v1/products/${id}`)
        return mapProduct(response.data.data)
      } catch {
        return null
      }
    },

    async createProduct(payload: ProductFormPayload): Promise<Product | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawProduct }>(
          '/api/v1/products',
          toRawPayload(payload),
        )
        return mapProduct(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async updateProduct(id: string, payload: ProductFormPayload): Promise<Product | null> {
      this.error = null
      try {
        const response = await http.patch<{ data: RawProduct }>(
          `/api/v1/products/${id}`,
          toRawPayload(payload),
        )
        return mapProduct(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async deleteProduct(id: string): Promise<boolean> {
      this.error = null
      try {
        await http.delete(`/api/v1/products/${id}`)
        return true
      } catch (error) {
        this.error = extractErrorMessage(error)
        return false
      }
    },

    async importProducts(file: File): Promise<ImportResult | null> {
      this.error = null
      try {
        const formData = new FormData()
        formData.append('file', file)
        const response = await http.post<{ data: RawImportResult }>(
          '/api/v1/products/import',
          formData,
        )
        return mapImportResult(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },
  },
})
