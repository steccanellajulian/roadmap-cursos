# Checklist de Autoregla — Instancia A (Entrega de Documentación)

> Esta checklist consolida todos los criterios de evaluación exigidos en la consigna de la cátedra
> y en las definiciones de "Cuándo está bien" de cada una de las 7 plantillas de documentación.
> **Estado:** 100% verificada antes de la entrega formal.

---

## 1. Estructura y Reglas de Oro (§3 y §4.1 de la consigna)

- [x] **Gate de aprobación:** Cero archivos fuente de la aplicación (`.py`, `.js`, `.jsx`, `.ts`, lockfiles, `node_modules`, `.venv`...) en el repositorio.
- [x] **Estructura de archivos exacta:**
  - `README.md` en la raíz (completo, adaptado del ejemplo oficial, sin placeholders).
  - `.gitignore` en la raíz (preparado para React/Vite/pnpm + FastAPI/uv + Docker).
  - Directorio `docs/` conteniendo exclusivamente los 7 documentos exigidos.
- [x] **Sin archivos temporales ni de ejemplo:** Se removieron archivos como `UX-UI_EJEMPLO.md` o borradores de clase del árbol versionado para mantener un repo profesional.

---

## 2. Versionado y Flujo de Git (§3, §4.3 de la consigna y TRD §4.2)

- [x] **Primer commit histórico:** Contiene la `SPEC.md` original tal cual fue entregada en el aula, sin editar (commit `338450c` en GitHub).
- [x] **Conventional Commits:** El 100% de los commits utilizan la convención estricta (`docs:`, `feat:`, `fix:`, etc.) en idioma español y con mensajes imperativos específicos.
- [x] **Flujo de Git documentado:** Se definió y justificó **GitHub Flow** en el [TRD §4.2](TRD.md#42-flujo-de-git--github-flow) y en el [README](../README.md#versionado-y-flujo-de-trabajo).
- [x] **Historial observable:** El trabajo no se commitea directo sobre `main`; se evidencia la creación e integración de ramas mediante Pull Requests con merge commit.

---

## 3. Calidad y Completitud de los 7 Documentos

### 3.1 `docs/SPEC.md` (Refinamiento de Especificación)
- [x] Explica el producto con identidad propia (**Aprende-Gratis**) y visión clara.
- [x] Un lector externo entiende el producto completo leyendo únicamente este documento.
- [x] Se resolvieron y justificaron los 11 vacíos detectados en la SPEC de clase (§8).
- [x] Se registraron las versiones exactas verificadas de las herramientas e imágenes (§6).
- [x] Se eliminaron todos los textos de instrucción y corchetes `[...]` de la plantilla.

### 3.2 `docs/PRD.md` (Product Requirements Document)
- [x] Resumen ejecutivo, objetivos cuantificables y 2 personas arquetípicas detalladas.
- [x] Mínimo de 6 historias de usuario cumplido (cuenta con 6 P0 y 1 P1), todas en formato Como/Quiero/Para.
- [x] Criterios de aceptación verificables en formato Dado/Cuando/Entonces.
- [x] El "Out of Scope" (fuera de alcance) está definido con la misma claridad que las funcionalidades activas (§8).
- [x] Matriz de Requisitos Funcionales (RF), No Funcionales (RNF) y Reglas de Negocio (BR) unificadas y numeradas.

### 3.3 `docs/TRD.md` (Technical Requirements Document)
- [x] Stack y versiones exactas verificadas en npm, PyPI y Docker Hub (§1).
- [x] 8 decisiones técnicas clave (TD-001 a TD-008) con alternativas analizadas, opción elegida y justificación de trade-offs.
- [x] Diagrama de arquitectura en capas y árbol de directorios con **Screaming Architecture** (`identidad`, `catalogo`, `aportes`, `roadmap`).
- [x] Topología de servicios en Docker Compose (Postgres 18.6, FastAPI, Vite, Mailpit).
- [x] Formato unificado de errores de API, tabla de variables de entorno y estrategia de excepciones.

### 3.4 `docs/UX-UI.md` (Guía Visual de Estilos)
- [x] Inspiración clara y demostrable en Google Material Design 3.
- [x] Sistema de Design Tokens con valores numéricos y colores HEX concretos (azul primario `#1a73e8`, tipografía Roboto, radios píldora).
- [x] Ratios de contraste WCAG AA verificados numéricamente para cada par de colores.
- [x] Estrategia **Mobile-First con Mejora Progresiva**: CSS base para 360px sin media queries; `@media (min-width: 768px)` y `(min-width: 1024px)` para expansión.
- [x] Anatomía detallada y estados completos (default, hover, focus-visible, active, disabled, loading) para todos los componentes.
- [x] Especificación de accesibilidad para Menú Sándwich (`aria-expanded`, `aria-controls`), Modales (focus trap) y Formularios.

### 3.5 `docs/APPFlow.md` (Mapa del Sitio y Flujos)
- [x] Diagrama Sitemap completo en Mermaid.
- [x] Tabla de rutas exhaustiva asociando cada pantalla a su requisito de autenticación y rol.
- [x] Ficha técnica por pantalla con componentes, estados visuales y endpoints exactos del backend que consume.
- [x] 4 flujos de usuario detallados paso a paso de punta a punta (incluyendo validación y recuperación de contraseña).
- [x] Tabla de manejo de estados globales (sin sesión, token expirado, rate limit 429, caída de red).

### 3.6 `docs/BackendSchema.md` (Base de Datos y API REST)
- [x] Diagrama Entidad-Relación en Mermaid con llaves foráneas y tipos de relación.
- [x] Definición DDL de tablas en PostgreSQL 18.6 con tipos de datos, constraints `UNIQUE`, `NOT NULL`, `CHECK` e índices de rendimiento.
- [x] Diagrama de estados de ciclo de vida del curso (`en_revision` -> `publicado` / `rechazado`).
- [x] Especificación completa de endpoints REST `/api/v1` con métodos HTTP, query params, payloads JSON de request y códigos de respuesta (200, 201, 204, 400, 401, 403, 404, 409, 422, 429).

### 3.7 `docs/IMPLEMENTATION_PLAN.md` (Plan de Implementación)
- [x] Criterio inequívoco de éxito del MVP verificable en máquina limpia con `docker compose up`.
- [x] Grafo de dependencias lógicas entre módulos (M0 a M4).
- [x] Tareas desglosadas con criterio de "Hecho cuando..." comprobable mediante comandos curl o interacciones UI.
- [x] Tabla de seguimiento lista para la Instancia B con mapeo de ramas y commits.
- [x] Estrategia de testing formal para la clase del 27/10 (unit tests en services con cobertura >= 80%, integration tests en repositories).

---

## 4. Coherencia Transversal entre Documentos (§9 de la consigna)

- [x] **Cero pantallas sin endpoint:** Cada vista descripta en `APPFlow.md` consume endpoints formalmente tipados en `BackendSchema.md`.
- [x] **Cero historias P0 sin tarea:** Cada una de las 6 historias de usuario P0 del `PRD.md` cuenta con sus respectivas tareas de backend y frontend en `IMPLEMENTATION_PLAN.md`.
- [x] **Cero rutas inventadas:** Los paths declarados en el frontend (`/catalogo`, `/roadmap`, `/aportar`, `/validar`, etc.) coinciden unívocamente a lo largo de SPEC, PRD, APPFlow e Implementation Plan.
- [x] **Cumplimiento estricto de las 4 prácticas obligatorias:**
  1. *Mobile-First con mejora progresiva:* Detallado en `SPEC.md` §7, `PRD.md` RNF-002, `TRD.md` §5 y `UX-UI.md` §3.
  2. *Paginación:* Especificada en `TRD.md` TD-002, `BackendSchema.md` §3 y `UX-UI.md` §4.5.
  3. *Menú Sándwich:* Especificado en `TRD.md` §5, `UX-UI.md` §4.4 y `APPFlow.md` §3.
  4. *Screaming Architecture:* Estructurada en `TRD.md` §3.2, `BackendSchema.md` §3 y `IMPLEMENTATION_PLAN.md` Tarea 0.1.

---

## 5. Verificación de Entrega

- [x] Todos los bloques de diagramas Mermaid (`erDiagram`, `flowchart`, `stateDiagram-v2`) renderizan de forma válida sin errores sintácticos.
- [x] No hay enlaces rotos relativos entre documentos.
