<script setup lang="ts">
import { ShieldCheck } from 'lucide-vue-next'

import LegalPageShell from '@/components/marketing/LegalPageShell.vue'
import {
  CONTACT_EMAIL,
  LEGAL_ENTITY_ADDRESS,
  LEGAL_ENTITY_CNPJ,
  LEGAL_ENTITY_NAME,
} from '@/config/contact'
</script>

<template>
  <LegalPageShell
    :icon="ShieldCheck"
    title="Política de Privacidade"
    subtitle="Como o VeloAI coleta, usa, armazena e protege os dados da sua empresa e dos seus usuários."
    updated-at="24 de julho de 2026"
  >
    <h2>1. Introdução</h2>
    <p>
      Esta Política de Privacidade descreve como o <strong>VeloAI</strong> ("nós", "nosso" ou
      "Plataforma") coleta, utiliza, armazena e protege dados pessoais no contexto do uso do
      nosso sistema de gestão empresarial. Ao criar uma conta ou utilizar o VeloAI, você declara
      estar ciente e de acordo com as práticas aqui descritas, em conformidade com a Lei Geral de
      Proteção de Dados Pessoais (Lei nº 13.709/2018 — LGPD).
    </p>

    <h2>2. Quem somos</h2>
    <p>
      O VeloAI é operado por <strong>{{ LEGAL_ENTITY_NAME }}</strong>, inscrita no CNPJ sob o nº
      <strong>{{ LEGAL_ENTITY_CNPJ }}</strong>, com sede em <strong>{{ LEGAL_ENTITY_ADDRESS }}</strong>,
      atuando como controladora dos dados tratados nesta Plataforma para fins de cadastro,
      cobrança e suporte, e como operadora dos dados inseridos pelas empresas clientes no uso
      cotidiano do sistema (clientes, vendas, financeiro, ordens de serviço, etc.).
    </p>

    <h2>3. Quais dados coletamos</h2>
    <ul>
      <li><strong>Dados de cadastro:</strong> nome, e-mail, telefone e dados da empresa (razão social, CNPJ).</li>
      <li><strong>Dados de acesso:</strong> credenciais de login, endereço IP, data e hora de acesso.</li>
      <li>
        <strong>Dados operacionais inseridos por você:</strong> clientes, fornecedores, produtos,
        serviços, vendas, ordens de serviço e lançamentos financeiros cadastrados dentro do
        sistema.
      </li>
      <li><strong>Dados de comunicação:</strong> mensagens trocadas via WhatsApp, e-mail ou suporte.</li>
      <li><strong>Dados de navegação:</strong> cookies e identificadores de sessão (veja nossa Política de Cookies).</li>
    </ul>

    <h2>4. Como usamos os dados</h2>
    <ul>
      <li>Viabilizar a criação e manutenção da sua conta e do teste gratuito de 14 dias.</li>
      <li>Processar cobranças e gerenciar o plano contratado.</li>
      <li>Fornecer suporte técnico e comercial.</li>
      <li>Melhorar a Plataforma, incluindo as respostas geradas pelo assistente de Inteligência Artificial.</li>
      <li>Cumprir obrigações legais, regulatórias e contratuais.</li>
      <li>Prevenir fraudes e garantir a segurança da Plataforma.</li>
    </ul>

    <h2>5. Base legal para o tratamento</h2>
    <p>
      Tratamos dados pessoais com base na execução de contrato (prestação do serviço contratado),
      no cumprimento de obrigação legal ou regulatória, no legítimo interesse (segurança e
      prevenção a fraudes) e, quando aplicável, no consentimento do titular.
    </p>

    <h2>6. Compartilhamento de dados</h2>
    <p>
      Não vendemos dados pessoais. Dados podem ser compartilhados com prestadores de serviço que
      apoiam a operação da Plataforma (processamento de pagamentos, hospedagem em nuvem e envio de
      comunicações), sempre sob obrigações contratuais de confidencialidade e segurança, ou quando
      exigido por autoridade competente.
    </p>

    <h2>7. Armazenamento e segurança</h2>
    <ul>
      <li>Cada empresa cliente possui um <strong>banco de dados isolado e dedicado</strong>, sem compartilhamento de dados entre empresas.</li>
      <li>Senhas são armazenadas com hash <strong>Argon2id</strong>, nunca em texto plano.</li>
      <li>Sessões de acesso são protegidas por cookies criptografados.</li>
      <li>Adotamos controles técnicos e organizacionais para prevenir acessos não autorizados, perda ou alteração indevida de dados.</li>
    </ul>

    <h2>8. Retenção de dados</h2>
    <p>
      Mantemos os dados pelo tempo necessário para cumprir as finalidades descritas nesta
      Política, o prazo contratual vigente e as obrigações legais aplicáveis. Ao encerrar sua
      conta, você pode solicitar a exclusão dos dados, observados os prazos legais mínimos de
      guarda (por exemplo, obrigações fiscais e contábeis).
    </p>

    <h2>9. Seus direitos como titular de dados</h2>
    <p>Nos termos da LGPD, você pode solicitar, a qualquer momento:</p>
    <ul>
      <li>Confirmação da existência de tratamento e acesso aos dados;</li>
      <li>Correção de dados incompletos, inexatos ou desatualizados;</li>
      <li>Anonimização, bloqueio ou eliminação de dados desnecessários ou tratados em desconformidade com a lei;</li>
      <li>Portabilidade dos dados a outro fornecedor de serviço;</li>
      <li>Eliminação dos dados tratados com base no consentimento;</li>
      <li>Informação sobre entidades com as quais compartilhamos dados;</li>
      <li>Revogação do consentimento, quando aplicável.</li>
    </ul>
    <p>
      Para exercer esses direitos, entre em contato pelo e-mail
      <a :href="`mailto:${CONTACT_EMAIL}`">{{ CONTACT_EMAIL }}</a>.
    </p>

    <h2>10. Cookies</h2>
    <p>
      Utilizamos cookies essenciais para autenticação e preferências de tema. Detalhes completos
      estão na nossa
      <router-link :to="{ name: 'cookie-policy' }">Política de Cookies</router-link>.
    </p>

    <h2>11. Alterações desta política</h2>
    <p>
      Podemos atualizar esta Política periodicamente para refletir melhorias na Plataforma ou
      mudanças legais. A data da última atualização é sempre indicada no topo desta página.
      Alterações relevantes serão comunicadas por e-mail ou aviso no sistema.
    </p>

    <h2>12. Contato</h2>
    <p>
      Dúvidas sobre esta Política ou sobre o tratamento dos seus dados podem ser enviadas para
      <a :href="`mailto:${CONTACT_EMAIL}`">{{ CONTACT_EMAIL }}</a>.
    </p>
  </LegalPageShell>
</template>
