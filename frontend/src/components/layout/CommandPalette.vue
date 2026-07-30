<script setup lang="ts">
import {
  ArrowDownCircle,
  ArrowUpCircle,
  BookOpen,
  ClipboardList,
  CreditCard,
  LayoutDashboard,
  Package,
  Plus,
  Search,
  ShoppingCart,
  Tag,
  Truck,
  Users,
  Wallet,
  Wrench,
} from 'lucide-vue-next'
import { type Component, computed, nextTick, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const emit = defineEmits<{ close: [] }>()

const router = useRouter()
const query = ref('')
const inputRef = ref<HTMLInputElement | null>(null)
const activeIndex = ref(0)

interface PaletteItem {
  label: string
  routeName: string
  icon: Component
}

// Mesmos destinos do AppSidebar.vue, + atalhos de criação — mantém em sincronia
// manualmente, já que são poucos itens e raramente mudam.
const items: PaletteItem[] = [
  { label: 'Dashboard', routeName: 'dashboard', icon: LayoutDashboard },
  { label: 'Clientes', routeName: 'customers', icon: Users },
  { label: 'Novo Cliente', routeName: 'customers-new', icon: Plus },
  { label: 'Fornecedores', routeName: 'suppliers', icon: Truck },
  { label: 'Novo Fornecedor', routeName: 'suppliers-new', icon: Plus },
  { label: 'Categorias', routeName: 'categories', icon: Tag },
  { label: 'Nova Categoria', routeName: 'categories-new', icon: Plus },
  { label: 'Produtos', routeName: 'products', icon: Package },
  { label: 'Novo Produto', routeName: 'products-new', icon: Plus },
  { label: 'Serviços', routeName: 'services', icon: Wrench },
  { label: 'Novo Serviço', routeName: 'services-new', icon: Plus },
  { label: 'Ordens de Serviço', routeName: 'service-orders', icon: ClipboardList },
  { label: 'Nova Ordem de Serviço', routeName: 'service-orders-new', icon: Plus },
  { label: 'Vendas', routeName: 'sales', icon: ShoppingCart },
  { label: 'Nova Venda', routeName: 'sales-new', icon: Plus },
  { label: 'Contas a Receber', routeName: 'accounts-receivable', icon: ArrowDownCircle },
  { label: 'Contas a Pagar', routeName: 'accounts-payable', icon: ArrowUpCircle },
  { label: 'Fluxo de Caixa', routeName: 'cash-flow', icon: Wallet },
  { label: 'Base de Conhecimento', routeName: 'knowledge', icon: BookOpen },
  { label: 'Assinatura', routeName: 'billing', icon: CreditCard },
]

const filteredItems = computed(() => {
  const normalized = query.value.trim().toLowerCase()
  if (!normalized) {
    return items
  }
  return items.filter((item) => item.label.toLowerCase().includes(normalized))
})

function select(item: PaletteItem): void {
  router.push({ name: item.routeName })
  emit('close')
}

function handleKeydown(event: KeyboardEvent): void {
  if (event.key === 'Escape') {
    emit('close')
  } else if (event.key === 'ArrowDown') {
    event.preventDefault()
    activeIndex.value = Math.min(activeIndex.value + 1, filteredItems.value.length - 1)
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    activeIndex.value = Math.max(activeIndex.value - 1, 0)
  } else if (event.key === 'Enter') {
    const item = filteredItems.value[activeIndex.value]
    if (item) {
      select(item)
    }
  }
}

onMounted(() => {
  void nextTick(() => inputRef.value?.focus())
})
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-start justify-center bg-black/40 pt-24"
    @click.self="emit('close')"
  >
    <div
      class="w-full max-w-lg overflow-hidden rounded-lg border border-black/10 bg-surface-light shadow-xl dark:border-white/10 dark:bg-surface-dark"
    >
      <div class="flex items-center gap-2 border-b border-black/10 px-4 py-3 dark:border-white/10">
        <Search :size="16" class="shrink-0 text-text-secondary" />
        <input
          ref="inputRef"
          v-model="query"
          type="text"
          placeholder="Ir para..."
          class="w-full bg-transparent text-sm text-text-primary outline-none dark:text-white"
          @keydown="handleKeydown"
        />
        <kbd class="shrink-0 rounded bg-black/5 px-1.5 py-0.5 text-xs text-text-secondary dark:bg-white/10">
          Esc
        </kbd>
      </div>
      <ul class="max-h-80 overflow-y-auto p-1.5">
        <li
          v-if="filteredItems.length === 0"
          class="px-3 py-6 text-center text-sm text-text-secondary"
        >
          Nenhum resultado.
        </li>
        <li
          v-for="(item, index) in filteredItems"
          :key="item.routeName"
          class="flex cursor-pointer items-center gap-2.5 rounded-md px-3 py-2 text-sm"
          :class="
            index === activeIndex
              ? 'bg-primary/10 text-primary'
              : 'text-text-primary dark:text-white'
          "
          @mouseenter="activeIndex = index"
          @click="select(item)"
        >
          <component :is="item.icon" :size="16" />
          {{ item.label }}
        </li>
      </ul>
    </div>
  </div>
</template>
