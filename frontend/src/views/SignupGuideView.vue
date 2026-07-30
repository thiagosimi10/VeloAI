<script setup lang="ts">
import {
  Check,
  CircleCheck,
  Mail,
  MessageCircle,
  Rocket,
  Sparkles,
} from 'lucide-vue-next'
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import MarketingFooter from '@/components/marketing/MarketingFooter.vue'
import MarketingHeader from '@/components/marketing/MarketingHeader.vue'
import { mailtoLink, whatsappLink } from '@/config/contact'
import { useBillingStore } from '@/stores/billing'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
const billingStore = useBillingStore()
const router = useRouter()

const monthlyPrice = computed(() => {
  const monthly = billingStore.planTiers.find((tier) => tier.cycle === 'MONTHLY')
  return monthly
    ? Number(monthly.monthlyPrice).toLocaleString('pt-BR', { minimumFractionDigits: 2 })
    : '129,90'
})

const steps = [
  {
    title: 'Preencha o formulário',
    description:
      'Nome da empresa, CNPJ/CPF, seus dados e uma senha — leva menos de 2 minutos.',
  },
  {
    title: 'Seu ambiente é criado na hora',
    description:
      'Banco de dados isolado e exclusivo para a sua empresa, pronto em segundos. Sem instalação, sem complicação.',
  },
  {
    title: 'Você já sai usando, com 14 dias grátis',
    description:
      'Acesso completo a todos os módulos, sem pedir cartão de crédito e sem nenhuma cobrança nesse período.',
  },
  {
    title: 'Decide se quer continuar',
    description:
      'Gostou? Segue no plano Professional. Não é pra você? Cancela sem multa e sem perguntas.',
  },
]

function goToSignup(): void {
  router.push({ name: 'signup' })
}

const reassurances = [
  'Sem cartão de crédito para começar',
  'Sem fidelidade e sem multa de cancelamento',
  'Banco de dados isolado e dedicado para a sua empresa',
  'Suporte humano pelo WhatsApp durante todo o teste',
]

onMounted(() => {
  themeStore.initialize()
  void billingStore.fetchPublicPlanTiers()
})
</script>

<template>
  <div class="min-h-screen bg-background-light text-text-primary dark:bg-background-dark dark:text-white">
    <MarketingHeader />

    <!-- Hero -->
    <section class="relative overflow-hidden">
      <div
        class="pointer-events-none absolute -left-32 -top-32 h-96 w-96 rounded-full bg-primary/20 blur-3xl"
      />
      <div
        class="pointer-events-none absolute -right-24 top-40 h-80 w-80 rounded-full bg-info/10 blur-3xl"
      />

      <div class="relative mx-auto max-w-3xl px-6 py-20 text-center md:py-24">
        <span
          class="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary"
        >
          <Sparkles :size="12" />
          Cadastro simples, você mesmo cria sua conta
        </span>
        <h1 class="mt-4 text-4xl font-bold leading-tight tracking-tight md:text-5xl">
          Comece a usar o VeloAI hoje mesmo
        </h1>
        <p class="mx-auto mt-5 max-w-xl text-lg text-text-secondary">
          Sem cartão de crédito. Preencha o formulário, seu ambiente é criado na hora e
          você já sai usando, com <strong class="text-text-primary dark:text-white">14 dias grátis</strong>
          pra testar à vontade.
        </p>

        <div class="mt-8 flex flex-wrap justify-center gap-3">
          <button
            type="button"
            class="flex items-center gap-2 rounded-md bg-primary px-6 py-3 text-sm font-semibold text-white shadow-sm transition-all duration-150 hover:bg-primary-hover hover:shadow-md active:scale-[0.98]"
            @click="goToSignup"
          >
            <Rocket :size="18" />
            Criar minha conta agora
          </button>
          <a
            :href="whatsappLink"
            target="_blank"
            rel="noopener"
            class="flex items-center gap-2 rounded-md border border-black/10 px-6 py-3 text-sm font-semibold text-text-primary transition-colors hover:bg-black/5 dark:border-white/15 dark:text-white dark:hover:bg-white/10"
          >
            <MessageCircle :size="18" />
            Prefiro falar com alguém
          </a>
        </div>

        <p class="mt-4 text-xs text-text-secondary">
          Leva menos de 2 minutos. Precisa de ajuda? Resposta rápida no WhatsApp.
        </p>
      </div>
    </section>

    <!-- Como funciona -->
    <section class="border-y border-black/5 bg-surface-light py-20 dark:border-white/10 dark:bg-surface-dark">
      <div class="mx-auto max-w-5xl px-6">
        <div class="mx-auto max-w-2xl text-center">
          <h2 class="text-3xl font-bold tracking-tight md:text-4xl">Como funciona o seu cadastro</h2>
          <p class="mt-3 text-text-secondary">
            Quatro passos simples, sem burocracia, pra sua empresa começar a usar o VeloAI.
          </p>
        </div>

        <div class="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div
            v-for="(step, index) in steps"
            :key="step.title"
            class="relative rounded-lg border border-black/5 bg-background-light p-6 shadow-sm dark:border-white/10 dark:bg-background-dark"
          >
            <span
              class="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary"
            >
              {{ index + 1 }}
            </span>
            <h3 class="mt-4 font-semibold text-text-primary dark:text-white">{{ step.title }}</h3>
            <p class="mt-1.5 text-sm text-text-secondary">{{ step.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Preço e garantias -->
    <section class="mx-auto max-w-2xl px-6 py-20 text-center">
      <h2 class="text-3xl font-bold tracking-tight md:text-4xl">Um plano simples, sem pegadinha</h2>
      <p class="mt-3 text-text-secondary">
        É só isso que você vai pagar — depois dos 14 dias grátis, se quiser continuar.
      </p>

      <div
        class="relative mt-10 rounded-xl border-2 border-primary bg-surface-light p-8 text-left shadow-lg dark:bg-surface-dark"
      >
        <span
          class="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-primary px-3 py-1 text-xs font-semibold text-white"
        >
          14 dias grátis, sem cartão
        </span>

        <p class="text-sm font-medium text-text-secondary">VeloAI Professional</p>
        <p class="mt-1 flex items-baseline gap-1">
          <span class="text-4xl font-bold text-text-primary dark:text-white">R$ {{ monthlyPrice }}</span>
          <span class="text-text-secondary">/mês</span>
        </p>
        <p class="mt-1 text-xs text-text-secondary">
          Cobrado somente depois do período de teste, e só se você decidir continuar.
        </p>

        <ul class="mt-6 space-y-3 text-sm">
          <li v-for="reassurance in reassurances" :key="reassurance" class="flex items-center gap-2">
            <Check :size="16" class="shrink-0 text-success" />
            {{ reassurance }}
          </li>
        </ul>

        <button
          type="button"
          class="mt-8 flex w-full items-center justify-center gap-2 rounded-md bg-primary px-6 py-3 text-sm font-semibold text-white shadow-sm transition-all duration-150 hover:bg-primary-hover hover:shadow-md active:scale-[0.98]"
          @click="goToSignup"
        >
          <Rocket :size="18" />
          Quero Começar Agora
        </button>
      </div>
    </section>

    <!-- Ajuda -->
    <section class="mx-auto max-w-4xl px-6 pb-24">
      <div
        class="flex flex-col items-center gap-4 rounded-xl bg-gradient-to-br from-primary to-primary-active p-12 text-center text-white shadow-lg"
      >
        <CircleCheck :size="32" />
        <h2 class="text-2xl font-bold md:text-3xl">Ficou com alguma dúvida?</h2>
        <p class="max-w-md text-white/80">
          Fala com a gente pelo WhatsApp — te ajudamos em cada passo do cadastro, sem enrolação.
        </p>
        <div class="mt-2 flex flex-wrap justify-center gap-3">
          <a
            :href="whatsappLink"
            target="_blank"
            rel="noopener"
            class="flex items-center gap-2 rounded-md bg-white px-6 py-3 text-sm font-semibold text-primary shadow-sm transition-transform active:scale-[0.98]"
          >
            <MessageCircle :size="18" />
            Chamar no WhatsApp
          </a>
          <a
            :href="mailtoLink"
            class="flex items-center gap-2 rounded-md border border-white/40 px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-white/10"
          >
            <Mail :size="18" />
            Enviar E-mail
          </a>
        </div>
      </div>
    </section>

    <MarketingFooter />
  </div>
</template>
