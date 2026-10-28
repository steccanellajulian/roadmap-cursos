/**
 * Hook personalizado: useCursos
 * 
 * Responsabilidad:
 * Gestiona el ciclo de vida del catálogo de cursos (carga inicial, paginación,
 * búsqueda/filtro y reintentos) desacoplando la lógica de negocio del componente visual.
 * 
 * Especificaciones de Ticket T6:
 * - Carga inicial: loading=true -> loading=false con datos
 * - Error de red: estado de error seteado, lista vacía
 * - setPage(n): recarga con page=n (y resetea a 1 si cambia el filtro)
 * - refetch(): recarga con parámetros actuales
 */
import { useState, useEffect } from 'react'

/**
 * Gestor puro de estado y peticiones para el catálogo de cursos.
 * Permite ejecutar pruebas unitarias deterministas sin requerir emulación DOM pesada.
 */
export function crearGestorCursos({
  initialPage = 1,
  initialPageSize = 20,
  initialFiltro = '',
  fetchFn = globalThis.fetch,
} = {}) {
  const state = {
    cursos: [],
    total: 0,
    page: initialPage,
    pageSize: initialPageSize,
    filtro: initialFiltro,
    cargando: true,
    error: null,
  }

  const listeners = new Set()

  function notify() {
    const snapshot = { ...state }
    for (const listener of listeners) {
      listener(snapshot)
    }
  }

  async function cargarCursos(p = state.page, q = state.filtro) {
    state.cargando = true
    state.error = null
    notify()

    try {
      const params = new URLSearchParams()
      params.set('page', String(p))
      params.set('page_size', String(state.pageSize))
      if (q && q.trim()) {
        params.set('q', q.trim())
      }

      const respuesta = await fetchFn(`/api/v1/cursos?${params.toString()}`)
      if (!respuesta.ok) {
        throw new Error(`Error en la respuesta del servidor (código ${respuesta.status})`)
      }

      const datos = await respuesta.json()
      state.cursos = datos.items || []
      state.total = datos.total ?? state.cursos.length
      state.page = p
      state.filtro = q
      state.error = null
    } catch (err) {
      state.cursos = []
      state.error = err.message || 'Error de conexión con el backend'
    } finally {
      state.cargando = false
      notify()
    }
  }

  function setPage(nuevaPagina) {
    state.page = nuevaPagina
    return cargarCursos(nuevaPagina, state.filtro)
  }

  function setFiltro(nuevoFiltro) {
    state.filtro = nuevoFiltro
    state.page = 1 // Spec T6: resetea a 1 si cambia el filtro
    return cargarCursos(1, nuevoFiltro)
  }

  function refetch() {
    return cargarCursos(state.page, state.filtro)
  }

  function getState() {
    return { ...state }
  }

  function subscribe(listener) {
    listeners.add(listener)
    return () => listeners.delete(listener)
  }

  // Carga inicial automática
  const inicializacionPromise = cargarCursos(initialPage, initialFiltro)

  return {
    getState,
    subscribe,
    setPage,
    setFiltro,
    refetch,
    cargarCursos,
    inicializacionPromise,
  }
}

/**
 * Hook de React para componentes.
 */
export function useCursos(options = {}) {
  const [gestor] = useState(() => crearGestorCursos(options))
  const [state, setState] = useState(() => gestor.getState())

  useEffect(() => {
    const unsubscribe = gestor.subscribe((nuevoEstado) => {
      setState(nuevoEstado)
    })
    return unsubscribe
  }, [gestor])

  return {
    ...state,
    setPage: gestor.setPage,
    setFiltro: gestor.setFiltro,
    refetch: gestor.refetch,
  }
}
