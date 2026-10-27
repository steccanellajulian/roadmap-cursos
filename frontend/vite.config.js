/**
 * Configuración de Vite para el entorno de desarrollo.
 * 
 * Responsabilidad:
 * Configura el soporte para React y define el proxy de desarrollo
 * para redirigir las peticiones con prefijo /api hacia el backend (TRD TD-009).
 * Permite usar BACKEND_URL en Docker Compose o por defecto http://localhost:8000 en local.
 */
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.BACKEND_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
