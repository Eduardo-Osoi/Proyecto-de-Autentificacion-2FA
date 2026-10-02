<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useUsuarioStore } from './store/usuario'

const usuario = useUsuarioStore()
const route = useRoute()
const router = useRouter()

function salir() {
  usuario.cerrarSesion()
  router.push({ name: 'entrar' })
}
</script>

<template>
  <div class="app-shell">
    <header v-if="usuario.autenticado && !route.meta.publica" class="barra">
      <RouterLink to="/panel" class="barra__marca">
        <span class="barra__escudo">B</span>
        <h1>Bastion</h1>
      </RouterLink>

      <nav class="barra__nav">
        <RouterLink to="/panel" class="barra__enlace" active-class="barra__enlace--activo">Mi cuenta</RouterLink>
        <RouterLink
          v-if="usuario.tienePermiso('usuarios:administrar') || usuario.tienePermiso('roles:administrar')"
          to="/admin"
          class="barra__enlace"
          active-class="barra__enlace--activo"
        >
          Administración
        </RouterLink>
      </nav>

      <div class="barra__usuario">
        <span>{{ usuario.nombre }}</span>
        <button class="barra__salir" @click="salir">Salir</button>
      </div>
    </header>

    <main class="app-contenido">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.barra {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 1rem 2rem;
  background: var(--color-panel);
  border-bottom: 1px solid var(--color-borde);
}

.barra__marca {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  text-decoration: none;
}

.barra__escudo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: 1.5px solid var(--color-bronce);
  border-radius: 6px;
  color: var(--color-bronce);
  font-family: var(--fuente-titulo);
  font-weight: 700;
}

.barra__marca h1 {
  font-size: 1.2rem;
}

.barra__nav {
  display: flex;
  gap: 1.25rem;
  flex: 1;
}

.barra__enlace {
  text-decoration: none;
  color: var(--color-texto-suave);
  font-weight: 600;
  font-size: 0.9rem;
  padding-bottom: 0.3rem;
  border-bottom: 2px solid transparent;
}

.barra__enlace--activo {
  color: var(--color-bronce);
  border-bottom-color: var(--color-bronce);
}

.barra__usuario {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.88rem;
  color: var(--color-texto-suave);
}

.barra__salir {
  background: transparent;
  border: 1px solid var(--color-borde);
  border-radius: var(--radio);
  padding: 0.4rem 0.8rem;
  color: var(--color-texto);
  font-size: 0.82rem;
}

.barra__salir:hover {
  border-color: var(--color-peligro);
  color: var(--color-peligro);
}

.app-contenido {
  flex: 1;
  padding: 2rem;
}
</style>
