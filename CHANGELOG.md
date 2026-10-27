# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.1.0] - 2026-10-27

### Added
- **T1:** Scaffold del proyecto: estructura modular según TRD (*Screaming Architecture*), `.env.example` con variables de entorno y sección inicial de levantamiento en `README.md`.
- **T2:** Backend mínimo con FastAPI y gestor `uv`: endpoints `GET /health` (`{"status":"ok"}`) y `GET /api/v1/cursos` con estructura paginada según `BackendSchema.md`.
- **T3:** Frontend mínimo con React 19 y Vite: componentes semánticos y accesibles (`BarraNavegacion`, `CatalogoCursos`, `TarjetaCurso`, `PiePagina`), proxy `/api` en `vite.config.js` y manejo de estados (cargando, error, lista vacía).
- **T4:** Entorno de desarrollo con Docker Compose: orquestación de servicios `postgres` (18.6), `backend` y `frontend` con volumen persistente `postgres_data`.
