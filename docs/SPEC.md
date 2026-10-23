# SPEC — WebApp de Gestión de Comunidad de Cursos

> **Entregada al alumno el 21/10/2026.**
> Esta SPEC es **intencionalmente breve e incompleta**: una SPEC de cliente real no llega cerrada.
> Parte de tu trabajo en el PRD es detectar los vacíos, tomar decisiones y documentarlas.

## Producto

Una webapp donde una comunidad de estudiantes construye **en conjunto** un catálogo de cursos
gratuitos y gestiona su aprendizaje con **roadmaps personales**.

### Funcionalidades principales

1. **Roadmap personal**: cada usuario crea y gestiona su propio roadmap de cursos.
2. **Aporte de cursos**: el usuario carga cursos gratuitos de cualquier plataforma o proveedor,
   indicando su enlace web activo y, como mínimo:
   - categoría / rubro (seleccionado de una lista)
   - tema
   - título
   - versión
   - año de edición
   - docentes o disertantes que lo imparten
   - ¿cuenta con cuestionarios?
   - ¿requiere examen?
   - ¿extiende certificado?
   - ¿lo avala una organización?
3. **Declaración de toma**: quien aporta un curso declara si él o ella lo tomó o no.
4. **Catálogo comunitario**: todo curso aportado y **validado** pasa al catálogo comunitario;
   desde allí, cualquier usuario puede incluirlo en su catálogo / roadmap personal.
5. **Cuenta de usuario y autenticación**:
   - registro de usuario;
   - login;
   - recuperación de contraseña (ciclo completo: solicitud → enlace/token → nueva contraseña);
   - protección del **login con rate limiting** (como mínimo en el endpoint de login);
   - contraseñas cifradas con **bcrypt como mínimo** (se puede elegir un algoritmo más fuerte
     si se justifica en el TRD).

## Stack tecnológico (fijo)

| Capa         | Tecnología          | Versión                                      |
| ------------ | ------------------- | -------------------------------------------- |
| Frontend     | React + Vite + pnpm | React 19 (última stable)                     |
| Backend      | FastAPI + uv        | última stable (ref. 21/10/2026: `0.158.2`)   |
| Base de datos | PostgreSQL         | **18.6** (versión actual stable)             |
| Infra (dev)  | Docker + Compose    | última stable                                |

> Registrá en tu TRD la versión exacta que resuelvas instalar.

## Indicaciones técnicas (buenas prácticas obligatorias)

1. **Mobile-first con mejora progresiva** (*Progressive Enhancement*):
   estilos base **sin media queries**; a partir de ahí, `@media (min-width: ...)` **únicamente**
   para agregar o mejorar a medida que la pantalla crece (nunca para “arreglar” lo base).
2. **Paginación** de todas las consultas de listado y de sus tablas en pantalla.
3. **Menú sándwich** en mobile.
4. **Screaming Architecture**: la estructura de carpetas debe comunicar el **dominio del negocio**,
   no el framework que usás.
5. **Apariencia y experiencia inspiradas en Google**: estética limpia tipo Material — mucho espacio
   en blanco, jerarquía tipográfica clara, azul primario de Google, sombras sutiles, bordes
   redondeados, componentes con estados definidos. La guía visual completa (UX-UI) debe reflejar
   esa inspiración con valores concretos, no con adjetivos.

## Fuera de esta SPEC (lo definís vos en la documentación del TP)

Autenticación y roles · modelo de datos · API · diseño visual · flujos de navegación ·
plan de tareas · estrategia de testing.

Especificar es **tomar decisiones con criterio y dejarlas escritas**, no esperar a que alguien
las tome por vos.
