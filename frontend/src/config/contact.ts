// Placeholder — trocar pelo número real de WhatsApp comercial antes de divulgar o link.
export const WHATSAPP_NUMBER = '(019) 99186-9983'
export const CONTACT_EMAIL = 'thiagosimi10@gmail.com'

// Identificação da pessoa jurídica que opera o VeloAI — usada no rodapé e nas páginas
// legais (Termos de Uso, Política de Privacidade).
export const LEGAL_ENTITY_NAME = 'Dominus Dev'
export const LEGAL_ENTITY_CNPJ = '31.248.227/0001-84'
export const LEGAL_ENTITY_ADDRESS = 'Rua Maria Belini Fachini, 381 — Araras/SP'
export const LEGAL_ENTITY_FORUM = 'Araras/SP'

const WHATSAPP_DEFAULT_MESSAGE = encodeURIComponent(
  'Olá! Quero conhecer o VeloAI e testar por 14 dias grátis.',
)

export function buildWhatsappLink(message: string = WHATSAPP_DEFAULT_MESSAGE): string {
  return `https://wa.me/${WHATSAPP_NUMBER}?text=${message}`
}

export function buildMailtoLink(subject: string): string {
  return `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(subject)}`
}

export const whatsappLink = buildWhatsappLink()
export const mailtoLink = buildMailtoLink('Quero conhecer o VeloAI')
