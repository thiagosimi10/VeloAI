<script setup lang="ts">
import {
  ArrowDownCircle,
  ArrowUpCircle,
  BookOpen,
  ClipboardList,
  CreditCard,
  LayoutDashboard,
  Package,
  PanelLeftClose,
  PanelLeftOpen,
  ShoppingCart,
  Tag,
  Truck,
  Users,
  Wallet,
  Wrench,
} from 'lucide-vue-next'
import { ref } from 'vue'

const STORAGE_KEY = 'veloai:sidebar-collapsed'

const collapsed = ref(localStorage.getItem(STORAGE_KEY) === 'true')

function toggleCollapsed(): void {
  collapsed.value = !collapsed.value
  localStorage.setItem(STORAGE_KEY, String(collapsed.value))
}
</script>

<template>
  <aside
    class="flex flex-col border-r border-black/5 bg-surface-light transition-all duration-150 dark:border-white/10 dark:bg-surface-dark"
    :class="collapsed ? 'w-[72px]' : 'w-[280px]'"
    data-testid="app-sidebar"
  >
    <div class="flex h-16 items-center justify-between px-4">
      <span v-if="!collapsed" class="truncate text-lg font-bold text-primary">VeloAI</span>
      <button
        type="button"
        class="rounded-md p-2 text-text-secondary hover:bg-black/5 dark:hover:bg-white/10"
        :aria-label="collapsed ? 'Expandir menu' : 'Recolher menu'"
        @click="toggleCollapsed"
      >
        <PanelLeftOpen v-if="collapsed" :size="20" />
        <PanelLeftClose v-else :size="20" />
      </button>
    </div>

    <nav class="flex-1 space-y-1 px-2">
      <router-link
        to="/dashboard"
        class="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-text-secondary hover:bg-black/5 dark:hover:bg-white/10"
        active-class="bg-primary/10 text-primary"
      >
        <LayoutDashboard :size="20" />
        <span v-if="!collapsed">Dashboard</span>
      </router-link>

      <router-link
        to="/customers"
        class="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-text-secondary hover:bg-black/5 dark:hover:bg-white/10"
        active-class="bg-primary/10 text-primary"
      >
        <Users :size="20" />
        <span v-if="!collapsed">Clientes</span>
      </router-link>

      <router-link
        to="/suppliers"
        class="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-text-secondary hover:bg-black/5 dark:hover:bg-white/10"
        active-class="bg-primary/10 text-primary"
      >
        <Truck :size="20" />
        <span v-if="!collapsed">Fornecedores</span>
      </router-link>

      <router-link
        to="/categories"
        class="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-text-secondary hover:bg-black/5 dark:hover:bg-white/10"
        active-class="bg-primary/10 text-primary"
      >
        <Tag :size="20" />
        <span v-if="!collapsed">Categorias</span>
      </router-link>

      <router-link
        to="/products"
        class="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-text-secondary hover:bg-black/5 dark:hover:bg-white/10"
        active-class="bg-primary/10 text-primary"
      >
        <Package :size="20" />
        <span v-if="!collapsed">Produtos</span>
      </router-link>

      <router-link
        to="/services"
        class="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-text-secondary hover:bg-black/5 dark:hover:bg-white/10"
        active-class="bg-primary/10 text-primary"
      >
        <Wrench :size="20" />
        <span v-if="!collapsed">Serviços</span>
      </router-link>

      <router-link
        to="/service-orders"
        class="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-text-secondary hover:bg-black/5 dark:hover:bg-white/10"
        active-class="bg-primary/10 text-primary"
      >
        <ClipboardList :size="20" />
        <span v-if="!collapsed">Ordens de Serviço</span>
      </router-link>

      <router-link
        to="/sales"
        class="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-text-secondary hover:bg-black/5 dark:hover:bg-white/10"
        active-class="bg-primary/10 text-primary"
      >
        <ShoppingCart :size="20" />
        <span v-if="!collapsed">Vendas</span>
      </router-link>

      <router-link
        to="/accounts-receivable"
        class="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-text-secondary hover:bg-black/5 dark:hover:bg-white/10"
        active-class="bg-primary/10 text-primary"
      >
        <ArrowDownCircle :size="20" />
        <span v-if="!collapsed">Contas a Receber</span>
      </router-link>

      <router-link
        to="/accounts-payable"
        class="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-text-secondary hover:bg-black/5 dark:hover:bg-white/10"
        active-class="bg-primary/10 text-primary"
      >
        <ArrowUpCircle :size="20" />
        <span v-if="!collapsed">Contas a Pagar</span>
      </router-link>

      <router-link
        to="/cash-flow"
        class="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-text-secondary hover:bg-black/5 dark:hover:bg-white/10"
        active-class="bg-primary/10 text-primary"
      >
        <Wallet :size="20" />
        <span v-if="!collapsed">Fluxo de Caixa</span>
      </router-link>

      <router-link
        to="/knowledge"
        class="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-text-secondary hover:bg-black/5 dark:hover:bg-white/10"
        active-class="bg-primary/10 text-primary"
      >
        <BookOpen :size="20" />
        <span v-if="!collapsed">Base de Conhecimento</span>
      </router-link>

      <router-link
        to="/billing"
        class="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-text-secondary hover:bg-black/5 dark:hover:bg-white/10"
        active-class="bg-primary/10 text-primary"
      >
        <CreditCard :size="20" />
        <span v-if="!collapsed">Assinatura</span>
      </router-link>
    </nav>
  </aside>
</template>
