# SPEC — Aprende-Gratis

> **Qué es este documento:** versión refinada de la SPEC de clase.
> El repo empieza con la SPEC de clase **tal cual** (primer commit). Este archivo es su evolución:
> mismos requisitos, ambigüedades resueltas, decisiones incorporadas.
> Si la SPEC de clase no lo decía y lo definimos nosotros, queda acá (con el porqué)
> o se referencia al documento donde quedó decidido (PRD para producto, TRD para técnica).

## 1. Identidad del producto

- **Nombre propio:** Aprende-Gratis
- **Una línea:** Una comunidad que reúne cursos gratuitos validados de cualquier plataforma y ayuda a cada persona a organizar y seguir su propio camino de aprendizaje.

## 2. Problema

Hoy hay muchas personas, en especial jóvenes, que quieren formarse pero no pueden pagar un curso o todavía no saben qué estudiar. Cursos gratuitos existen (YouTube, plataformas de universidades, Coursera, freeCodeCamp, etc.), pero están **dispersos**: cada uno en su sitio, con información incompleta y mezclados con cursos que dicen ser gratis y no lo son.

Quien aprende por su cuenta termina guardando enlaces sueltos en marcadores, pierde el hilo de qué empezó y qué terminó, y se desmotiva. No hay un lugar que responda a la vez "¿qué cursos gratuitos buenos hay sobre esto?" y "¿por dónde voy yo?".

Una **comunidad** cambia esa ecuación: muchos usuarios aportan los cursos que conocen (muchos, porque ya los tomaron), un validador controla que la información sea real antes de publicarla, y cada persona arma su **roadmap personal** para ordenar y seguir su avance. El foco del producto es la experiencia del alumno: encontrar rápido y no perder el rumbo.

## 3. Visión

En un año, Aprende-Gratis es el lugar de referencia de su comunidad para encontrar cursos gratuitos confiables: un catálogo amplio, validado y fácil de filtrar, donde cada usuario tiene su roadmap con el orden y el estado de cada curso (pendiente, en curso, completado) y puede ver de un vistazo cuánto avanzó. El contenido sigue viviendo en la plataforma original de cada curso; Aprende-Gratis organiza, valida y acompaña.

## 4. Alcance

### Dentro

- **Gestión de cuenta y autenticación segura:** Registro de usuarios, inicio de sesión protegido con rate limiting, contraseñas cifradas con bcrypt y flujo completo de recuperación de contraseña mediante token/enlace.
- **Aporte comunitario de cursos gratuitos:** Formulario para que usuarios autenticados carguen cursos indicando su URL activa, metadatos obligatorios (categoría de lista cerrada, tema, título, versión, año, docentes, cuestionarios, examen, certificado y aval) y la declaración de si tomaron el curso.
- **Ciclo de revisión y validación de aportes:** Panel para usuarios con rol validador/moderador que permite aprobar o rechazar los cursos en estado de revisión antes de que sean visibles públicamente.
- **Catálogo comunitario público:** Listado paginado de cursos validados con búsqueda por texto, filtro por categoría y vista de detalle de cada curso.
- **Roadmap personal de aprendizaje:** Espacio privado donde cada usuario agrega cursos desde el catálogo comunitario, define su orden de estudio y actualiza su estado de avance personal.
- **Seguimiento de mis aportes (P1):** El autor ve la lista de cursos que aportó con su estado (`en_revision`, `publicado`, `rechazado`) y, si fue rechazado, el motivo escrito por el validador.

### Fuera (out of scope explícito)

- **Cursos pagos o pasarelas de cobro:** La plataforma solo admite enlaces a cursos 100% gratuitos; no se procesan pagos ni suscripciones.
- **Alojamiento o dictado de contenido propio:** No se suben videos, PDFs ni se rinden exámenes dentro de la webapp; el sistema redirige al sitio oficial de cada curso.
- **Emisión de certificados:** La aplicación no emite diplomas propios; solo informa si la plataforma externa del curso extiende certificado.
- **Funciones de red social o foros:** No habrá comentarios públicos en los cursos, chat entre usuarios, ni votación con estrellas en esta versión.
- **Aplicación móvil nativa:** El acceso mobile se resuelve mediante diseño web responsive (mobile-first), sin publicar apps en Android o iOS.
- **Edición o reenvío de aportes:** Un aporte enviado no se edita; si fue rechazado, el autor puede cargar uno nuevo.

## 5. Reglas de producto clave

> Los IDs son **los mismos** que en el PRD §7 (un ID = una regla en todos los documentos).

| # | Regla | Origen |
|---|-------|--------|
| BR-001 | Un curso aportado entra en estado `en_revision` y solo llega al catálogo comunitario tras ser validado (`publicado`) | SPEC clase ("cursos cargados y **validados** pasan al catálogo") |
| BR-002 | Quien aporta un curso declara obligatoriamente si lo tomó o no | SPEC clase |
| BR-003 | Cada usuario ve y edita solo su propio roadmap | decisión propia |
| BR-004 | No se puede aportar dos veces la misma URL | decisión propia |
| BR-005 | Solo cursos 100% gratuitos, con categoría de una lista cerrada | SPEC clase |

> El detalle completo de reglas (incluida BR-006) vive en el PRD §7.

## 6. Stack registrado

> Dos tipos de versión: las **herramientas** ya instaladas en la máquina de desarrollo (verificadas con `--version`)
> y las **librerías/imágenes**, verificadas en npm / PyPI / Docker Hub el 23/10/2026, que se fijan en el lockfile al crear el proyecto en la Instancia B.
> El detalle y el porqué de cada elección está en [`docs/TRD.md` §1](./TRD.md#1-stack-y-versiones-exactas).

| Capa | Tecnología | Versión |
|------|------------|---------|
| Frontend | React + Vite + pnpm | Node `v24.16.0` y pnpm `12.15.0` (instalados) · React `19.3.1` · Vite `8.3.5` |
| Backend | FastAPI + uv | uv `0.13.5` (a instalar) · FastAPI `0.162.0` · imagen `python:3.14-slim` |
| Base de datos | PostgreSQL | `18.6` (imagen oficial `postgres:18.6`) |
| Infra (dev) | Docker + Docker Compose | Docker `27.3.1` y Compose `v2.29.7` (instalados) |

## 7. Restricciones técnicas heredadas de la SPEC de clase

| # | Restricción | Cómo la vamos a cumplir (1-2 líneas) |
|---|-------------|--------------------------------------|
| 1 | Mobile-first con mejora progresiva: base sin media queries; `@media (min-width: …)` solo para agregar/mejorar | CSS base sin media queries para móvil (360px, 1 columna, cards apiladas), sumando `@media (min-width: 768px)` (2 columnas y tablas) y `@media (min-width: 1024px)` (3 columnas y nav horizontal) — ver `docs/UX-UI.md` §3. |
| 2 | Paginación de todas las consultas de listado y de sus tablas | Estrategia `offset + total` en la API (`?page=1&page_size=20`) y componente paginador numerado en el frontend — ver `docs/TRD.md` TD-002 y `docs/BackendSchema.md` §3. |
| 3 | Menú sándwich en mobile | Botón hamburguesa en el header para pantallas `< 1024px` que despliega un drawer lateral accesible con atributos ARIA (`aria-expanded`, `aria-controls`) — ver `docs/UX-UI.md` §4.5. |
| 4 | Screaming Architecture | Estructura de directorios organizada por módulos del dominio (`identidad/`, `catalogo/`, `aportes/`, `roadmap/`) tanto en FastAPI como en React — ver `docs/TRD.md` §3.2. |
| 5 | Apariencia y experiencia inspiradas en Google | Sistema de tokens CSS basado en Material Design 3 (azul primario `#1a73e8`, tipografía limpia, radios redondeados y sombras sutiles) documentado en `docs/UX-UI.md` §2. |

## 8. Vacíos de la SPEC de clase y decisiones tomadas

> La SPEC de clase fue escrita a propósito incompleta. Esta tabla registra cómo se resolvió cada hueco.

| # | Vacío detectado en la SPEC | Opciones consideradas | Decisión | Dónde se desarrolla |
|---|----------------------------|-----------------------|----------|---------------------|
| 1 | ¿Quién valida los cursos aportados antes de publicarse? | Auto-publicación sin filtro / Validación por rol moderador / Puntuación comunitaria por votos | Un usuario con rol `validador` aprueba o rechaza los aportes en estado `en_revision` desde un panel dedicado. | `docs/PRD.md` (BR-001, US-005) y `docs/BackendSchema.md` (§2, §3.3) |
| 2 | ¿Qué roles de usuario existen en la plataforma? | Sin roles (todos hacen todo) / Dos roles (`estudiante` y `validador`) / RBAC complejo con permisos granulares | Dos roles simples en la entidad usuario: `estudiante` (aporta y gestiona su roadmap) y `validador` (además modera aportes). | `docs/PRD.md` (§3) y `docs/BackendSchema.md` (§1.2) |
| 3 | ¿Qué significa exactamente "incluir en mi catálogo / roadmap"? | Simple lista de favoritos (bookmark) / Ruta personal con orden de prioridad y estado de progreso | Tabla intermedia (`roadmap_items`) donde el usuario asigna un `orden` numérico y un estado (`pendiente`, `en_curso`, `completado`) a cada curso. | `docs/PRD.md` (US-004, BR-003), `docs/TRD.md` (TD-004) y `docs/BackendSchema.md` (§1.2, §3.4) |
| 4 | ¿Cómo se buscan y filtran los cursos en el catálogo comunitario? | Solo filtro por categoría / Solo búsqueda por texto libre / Combinación de búsqueda por texto y filtro por categoría | Búsqueda combinada mediante query params: texto libre (`q` sobre título y tema) y filtro por `categoria` sobre el listado paginado. | `docs/APPFlow.md` (§3) y `docs/BackendSchema.md` (§3.2) |
| 5 | ¿Qué sucede si un usuario intenta aportar un curso que ya fue cargado? | Permitir duplicados / Bloquear por título similar / Validar unicidad estricta por URL del curso | Restricción de unicidad (`UNIQUE`) sobre el campo `url` del curso; si el enlace ya existe, se rechaza el alta con error `409 Conflict`. | `docs/PRD.md` (BR-004) y `docs/BackendSchema.md` (§1.2, §3.3) |
| 6 | ¿De dónde sale la "lista" de categorías al aportar un curso? | Texto libre ingresado por el usuario / Lista cerrada precargada en base de datos (seed) | Tabla `categorias` con lista cerrada precargada mediante seed inicial (ej. Desarrollo Web, Datos e IA, DevOps, Diseño UX/UI, Ciberseguridad). | `docs/BackendSchema.md` (§1.2, §3.5, §4) y `docs/IMPLEMENTATION_PLAN.md` (Tarea 2.1) |
| 7 | ¿Cómo existe el primer usuario `validador` si nadie se registra con ese rol? | Endpoint de administración / Editar la BD a mano / Seed al iniciar | Un usuario `validador` se crea por **seed** con email y contraseña tomados de variables de entorno (documentados en el README). | `docs/TRD.md` (§3.2, §4.4) y `docs/IMPLEMENTATION_PLAN.md` (M1) |
| 8 | ¿Qué es "¿lo avala una organización?" | Solo sí/no / Sí/no + nombre de la organización | Sí/no + nombre de la organización, obligatorio solo cuando la respuesta es sí. | `docs/PRD.md` (US-003) y `docs/BackendSchema.md` (§1.2) |
| 9 | ¿Cómo se cargan los "docentes o disertantes"? | Texto libre / Tabla de docentes con relación muchos a muchos | Texto libre (ej. "Ana Pérez, Juan Gómez"): alcanza para mostrar y buscar; una tabla aparte no aporta valor al MVP. | `docs/BackendSchema.md` (§1.2, §4) |
| 10 | ¿Cómo se entera el autor de que su aporte fue rechazado? | Sin feedback / Motivo de rechazo visible en "Mis aportes" | El validador escribe un motivo obligatorio al rechazar; el autor lo ve en "Mis aportes" (prioridad P1). | `docs/PRD.md` (US-005, US-007) y `docs/APPFlow.md` |
| 11 | ¿Cómo llega el enlace de recuperación de contraseña en desarrollo? | SMTP real / Imprimir el link en el log / Servidor SMTP de prueba | Servidor SMTP de prueba **Mailpit** en Docker Compose, con bandeja web para ver el email. | `docs/TRD.md` (TD-007) |

## 9. Historia de la SPEC (autoregistro de cambios)

| Fecha | Cambio | Por qué |
|-------|--------|---------|
| 20/10/2026 | SPEC de clase recibida en el aula | — |
| 21/10/2026 | Primer commit: SPEC de clase tal cual | regla de la consigna |
| 23/10/2026 | Refinamiento sobre plantilla `00_SPEC.md` y cierre de vacíos 1–6 en §8 | Formalizar alcance y decisiones antes de redactar el PRD y TRD |
| 23/10/2026 | Problema/visión alineados con el alcance; IDs de reglas unificados con el PRD; versiones verificadas; vacíos 7–11 | Eliminar contradicciones entre documentos y no registrar versiones sin verificar |
