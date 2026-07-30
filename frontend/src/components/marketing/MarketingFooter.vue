<script setup lang="ts">
import { BadgeCheck, KeyRound, Mail, MessageCircle, ShieldCheck, Sparkles } from 'lucide-vue-next'

import { LEGAL_ENTITY_CNPJ, LEGAL_ENTITY_NAME, mailtoLink, whatsappLink } from '@/config/contact'

const trustBadges = [
  { icon: ShieldCheck, label: 'Conformidade com a LGPD' },
  { icon: KeyRound, label: 'Senhas com hash Argon2id' },
  { icon: BadgeCheck, label: 'Banco de dados isolado por empresa' },
]

const productLinks = [
  { label: 'Recursos', href: '/#recursos' },
  { label: 'Preços', href: '/#precos' },
  { label: 'Perguntas Frequentes', href: '/#faq' },
]

const legalLinks = [
  { label: 'Política de Privacidade', to: { name: 'privacy-policy' } },
  { label: 'Termos de Uso', to: { name: 'terms-of-service' } },
  { label: 'Política de Cookies', to: { name: 'cookie-policy' } },
]
</script>

<template>
  <footer class="border-t border-black/5 dark:border-white/10">
    <!-- Selos de confiança -->
    <div class="border-b border-black/5 bg-surface-light dark:border-white/10 dark:bg-surface-dark">
      <div
        class="mx-auto flex max-w-6xl flex-col flex-wrap items-center justify-center gap-x-8 gap-y-3 px-6 py-6 text-sm text-text-secondary sm:flex-row"
      >
        <div
          v-for="badge in trustBadges"
          :key="badge.label"
          class="flex items-center gap-2"
        >
          <component :is="badge.icon" :size="16" class="shrink-0 text-primary" />
          <span>{{ badge.label }}</span>
        </div>
      </div>
    </div>

    <!-- Colunas -->
    <div class="mx-auto max-w-6xl px-6 py-12">
      <div class="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <div class="flex items-center gap-2">
            <div
              class="flex h-8 w-8 items-center justify-center rounded-md bg-gradient-to-br from-primary to-primary-active text-white"
            >
              <Sparkles :size="18" />
            </div>
            <span class="text-lg font-bold text-text-primary dark:text-white">VeloAI</span>
          </div>
          <p class="mt-3 text-sm text-text-secondary">
            O sistema de gestão com Inteligência Artificial para empresas que querem crescer com
            organização e segurança.
          </p>
        </div>

        <div>
          <h3 class="text-sm font-semibold text-text-primary dark:text-white">Produto</h3>
          <ul class="mt-3 space-y-2 text-sm text-text-secondary">
            <li v-for="link in productLinks" :key="link.label">
              <a :href="link.href" class="transition-colors hover:text-primary">{{ link.label }}</a>
            </li>
          </ul>
        </div>

        <div>
          <h3 class="text-sm font-semibold text-text-primary dark:text-white">Legal</h3>
          <ul class="mt-3 space-y-2 text-sm text-text-secondary">
            <li v-for="link in legalLinks" :key="link.label">
              <router-link :to="link.to" class="transition-colors hover:text-primary">
                {{ link.label }}
              </router-link>
            </li>
          </ul>
        </div>

        <div>
          <h3 class="text-sm font-semibold text-text-primary dark:text-white">Contato</h3>
          <ul class="mt-3 space-y-2 text-sm text-text-secondary">
            <li>
              <a
                :href="whatsappLink"
                target="_blank"
                rel="noopener"
                class="flex items-center gap-1.5 transition-colors hover:text-primary"
              >
                <MessageCircle :size="14" />
                WhatsApp
              </a>
            </li>
            <li>
              <a :href="mailtoLink" class="flex items-center gap-1.5 transition-colors hover:text-primary">
                <Mail :size="14" />
                E-mail
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div
        class="mt-10 flex flex-col items-center justify-between gap-3 border-t border-black/5 pt-6 text-xs text-text-secondary dark:border-white/10 sm:flex-row"
      >
        <span>© {{ new Date().getFullYear() }} VeloAI. Todos os direitos reservados.</span>
        <span>{{ LEGAL_ENTITY_NAME }} — CNPJ {{ LEGAL_ENTITY_CNPJ }}</span>
      </div>
    </div>
  </footer>
</template>
