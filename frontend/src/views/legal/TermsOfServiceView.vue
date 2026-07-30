<script setup lang="ts">
import { FileText } from 'lucide-vue-next'

import LegalPageShell from '@/components/marketing/LegalPageShell.vue'
import { CONTACT_EMAIL, LEGAL_ENTITY_FORUM, LEGAL_ENTITY_NAME } from '@/config/contact'
</script>

<template>
  <LegalPageShell
    :icon="FileText"
    title="Termos de Uso"
    subtitle="Regras e condições para uso da plataforma VeloAI."
    updated-at="24 de julho de 2026"
  >
    <h2>1. Aceitação dos termos</h2>
    <p>
      Estes Termos de Uso regulam o acesso e a utilização do sistema de gestão empresarial
      <strong>VeloAI</strong>, disponibilizado por <strong>{{ LEGAL_ENTITY_NAME }}</strong>
      ("VeloAI", "nós"). Ao criar uma conta ou utilizar a Plataforma, você ("Cliente" ou
      "usuário") concorda integralmente com estes Termos e com a nossa
      <router-link :to="{ name: 'privacy-policy' }">Política de Privacidade</router-link>.
    </p>

    <h2>2. Descrição do serviço</h2>
    <p>
      O VeloAI é uma plataforma em nuvem (SaaS) que oferece módulos de CRM, ordens de serviço,
      vendas, financeiro, dashboard e um assistente de Inteligência Artificial, para apoiar a
      gestão de empresas de pequeno e médio porte.
    </p>

    <h2>3. Cadastro e conta</h2>
    <ul>
      <li>Para usar o VeloAI, é necessário criar uma conta com informações verdadeiras, completas e atualizadas.</li>
      <li>Você é responsável por manter a confidencialidade das suas credenciais de acesso.</li>
      <li>Você é responsável por todas as atividades realizadas na sua conta e pelos usuários que convidar.</li>
    </ul>

    <h2>4. Teste gratuito de 14 dias</h2>
    <p>
      Novos clientes têm acesso a um período de teste gratuito de 14 dias, sem necessidade de
      cartão de crédito. Ao final do período de teste, a continuidade do uso está condicionada à
      contratação de um plano pago. Não há cobrança automática ao término do teste sem
      confirmação prévia do cliente.
    </p>

    <h2>5. Planos e pagamento</h2>
    <ul>
      <li>Os valores, condições e recursos de cada plano estão descritos na página de preços da Plataforma.</li>
      <li>O pagamento é processado de forma recorrente (mensal), conforme o plano contratado.</li>
      <li>Reajustes de preço serão informados com antecedência mínima de 30 dias.</li>
      <li>O não pagamento pode acarretar suspensão temporária do acesso até a regularização.</li>
    </ul>

    <h2>6. Cancelamento e reembolso</h2>
    <p>
      O cancelamento pode ser solicitado a qualquer momento, diretamente pelo sistema ou pelos
      nossos canais de atendimento, sem multa ou fidelidade. Valores já pagos referentes a
      períodos não utilizados poderão ser reembolsados a critério do VeloAI, salvo disposição
      legal em contrário.
    </p>

    <h2>7. Uso aceitável</h2>
    <p>Ao utilizar o VeloAI, você concorda em não:</p>
    <ul>
      <li>Utilizar a Plataforma para fins ilícitos, fraudulentos ou que violem direitos de terceiros;</li>
      <li>Tentar acessar áreas, dados ou contas de outras empresas sem autorização;</li>
      <li>Realizar engenharia reversa, copiar ou revender a Plataforma sem autorização expressa;</li>
      <li>Sobrecarregar ou comprometer a infraestrutura do sistema (ex.: ataques automatizados).</li>
    </ul>

    <h2>8. Propriedade intelectual</h2>
    <p>
      Todo o software, marca, layout, funcionalidades e demais elementos do VeloAI são de
      propriedade exclusiva de <strong>{{ LEGAL_ENTITY_NAME }}</strong> ou de seus licenciantes,
      protegidos pela legislação de propriedade intelectual aplicável. Nenhuma cláusula destes
      Termos transfere ao Cliente qualquer direito sobre o software.
    </p>

    <h2>9. Titularidade dos seus dados</h2>
    <p>
      Todos os dados operacionais inseridos por você na Plataforma (clientes, vendas, financeiro,
      ordens de serviço, etc.) permanecem de propriedade da sua empresa. O VeloAI atua como
      operador desses dados, podendo exportá-los ou excluí-los mediante solicitação, conforme
      nossa <router-link :to="{ name: 'privacy-policy' }">Política de Privacidade</router-link>.
    </p>

    <h2>10. Disponibilidade do serviço</h2>
    <p>
      Envidamos esforços comercialmente razoáveis para manter a Plataforma disponível de forma
      contínua. No entanto, podem ocorrer interrupções programadas para manutenção ou eventos
      fora do nosso controle razoável. Sempre que possível, manutenções programadas serão
      comunicadas com antecedência.
    </p>

    <h2>11. Limitação de responsabilidade</h2>
    <p>
      O VeloAI não se responsabiliza por decisões de negócio tomadas com base nos dados ou
      relatórios gerados pela Plataforma, incluindo respostas do assistente de Inteligência
      Artificial, que possuem caráter de apoio e não substituem julgamento profissional. Na
      máxima extensão permitida por lei, nossa responsabilidade limita-se aos valores pagos pelo
      Cliente nos 12 meses anteriores ao evento gerador do dano.
    </p>

    <h2>12. Rescisão</h2>
    <p>
      Podemos suspender ou encerrar contas que violem estes Termos, mediante notificação prévia
      sempre que possível. Você pode encerrar sua conta a qualquer momento, conforme descrito na
      seção "Cancelamento e reembolso".
    </p>

    <h2>13. Alterações destes Termos</h2>
    <p>
      Estes Termos podem ser atualizados periodicamente. Alterações relevantes serão comunicadas
      por e-mail ou aviso no sistema, com a data da última atualização sempre indicada no topo
      desta página.
    </p>

    <h2>14. Legislação aplicável e foro</h2>
    <p>
      Estes Termos são regidos pelas leis da República Federativa do Brasil. Fica eleito o foro
      da comarca de <strong>{{ LEGAL_ENTITY_FORUM }}</strong> para dirimir eventuais controvérsias,
      com renúncia a qualquer outro, por mais privilegiado que seja.
    </p>

    <h2>15. Contato</h2>
    <p>
      Dúvidas sobre estes Termos podem ser enviadas para
      <a :href="`mailto:${CONTACT_EMAIL}`">{{ CONTACT_EMAIL }}</a>.
    </p>
  </LegalPageShell>
</template>
