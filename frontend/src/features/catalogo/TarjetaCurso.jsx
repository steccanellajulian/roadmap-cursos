/**
 * Componente: TarjetaCurso
 * Responsabilidad:
 * Representa un curso individual en el catálogo comunitario.
 * Utiliza la etiqueta semántica <article> y estructura jerárquica de encabezados (<h3>).
 */

export function TarjetaCurso({ curso }) {
  return (
    <article className="tarjeta-curso">
      {curso.categoria && (
        <span className="tarjeta-categoria">{curso.categoria.nombre}</span>
      )}
      <h3 className="tarjeta-titulo">{curso.titulo}</h3>
      <p className="tarjeta-tema">{curso.tema}</p>

      <ul className="tarjeta-metadatos" aria-label="Detalles del curso">
        <li>👨‍🏫 {curso.docentes}</li>
        <li>📅 Edición {curso.anio_edicion}</li>
        {curso.extiende_certificado && <li>📜 Certificado</li>}
      </ul>

      <a
        href={curso.url}
        target="_blank"
        rel="noopener noreferrer"
        className="tarjeta-enlace"
        aria-label={`Acceder al curso gratuito ${curso.titulo} (abre en nueva pestaña)`}
      >
        Ir al curso gratuito
      </a>
    </article>
  )
}
