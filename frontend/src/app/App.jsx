/**
 * Componente: App
 * Responsabilidad:
 * Estructura raíz de la aplicación (layout principal).
 * Ensambla la barra de navegación, el contenido principal (<main>) y el pie de página.
 */

import { BarraNavegacion } from '../compartido/BarraNavegacion'
import { PiePagina } from '../compartido/PiePagina'
import { CatalogoCursos } from '../features/catalogo/CatalogoCursos'

export function App() {
  return (
    <>
      <BarraNavegacion />
      <main className="contenido-principal">
        <CatalogoCursos />
      </main>
      <PiePagina />
    </>
  )
}
