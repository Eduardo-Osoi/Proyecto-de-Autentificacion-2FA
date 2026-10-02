import { defineStore } from 'pinia'
import { api } from '../api/client'

interface DatosSesion {
  token: string
  usuario_id: number
  nombre: string
  roles: string[]
  permisos: string[]
}

export const useUsuarioStore = defineStore('usuario', {
  state: () => ({
    token: localStorage.getItem('bastion_token') || '',
    usuarioId: Number(localStorage.getItem('bastion_usuario_id')) || 0,
    nombre: localStorage.getItem('bastion_nombre') || '',
    roles: JSON.parse(localStorage.getItem('bastion_roles') || '[]') as string[],
    permisos: JSON.parse(localStorage.getItem('bastion_permisos') || '[]') as string[]
  }),

  getters: {
    autenticado: (state) => Boolean(state.token),
    tienePermiso: (state) => (clave: string) => state.permisos.includes(clave)
  },

  actions: {
    guardarSesion(sesion: DatosSesion) {
      this.token = sesion.token
      this.usuarioId = sesion.usuario_id
      this.nombre = sesion.nombre
      this.roles = sesion.roles
      this.permisos = sesion.permisos

      localStorage.setItem('bastion_token', sesion.token)
      localStorage.setItem('bastion_usuario_id', String(sesion.usuario_id))
      localStorage.setItem('bastion_nombre', sesion.nombre)
      localStorage.setItem('bastion_roles', JSON.stringify(sesion.roles))
      localStorage.setItem('bastion_permisos', JSON.stringify(sesion.permisos))
    },

    async registrar(nombre: string, email: string, password: string) {
      const { data } = await api.post('/api/auth/registro', { nombre, email, password })
      this.guardarSesion(data)
    },

    async refrescarPermisos() {
      const { data } = await api.post('/api/auth/refrescar')
      this.guardarSesion(data)
    },

    guardarSesionDesdeToken(token: string) {
      this.token = token
      localStorage.setItem('bastion_token', token)
    },

    cerrarSesion() {
      this.token = ''
      this.usuarioId = 0
      this.nombre = ''
      this.roles = []
      this.permisos = []
      localStorage.removeItem('bastion_token')
      localStorage.removeItem('bastion_usuario_id')
      localStorage.removeItem('bastion_nombre')
      localStorage.removeItem('bastion_roles')
      localStorage.removeItem('bastion_permisos')
    }
  }
})
