# TRD — Technical Requirements Document — Aprende-Gratis

> **Qué es:** el CÓMO técnico. Decisiones de arquitectura, stack, estructura de carpetas y
> convenciones. No es el plan de tareas (eso es el IMPLEMENTATION_PLAN) ni el producto (PRD).

## 1. Stack y versiones exactas

> Herramientas: verificadas con `--version` en la máquina de desarrollo.
> Librerías e imágenes: última estable verificada en npm / PyPI / Docker Hub el **23/10/2026**.
> Se fijan en `pnpm-lock.yaml` y `uv.lock` al crear el proyecto (Instancia B).

| Capa | Elección | Versión exacta | Por qué |
|------|----------|----------------|---------|
| Runtime frontend | Node.js + pnpm | Node `24.16.0` (local), imagen `node:24-alpine` · pnpm `12.15.0` | Node 24 es LTS; la imagen alpine coincide con la versión mayor local y es liviana |
| Frontend | React + Vite | React `19.3.1` · Vite `8.3.5` | fijado por SPEC (React 19); Vite da dev server rápido y proxy integrado |
| Ruteo frontend | React Router | `8.5.0` | estándar de facto para SPA en React; soporta rutas protegidas |
| Backend | FastAPI + uv | FastAPI `0.162.0` · uv `0.13.5` · Uvicorn `0.54.0` | fijado por SPEC; uv gestiona Python y dependencias con lockfile reproducible |
| Python | CPython | imagen `python:3.14-slim` (local `3.14.5`) | misma versión mayor que la máquina de desarrollo → menos sorpresas "en mi máquina anda" |
| ORM | SQLModel | `0.0.48` (sobre SQLAlchemy) | ver TD-011 |
| Driver BD | psycopg | `3.3.6` | driver PostgreSQL moderno y mantenido, soportado por SQLAlchemy |
| Config | pydantic-settings | `2.16.1` | lee variables de entorno con tipos y validación |
| Auth | PyJWT · bcrypt | PyJWT `2.15.1` · bcrypt `5.0.0` | ver TD-001 y TD-005 |
| Rate limiting | slowapi | `0.1.10` | ver TD-006 |
| BD | PostgreSQL | `18.6` (imagen `postgres:18.6`) | fijado por SPEC |
| Email (dev) | Mailpit | imagen `axllent/mailpit:v1.32.0` | ver TD-007 |
| Infra (dev) | Docker + Compose | Docker `27.3.1` · Compose `v2.29.7` (local) | fijado por SPEC |

## 2. Decisiones técnicas

> La plantilla exige mínimo 3 decisiones importantes con sus alternativas y justificación.
> Documentamos las 8 decisiones técnicas principales que definen cómo se va a construir el proyecto:

| # | Decisión | Alternativas consideradas | Elegida | Por qué |
|---|----------|---------------------------|---------|---------|
| TD-001 | Estrategia de autenticación | JWT stateless / sesión server-side con cookies / OAuth externo (Google/GitHub) | **JWT** firmado con HS256, enviado en el header `Authorization: Bearer <token>`, con expiración de 60 min. El token guarda el ID del usuario y su rol (`estudiante` o `validador`). | Es el patrón estándar que enseña el tutorial oficial de FastAPI (`OAuth2PasswordBearer`). No necesita guardar sesiones en la base de datos y permite que el frontend sepa el rol del usuario para mostrar u ocultar opciones. El frontend lo guarda en `localStorage` por simplicidad en el MVP. |
| TD-002 | Estrategia de paginación | offset + total / cursor-based | **offset + total**: `?page=1&page_size=20` devolviendo `{ items, total, page, page_size }`. Por defecto 20, máximo 50 ítems. | Es la forma más fácil y directa de implementar un paginador numerado ("página 1 de 4") tanto en SQL (`OFFSET` y `LIMIT`) como en los componentes de React. Como el catálogo no maneja millones de registros, el costo de calcular el total es despreciable. |
| TD-003 | Formato de errores de API | envelope propio simple / formato por defecto de FastAPI / RFC 7807 | **Envelope propio simple**: `{ "error": { "code", "message", "details" } }` | Unifica todos los errores: si el frontend recibe un error, siempre busca `error.message` para mostrárselo al usuario. En FastAPI se agregan dos handlers globales en `main.py` para transformar los errores automáticos de validación (422) a este formato. |
| TD-004 | Cómo modelar el roadmap personal | tabla intermedia con estado / lista de IDs guardada en el usuario | **Tabla intermedia `roadmap_items`** con `UNIQUE(usuario_id, curso_id)` y campos `orden` y `estado` | El roadmap no es solo una lista de favoritos: el usuario necesita ordenar sus cursos y cambiar su avance (`pendiente`, `en_curso`, `completado`). La restricción `UNIQUE` en la base evita duplicados sin tener que programar lógica extra. |
| TD-005 | Cifrado de contraseñas | bcrypt / Argon2id / hashlib nativo | **bcrypt** directamente con la librería oficial `bcrypt` | Cumple con la exigencia mínima de la SPEC y del PRD. Se limita la longitud de la clave a 72 caracteres en la validación porque bcrypt ignora caracteres a partir de esa longitud. |
| TD-006 | Protección contra fuerza bruta (Rate limiting) | slowapi (en memoria) / contador manual en base de datos / Redis | **slowapi** en memoria: límite de 5 intentos por minuto por IP en `/auth/login` y 3 por minuto en `/auth/recuperar` | Se aplica con un simple decorador sobre la función del endpoint de FastAPI. Al ser un entorno de desarrollo con una sola instancia del backend, guardar el contador en memoria alcanza perfectamente sin agregar otro servicio como Redis. |
| TD-007 | Envío de emails en desarrollo | Mailpit en Docker / SMTP real (Gmail) / imprimir enlace en la consola | **Mailpit** en Docker Compose (puerto SMTP 1025 y panel web 8025) | Permite probar el flujo completo de recuperación de contraseña en una máquina limpia sin pedir contraseñas reales ni configurar cuentas de correo. Al probar, el docente abre `localhost:8025` y ve el email simulado de inmediato. |
| TD-008 | Estilos del frontend | CSS nativo con variables / Tailwind CSS / librerías como MUI o Shadcn | **CSS nativo con variables** (tokens de `docs/UX-UI.md`) | Es la forma más clara de cumplir y demostrar la restricción mobile-first de la consigna: el CSS base se escribe sin media queries y los `@media (min-width)` se ven explícitos en el código. No suma librerías pesadas ni curvas de aprendizaje extras para los 3 días de desarrollo. |


## 3. Arquitectura

### 3.1 Patrón y capas

Screaming Architecture + arquitectura en capas dentro de cada módulo del dominio:

```mermaid
flowchart LR
    HTTP["router.py — HTTP"] --> SVC["service.py — reglas de negocio"]
    SVC --> REPO["repository.py — acceso a datos"]
    REPO --> DB[(PostgreSQL)]
    SVC --> MODELS["models.py — entidades y schemas"]
```

- **router.py:** recibe la petición, valida la entrada (schemas), llama al service y devuelve la respuesta. Sin reglas de negocio.
- **service.py:** reglas de negocio (ej. "solo cursos publicados entran al roadmap", "rechazar exige motivo"). No conoce HTTP.
- **repository.py:** única puerta a la base de datos. Sin reglas de negocio.
- **models.py:** tablas (SQLModel) y schemas de entrada/salida.

### 3.2 Estructura de carpetas (la que se va a crear en la Instancia B)

Los módulos tienen **los mismos nombres** en backend y frontend: `identidad`, `catalogo`, `aportes`, `roadmap`. Al abrir el repo se lee de qué trata el negocio, no qué framework se usa.

```
roadmap-cursos/
├── backend/
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── Dockerfile
│   └── app/
│       ├── main.py                  # crea la app, registra routers y handlers de error
│       ├── compartido/              # lo transversal a todos los módulos
│       │   ├── config.py            # variables de entorno (pydantic-settings)
│       │   ├── database.py          # engine y sesión
│       │   ├── errores.py           # envelope de errores (TD-003)
│       │   ├── paginacion.py        # parámetros y respuesta paginada (TD-002)
│       │   └── seed.py              # categorías, validador y cursos de ejemplo (TD-010/011)
│       ├── identidad/               # registro, login, recuperación, roles
│       │   ├── router.py
│       │   ├── service.py
│       │   ├── repository.py
│       │   ├── models.py
│       │   ├── seguridad.py         # hash bcrypt, JWT, dependencia "usuario actual"
│       │   └── email.py             # envío del enlace de recuperación (TD-007)
│       ├── catalogo/                # cursos publicados y categorías
│       │   ├── router.py
│       │   ├── service.py
│       │   ├── repository.py
│       │   └── models.py            # Curso, Categoria, estados del curso
│       ├── aportes/                 # alta de aportes, mis aportes, validación
│       │   ├── router.py
│       │   ├── service.py
│       │   └── repository.py
│       └── roadmap/                 # roadmap personal
│           ├── router.py
│           ├── service.py
│           ├── repository.py
│           └── models.py
│   └── tests/                       # se completa en la clase del 27/10
├── frontend/
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── vite.config.js               # proxy /api → backend (TD-009)
│   ├── Dockerfile
│   └── src/
│       ├── main.jsx
│       ├── app/                     # shell: router, layout, Header con menú sándwich
│       ├── compartido/              # componentes reutilizables (Boton, Paginador, Campo…) y cliente HTTP
│       ├── estilos/                 # tokens.css y estilos globales (UX-UI §2)
│       └── features/
│           ├── identidad/           # Login, Registro, Recuperar, Restablecer
│           ├── catalogo/            # Catálogo, Detalle de curso
│           ├── aportes/             # Aportar, Mis aportes, Panel de validación
│           └── roadmap/             # Mi roadmap
│               ├── components/
│               ├── hooks/
│               └── api.js
├── docker-compose.yml
├── .env.example
└── docs/
```

> **Por qué `Curso` vive en `catalogo/`:** el curso es la entidad central del catálogo. `aportes/` y `roadmap/` lo usan importando desde `catalogo`. Así hay un único dueño del modelo.

### 3.3 Servicios Docker (entorno de desarrollo)

| Servicio | Imagen/base | Puerto | Rol |
|----------|-------------|--------|-----|
| postgres | `postgres:18.6` | 5432 | base de datos (volumen con nombre para persistir) |
| backend | `python:3.14-slim` + uv | 8000 | API FastAPI con recarga automática |
| frontend | `node:24-alpine` + pnpm | 5173 | SPA Vite (dev server + proxy `/api`) |
| mailpit | `axllent/mailpit:v1.32.0` | 1025 (SMTP) · 8025 (web) | recibe y muestra los emails de recuperación |

```mermaid
flowchart LR
    BROWSER["Navegador"] -->|":5173"| FE["frontend Vite"]
    FE -->|"/api/* (proxy)"| BE["backend FastAPI :8000"]
    BE --> PG[("postgres :5432")]
    BE -->|"SMTP :1025"| MP["mailpit"]
    BROWSER -->|":8025 bandeja"| MP
```

> En la clase del 27/10 estos Dockerfiles evolucionan a multi-stage. Por ahora, lo mínimo que levanta.

## 4. Convenciones

### 4.1 Commits

Conventional Commits en **español**, en el 100% de la historia: `tipo(alcance): descripción en imperativo`.

| Tipo | Uso | Ejemplo |
|------|-----|---------|
| `docs` | documentación | `docs(trd): agregar decisiones técnicas` |
| `feat` | funcionalidad nueva | `feat(catalogo): listar cursos publicados con paginación` |
| `fix` | corrección | `fix(identidad): devolver 401 con credenciales inválidas` |
| `chore` | configuración, dependencias | `chore: agregar .gitignore para React y FastAPI` |
| `docker` | Dockerfiles y compose | `docker: agregar servicio postgres 18.6` |
| `test` / `refactor` | tests / cambios sin cambiar comportamiento | `test(roadmap): validar curso duplicado` |

Prohibidos los mensajes genéricos (`cambios`, `wip`, `fix`).

### 4.2 Flujo de Git — GitHub Flow

- **`main`**: siempre estable. Nunca se commitea directo sobre `main`.
- **Una rama corta por documento o tarea**, creada desde `main` actualizado:
  - Instancia A: `docs/<documento>` (ej. `docs/prd`, `docs/trd`).
  - Instancia B: `feat/<modulo>-<tarea>` (ej. `feat/catalogo-listado`), `fix/<descripcion>`, `docker/<descripcion>`, `chore/<descripcion>`.
- **Merge:** Pull Request en GitHub hacia `main` con **merge commit** (no squash), para que la rama quede visible en la historia. Se borra la rama después del merge.
- **Revisión:** trabajo individual → antes de mergear reviso yo el diff del PR contra el "Hecho cuando…" del IMPLEMENTATION_PLAN.
- **Por qué GitHub Flow:** es el más simple que cumple "nada directo en main" y deja la historia observable. Git Flow (`develop`, `release/*`, `hotfix/*`) está pensado para equipos con versiones planificadas: es ceremonia de más para una persona en 3 días.

### 4.3 Errores de API (TD-003)

Todas las respuestas de error usan el mismo formato:

```json
{
  "error": {
    "code": "CURSO_DUPLICADO",
    "message": "Este curso ya fue aportado.",
    "details": null
  }
}
```

Errores de validación (422), con el detalle por campo:

```json
{
  "error": {
    "code": "VALIDACION",
    "message": "Hay campos con errores.",
    "details": [ { "campo": "anio_edicion", "mensaje": "Debe estar entre 1990 y el año actual." } ]
  }
}
```

| HTTP | Cuándo |
|------|--------|
| 400 | regla de negocio violada (ej. agregar al roadmap un curso no publicado) |
| 401 | sin token, token inválido/vencido, o credenciales incorrectas |
| 403 | autenticado pero sin permiso (ej. estudiante en `/validar`) |
| 404 | recurso inexistente |
| 409 | conflicto de unicidad (email o URL ya existentes, curso ya en el roadmap) |
| 422 | datos de entrada inválidos |
| 429 | rate limit superado |

### 4.4 Variables de entorno

Se documentan en `.env.example` (versionado); el `.env` real está en `.gitignore`.

| Variable | Ejemplo | Obligatoria | Descripción |
|----------|---------|-------------|-------------|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `aprende` / `aprende` / `aprende_gratis` | sí | credenciales del contenedor postgres |
| `DATABASE_URL` | `postgresql+psycopg://aprende:aprende@postgres:5432/aprende_gratis` | sí | conexión del backend |
| `JWT_SECRET` | `cambiar-por-un-valor-largo-y-aleatorio` | sí | clave de firma de los JWT |
| `JWT_EXPIRA_MINUTOS` | `60` | no (def. 60) | vida del token de sesión |
| `LOGIN_RATE_LIMIT` | `5/minute` | no (def. `5/minute`) | límite de TD-006 |
| `SMTP_HOST` / `SMTP_PORT` | `mailpit` / `1025` | sí | servidor de email (TD-007) |
| `EMAIL_REMITENTE` | `no-responder@aprende-gratis.local` | sí | remitente de los emails |
| `FRONTEND_URL` | `http://localhost:5173` | sí | para armar el enlace `/restablecer?token=…` |
| `RESET_TOKEN_MINUTOS` | `30` | no (def. 30) | vigencia del enlace de recuperación |
| `SEED_VALIDADOR_EMAIL` / `SEED_VALIDADOR_PASSWORD` | `validador@aprende.local` / `Validador123` | sí | usuario validador inicial (TD-010) |

### 4.5 Logging y excepciones

- Logs a la salida estándar con el módulo `logging` de Python (nivel `INFO`); se ven con `docker compose logs backend`.
- Se registra: arranque y seed, cada login fallido y cada 429, envío de emails (destinatario, nunca el token) y errores no controlados con su traza.
- Nunca se loggean contraseñas, hashes ni tokens.
- Las excepciones de negocio se lanzan desde los services como errores propios y se transforman en el envelope de §4.3 en handlers globales registrados en `main.py`. Cualquier error no previsto → `500` con `code: "ERROR_INTERNO"` sin detalles internos.

## 5. Requisitos no funcionales técnicos (traducción de las restricciones)

| Restricción (SPEC) | Cómo se cumple | Dónde se verifica |
|--------------------|----------------|-------------------|
| Paginación de listados | TD-002: todos los `GET` de listado aceptan `page`/`page_size` y devuelven `{items,total,page,page_size}`; componente `Paginador` en el frontend | `GET /api/v1/cursos`, `/aportes/pendientes`, `/aportes/mios`, `/roadmap` (BackendSchema §3) |
| Mobile-first con mejora progresiva | TD-008: estilos base sin media queries; solo `@media (min-width: 768px)` y `(min-width: 1024px)` para agregar | `src/estilos/` y CSS de Catálogo, Header y Roadmap (UX-UI §3) |
| Menú sándwich | `Header` con botón hamburguesa `< 1024px`, `aria-expanded` y `aria-controls` | `src/app/` (APPFlow, UX-UI §4.5) |
| Screaming Architecture | árbol §3.2 con módulos `identidad`, `catalogo`, `aportes`, `roadmap` en backend y frontend | revisión del repo |
| Contraseñas con bcrypt | TD-005 | `identidad/seguridad.py`; columna `password_hash` (BackendSchema §1.2) |
| Rate limiting en login | TD-006 | 6 intentos seguidos a `POST /api/v1/auth/login` → el 6.º responde `429` |
| Recuperación de contraseña (ciclo completo) | TD-007 + TD-012 | `POST /auth/recuperar` → email en Mailpit (`:8025`) → `POST /auth/restablecer` |

## 6. Riesgos técnicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Primera vez con FastAPI + JWT: la autenticación lleva más tiempo del estimado | alta | alto | seguir el tutorial oficial de seguridad de FastAPI; construir M1 primero y probarlo con `/docs` (Swagger) antes de seguir |
| La imagen `postgres:18` cambió dónde guarda los datos respecto de versiones anteriores; un volumen mal montado pierde datos o no arranca | media | medio | montar el volumen como indica la documentación de la imagen oficial para la versión 18 y probar `docker compose down` / `up` conservando datos |
| Detrás del proxy de Vite y de Docker Desktop, el backend ve la misma IP para todos los clientes → el rate limit es global en dev | alta | bajo | aceptado en dev (igual demuestra el 429); documentado en el README |
| El formulario de aporte tiene 12 campos: la validación en front y back puede divergir | media | medio | el backend es la fuente de verdad (422 con `details` por campo) y el frontend muestra esos mensajes junto a cada campo |
| El email de recuperación no llega (SMTP mal configurado) | baja | medio | Mailpit no requiere autenticación; probar el flujo completo apenas está M1 |
| Recarga en caliente de Vite/Uvicorn lenta o sin detectar cambios con volúmenes en Windows | media | bajo | si pasa, activar el modo polling del watcher (opción de Vite `server.watch.usePolling`) |

---

**Referencia:**
- Design Docs at Google: https://www.industrialempathy.com/posts/design-docs-at-google/
- FastAPI — Security / OAuth2 con JWT: https://fastapi.tiangolo.com/tutorial/security/
