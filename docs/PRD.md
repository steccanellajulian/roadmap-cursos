# PRD — Product Requirements Document — Aprende-Gratis

> **Qué es:** el QUÉ y el POR QUÉ. Para quién construimos, qué problema resuelve, qué hace
> y — con el mismo peso — qué **no** hace. No habla de tecnología ni de carpetas (eso es el TRD).

## 1. Resumen ejecutivo

Aprende-Gratis es una webapp comunitaria que reúne en un solo lugar cursos **gratuitos** de cualquier plataforma (YouTube, universidades, MOOCs, etc.). Los usuarios registrados **aportan** los cursos que conocen indicando su enlace y sus datos principales; un **validador** revisa cada aporte y, si es correcto, lo publica en el **catálogo comunitario**, que cualquiera puede explorar y filtrar sin registrarse. Cada usuario arma además su **roadmap personal**: elige cursos del catálogo, los ordena y marca su estado (pendiente, en curso, completado) para no perder el rumbo. Aprende-Gratis no aloja contenido ni toma exámenes: organiza, valida y acompaña; el curso se hace en su sitio original.

## 2. Objetivos y métricas de éxito

| Objetivo | Cómo sabemos que lo logramos |
|----------|------------------------------|
| Construir un catálogo comunitario curado, sin duplicados ni enlaces caídos | 100% de los cursos visibles en el catálogo pasaron por validación; 0 URLs duplicadas en la base |
| Facilitar el descubrimiento rápido de cursos gratuitos por área | Desde el inicio, un usuario llega a una lista filtrada por categoría o texto en ≤ 2 clics |
| Permitir que los estudiantes organicen y sigan su ruta de estudio | % de usuarios registrados que agregan al menos 1 curso a su roadmap y cambian su estado al menos una vez |

## 3. Personas

### Persona 1 — Lucía, estudiante

- **Contexto:** Estudiante universitaria que busca complementar la facultad con cursos gratuitos online en su tiempo libre.
- **Motivaciones:** Encontrar cursos de calidad sin perder horas buscando y llevar un orden claro de qué estudiar primero y qué después.
- **Frustraciones hoy:** Guarda links sueltos en marcadores del navegador, se olvida por cuál iba y se topa con cursos que dicen ser gratis pero son pagos.
- **Historias tipo:** "Quiero ver rápido qué cursos gratuitos de Python tienen certificado" / "Quiero armar mi lista ordenada de cursos para este cuatrimestre y marcar los que ya terminé".

### Persona 2 — Martín, validador

- **Contexto:** Desarrollador o docente de la comunidad que aporta material y revisa las sugerencias que suben otros usuarios.
- **Motivaciones:** Mantener el catálogo limpio, verificar que los enlaces funcionen y que los datos del curso sean reales.
- **Frustraciones hoy:** En los foros o grupos de estudio se comparten links repetidos, incompletos o rotos sin ningún filtro.
- **Historias tipo:** "Quiero revisar los cursos pendientes de validación para aprobar los correctos y rechazar los enlaces rotos, explicando por qué".

## 4. User stories

> P0 = el producto no funciona sin esto el día del MVP. P1 = deseable; se construye si el P0 está terminado.

| ID | Prioridad | Historia | Criterios de aceptación |
|----|-----------|----------|-------------------------|
| US-001 | P0 | Como visitante, quiero ver el catálogo comunitario paginado y filtrar por categoría o texto, para descubrir cursos gratuitos sin registrarme | - [ ] Dado que visito `/catalogo`, veo la primera página con hasta 20 cursos en estado `publicado`<br>- [ ] Dado que hay más de 20 cursos publicados, aparece el paginador y puedo ir a la página siguiente<br>- [ ] Dado que elijo una categoría y/o escribo un texto (busca en título y tema), el listado muestra solo las coincidencias<br>- [ ] Dado que no hay cursos para el filtro aplicado, veo un mensaje "sin resultados" con un botón para aportar un curso<br>- [ ] Dado que abro un curso, veo todos sus datos y un enlace que abre el sitio original en otra pestaña |
| US-002 | P0 | Como visitante, quiero registrarme e iniciar sesión con mi email y contraseña, para acceder a las funciones de aporte y roadmap personal | - [ ] Dado que completo `/registro` con nombre, email no registrado y contraseña de 8 caracteres o más, se crea mi cuenta con rol `estudiante` y la contraseña se guarda cifrada con bcrypt<br>- [ ] Dado que uso un email ya registrado, veo el error "ese email ya está registrado"<br>- [ ] Dado que ingreso credenciales válidas en `/login`, inicio sesión y puedo entrar a las pantallas privadas<br>- [ ] Dado que ingreso credenciales inválidas, veo "email o contraseña incorrectos" (sin indicar cuál de los dos falló)<br>- [ ] Dado que hago más de 5 intentos de login en 1 minuto desde la misma IP, el sistema rechaza los siguientes con el mensaje "demasiados intentos, probá en un minuto"<br>- [ ] Dado que tengo sesión iniciada, puedo cerrar sesión desde el menú |
| US-003 | P0 | Como usuario autenticado, quiero aportar un curso gratuito con todos sus datos y declarar si lo tomé, para enriquecer el catálogo comunitario | - [ ] Dado que completo `/aportar` con: URL (formato `http(s)://`), categoría (de la lista), tema, título, versión, año de edición, docentes (texto libre), ¿tiene cuestionarios?, ¿requiere examen?, ¿extiende certificado?, ¿lo avala una organización? y "¿lo tomaste?", el curso se guarda en estado `en_revision` y veo una confirmación<br>- [ ] Dado que marco "lo avala una organización = sí", el nombre de la organización es obligatorio<br>- [ ] Dado que dejo un campo obligatorio vacío o un año inválido (menor a 1990 o mayor al año actual), veo el error junto al campo y no se pierde lo que cargué<br>- [ ] Dado que la URL ya existe en el sistema, veo el error "este curso ya fue aportado" |
| US-004 | P0 | Como usuario autenticado, quiero agregar cursos publicados a mi roadmap personal, ordenarlos y actualizar mi estado de avance, para organizar mi aprendizaje | - [ ] Dado que estoy en el detalle de un curso `publicado`, puedo agregarlo a mi roadmap; queda al final con estado `pendiente`<br>- [ ] Dado que el curso ya está en mi roadmap, el botón indica "ya está en tu roadmap" y no se duplica<br>- [ ] Dado que ingreso a `/roadmap`, veo mis cursos paginados en el orden que definí<br>- [ ] Dado que tengo un curso en mi roadmap, puedo cambiar su estado (`pendiente`, `en_curso`, `completado`), subirlo/bajarlo de posición o quitarlo<br>- [ ] Dado que entro sin sesión a `/roadmap`, me lleva a `/login` y después de iniciar sesión vuelvo al roadmap |
| US-005 | P0 | Como validador, quiero revisar los cursos pendientes y aprobarlos o rechazarlos, para garantizar la calidad del catálogo comunitario | - [ ] Dado que inicio sesión con rol `validador` e ingreso a `/validar`, veo la lista paginada de aportes en estado `en_revision` (los más antiguos primero)<br>- [ ] Dado que apruebo un aporte, pasa a `publicado` y aparece en `/catalogo`<br>- [ ] Dado que rechazo un aporte, debo escribir un motivo; pasa a `rechazado` y no aparece en el catálogo<br>- [ ] Dado que un usuario con rol `estudiante` entra a `/validar`, ve "no tenés permiso" |
| US-006 | P0 | Como usuario registrado, quiero recuperar mi contraseña mediante un enlace enviado a mi email, para volver a entrar si la olvido | - [ ] Dado que ingreso mi email en `/recuperar`, veo siempre el mismo mensaje "si el email está registrado, te enviamos un enlace" (no revela si la cuenta existe)<br>- [ ] Dado que el email está registrado, recibo un email con un enlace a `/restablecer?token=…` válido por 30 minutos<br>- [ ] Dado que abro el enlace vigente y escribo una nueva contraseña (8 caracteres o más), se guarda cifrada con bcrypt y puedo iniciar sesión con ella<br>- [ ] Dado que el enlace ya fue usado o venció, veo "el enlace no es válido o venció" y la opción de pedir uno nuevo |
| US-007 | P1 | Como usuario autenticado, quiero ver los cursos que aporté y su estado, para saber si fueron publicados o por qué se rechazaron | - [ ] Dado que ingreso a `/mis-aportes`, veo mis aportes paginados con su estado (`en_revision`, `publicado`, `rechazado`)<br>- [ ] Dado que un aporte fue rechazado, veo el motivo escrito por el validador<br>- [ ] Dado que acabo de enviar un aporte, la confirmación me ofrece ir a "Mis aportes" |

## 5. Requisitos funcionales

| ID | Requisito | Historia relacionada |
|----|-----------|----------------------|
| RF-001 | El sistema permite registrar usuarios con nombre, email único y contraseña cifrada con bcrypt; todo usuario nuevo tiene rol `estudiante`. | US-002 |
| RF-002 | El sistema permite iniciar y cerrar sesión, limitando los intentos de login por IP (rate limiting). | US-002 |
| RF-003 | El sistema permite recuperar la contraseña: solicitud por email, envío de un enlace con token temporal de un solo uso y definición de una nueva contraseña cifrada. | US-006 |
| RF-004 | El sistema expone el catálogo comunitario público y paginado de cursos en estado `publicado`, con filtro por categoría, búsqueda por texto (título y tema) y detalle de cada curso. | US-001 |
| RF-005 | El sistema permite a un usuario autenticado aportar un curso con URL única, categoría de lista cerrada, tema, título, versión, año de edición, docentes, cuestionarios, examen, certificado, aval de organización (sí/no + nombre) y la declaración de si lo tomó. | US-003 |
| RF-006 | Todo aporte se crea en estado `en_revision`; un usuario con rol `validador` los lista paginados y los aprueba (`publicado`) o rechaza (`rechazado`, con motivo obligatorio). | US-003, US-005 |
| RF-007 | Cada usuario autenticado gestiona su roadmap privado: agregar cursos publicados, listarlos paginados, cambiar su orden, actualizar su estado (`pendiente`, `en_curso`, `completado`) y quitarlos. | US-004 |
| RF-008 | El sistema permite a cada usuario listar, paginados, los aportes que realizó, con su estado y el motivo de rechazo si corresponde. | US-007 |

## 6. Requisitos no funcionales

| ID | Requisito | Notas |
|----|-----------|-------|
| RNF-001 | Todos los listados y tablas en pantalla deben estar paginados. | heredado de SPEC clase |
| RNF-002 | Diseño mobile-first con mejora progresiva (estilos base sin media queries y `@media (min-width: ...)` solo para agregar o mejorar). | heredado de SPEC clase |
| RNF-003 | Las contraseñas se almacenan cifradas con `bcrypt` (nunca en texto plano). | heredado de SPEC clase |
| RNF-004 | Protección contra fuerza bruta: máximo 5 intentos de login por minuto por IP. | heredado de SPEC clase; valor elegido en TRD TD-006 |
| RNF-005 | Apariencia inspirada en Google (Material Design) y accesibilidad mínima WCAG AA (contraste de texto ≥ 4.5:1, foco visible, ARIA en menú sándwich y formularios). | heredado de SPEC clase y `docs/UX-UI.md` |
| RNF-006 | Los listados paginados responden en menos de 2 segundos con hasta 1.000 cursos cargados. | decisión propia |

## 7. Reglas de negocio

| ID | Regla | Fuente |
|----|-------|--------|
| BR-001 | Un curso aportado entra en estado `en_revision` y no aparece en el catálogo comunitario hasta ser validado (`publicado`) por un usuario con rol `validador`. | SPEC clase + decisión propia |
| BR-002 | Quien aporta un curso debe declarar obligatoriamente si lo tomó o no. | SPEC clase |
| BR-003 | El roadmap es personal y privado; cada usuario solo puede ver, ordenar y editar los ítems de su propio roadmap. | decisión propia |
| BR-004 | No se puede aportar dos veces la misma URL de curso (unicidad estricta por enlace). | decisión propia |
| BR-005 | Solo se admiten cursos gratuitos; la categoría se elige de una lista cerrada predefinida. | SPEC clase |
| BR-006 | Solo se pueden agregar al roadmap cursos en estado `publicado`, y un mismo curso no puede estar dos veces en el roadmap de un usuario. | SPEC clase + decisión propia |
| BR-007 | Rechazar un aporte exige escribir un motivo, que solo ven el autor y los validadores. | decisión propia |
| BR-008 | Un aporte enviado no se edita ni se reenvía; si fue rechazado, el autor puede cargar uno nuevo. | decisión propia |

## 8. Fuera de alcance (out of scope)

- **Cursos pagos o pasarelas de cobro:** La plataforma solo admite enlaces a cursos 100% gratuitos; no se procesan pagos ni suscripciones.
- **Alojamiento o dictado de contenido propio:** No se suben videos, PDFs ni se rinden exámenes dentro de la webapp; el sistema redirige al sitio oficial de cada curso.
- **Emisión de certificados:** La aplicación no emite diplomas propios; solo informa si la plataforma externa del curso extiende certificado.
- **Funciones de red social o foros:** No habrá comentarios públicos, chat entre usuarios ni votación con estrellas en esta versión.
- **Aplicación móvil nativa:** El acceso mobile se resuelve con diseño web responsive (mobile-first).
- **Edición de aportes y gestión de usuarios/roles desde la UI:** No hay pantalla para editar aportes enviados ni para asignar el rol `validador` (se crea por seed, ver SPEC §8 #7).

## 9. Supuestos y decisiones sobre la SPEC de clase

- **Validación mediante rol `validador`:** los aportes entran `en_revision` y un validador los aprueba o rechaza, garantizando la curaduría sin complejizar el MVP con votación comunitaria.
- **Alcance del roadmap:** incluir un curso implica asociarlo al usuario con un `orden` y un estado (`pendiente`, `en_curso`, `completado`), para un seguimiento real y no solo una lista de favoritos.
- **Control de duplicados por URL:** el enlace identifica unívocamente a cada curso.
- **Categorías como lista cerrada precargada (seed):** filtros consistentes desde el primer arranque.
- **Aval de organización = sí/no + nombre**, y **docentes como texto libre**: lo mínimo para responder a la SPEC sin entidades extra.
- **Recuperación de contraseña es P0:** la SPEC la exige con ciclo completo; por eso forma parte del MVP.
- **Motivo de rechazo y "Mis aportes" (P1):** el autor recibe feedback; no es imprescindible para el MVP.

Alternativas y detalle en [`docs/SPEC.md` §8](./SPEC.md#8-vacíos-de-la-spec-de-clase-y-decisiones-tomadas).

## 10. Preguntas abiertas

| Pregunta | Impacto | Estado |
|----------|---------|--------|
| ¿Qué pasa con los aportes rechazados? ¿Se pueden editar y reenviar? | medio | **Decidida** — quedan en `rechazado` con su motivo (BR-007); no se editan ni reenvían, el autor carga uno nuevo (BR-008). |
| ¿Un visitante sin cuenta puede armar un roadmap temporal en su navegador? | bajo | **Decidida** — No; el roadmap requiere cuenta para asegurar su persistencia. |
| ¿Quién verifica que un curso sea realmente gratuito? | medio | **Decidida** — el validador, al revisar el aporte (BR-001, BR-005). |

---

**Referencias:**
- Atlassian — Plantilla PRD: https://www.atlassian.com/software/confluence/templates/product-requirements
- Lenny Rachitsky — Plantilla de requirements: https://www.atlassian.com/software/confluence/templates/requirements
