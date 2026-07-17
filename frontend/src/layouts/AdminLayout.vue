<script setup lang="ts">
import { LogOut } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

import { useAdminAuthStore } from '@/stores/adminAuth'

const adminAuthStore = useAdminAuthStore()
const router = useRouter()

async function handleLogout(): Promise<void> {
  await adminAuthStore.logout()
  await router.push({ name: 'admin-login' })
}
</script>

<template>
  <div class="flex h-screen flex-col overflow-hidden bg-background-light dark:bg-background-dark">
    <header
      class="flex h-16 items-center justify-between border-b border-black/5 bg-surface-light px-6 dark:border-white/10 dark:bg-surface-dark"
    >
      <span class="text-lg font-bold text-primary">VeloAI · Painel Administrativo</span>
      <div class="flex items-center gap-4">
        <span class="text-sm text-text-secondary">{{ adminAuthStore.admin?.email }}</span>
        <button
          type="button"
          data-testid="admin-logout-button"
          class="flex items-center gap-2 rounded-md px-3 py-1.5 text-sm text-text-primary hover:bg-black/5 dark:text-white dark:hover:bg-white/10"
          @click="handleLogout"
        >
          <LogOut :size="16" />
          Sair
        </button>
      </div>
    </header>
    <main class="flex-1 overflow-y-auto p-6">
      <slot />
    </main>
  </div>
</template>
