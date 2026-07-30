<script setup lang="ts">
import { Building2, CircleAlert, KeyRound, Loader2, Mail, MessageCircle, User } from 'lucide-vue-next'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import MarketingFooter from '@/components/marketing/MarketingFooter.vue'
import MarketingHeader from '@/components/marketing/MarketingHeader.vue'
import { whatsappLink } from '@/config/contact'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { formatDocumentInput } from '@/utils/mask'

const authStore = useAuthStore()
const themeStore = useThemeStore()
const router = useRouter()

const form = reactive({
  legalName: '',
  document: '',
  adminName: '',
  adminEmail: '',
  password: '',
  passwordConfirmation: '',
})

const documentDisplay = computed({
  get: () => form.document,
  set: (value: string) => {
    form.document = formatDocumentInput(value)
  },
})

// Honeypot: campo nunca preenchido por uma pessoa real (escondido via CSS, fora da ordem
// de tabulação) — se vier preenchido, o backend rejeita a requisição como bot.
const website = ref('')

const isSubmitting = ref(false)
const fieldError = ref<string | null>(null)

const passwordsMatch = computed(
  () => form.password.length === 0 || form.password === form.passwordConfirmation,
)

async function handleSubmit(): Promise<void> {
  fieldError.value = null

  if (website.value) {
    return
  }

  if (form.password.length < 8) {
    fieldError.value = 'A senha precisa ter pelo menos 8 caracteres.'
    return
  }

  if (form.password !== form.passwordConfirmation) {
    fieldError.value = 'As senhas não conferem.'
    return
  }

  isSubmitting.value = true

  const success = await authStore.signup({
    legalName: form.legalName,
    tradeName: null,
    document: form.document,
    adminName: form.adminName,
    adminEmail: form.adminEmail,
    password: form.password,
  })

  isSubmitting.value = false

  if (success) {
    await router.push({ name: 'dashboard' })
  }
}

onMounted(() => {
  themeStore.initialize()
})
</script>

<template>
  <div class="min-h-screen bg-background-light text-text-primary dark:bg-background-dark dark:text-white">
    <MarketingHeader />

    <section class="relative overflow-hidden">
      <div
        class="pointer-events-none absolute -left-32 -top-32 h-96 w-96 rounded-full bg-primary/20 blur-3xl"
      />
      <div
        class="pointer-events-none absolute -right-24 top-40 h-80 w-80 rounded-full bg-info/10 blur-3xl"
      />

      <div class="relative mx-auto max-w-lg px-6 py-16 md:py-20">
        <div class="text-center">
          <div
            class="mx-auto flex h-11 w-11 items-center justify-center rounded-md bg-primary/10 text-primary"
          >
            <Building2 :size="20" />
          </div>
          <h1 class="mt-4 text-3xl font-bold tracking-tight md:text-4xl">Crie sua conta</h1>
          <p class="mt-3 text-text-secondary">
            Leva menos de 2 minutos. 14 dias grátis, sem cartão de crédito — você já sai
            usando o sistema.
          </p>
        </div>

        <form
          class="mt-8 space-y-4 rounded-xl border border-black/5 bg-surface-light p-6 shadow-lg dark:border-white/10 dark:bg-surface-dark"
          @submit.prevent="handleSubmit"
        >
          <div
            v-if="authStore.error || fieldError"
            class="flex items-start gap-2 rounded-md bg-danger/10 px-3 py-2.5 text-sm text-danger"
          >
            <CircleAlert :size="16" class="mt-0.5 shrink-0" />
            <span>{{ fieldError ?? authStore.error }}</span>
          </div>

          <p class="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-text-secondary">
            <Building2 :size="12" />
            Dados da empresa
          </p>

          <div class="space-y-1">
            <label for="signup-legal-name" class="text-sm font-medium text-text-primary dark:text-white">
              Nome da empresa
            </label>
            <input
              id="signup-legal-name"
              v-model="form.legalName"
              type="text"
              required
              minlength="3"
              class="w-full rounded-md border border-black/10 bg-background-light px-3 py-2 text-sm text-text-primary outline-none transition-colors focus:border-primary dark:border-white/15 dark:bg-background-dark dark:text-white"
            />
          </div>

          <div class="space-y-1">
            <label for="signup-document" class="text-sm font-medium text-text-primary dark:text-white">
              CPF/CNPJ
            </label>
            <input
              id="signup-document"
              v-model="documentDisplay"
              type="text"
              inputmode="numeric"
              required
              placeholder="00.000.000/0000-00"
              class="w-full rounded-md border border-black/10 bg-background-light px-3 py-2 text-sm text-text-primary outline-none transition-colors focus:border-primary dark:border-white/15 dark:bg-background-dark dark:text-white"
            />
          </div>

          <div class="h-px bg-black/5 dark:bg-white/10" />

          <p class="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-text-secondary">
            <User :size="12" />
            Seus dados
          </p>

          <div class="space-y-1">
            <label for="signup-admin-name" class="text-sm font-medium text-text-primary dark:text-white">
              Seu nome
            </label>
            <input
              id="signup-admin-name"
              v-model="form.adminName"
              type="text"
              required
              minlength="3"
              class="w-full rounded-md border border-black/10 bg-background-light px-3 py-2 text-sm text-text-primary outline-none transition-colors focus:border-primary dark:border-white/15 dark:bg-background-dark dark:text-white"
            />
          </div>

          <div class="space-y-1">
            <label for="signup-admin-email" class="text-sm font-medium text-text-primary dark:text-white">
              E-mail
            </label>
            <div class="relative">
              <Mail :size="16" class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary" />
              <input
                id="signup-admin-email"
                v-model="form.adminEmail"
                type="email"
                required
                class="w-full rounded-md border border-black/10 bg-background-light py-2 pl-9 pr-3 text-sm text-text-primary outline-none transition-colors focus:border-primary dark:border-white/15 dark:bg-background-dark dark:text-white"
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1">
              <label for="signup-password" class="text-sm font-medium text-text-primary dark:text-white">
                Senha
              </label>
              <div class="relative">
                <KeyRound :size="16" class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary" />
                <input
                  id="signup-password"
                  v-model="form.password"
                  type="password"
                  required
                  minlength="8"
                  class="w-full rounded-md border border-black/10 bg-background-light py-2 pl-9 pr-3 text-sm text-text-primary outline-none transition-colors focus:border-primary dark:border-white/15 dark:bg-background-dark dark:text-white"
                />
              </div>
            </div>
            <div class="space-y-1">
              <label for="signup-password-confirmation" class="text-sm font-medium text-text-primary dark:text-white">
                Confirmar
              </label>
              <input
                id="signup-password-confirmation"
                v-model="form.passwordConfirmation"
                type="password"
                required
                minlength="8"
                class="w-full rounded-md border px-3 py-2 text-sm text-text-primary outline-none transition-colors dark:bg-background-dark dark:text-white"
                :class="
                  passwordsMatch
                    ? 'border-black/10 bg-background-light focus:border-primary dark:border-white/15'
                    : 'border-danger focus:border-danger'
                "
              />
            </div>
          </div>
          <p class="text-xs text-text-secondary">Mínimo de 8 caracteres.</p>

          <!-- Honeypot — invisível e fora da navegação por teclado, só bots preenchem. -->
          <div class="absolute -left-[9999px]" aria-hidden="true">
            <label for="signup-website">Website</label>
            <input id="signup-website" v-model="website" type="text" tabindex="-1" autocomplete="off" />
          </div>

          <button
            type="submit"
            :disabled="isSubmitting"
            class="flex w-full items-center justify-center gap-2 rounded-md bg-primary px-6 py-3 text-sm font-semibold text-white shadow-sm transition-all duration-150 hover:bg-primary-hover hover:shadow-md active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-70"
          >
            <Loader2 v-if="isSubmitting" :size="18" class="animate-spin" />
            {{ isSubmitting ? 'Preparando seu ambiente...' : 'Criar minha conta' }}
          </button>

          <p class="text-center text-xs text-text-secondary">
            Sem cartão de crédito. 14 dias grátis. Cancele quando quiser.
          </p>
        </form>

        <div class="mt-6 text-center">
          <a
            :href="whatsappLink"
            target="_blank"
            rel="noopener"
            class="inline-flex items-center gap-1.5 text-sm text-text-secondary transition-colors hover:text-primary"
          >
            <MessageCircle :size="14" />
            Prefere que a gente te ajude? Chama no WhatsApp
          </a>
        </div>
      </div>
    </section>

    <MarketingFooter />
  </div>
</template>
