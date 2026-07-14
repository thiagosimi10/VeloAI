import axios from 'axios'

/**
 * Instância única de comunicação com o Backend. O Frontend nunca acessa banco ou IA
 * diretamente — sempre através da API (docs/17-FRONTEND-ARCHITECTURE.md).
 */
export const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true,
})
