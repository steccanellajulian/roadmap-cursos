# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.2.0] - 2026-10-27 (Tickets de Clase — Testing, Docker Multi-Stage y Calidad)

### Added
- **T1 (Reglas de Curso - Unit tests):** Extracción de reglas de negocio puras a `backend/app/catalogo/reglas.py` (validaciones de URL, campos requeridos, límites de año de edición 1990..año_actual, declaración jurada de toma obligatoria BR-002, y máquina de estados del curso `borrador` → `en_revision` → `publicado` / `rechazado`). Suite de 21 tests unitarios en `backend/tests/test_catalogo_unit.py` con patrón AAA estricto y 100% de cobertura.
- **T2 (Reglas de Roadmap - Unit tests):** Implementación de reglas puras en `backend/app/roadmap/reglas.py` (incorporación de cursos únicamente publicados, unicidad de curso por usuario BR-006, reordenamiento secuencial sin gaps, recompactación al eliminar y límite máximo de ítems). Suite de 16 tests unitarios en `backend/tests/test_roadmap_unit.py` con 100% de cobertura.
- **T3 (Servicio de Aportes - Unit tests):** Lógica pura de moderación y auditoría en `backend/app/aportes/reglas.py` (verificación de rol validador, prohibición de autovalidación por conflicto de intereses y motivo de rechazo obligatorio). Desacoplamiento de tests mediante códigos de error semánticos estables (`CodigosErrorAportes`). Suite de 11 tests unitarios en `backend/tests/test_aportes_unit.py` con 100% de cobertura.
- **T4 (CursoRepository - Integration tests):** Implementación del repositorio de persistencia `CursoRepository` en `backend/app/catalogo/repository.py` con SQLModel/SQLAlchemy. Suite de 11 tests de integración en `backend/tests/test_integration.py` contra base de datos relacional real (SQLite in-memory aislada por test con StaticPool) validando CRUD completo, paginación con total count, filtros de búsqueda `q` case-insensitive y filtrado por categoría.
- **T5 (Flujo Aporte → Validación - Integration tests):** Rutas de API REST en `app/aportes/router.py` y `app/catalogo/router.py`. Suite de integración en `backend/tests/test_flujo_aportes_integration.py` con FastAPI `TestClient`, validando que el aporte ingresa en `en_revision`, pasa a `publicado` y se visualiza en `/api/v1/cursos` tras aprobación, o se oculta del catálogo si es rechazado. Verificación de códigos HTTP 401 (sin sesión) y 403 (estudiante intentando dictaminar).
- **T6 (Frontend Hook useCursos - Unit tests):** Hook `useCursos` en `frontend/src/features/catalogo/hooks/useCursos.js` desacoplado del componente visual. Suite de 4 tests en `useCursos.test.js` testeando carga inicial (`loading=true` → `loading=false` con datos), captura de error de red (estado de error seteado y lista vacía), paginación con reseteo automático a página 1 al cambiar filtros (`setPage` / `setFiltro`) y recarga con parámetros vigentes (`refetch`).
- **T7 (Backend Dockerfile Multi-Stage):** Dockerfile multi-stage en `backend/Dockerfile` con stage `builder` (`python:3.12-slim` + `uv sync --frozen --no-dev`) y stage `runtime` que solo contiene el virtualenv compilado y el código de `app/`. Ejecución con usuario no-root `appuser`, puerto 8000 expuesto y healthcheck nativo contra `/health`.
- **T8 (.dockerignore optimizado):** Exclusión estricta de artefactos volátiles, dependencias locales y credenciales en `backend/.dockerignore` (`.venv`, `__pycache__`, `tests/`, `.pytest_cache`, `.coverage`, `.env`) y `frontend/.dockerignore` (`node_modules`, `dist`, `coverage`, `*.test.js`).
- **T9 (Frontend Dockerfile Multi-Stage con Nginx):** Dockerfile multi-stage en `frontend/Dockerfile` con stage `builder` (`node:20-alpine` + `corepack enable pnpm` + `pnpm run build`) y stage `runtime` (`nginx:alpine` < 30 MB). Configuración `frontend/nginx.conf` con SPA fallback (`try_files $uri $uri/ /index.html`), proxy inverso `/api/` hacia `backend:8000`, caché inmutable para assets con hash y cabeceras de seguridad.
- **T10 (Docker Compose con Healthchecks y Dependencias):** Orquestación integral en `docker-compose.yml` de 3/3 servicios con healthcheck: `postgres` (`pg_isready`), `backend` (Python urllib `/health`) y `frontend` (Wget `/health`). Dependencias condicionadas con `depends_on: { condition: service_healthy }` y volumen nombrado `postgres_data`.

### Retrospectiva del Ciclo (Clase 27/10/2026)
1. **Flujo y Trazabilidad:** El flujo GitHub Flow documentado (1 rama corta por ticket y merge con `--no-ff` hacia `dev`) funcionó a la perfección, logrando un historial 100% auditable con Conventional Commits y sin branches huérfanas.
2. **Arquitectura Limpia:** Separar las reglas de negocio en funciones puras libres de HTTP y bases de datos (T1–T3) permitió alcanzar 48 tests unitarios deterministas que se ejecutan en menos de 1 segundo.
3. **Decisión de Testing de Integración:** Sobre la marcha elegimos SQLite in-memory para los tests del repository (T4–T5) en lugar de levantar PostgreSQL externo; esto garantizó aislamiento total entre tests, velocidad instantánea y portabilidad en cualquier máquina.
4. **Eficiencia en Docker Multi-Stage:** El patrón builder/runtime (T7 y T9) demostró ser clave para la seguridad (al correr sin privilegios de root) y redujo drásticamente el peso de las imágenes al descartar compiladores y dependencias de test.
5. **Orquestación Robusta:** Los healthchecks en Docker Compose (T10) resolvieron definitivamente las condiciones de carrera al arrancar, asegurando que la base de datos esté lista para recibir consultas antes de que el backend empiece a servir tráfico.

---

## [v0.1.0] - 2026-10-27

### Added
- **T1:** Scaffold del proyecto: estructura modular según TRD (*Screaming Architecture*), `.env.example` con variables de entorno y sección inicial de levantamiento en `README.md`.
- **T2:** Backend mínimo con FastAPI y gestor `uv`: endpoints `GET /health` (`{"status":"ok"}`) y `GET /api/v1/cursos` con estructura paginada según `BackendSchema.md`.
- **T3:** Frontend mínimo con React 19 y Vite: componentes semánticos y accesibles (`BarraNavegacion`, `CatalogoCursos`, `TarjetaCurso`, `PiePagina`), proxy `/api` en `vite.config.js` y manejo de estados (cargando, error, lista vacía).
- **T4:** Entorno de desarrollo con Docker Compose: orquestación de servicios `postgres` (18.6), `backend` y `frontend` con volumen persistente `postgres_data`.
