/**
 * Componente: CatalogoCursos
 * Responsabilidad:
 * Renderiza la interfaz de catálogo consumiendo el hook useCursos.
 * Gestiona los estados visuales (cargando, error, lista vacía y grilla de cursos)
 * cumpliendo con semántica HTML (<section>, <ul>, <li>) y accesibilidad (ARIA).
 */

import { TarjetaCurso } from './TarjetaCurso'
import { useCursos } from './hooks/useCursos'

export function CatalogoCursos() {
  const { cursos, cargando, error } = useCursos()

  return (
    <section className="seccion-catalogo" id="catalogo" aria-labelledby="titulo-catalogo">
      <header className="seccion-encabezado">
        <h2 id="titulo-catalogo" className="seccion-titulo">
          Catálogo Comunitario de Cursos
        </h2>
        <p className="seccion-bajada">
          Cursos 100% gratuitos y de acceso libre validados por la comunidad.
        </p>
      </header>

      {/* Estado 1: Cargando */}
      {cargando && (
        <p className="estado-mensaje" role="status" aria-live="polite">
          ⏳ Cargando cursos disponibles...
        </p>
      )}

      {/* Estado 2: Error */}
      {error && !cargando && (
        <p className="estado-mensaje estado-mensaje--error" role="alert">
          ⚠️ No se pudieron cargar los cursos: {error}. Asegurate de que el backend esté ejecutándose en el puerto 8000.
        </p>
      )}

      {/* Estado 3: Lista vacía */}
      {!cargando && !error && cursos.length === 0 && (
        <p className="estado-mensaje">
          No hay cursos disponibles en el catálogo en este momento.
        </p>
      )}

      {/* Estado 4: Éxito con datos */}
      {!cargando && !error && cursos.length > 0 && (
        <ul className="grilla-cursos" aria-label="Listado de cursos disponibles">
          {cursos.map((curso) => (
            <li key={curso.id}>
              <TarjetaCurso curso={curso} />
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
