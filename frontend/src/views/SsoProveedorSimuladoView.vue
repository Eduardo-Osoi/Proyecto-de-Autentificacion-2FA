<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { API_BASE_URL } from '../api/client'

const route = useRoute()

const email = ref('demo@proveedor-simulado.com')
const nombre = ref('Usuario de Prueba')

function continuar() {
  const params = new URLSearchParams({
    client_id: String(route.query.client_id || ''),
    redirect_uri: String(route.query.redirect_uri || ''),
    state: String(route.query.state || ''),
    email_simulado: email.value,
    nombre_simulado: nombre.value
  })
  window.location.href = `${API_BASE_URL}/mock-idp/autorizar?${params.toString()}`
}
</script>

<template>
  <div class="pagina-proveedor">
    <div class="tarjeta-proveedor">
      <span class="etiqueta-mock">PROVEEDOR SIMULADO — solo para demo</span>
      <h2>Iniciar sesión</h2>
      <p class="texto-ayuda">
        <strong>Bastion</strong> quiere que inicies sesión con esta identidad. En producción esto sería la
        pantalla real de Google, Microsoft o el proveedor que configures.
      </p>

      <label>
        Correo a simular
        <input v-model="email" type="email" />
      </label>
      <label>
        Nombre a simular
        <input v-model="nombre" type="text" />
      </label>

      <button type="button" class="boton-principal" @click="continuar">Continuar y autorizar a Bastion</button>
    </div>
  </div>
</template>

<style scoped>
.pagina-proveedor {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: #0a0a0c;
}

.tarjeta-proveedor {
  width: min(400px, 100%);
  background: #fff;
  color: #1a1a1a;
  border-radius: 10px;
  padding: 2rem;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
}

.etiqueta-mock {
  display: inline-block;
  background: #fef3c7;
  color: #92400e;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  margin-bottom: 0.75rem;
}

.tarjeta-proveedor h2 {
  font-family: 'Inter', sans-serif;
  color: #1a1a1a;
  margin-bottom: 0.5rem;
}

.texto-ayuda {
  font-size: 0.85rem;
  color: #555;
  line-height: 1.5;
  margin-bottom: 1.25rem;
}

label {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.8rem;
  color: #444;
  margin-bottom: 0.9rem;
}

input {
  padding: 0.6rem 0.7rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 0.9rem;
}

.boton-principal {
  width: 100%;
  background: #1a73e8;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.75rem;
  font-weight: 600;
  margin-top: 0.5rem;
}
</style>
