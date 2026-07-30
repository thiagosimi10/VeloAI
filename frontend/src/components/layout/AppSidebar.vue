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
  Zap,
} from 'lucide-vue-next'
import { ref } from 'vue'

import { useAuthStore } from '@/stores/auth'

const STORAGE_KEY = 'veloai:sidebar-collapsed'

const authStore = useAuthStore()
const collapsed = ref(localStorage.getItem(STORAGE_KEY) === 'true')

function toggleCollapsed(): void {
  collapsed.value = !collapsed.value
  localStorage.setItem(STORAGE_KEY, String(collapsed.value))
}

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/customers', icon: Users, label: 'Clientes' },
  { to: '/suppliers', icon: Truck, label: 'Fornecedores' },
  { to: '/categories', icon: Tag, label: 'Categorias' },
  { to: '/products', icon: Package, label: 'Produtos' },
  { to: '/services', icon: Wrench, label: 'Serviços' },
  { to: '/service-orders', icon: ClipboardList, label: 'Ordens de Serviço' },
  { to: '/sales', icon: ShoppingCart, label: 'Vendas' },
  { to: '/accounts-receivable', icon: ArrowDownCircle, label: 'Contas a Receber' },
  { to: '/accounts-payable', icon: ArrowUpCircle, label: 'Contas a Pagar' },
  { to: '/cash-flow', icon: Wallet, label: 'Fluxo de Caixa' },
  { to: '/knowledge', icon: BookOpen, label: 'Base de Conhecimento' },
  { to: '/billing', icon: CreditCard, label: 'Assinatura' },
]
</script>

<template>
  <aside
    class="flex flex-col bg-gradient-to-b from-primary-hover via-primary to-primary-active shadow-xl transition-all duration-150"
    :class="collapsed ? 'w-[72px]' : 'w-[280px]'"
    data-testid="app-sidebar"
  >
    <div class="flex h-16 items-center justify-between border-b border-white/10 px-4">
      <div v-if="!collapsed" class="flex min-w-0 items-center gap-2">
        <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/15">
          <Zap :size="18" class="fill-white text-white" />
        </span>
        <div class="flex min-w-0 flex-col justify-center leading-tight">
          <span class="truncate text-lg font-bold text-white">VeloAI</span>
          <span
            v-if="authStore.user?.tenantName"
            class="truncate text-xs text-white/60"
            :title="authStore.user.tenantName"
          >
            {{ authStore.user.tenantName }}
          </span>
        </div>
      </div>
      <button
        type="button"
        class="rounded-md p-2 text-white/70 hover:bg-white/10 hover:text-white"
        :class="{ 'mx-auto': collapsed }"
        :aria-label="collapsed ? 'Expandir menu' : 'Recolher menu'"
        @click="toggleCollapsed"
      >
        <PanelLeftOpen v-if="collapsed" :size="20" />
        <PanelLeftClose v-else :size="20" />
      </button>
    </div>

    <nav class="flex-1 space-y-1 overflow-y-auto px-2 py-3">
      <router-link
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-white/70 transition-colors duration-150 hover:bg-white/10 hover:text-white"
        active-class="bg-white/15 text-white shadow-sm"
      >
        <component :is="item.icon" :size="20" class="shrink-0" />
        <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
      </router-link>
    </nav>
  </aside>
</template>
