/**
 * Componente: CatalogoCursos
 * Responsabilidad:
 * Consume el endpoint del backend (/api/v1/cursos) mediante fetch asíncrono y gestiona
 * los tres estados fundamentales de la interfaz: cargando, error y lista vacía.
 * Utiliza las etiquetas semánticas <section>, <ul> y <li>.
 */

import { useState, useEffect } from 'react'
import { TarjetaCurso } from './TarjetaCurso'

export function CatalogoCursos() {
  const [cursos, setCursos] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function cargarCursos() {
      try {
        setCargando(true)
        setError(null)

        // Hacemos la petición a través del proxy de Vite (/api -> backend:8000)
        const respuesta = await fetch('/api/v1/cursos')

        if (!respuesta.ok) {
          throw new Error(`Error en la respuesta del servidor (código ${respuesta.status})`)
        }

        const datos = await respuesta.json()
        setCursos(datos.items || [])
      } catch (err) {
        setError(err.message || 'Error de conexión con el backend')
      } finally {
        setCargando(false)
      }
    }

    cargarCursos()
  }, [])

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
