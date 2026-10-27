/**
 * Punto de entrada de la aplicación React (React 19).
 * Responsabilidad:
 * Monta la aplicación en el elemento raíz del DOM e importa los estilos globales.
 */

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { App } from './app/App'
import './estilos/global.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
