/**
 * Componente: BarraNavegacion
 * Responsabilidad:
 * Encabezado principal accesible con el logotipo y enlaces de navegación de la aplicación.
 * Utiliza las etiquetas semánticas <header> y <nav>.
 */

export function BarraNavegacion() {
  return (
    <header className="barra-navegacion">
      <nav className="barra-navegacion-contenido" aria-label="Navegación principal">
        <a href="/" className="logo-sitio">
          <span>📚</span>
          <span>Aprende-Gratis</span>
        </a>
        <ul className="menu-navegacion">
          <li>
            <a href="#catalogo" className="menu-enlace">Catálogo</a>
          </li>
          <li>
            <a href="#roadmaps" className="menu-enlace">Roadmaps</a>
          </li>
        </ul>
      </nav>
    </header>
  )
}
