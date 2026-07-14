<script setup lang="ts"></script>

<template>
  <div
    class="flex min-h-screen items-center justify-center bg-background-light px-4 dark:bg-background-dark"
  >
    <div class="w-full max-w-md">
      <div class="mb-8 flex justify-center">
        <span class="text-2xl font-bold text-primary">VeloAI</span>
      </div>
      <div
        class="rounded-lg border border-black/5 bg-surface-light p-8 shadow-sm dark:border-white/10 dark:bg-surface-dark"
      >
        <slot />
      </div>
    </div>
  </div>
</template>
