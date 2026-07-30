<script setup lang="ts">
import type { Component } from 'vue'

import MarketingFooter from '@/components/marketing/MarketingFooter.vue'
import MarketingHeader from '@/components/marketing/MarketingHeader.vue'

defineProps<{
  icon: Component
  title: string
  subtitle: string
  updatedAt: string
}>()
</script>

<template>
  <div class="min-h-screen bg-background-light text-text-primary dark:bg-background-dark dark:text-white">
    <MarketingHeader />

    <section class="border-b border-black/5 bg-surface-light py-14 dark:border-white/10 dark:bg-surface-dark">
      <div class="mx-auto max-w-3xl px-6">
        <div
          class="flex h-11 w-11 items-center justify-center rounded-md bg-primary/10 text-primary"
        >
          <component :is="icon" :size="20" />
        </div>
        <h1 class="mt-4 text-3xl font-bold tracking-tight md:text-4xl">{{ title }}</h1>
        <p class="mt-3 text-text-secondary">{{ subtitle }}</p>
        <p class="mt-2 text-xs text-text-secondary">Última atualização: {{ updatedAt }}</p>
      </div>
    </section>

    <article class="legal-content mx-auto max-w-3xl px-6 py-14">
      <slot />
    </article>

    <MarketingFooter />
  </div>
</template>

<style scoped>
.legal-content :deep(h2) {
  margin-top: 2.5rem;
  margin-bottom: 0.75rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: rgb(17 24 39);
}

:global(.dark) .legal-content :deep(h2) {
  color: rgb(255 255 255);
}

.legal-content :deep(h2:first-child) {
  margin-top: 0;
}

.legal-content :deep(p) {
  margin-bottom: 1rem;
  font-size: 0.9375rem;
  line-height: 1.7;
  color: #6b7280;
}

.legal-content :deep(ul) {
  margin-bottom: 1rem;
  list-style-type: disc;
  padding-left: 1.25rem;
  font-size: 0.9375rem;
  line-height: 1.7;
  color: #6b7280;
}

.legal-content :deep(li) {
  margin-bottom: 0.375rem;
}

.legal-content :deep(strong) {
  font-weight: 600;
  color: rgb(17 24 39);
}

:global(.dark) .legal-content :deep(strong) {
  color: rgb(255 255 255);
}

.legal-content :deep(a) {
  color: #6d28d9;
  text-decoration: underline;
  text-underline-offset: 2px;
}

/* #6D28D9 tem contraste baixo sobre o fundo escuro (#0F172A) em texto corrido — usa o
   mesmo tom mais claro (primary.400) já presente na paleta estendida do preset PrimeVue
   (src/plugins/primevue-theme.ts) para links legíveis no modo escuro. */
:global(.dark) .legal-content :deep(a) {
  color: #a78bfa;
}
</style>
