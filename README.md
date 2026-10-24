# Aprende-Gratis

> **WebApp de gestión de comunidad de cursos:** catálogo comunitario de cursos gratuitos
> (aportados por usuarios y validados por moderadores) + roadmaps personales de aprendizaje.
>
> **Estado del proyecto:** 📚 **Instancia A (Documentación)** — entregada y pendiente de aprobación docente.

**Stack tecnológico registrado:** React 19 + Vite + pnpm · FastAPI + uv · PostgreSQL 18.6 · Docker Compose (dev)

---

## Qué hace Aprende-Gratis

Aprende-Gratis reúne en un único catálogo comunitario enlaces a cursos 100% gratuitos y de libre acceso dispersos en la web (YouTube, plataformas universitarias, MOOCs). Cualquier usuario registrado puede **aportar** cursos indicando su enlace y metadatos; tras una **validación** por parte de un moderador para asegurar la gratuidad y el funcionamiento del link, el curso ingresa al **catálogo comunitario** público. A partir de allí, cada estudiante puede incorporarlo a su **roadmap personal** para establecer su propio orden de estudio y dar seguimiento a su estado de avance (`pendiente`, `en_curso`, `completado`).

---

## Documentación del sistema (Instancia A)

| Documento | Pregunta clave que responde | Enlace directo |
|-----------|-----------------------------|----------------|
| **SPEC** | ¿Qué nos pidieron construir y qué decidimos sobre los vacíos? | [docs/SPEC.md](docs/SPEC.md) |
| **PRD** | ¿Para quién, qué problema resuelve, qué hace y qué NO hace? | [docs/PRD.md](docs/PRD.md) |
| **TRD** | ¿Cómo lo construimos técnicamente, con qué arquitectura y por qué? | [docs/TRD.md](docs/TRD.md) |
| **UX-UI** | ¿Cómo se ve, se siente y se comporta la interfaz (tokens y componentes)? | [docs/UX-UI.md](docs/UX-UI.md) |
| **APPFlow** | ¿Qué pantallas existen, cómo se navegan y qué flujos conectan con la API? | [docs/APPFlow.md](docs/APPFlow.md) |
| **BackendSchema** | ¿Qué modelo de datos persistimos y qué API REST expone el backend? | [docs/BackendSchema.md](docs/BackendSchema.md) |
| **Implementation Plan** | ¿En qué orden construimos las tareas y cómo verificamos el MVP? | [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) |

Adicionalmente, se incluye la [Checklist de autoregla de entrega](docs/CHECKLIST_AUTOREGLA.md) verificada punto por punto previo al envío.

---

## Cómo revisar este repositorio

- Todos los documentos están escritos en **GitHub Flavored Markdown (GFM)** y se renderizan nativamente en la web de GitHub.
- Los diagramas de arquitectura, flujo y base de datos utilizan sintaxis nativa **Mermaid** (`flowchart`, `erDiagram`, `stateDiagram-v2`).
- Para previsualización local: abrir en VS Code y presionar `Ctrl + Shift + V` (o `Ctrl + K, V`).

---

## Estado del trabajo y fases

| Instancia | Alcance | Estado |
|-----------|---------|:------:|
| **Instancia A — Documentación y Git** | Especificación, 7 documentos técnicos completos, README y .gitignore | ✅ Completa |
| **Instancia B — Desarrollo de MVP (P0)** | Construcción guiada por tareas M0 a M4 mediante Docker Compose | ⏳ En espera de aprobación |
| **Instancia C — Clase presencial (27/10)** | Pruebas unitarias/integración, Docker multi-stage y gestión del cambio | ⏳ Planificada |

---

## Versionado y flujo de trabajo

- **Flujo de Git:** **GitHub Flow** (documentado en [TRD §4.2](docs/TRD.md#42-flujo-de-git--github-flow)). La rama `main` se mantiene siempre estable y protegida. Cada documento o tarea se desarrolla en una rama corta aislada (`docs/...` en Instancia A, `feat/...` en Instancia B) y se integra mediante **Pull Request con merge commit** explícito para evidenciar el historial de ramas.
- **Convención de commits:** [Conventional Commits](https://www.conventionalcommits.org/) en idioma español (`docs:`, `feat:`, `fix:`, `chore:`, `docker:`, `test:`), con mensajes descriptivos en imperativo.

---

## Instrucciones previstas para la Instancia B (Desarrollo)

Una vez aprobada la fase de documentación y habilitado el ticket T1, el proyecto levantará íntegramente en entorno local mediante Docker:

```bash
# 1. Clonar el repositorio
git clone https://github.com/steccanellajulian/roadmap-cursos.git
cd roadmap-cursos

# 2. Configurar variables de entorno iniciales
cp .env.example .env

# 3. Levantar los 4 servicios con Docker Compose
docker compose up -d

# 4. Accesos a los servicios:
# - Frontend SPA (React + Vite):    http://localhost:5173
# - Backend API Docs (FastAPI):      http://localhost:8000/docs
# - Bandeja de emails (Mailpit):     http://localhost:8025
# - Base de datos PostgreSQL:        localhost:5432
```

---

## Licencia y contexto académico

Trabajo Práctico para la materia **Desarrollo de Software** — Sección S34 · Ciclo lectivo 2026.  
Facultad Regional La Plata — Universidad Tecnológica Nacional (UTN).
