<script setup lang="ts">
import { Cookie } from 'lucide-vue-next'

import LegalPageShell from '@/components/marketing/LegalPageShell.vue'
import { CONTACT_EMAIL } from '@/config/contact'
</script>

<template>
  <LegalPageShell
    :icon="Cookie"
    title="Política de Cookies"
    subtitle="Como e por que utilizamos cookies e tecnologias semelhantes no VeloAI."
    updated-at="24 de julho de 2026"
  >
    <h2>1. O que são cookies</h2>
    <p>
      Cookies são pequenos arquivos de texto armazenados no seu navegador quando você visita um
      site ou utiliza uma aplicação web. Eles permitem que a Plataforma reconheça seu dispositivo
      e lembre de informações sobre sua sessão e preferências.
    </p>

    <h2>2. Quais cookies utilizamos</h2>
    <ul>
      <li>
        <strong>Cookies essenciais (estritamente necessários):</strong> usados para manter sua
        sessão autenticada com segurança. Sem eles, não é possível acessar áreas restritas do
        VeloAI. Não podem ser desativados.
      </li>
      <li>
        <strong>Cookies de preferências:</strong> armazenam escolhas como o tema claro/escuro da
        interface, para que não seja necessário reconfigurar a cada acesso.
      </li>
      <li>
        <strong>Cookies de desempenho e análise:</strong> quando utilizados, ajudam a entender
        como a Plataforma é usada, para priorizarmos melhorias. Podem ser desativados sem afetar
        o funcionamento essencial do sistema.
      </li>
    </ul>

    <h2>3. Cookies de terceiros</h2>
    <p>
      Podemos utilizar serviços de terceiros (por exemplo, processadores de pagamento ou
      ferramentas de suporte) que definem seus próprios cookies, sujeitos às respectivas
      políticas de privacidade. Não temos controle direto sobre esses cookies.
    </p>

    <h2>4. Como gerenciar cookies</h2>
    <p>
      Você pode gerenciar ou desativar cookies diretamente nas configurações do seu navegador. A
      desativação de cookies essenciais pode impedir o funcionamento correto do login e de áreas
      protegidas da Plataforma. Consulte a documentação do seu navegador para instruções
      específicas.
    </p>

    <h2>5. Alterações desta política</h2>
    <p>
      Esta Política de Cookies pode ser atualizada periodicamente para refletir mudanças na
      Plataforma ou na legislação aplicável. A data da última atualização é sempre indicada no
      topo desta página.
    </p>

    <h2>6. Contato</h2>
    <p>
      Dúvidas sobre o uso de cookies podem ser enviadas para
      <a :href="`mailto:${CONTACT_EMAIL}`">{{ CONTACT_EMAIL }}</a>. Para mais informações sobre
      como tratamos dados pessoais, consulte nossa
      <router-link :to="{ name: 'privacy-policy' }">Política de Privacidade</router-link>.
    </p>
  </LegalPageShell>
</template>
