<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'

interface Rol {
  id: number
  nombre: string
  descripcion: string | null
}

interface Permiso {
  id: number
  clave: string
  descripcion: string | null
}

interface UsuarioAdmin {
  id: number
  nombre: string
  email: string
  roles: string[]
  totp_habilitado: boolean
}

const roles = ref<Rol[]>([])
const permisos = ref<Permiso[]>([])
const usuarios = ref<UsuarioAdmin[]>([])
const error = ref('')

const nuevoRol = reactive({ nombre: '', descripcion: '' })
const nuevoPermiso = reactive({ clave: '', descripcion: '' })
const asignacionPermiso = reactive({ rolId: '', permisoId: '' })
const asignacionUsuario = reactive({ usuarioId: '', rolId: '' })

async function cargarTodo() {
  error.value = ''
  try {
    const [resRoles, resPermisos, resUsuarios] = await Promise.all([
      api.get('/api/roles'),
      api.get('/api/permisos'),
      api.get('/api/usuarios')
    ])
    roles.value = resRoles.data
    permisos.value = resPermisos.data
    usuarios.value = resUsuarios.data
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'No tienes permiso para ver esta sección.'
  }
}

async function crearRol() {
  if (!nuevoRol.nombre) return
  await api.post('/api/roles', { nombre: nuevoRol.nombre, descripcion: nuevoRol.descripcion || null })
  nuevoRol.nombre = ''
  nuevoRol.descripcion = ''
  await cargarTodo()
}

async function crearPermiso() {
  if (!nuevoPermiso.clave) return
  await api.post('/api/permisos', { clave: nuevoPermiso.clave, descripcion: nuevoPermiso.descripcion || null })
  nuevoPermiso.clave = ''
  nuevoPermiso.descripcion = ''
  await cargarTodo()
}

async function asignarPermisoARol() {
  if (!asignacionPermiso.rolId || !asignacionPermiso.permisoId) return
  await api.post(`/api/roles/${asignacionPermiso.rolId}/permisos/${asignacionPermiso.permisoId}`)
  asignacionPermiso.rolId = ''
  asignacionPermiso.permisoId = ''
}

async function asignarRolAUsuario() {
  if (!asignacionUsuario.usuarioId || !asignacionUsuario.rolId) return
  await api.post(`/api/usuarios/${asignacionUsuario.usuarioId}/roles/${asignacionUsuario.rolId}`)
  asignacionUsuario.usuarioId = ''
  asignacionUsuario.rolId = ''
  await cargarTodo()
}

async function quitarRol(usuarioId: number, nombreRol: string) {
  const rol = roles.value.find((r) => r.nombre === nombreRol)
  if (!rol) return
  await api.delete(`/api/usuarios/${usuarioId}/roles/${rol.id}`)
  await cargarTodo()
}

onMounted(cargarTodo)
</script>

<template>
  <div class="admin">
    <p v-if="error" class="mensaje-error">{{ error }}</p>

    <div class="rejilla">
      <section class="tarjeta">
        <h2>Roles</h2>
        <div class="formulario-en-linea">
          <input v-model="nuevoRol.nombre" placeholder="Nombre del rol" />
          <input v-model="nuevoRol.descripcion" placeholder="Descripción (opcional)" />
          <button type="button" @click="crearRol">Crear</button>
        </div>
        <ul class="lista">
          <li v-for="rol in roles" :key="rol.id">
            <strong>{{ rol.nombre }}</strong>
            <span v-if="rol.descripcion" class="texto-suave"> — {{ rol.descripcion }}</span>
          </li>
        </ul>
      </section>

      <section class="tarjeta">
        <h2>Permisos</h2>
        <div class="formulario-en-linea">
          <input v-model="nuevoPermiso.clave" placeholder="clave:accion" />
          <input v-model="nuevoPermiso.descripcion" placeholder="Descripción (opcional)" />
          <button type="button" @click="crearPermiso">Crear</button>
        </div>
        <ul class="lista">
          <li v-for="permiso in permisos" :key="permiso.id">
            <code>{{ permiso.clave }}</code>
            <span v-if="permiso.descripcion" class="texto-suave"> — {{ permiso.descripcion }}</span>
          </li>
        </ul>
      </section>

      <section class="tarjeta">
        <h2>Asignar permiso a rol</h2>
        <div class="formulario-en-linea">
          <select v-model="asignacionPermiso.rolId">
            <option value="">Rol…</option>
            <option v-for="rol in roles" :key="rol.id" :value="rol.id">{{ rol.nombre }}</option>
          </select>
          <select v-model="asignacionPermiso.permisoId">
            <option value="">Permiso…</option>
            <option v-for="permiso in permisos" :key="permiso.id" :value="permiso.id">{{ permiso.clave }}</option>
          </select>
          <button type="button" @click="asignarPermisoARol">Asignar</button>
        </div>
      </section>

      <section class="tarjeta tarjeta--ancha">
        <h2>Usuarios</h2>
        <div class="formulario-en-linea">
          <select v-model="asignacionUsuario.usuarioId">
            <option value="">Usuario…</option>
            <option v-for="u in usuarios" :key="u.id" :value="u.id">{{ u.nombre }} ({{ u.email }})</option>
          </select>
          <select v-model="asignacionUsuario.rolId">
            <option value="">Rol a asignar…</option>
            <option v-for="rol in roles" :key="rol.id" :value="rol.id">{{ rol.nombre }}</option>
          </select>
          <button type="button" @click="asignarRolAUsuario">Asignar rol</button>
        </div>

        <table class="tabla-usuarios">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Correo</th>
              <th>Roles</th>
              <th>2FA</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in usuarios" :key="u.id">
              <td>{{ u.nombre }}</td>
              <td>{{ u.email }}</td>
              <td>
                <span v-for="rol in u.roles" :key="rol" class="chip-rol">
                  {{ rol }}
                  <button type="button" @click="quitarRol(u.id, rol)">✕</button>
                </span>
                <span v-if="u.roles.length === 0" class="texto-suave">—</span>
              </td>
              <td>{{ u.totp_habilitado ? '✓' : '—' }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  </div>
</template>

<style scoped>
.admin {
  max-width: 1000px;
  margin: 0 auto;
}

.mensaje-error {
  color: var(--color-peligro);
  margin-bottom: 1rem;
}

.rejilla {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

.tarjeta--ancha {
  grid-column: 1 / -1;
}

.tarjeta {
  background: var(--color-panel);
  border: 1px solid var(--color-borde);
  border-radius: var(--radio);
  box-shadow: var(--sombra);
  padding: 1.5rem;
}

.tarjeta h2 {
  font-size: 1.1rem;
  margin-bottom: 0.9rem;
}

.formulario-en-linea {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.formulario-en-linea input,
.formulario-en-linea select {
  flex: 1;
  min-width: 120px;
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--color-borde);
  border-radius: 6px;
  background: var(--color-panel-claro);
  color: var(--color-texto);
  font-size: 0.85rem;
}

.formulario-en-linea button {
  background: var(--color-bronce);
  color: #1a1408;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 0.9rem;
  font-weight: 700;
  font-size: 0.82rem;
}

.lista {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.85rem;
}

.texto-suave {
  color: var(--color-texto-suave);
}

.tabla-usuarios {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.tabla-usuarios th,
.tabla-usuarios td {
  text-align: left;
  padding: 0.55rem 0.5rem;
  border-bottom: 1px solid var(--color-borde);
}

.chip-rol {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: rgba(201, 163, 78, 0.12);
  color: var(--color-bronce);
  border: 1px solid var(--color-bronce);
  border-radius: 10px;
  padding: 0.1rem 0.5rem;
  font-size: 0.72rem;
  margin-right: 0.3rem;
}

.chip-rol button {
  background: none;
  border: none;
  color: var(--color-bronce);
  font-size: 0.65rem;
  padding: 0;
}

@media (max-width: 760px) {
  .rejilla {
    grid-template-columns: 1fr;
  }
}
</style>
