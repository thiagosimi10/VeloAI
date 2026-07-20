<script setup lang="ts">
import { Building2, LogOut, ShieldCheck } from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'

import { useAdminAuthStore } from '@/stores/adminAuth'

const adminAuthStore = useAdminAuthStore()
const router = useRouter()
const route = useRoute()

async function handleLogout(): Promise<void> {
  await adminAuthStore.logout()
  await router.push({ name: 'admin-login' })
}

const navItems = [{ name: 'admin-tenants', label: 'Empresas', icon: Building2 }]

function initials(email: string | undefined): string {
  return (email ?? '?').slice(0, 2).toUpperCase()
}
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-background-light dark:bg-background-dark">
    <aside
      class="flex w-64 shrink-0 flex-col border-r border-black/5 bg-surface-light dark:border-white/10 dark:bg-surface-dark"
    >
      <div class="flex h-16 items-center gap-2.5 border-b border-black/5 px-6 dark:border-white/10">
        <div
          class="flex h-8 w-8 items-center justify-center rounded-md bg-gradient-to-br from-primary to-primary-active text-white shadow-sm"
        >
          <ShieldCheck :size="18" />
        </div>
        <div class="leading-tight">
          <p class="text-sm font-bold text-text-primary dark:text-white">VeloAI</p>
          <p class="text-[11px] text-text-secondary">Painel Administrativo</p>
        </div>
      </div>

      <nav class="flex-1 space-y-1 p-3">
        <button
          v-for="item in navItems"
          :key="item.name"
          type="button"
          class="relative flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
          :class="
            route.name === item.name
              ? 'bg-primary/10 text-primary'
              : 'text-text-secondary hover:bg-black/5 hover:text-text-primary dark:hover:bg-white/10 dark:hover:text-white'
          "
          @click="router.push({ name: item.name })"
        >
          <span
            v-if="route.name === item.name"
            class="absolute inset-y-1 left-0 w-0.5 rounded-full bg-primary"
          />
          <component :is="item.icon" :size="18" />
          {{ item.label }}
        </button>
      </nav>

      <div class="border-t border-black/5 p-3 dark:border-white/10">
        <div class="flex items-center gap-3 rounded-md px-3 py-2">
          <div
            class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary"
          >
            {{ initials(adminAuthStore.admin?.email) }}
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate text-xs font-medium text-text-primary dark:text-white">
              {{ adminAuthStore.admin?.email }}
            </p>
            <p class="text-[11px] text-text-secondary">Operador da plataforma</p>
          </div>
          <button
            type="button"
            aria-label="Sair"
            data-testid="admin-logout-button"
            class="rounded-md p-1.5 text-text-secondary transition-colors hover:bg-danger/10 hover:text-danger focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-danger/40"
            @click="handleLogout"
          >
            <LogOut :size="16" />
          </button>
        </div>
      </div>
    </aside>

    <main class="flex-1 overflow-y-auto">
      <div class="mx-auto max-w-6xl p-8">
        <Transition
          mode="out-in"
          enter-active-class="transition duration-150 ease-out"
          enter-from-class="opacity-0 translate-y-1"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition duration-100 ease-in"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
        >
          <slot />
        </Transition>
      </div>
    </main>
  </div>
</template>
