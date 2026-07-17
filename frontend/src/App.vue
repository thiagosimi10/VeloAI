<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import AdminLayout from '@/layouts/AdminLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

const route = useRoute()

const layouts = {
  auth: AuthLayout,
  admin: AdminLayout,
  default: DefaultLayout,
} as const

const layout = computed(() => layouts[(route.meta.layout as keyof typeof layouts) ?? 'default'])
</script>

<template>
  <component :is="layout">
    <router-view />
  </component>
</template>
