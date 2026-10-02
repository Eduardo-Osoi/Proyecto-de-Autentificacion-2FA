<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api/client'
import { useUsuarioStore } from '../store/usuario'

const route = useRoute()
const router = useRouter()
const usuarioStore = useUsuarioStore()
const error = ref('')

onMounted(async () => {
  const token = String(route.query.token || '')
  if (!token) {
    error.value = 'No se recibió un token de sesión.'
    return
  }

  usuarioStore.guardarSesionDesdeToken(token)

  try {
    const { data } = await api.post('/api/auth/refrescar')
    usuarioStore.guardarSesion(data)
    router.push({ name: 'panel' })
  } catch (e) {
    error.value = 'No se pudo completar el inicio de sesión con SSO.'
  }
})
</script>

<template>
  <div class="pagina-completado">
    <p v-if="error" class="mensaje-error">{{ error }}</p>
    <p v-else class="texto-cargando">Completando inicio de sesión…</p>
  </div>
</template>

<style scoped>
.pagina-completado {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-texto-suave);
}

.mensaje-error {
  color: var(--color-peligro);
}
</style>
