/**
 * Configuración de Vite para el entorno de desarrollo.
 * 
 * Responsabilidad:
 * Configura el soporte para React y define el proxy de desarrollo
 * para redirigir las peticiones con prefijo /api hacia el backend en http://localhost:8000.
 */
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
