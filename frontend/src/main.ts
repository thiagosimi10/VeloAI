import { createPinia } from 'pinia'
import ConfirmationService from 'primevue/confirmationservice'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import { createApp } from 'vue'

import App from '@/App.vue'
import { VeloAIPreset } from '@/plugins/primevue-theme'
import router from '@/router'

import '@/assets/styles/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(PrimeVue, {
  theme: {
    preset: VeloAIPreset,
    options: {
      darkModeSelector: '.dark',
      cssLayer: false,
    },
  },
})
app.use(ToastService)
app.use(ConfirmationService)

// Só monta depois que a navegação inicial resolve — o guard em `router/index.ts` já
// checou a sessão (`/auth/me`) e decidiu a rota final até aqui. Sem isso, o primeiro
// paint mostraria a rota "otimista" (ex.: a casca do app) antes do guard redirecionar
// quem não está logado pro /login.
router.isReady().then(() => {
  app.mount('#app')
})
