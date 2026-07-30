<script setup lang="ts">
import ConfirmDialog from 'primevue/confirmdialog'
import Toast from 'primevue/toast'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import AdminLayout from '@/layouts/AdminLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import MarketingLayout from '@/layouts/MarketingLayout.vue'

const route = useRoute()

const layouts = {
  auth: AuthLayout,
  admin: AdminLayout,
  default: DefaultLayout,
  marketing: MarketingLayout,
} as const

// Fallback nunca é 'default' (o layout com sidebar/menu do app) — enquanto a
// navegação inicial ainda não resolveu (guard de autenticação em `router/index.ts`
// ainda checando a sessão), mostrar a casca do app seria vazar a interface interna
// pra quem nem logou ainda.
const layout = computed(() => layouts[(route.meta.layout as keyof typeof layouts) ?? 'auth'])
</script>

<template>
  <Toast position="top-right" />
  <ConfirmDialog />
  <component :is="layout">
    <router-view />
  </component>
</template>
