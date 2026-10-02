<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import QRCode from 'qrcode'
import { api } from '../api/client'
import { useUsuarioStore } from '../store/usuario'

interface Perfil {
  id: number
  nombre: string
  email: string
  roles: string[]
  permisos: string[]
  totp_habilitado: boolean
}

const usuarioStore = useUsuarioStore()
const perfil = ref<Perfil | null>(null)

const configurando2fa = ref(false)
const secreto2fa = ref('')
const uriOtpauth = ref('')
const codigoConfirmacion = ref('')
const errorConfiguracion = ref('')
const canvasQr = ref<HTMLCanvasElement | null>(null)

const resultadoDemo = ref('')
const errorDemo = ref('')

async function cargarPerfil() {
  const { data } = await api.get('/api/auth/perfil')
  perfil.value = data
}

async function iniciarConfiguracion2fa() {
  errorConfiguracion.value = ''
  const { data } = await api.post('/api/2fa/iniciar-configuracion')
  secreto2fa.value = data.secreto
  uriOtpauth.value = data.uri_otpauth
  configurando2fa.value = true

  await nextTick()
  if (canvasQr.value) {
    QRCode.toCanvas(canvasQr.value, uriOtpauth.value, { width: 200 })
  }
}

async function confirmar2fa() {
  errorConfiguracion.value = ''
  try {
    await api.post('/api/2fa/confirmar', { codigo: codigoConfirmacion.value })
    configurando2fa.value = false
    codigoConfirmacion.value = ''
    await cargarPerfil()
    await usuarioStore.refrescarPermisos()
  } catch (e: any) {
    errorConfiguracion.value = e?.response?.data?.detail || 'Código incorrecto.'
  }
}

async function deshabilitar2fa() {
  await api.post('/api/2fa/deshabilitar')
  await cargarPerfil()
}

async function probarEndpointProtegido() {
  resultadoDemo.value = ''
  errorDemo.value = ''
  try {
    const { data } = await api.get('/api/demo/solo-admins')
    resultadoDemo.value = data.mensaje
  } catch (e: any) {
    errorDemo.value = e?.response?.data?.detail || 'No autorizado.'
  }
}

onMounted(cargarPerfil)
</script>

<template>
  <div class="panel" v-if="perfil">
    <section class="tarjeta">
      <h2>Mi cuenta</h2>
      <p class="dato"><strong>{{ perfil.nombre }}</strong> · {{ perfil.email }}</p>

      <div class="chips">
        <span v-for="rol in perfil.roles" :key="rol" class="chip chip--rol">{{ rol }}</span>
        <span v-if="perfil.roles.length === 0" class="texto-suave">Sin roles asignados todavía.</span>
      </div>

      <p class="etiqueta-seccion">Permisos efectivos</p>
      <div class="chips">
        <code v-for="permiso in perfil.permisos" :key="permiso" class="chip chip--permiso">{{ permiso }}</code>
        <span v-if="perfil.permisos.length === 0" class="texto-suave">Ninguno todavía.</span>
      </div>
    </section>

    <section class="tarjeta">
      <h2>Autenticación de dos factores</h2>

      <div v-if="perfil.totp_habilitado" class="estado-2fa estado-2fa--activo">
        <span>✓ 2FA activado</span>
        <button type="button" class="boton-secundario" @click="deshabilitar2fa">Desactivar</button>
      </div>

      <div v-else-if="!configurando2fa">
        <p class="texto-suave">Protege tu cuenta con un código de tu app autenticadora (Google Authenticator, Authy, etc).</p>
        <button type="button" class="boton-principal" @click="iniciarConfiguracion2fa">Activar 2FA</button>
      </div>

      <div v-else class="configuracion-2fa">
        <p class="texto-suave">Escanea este código con tu app autenticadora, o escribe el secreto manualmente:</p>
        <canvas ref="canvasQr"></canvas>
        <code class="secreto-manual">{{ secreto2fa }}</code>

        <label>
          Código de verificación
          <input v-model="codigoConfirmacion" type="text" inputmode="numeric" maxlength="6" placeholder="000000" />
        </label>

        <p v-if="errorConfiguracion" class="mensaje-error">{{ errorConfiguracion }}</p>

        <button type="button" class="boton-principal" @click="confirmar2fa">Confirmar y activar</button>
      </div>
    </section>

    <section class="tarjeta">
      <h2>Probar autorización</h2>
      <p class="texto-suave">
        Este endpoint requiere el permiso <code>admin:acceso</code>. Solo funcionará si tu cuenta lo tiene.
      </p>
      <button type="button" class="boton-secundario" @click="probarEndpointProtegido">
        Llamar a /api/demo/solo-admins
      </button>
      <p v-if="resultadoDemo" class="mensaje-exito">{{ resultadoDemo }}</p>
      <p v-if="errorDemo" class="mensaje-error">{{ errorDemo }}</p>
    </section>
  </div>
</template>

<style scoped>
.panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 640px;
  margin: 0 auto;
}

.tarjeta {
  background: var(--color-panel);
  border: 1px solid var(--color-borde);
  border-radius: var(--radio);
  box-shadow: var(--sombra);
  padding: 1.75rem;
}

.tarjeta h2 {
  font-size: 1.2rem;
  margin-bottom: 0.75rem;
}

.dato {
  color: var(--color-texto-suave);
  margin: 0 0 1rem;
}

.etiqueta-seccion {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-texto-suave);
  margin: 1.1rem 0 0.5rem;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.chip {
  font-size: 0.78rem;
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  border: 1px solid var(--color-borde);
}

.chip--rol {
  background: rgba(201, 163, 78, 0.12);
  color: var(--color-bronce);
  border-color: var(--color-bronce);
}

.chip--permiso {
  background: var(--color-panel-claro);
  color: var(--color-texto-suave);
}

.texto-suave {
  color: var(--color-texto-suave);
  font-size: 0.85rem;
}

.estado-2fa {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.estado-2fa--activo span {
  color: var(--color-exito);
  font-weight: 600;
}

.boton-principal {
  background: var(--color-bronce);
  color: #1a1408;
  border: none;
  border-radius: 6px;
  padding: 0.65rem 1.2rem;
  font-weight: 700;
  margin-top: 0.75rem;
}

.boton-secundario {
  background: transparent;
  border: 1px solid var(--color-borde);
  color: var(--color-texto);
  border-radius: 6px;
  padding: 0.55rem 1rem;
  font-size: 0.85rem;
}

.boton-secundario:hover {
  border-color: var(--color-peligro);
  color: var(--color-peligro);
}

.configuracion-2fa {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  text-align: center;
}

.secreto-manual {
  background: var(--color-panel-claro);
  padding: 0.4rem 0.7rem;
  border-radius: 4px;
  letter-spacing: 0.05em;
}

.configuracion-2fa label {
  width: 100%;
  max-width: 200px;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.8rem;
  color: var(--color-texto-suave);
}

.configuracion-2fa input {
  padding: 0.6rem;
  border: 1px solid var(--color-borde);
  border-radius: 6px;
  background: var(--color-panel-claro);
  color: var(--color-texto);
  text-align: center;
  font-family: var(--fuente-mono);
  letter-spacing: 0.2em;
  font-size: 1.1rem;
}

.mensaje-error {
  color: var(--color-peligro);
  font-size: 0.82rem;
}

.mensaje-exito {
  color: var(--color-exito);
  font-size: 0.85rem;
}
</style>
