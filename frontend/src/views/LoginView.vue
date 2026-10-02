<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'
import { useUsuarioStore } from '../store/usuario'

const usuario = useUsuarioStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const codigo = ref('')
const loginToken = ref('')
const fase = ref<'credenciales' | 'segundo-factor'>('credenciales')
const error = ref('')
const cargando = ref(false)

async function enviarCredenciales() {
  error.value = ''
  cargando.value = true
  try {
    const { data } = await api.post('/api/auth/login', { email: email.value, password: password.value })
    if (data.requiere_2fa) {
      loginToken.value = data.login_token
      fase.value = 'segundo-factor'
    } else {
      usuario.guardarSesion(data)
      router.push({ name: 'panel' })
    }
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Credenciales inválidas.'
  } finally {
    cargando.value = false
  }
}

async function enviarSegundoFactor() {
  error.value = ''
  cargando.value = true
  try {
    const { data } = await api.post('/api/auth/login/2fa', { login_token: loginToken.value, codigo: codigo.value })
    usuario.guardarSesion(data)
    router.push({ name: 'panel' })
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Código incorrecto.'
  } finally {
    cargando.value = false
  }
}

async function iniciarSsoRedireccion() {
  const { data } = await api.get('/api/sso/iniciar')
  window.location.href = data.url_autorizacion
}
</script>

<template>
  <div class="pagina-acceso">
    <div class="tarjeta-acceso">
      <div class="tarjeta-acceso__marca">
        <span class="escudo">B</span>
        <h2>Bastion</h2>
      </div>

      <form v-if="fase === 'credenciales'" @submit.prevent="enviarCredenciales">
        <label>
          Correo
          <input v-model="email" type="email" required />
        </label>
        <label>
          Contraseña
          <input v-model="password" type="password" required />
        </label>

        <p v-if="error" class="mensaje-error">{{ error }}</p>

        <button type="submit" class="boton-principal" :disabled="cargando">
          {{ cargando ? 'Entrando…' : 'Entrar' }}
        </button>
      </form>

      <form v-else @submit.prevent="enviarSegundoFactor">
        <p class="texto-ayuda">Ingresa el código de 6 dígitos de tu app autenticadora.</p>
        <label>
          Código
          <input v-model="codigo" type="text" inputmode="numeric" maxlength="6" required autofocus />
        </label>

        <p v-if="error" class="mensaje-error">{{ error }}</p>

        <button type="submit" class="boton-principal" :disabled="cargando">
          {{ cargando ? 'Verificando…' : 'Verificar' }}
        </button>
      </form>

      <div v-if="fase === 'credenciales'" class="separador">o</div>

      <button v-if="fase === 'credenciales'" type="button" class="boton-sso" @click="iniciarSsoRedireccion">
        Entrar con proveedor de prueba (SSO)
      </button>

      <RouterLink v-if="fase === 'credenciales'" to="/registro" class="enlace-registro">
        ¿No tienes cuenta? Regístrate
      </RouterLink>
    </div>
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
}

.tarjeta-acceso__marca {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 1.5rem;
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

form {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
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

.texto-ayuda {
  font-size: 0.85rem;
  color: var(--color-texto-suave);
  margin: 0;
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
}

.boton-principal:hover {
  background: var(--color-bronce-oscuro);
}

.boton-principal:disabled {
  opacity: 0.6;
}

.separador {
  text-align: center;
  color: var(--color-texto-suave);
  font-size: 0.78rem;
  margin: 1rem 0;
}

.boton-sso {
  width: 100%;
  background: transparent;
  border: 1px solid var(--color-borde);
  color: var(--color-texto);
  border-radius: 6px;
  padding: 0.7rem;
  font-size: 0.88rem;
}

.boton-sso:hover {
  border-color: var(--color-bronce);
}

.enlace-registro {
  display: block;
  text-align: center;
  margin-top: 1.25rem;
  font-size: 0.82rem;
}
</style>
