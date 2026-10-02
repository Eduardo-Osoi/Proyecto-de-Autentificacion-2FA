import axios from 'axios'
import { useUsuarioStore } from '../store/usuario'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8030'

export const api = axios.create({
  baseURL: API_BASE_URL
})

api.interceptors.request.use((config) => {
  const usuario = useUsuarioStore()
  if (usuario.token) {
    config.headers.Authorization = `Bearer ${usuario.token}`
  }
  return config
})
