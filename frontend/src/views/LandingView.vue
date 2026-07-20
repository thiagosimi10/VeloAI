<script setup lang="ts">
import {
  Banknote,
  Bot,
  Boxes,
  Check,
  ClipboardList,
  Handshake,
  LayoutDashboard,
  Lock,
  Mail,
  MessageCircle,
  Moon,
  ShieldCheck,
  Sparkles,
  Sun,
  Users,
  Wrench,
} from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

const authStore = useAuthStore()
const themeStore = useThemeStore()
const router = useRouter()

// Placeholder — trocar pelo número real de WhatsApp comercial antes de divulgar o link.
const WHATSAPP_NUMBER = '5500000000000'
const CONTACT_EMAIL = 'thiagosimi10@gmail.com'
const WHATSAPP_MESSAGE = encodeURIComponent(
  'Olá! Quero conhecer o VeloAI e testar por 14 dias grátis.',
)
const whatsappLink = `https://wa.me/${WHATSAPP_NUMBER}?text=${WHATSAPP_MESSAGE}`
const mailtoLink = `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent('Quero conhecer o VeloAI')}`

const features = [
  {
    icon: Users,
    title: 'CRM Completo',
    description: 'Clientes, fornecedores, categorias, produtos e serviços em um só lugar.',
  },
  {
    icon: Wrench,
    title: 'Ordens de Serviço',
    description: 'Do orçamento à execução, com histórico completo de cada atendimento.',
  },
  {
    icon: Handshake,
    title: 'Vendas',
    description: 'Registre vendas e acompanhe o desempenho comercial em tempo real.',
  },
  {
    icon: Banknote,
    title: 'Financeiro Completo',
    description: 'Contas a pagar, a receber e fluxo de caixa — sem planilha, sem retrabalho.',
  },
  {
    icon: LayoutDashboard,
    title: 'Dashboard Inteligente',
    description: 'Indicadores do seu negócio organizados para decisões rápidas.',
  },
  {
    icon: Bot,
    title: 'Inteligência Artificial',
    description: 'Assistente de IA que entende o seu negócio e responde perguntas sobre ele.',
  },
]

const pillars = [
  {
    icon: Boxes,
    title: 'Tudo integrado',
    description:
      'Vendas, financeiro, estoque e atendimento conversam entre si — sem exportar planilha de um sistema pra outro.',
  },
  {
    icon: Sparkles,
    title: 'Potencializado por IA',
    description:
      'Relatórios e respostas geradas por IA a partir dos dados reais da sua empresa, sem esforço manual.',
  },
  {
    icon: Lock,
    title: 'Seguro por padrão',
    description:
      'Cada empresa tem seu próprio banco de dados isolado, senhas com hash Argon2id e sessões criptografadas.',
  },
]

const faqs = ref([
  {
    question: 'Preciso de cartão de crédito para testar?',
    answer: 'Não. O teste de 14 dias é liberado assim que sua empresa é configurada, sem cobrança antecipada.',
    open: false,
  },
  {
    question: 'Posso cancelar quando quiser?',
    answer:
      'Sim. O cancelamento é feito diretamente no sistema, a qualquer momento, sem burocracia e sem multa.',
    open: false,
  },
  {
    question: 'Meus dados ficam seguros e isolados?',
    answer:
      'Sim. Cada empresa possui seu próprio banco de dados dedicado — os dados de uma empresa nunca são acessíveis por outra.',
    open: false,
  },
  {
    question: 'Quantos usuários posso cadastrar?',
    answer:
      'O plano Professional cobre toda a operação da sua empresa. Fale com a gente para necessidades específicas de volume.',
    open: false,
  },
])

function toggleFaq(index: number): void {
  const faq = faqs.value[index]
  if (faq) {
    faq.open = !faq.open
  }
}

function goToLogin(): void {
  router.push({ name: 'login' })
}

function goToDashboard(): void {
  router.push({ name: 'dashboard' })
}

onMounted(() => {
  themeStore.initialize()
})
</script>

<template>
  <div class="min-h-screen bg-background-light text-text-primary dark:bg-background-dark dark:text-white">
    <!-- Header -->
    <header
      class="sticky top-0 z-40 border-b border-black/5 bg-surface-light/80 backdrop-blur dark:border-white/10 dark:bg-surface-dark/80"
    >
      <div class="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <div class="flex items-center gap-2">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-md bg-gradient-to-br from-primary to-primary-active text-white"
          >
            <Sparkles :size="18" />
          </div>
          <span class="text-lg font-bold text-text-primary dark:text-white">VeloAI</span>
        </div>

        <nav class="hidden items-center gap-6 text-sm font-medium text-text-secondary md:flex">
          <a href="#recursos" class="transition-colors hover:text-primary">Recursos</a>
          <a href="#precos" class="transition-colors hover:text-primary">Preços</a>
          <a href="#faq" class="transition-colors hover:text-primary">Perguntas Frequentes</a>
        </nav>

        <div class="flex items-center gap-2">
          <button
            type="button"
            aria-label="Alternar tema"
            class="rounded-md p-2 text-text-secondary transition-colors hover:bg-black/5 dark:hover:bg-white/10"
            @click="themeStore.toggle()"
          >
            <Moon v-if="themeStore.mode === 'light'" :size="18" />
            <Sun v-else :size="18" />
          </button>
          <button
            v-if="authStore.isAuthenticated"
            type="button"
            class="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-hover"
            @click="goToDashboard"
          >
            Ir para o Painel
          </button>
          <button
            v-else
            type="button"
            class="rounded-md px-3 py-2 text-sm font-medium text-text-secondary transition-colors hover:text-primary"
            @click="goToLogin"
          >
            Entrar
          </button>
        </div>
      </div>
    </header>

    <!-- Hero -->
    <section class="relative overflow-hidden">
      <div
        class="pointer-events-none absolute -left-32 -top-32 h-96 w-96 rounded-full bg-primary/20 blur-3xl"
      />
      <div
        class="pointer-events-none absolute -right-24 top-40 h-80 w-80 rounded-full bg-info/10 blur-3xl"
      />

      <div class="relative mx-auto max-w-6xl px-6 py-20 md:py-28">
        <div class="grid items-center gap-12 md:grid-cols-2">
          <div>
            <span
              class="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary"
            >
              <Sparkles :size="12" />
              Gestão com Inteligência Artificial
            </span>
            <h1 class="mt-4 text-4xl font-bold leading-tight tracking-tight md:text-5xl">
              O sistema de gestão que a sua empresa merece.
            </h1>
            <p class="mt-5 text-lg text-text-secondary">
              Clientes, vendas, financeiro e ordens de serviço em uma única plataforma —
              organizada, segura e com Inteligência Artificial trabalhando pra você.
            </p>

            <div class="mt-8 flex flex-wrap gap-3">
              <a
                :href="whatsappLink"
                target="_blank"
                rel="noopener"
                class="flex items-center gap-2 rounded-md bg-primary px-6 py-3 text-sm font-semibold text-white shadow-sm transition-all duration-150 hover:bg-primary-hover hover:shadow-md active:scale-[0.98]"
              >
                <MessageCircle :size="18" />
                Testar Grátis por 14 Dias
              </a>
              <a
                :href="mailtoLink"
                class="flex items-center gap-2 rounded-md border border-black/10 px-6 py-3 text-sm font-semibold text-text-primary transition-colors hover:bg-black/5 dark:border-white/15 dark:text-white dark:hover:bg-white/10"
              >
                <Mail :size="18" />
                Falar por E-mail
              </a>
            </div>

            <p class="mt-4 text-xs text-text-secondary">
              Sem cartão de crédito. Sem fidelidade. Cancele quando quiser.
            </p>
          </div>

          <!-- Mockup ilustrativo do dashboard -->
          <div class="relative">
            <div
              class="rounded-xl border border-black/5 bg-surface-light p-5 shadow-xl dark:border-white/10 dark:bg-surface-dark"
            >
              <div class="mb-4 flex items-center gap-1.5">
                <span class="h-2.5 w-2.5 rounded-full bg-danger/60" />
                <span class="h-2.5 w-2.5 rounded-full bg-warning/60" />
                <span class="h-2.5 w-2.5 rounded-full bg-success/60" />
              </div>
              <div class="grid grid-cols-3 gap-3">
                <div class="rounded-lg bg-primary/10 p-3">
                  <p class="text-[10px] text-text-secondary">Faturamento</p>
                  <p class="text-lg font-semibold text-primary">R$ 48.2k</p>
                </div>
                <div class="rounded-lg bg-success/10 p-3">
                  <p class="text-[10px] text-text-secondary">Vendas</p>
                  <p class="text-lg font-semibold text-success">312</p>
                </div>
                <div class="rounded-lg bg-info/10 p-3">
                  <p class="text-[10px] text-text-secondary">Clientes</p>
                  <p class="text-lg font-semibold text-info">1.4k</p>
                </div>
              </div>
              <div class="mt-4 space-y-2 rounded-lg border border-black/5 p-3 dark:border-white/10">
                <div class="flex items-end gap-1.5">
                  <div class="h-10 w-6 rounded bg-primary/30" />
                  <div class="h-16 w-6 rounded bg-primary/50" />
                  <div class="h-8 w-6 rounded bg-primary/30" />
                  <div class="h-20 w-6 rounded bg-primary" />
                  <div class="h-14 w-6 rounded bg-primary/60" />
                  <div class="h-24 w-6 rounded bg-primary" />
                  <div class="h-12 w-6 rounded bg-primary/40" />
                </div>
              </div>
              <div class="mt-4 flex items-center gap-2 rounded-lg bg-black/5 p-3 dark:bg-white/5">
                <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary text-white">
                  <Bot :size="14" />
                </div>
                <p class="text-xs text-text-secondary">
                  "Suas vendas cresceram 18% este mês. Quer um resumo detalhado?"
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Pilares -->
    <section class="border-y border-black/5 bg-surface-light py-16 dark:border-white/10 dark:bg-surface-dark">
      <div class="mx-auto max-w-6xl px-6">
        <div class="grid gap-8 md:grid-cols-3">
          <div v-for="pillar in pillars" :key="pillar.title" class="text-center md:text-left">
            <div
              class="mx-auto flex h-11 w-11 items-center justify-center rounded-md bg-primary/10 text-primary md:mx-0"
            >
              <component :is="pillar.icon" :size="20" />
            </div>
            <h3 class="mt-3 text-base font-semibold text-text-primary dark:text-white">
              {{ pillar.title }}
            </h3>
            <p class="mt-1.5 text-sm text-text-secondary">{{ pillar.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Recursos -->
    <section id="recursos" class="mx-auto max-w-6xl px-6 py-20">
      <div class="mx-auto max-w-2xl text-center">
        <h2 class="text-3xl font-bold tracking-tight md:text-4xl">
          Tudo que sua empresa precisa, em um só sistema
        </h2>
        <p class="mt-3 text-text-secondary">
          Chega de sistemas soltos, planilhas paralelas e informação espalhada.
        </p>
      </div>

      <div class="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="feature in features"
          :key="feature.title"
          class="rounded-lg border border-black/5 bg-surface-light p-6 shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:shadow-md dark:border-white/10 dark:bg-surface-dark"
        >
          <div class="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 text-primary">
            <component :is="feature.icon" :size="20" />
          </div>
          <h3 class="mt-4 font-semibold text-text-primary dark:text-white">{{ feature.title }}</h3>
          <p class="mt-1.5 text-sm text-text-secondary">{{ feature.description }}</p>
        </div>
      </div>
    </section>

    <!-- Preços -->
    <section id="precos" class="border-y border-black/5 bg-surface-light py-20 dark:border-white/10 dark:bg-surface-dark">
      <div class="mx-auto max-w-2xl px-6 text-center">
        <h2 class="text-3xl font-bold tracking-tight md:text-4xl">Um plano simples e completo</h2>
        <p class="mt-3 text-text-secondary">
          Sem letras miúdas. Sem módulo escondido atrás de outro plano.
        </p>

        <div
          class="relative mt-10 rounded-xl border-2 border-primary bg-background-light p-8 text-left shadow-lg dark:bg-background-dark"
        >
          <span
            class="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-primary px-3 py-1 text-xs font-semibold text-white"
          >
            14 dias grátis
          </span>

          <p class="text-sm font-medium text-text-secondary">VeloAI Professional</p>
          <p class="mt-1 flex items-baseline gap-1">
            <span class="text-4xl font-bold text-text-primary dark:text-white">R$ 129,90</span>
            <span class="text-text-secondary">/mês</span>
          </p>

          <ul class="mt-6 space-y-3 text-sm">
            <li class="flex items-center gap-2">
              <Check :size="16" class="shrink-0 text-success" />
              CRM completo (clientes, fornecedores, produtos e serviços)
            </li>
            <li class="flex items-center gap-2">
              <Check :size="16" class="shrink-0 text-success" />
              Ordens de serviço e vendas
            </li>
            <li class="flex items-center gap-2">
              <Check :size="16" class="shrink-0 text-success" />
              Financeiro completo (contas a pagar, a receber e fluxo de caixa)
            </li>
            <li class="flex items-center gap-2">
              <Check :size="16" class="shrink-0 text-success" />
              Dashboard e assistente de Inteligência Artificial
            </li>
            <li class="flex items-center gap-2">
              <Check :size="16" class="shrink-0 text-success" />
              Banco de dados isolado e dedicado para a sua empresa
            </li>
            <li class="flex items-center gap-2">
              <Check :size="16" class="shrink-0 text-success" />
              Cancele quando quiser, sem multa
            </li>
          </ul>

          <a
            :href="whatsappLink"
            target="_blank"
            rel="noopener"
            class="mt-8 flex items-center justify-center gap-2 rounded-md bg-primary px-6 py-3 text-sm font-semibold text-white shadow-sm transition-all duration-150 hover:bg-primary-hover hover:shadow-md active:scale-[0.98]"
          >
            <MessageCircle :size="18" />
            Começar Teste Grátis
          </a>
        </div>
      </div>
    </section>

    <!-- FAQ -->
    <section id="faq" class="mx-auto max-w-3xl px-6 py-20">
      <h2 class="text-center text-3xl font-bold tracking-tight md:text-4xl">
        Perguntas Frequentes
      </h2>

      <div class="mt-10 space-y-3">
        <div
          v-for="(faq, index) in faqs"
          :key="faq.question"
          class="rounded-lg border border-black/5 bg-surface-light shadow-sm dark:border-white/10 dark:bg-surface-dark"
        >
          <button
            type="button"
            class="flex w-full items-center justify-between px-5 py-4 text-left text-sm font-medium text-text-primary dark:text-white"
            @click="toggleFaq(index)"
          >
            {{ faq.question }}
            <span
              class="ml-4 shrink-0 text-text-secondary transition-transform duration-150"
              :class="{ 'rotate-45': faq.open }"
            >
              +
            </span>
          </button>
          <div v-show="faq.open" class="px-5 pb-4 text-sm text-text-secondary">
            {{ faq.answer }}
          </div>
        </div>
      </div>
    </section>

    <!-- CTA final -->
    <section class="mx-auto max-w-4xl px-6 pb-24">
      <div
        class="flex flex-col items-center gap-4 rounded-xl bg-gradient-to-br from-primary to-primary-active p-12 text-center text-white shadow-lg"
      >
        <ShieldCheck :size="32" />
        <h2 class="text-2xl font-bold md:text-3xl">Pronto para organizar sua empresa?</h2>
        <p class="max-w-md text-white/80">
          Fale com a gente agora e comece seu teste gratuito de 14 dias, sem compromisso.
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

    <!-- Footer -->
    <footer class="border-t border-black/5 py-8 dark:border-white/10">
      <div
        class="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 text-sm text-text-secondary md:flex-row"
      >
        <div class="flex items-center gap-2">
          <ClipboardList :size="14" />
          <span>© {{ new Date().getFullYear() }} VeloAI. Todos os direitos reservados.</span>
        </div>
        <a :href="mailtoLink" class="hover:text-primary">{{ CONTACT_EMAIL }}</a>
      </div>
    </footer>
  </div>
</template>
