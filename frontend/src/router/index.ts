import { createRouter, createWebHistory } from 'vue-router'
import { useUsuarioStore } from '../store/usuario'

const routes = [
  {
    path: '/',
    redirect: '/entrar'
  },
  {
    path: '/entrar',
    name: 'entrar',
    component: () => import('../views/LoginView.vue'),
    meta: { publica: true }
  },
  {
    path: '/registro',
    name: 'registro',
    component: () => import('../views/RegistroView.vue'),
    meta: { publica: true }
  },
  {
    path: '/panel',
    name: 'panel',
    component: () => import('../views/PanelView.vue')
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('../views/AdminView.vue')
  },
  {
    path: '/sso/proveedor-simulado',
    name: 'sso-proveedor-simulado',
    component: () => import('../views/SsoProveedorSimuladoView.vue'),
    meta: { publica: true }
  },
  {
    path: '/sso/completado',
    name: 'sso-completado',
    component: () => import('../views/SsoCompletadoView.vue'),
    meta: { publica: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const usuario = useUsuarioStore()

  if (!to.meta.publica && !usuario.autenticado) {
    return { name: 'entrar' }
  }

  if (to.meta.publica && usuario.autenticado && (to.name === 'entrar' || to.name === 'registro')) {
    return { name: 'panel' }
  }

  return true
})

export default router
