<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUsuarioStore } from '../store/usuario'

const usuario = useUsuarioStore()
const router = useRouter()

const nombre = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const cargando = ref(false)

async function enviar() {
  error.value = ''
  cargando.value = true
  try {
    await usuario.registrar(nombre.value, email.value, password.value)
    router.push({ name: 'panel' })
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'No se pudo completar el registro.'
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <div class="pagina-acceso">
    <form class="tarjeta-acceso" @submit.prevent="enviar">
      <div class="tarjeta-acceso__marca">
        <span class="escudo">B</span>
        <h2>Crear cuenta</h2>
      </div>

      <p class="texto-ayuda">
        El primer usuario registrado en el sistema se vuelve administrador automáticamente.
      </p>

      <label>
        Nombre
        <input v-model="nombre" type="text" required />
      </label>
      <label>
        Correo
        <input v-model="email" type="email" required />
      </label>
      <label>
        Contraseña (mínimo 8 caracteres)
        <input v-model="password" type="password" required minlength="8" />
      </label>

      <p v-if="error" class="mensaje-error">{{ error }}</p>

      <button type="submit" class="boton-principal" :disabled="cargando">
        {{ cargando ? 'Creando cuenta…' : 'Crear cuenta' }}
      </button>

      <RouterLink to="/entrar" class="enlace-registro">Ya tengo cuenta</RouterLink>
    </form>
  </div>
</template>

<style scoped>
.pagina-acceso {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.tarjeta-acceso {
  width: min(380px, 100%);
  background: var(--color-panel);
  border: 1px solid var(--color-borde);
  border-radius: var(--radio);
  box-shadow: var(--sombra);
  padding: 2.25rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.tarjeta-acceso__marca {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.25rem;
}

.escudo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border: 1.5px solid var(--color-bronce);
  border-radius: 6px;
  color: var(--color-bronce);
  font-family: var(--fuente-titulo);
  font-weight: 700;
}

.texto-ayuda {
  font-size: 0.8rem;
  color: var(--color-texto-suave);
  margin: 0 0 0.5rem;
  line-height: 1.4;
}

label {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.82rem;
  color: var(--color-texto-suave);
}

input {
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--color-borde);
  border-radius: 6px;
  background: var(--color-panel-claro);
  color: var(--color-texto);
}

.mensaje-error {
  color: var(--color-peligro);
  font-size: 0.82rem;
  margin: 0;
}

.boton-principal {
  background: var(--color-bronce);
  color: #1a1408;
  border: none;
  border-radius: 6px;
  padding: 0.75rem;
  font-weight: 700;
  margin-top: 0.4rem;
}

.boton-principal:disabled {
  opacity: 0.6;
}

.enlace-registro {
  display: block;
  text-align: center;
  margin-top: 0.5rem;
  font-size: 0.82rem;
}
</style>
