/**
 * Tests para useCursos (Ticket T6)
 * 
 * Especificaciones validadas:
 * [x] Carga inicial: loading=true -> loading=false con datos
 * [x] Error de red: estado de error seteado, lista vacía
 * [x] setPage(n) -> recarga con page=n (y resetea a 1 si cambia el filtro)
 * [x] refetch() -> recarga con parámetros actuales
 * 
 * Compatible tanto con Vitest como con el test runner nativo de Node.js (node:test).
 */
import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import { crearGestorCursos } from './useCursos.js'

describe('useCursos — Tests del hook principal de Catálogo', () => {
  // Cursos de prueba simulados
  const cursosMock = [
    { id: 1, titulo: 'Curso FastAPI', tema: 'Backend' },
    { id: 2, titulo: 'Curso React', tema: 'Frontend' },
  ]

  it('Carga inicial: loading=true -> loading=false con datos', async () => {
    // Arrange: mock de fetch que devuelve 2 cursos
    const mockFetch = async (url) => {
      return {
        ok: true,
        status: 200,
        json: async () => ({ items: cursosMock, total: 2, page: 1, page_size: 20 }),
      }
    }

    // Act: se inicializa el gestor del hook
    const gestor = crearGestorCursos({ fetchFn: mockFetch })

    // Assert inicial: loading=true al comenzar
    assert.strictEqual(gestor.getState().cargando, true)
    assert.deepStrictEqual(gestor.getState().cursos, [])

    // Esperar a que resuelva la carga inicial
    await gestor.inicializacionPromise

    // Assert final: loading=false y datos cargados
    const estadoFinal = gestor.getState()
    assert.strictEqual(estadoFinal.cargando, false)
    assert.strictEqual(estadoFinal.error, null)
    assert.strictEqual(estadoFinal.cursos.length, 2)
    assert.strictEqual(estadoFinal.cursos[0].titulo, 'Curso FastAPI')
    assert.strictEqual(estadoFinal.total, 2)
  })

  it('Error de red: estado de error seteado, lista vacía', async () => {
    // Arrange: mock de fetch que simula una caída del servidor
    const mockFetchError = async () => {
      throw new Error('Fallo de conexión al backend')
    }

    // Act: se inicia la petición
    const gestor = crearGestorCursos({ fetchFn: mockFetchError })
    await gestor.inicializacionPromise

    // Assert: error seteado, cargando=false y lista vacía
    const estado = gestor.getState()
    assert.strictEqual(estado.cargando, false)
    assert.strictEqual(estado.cursos.length, 0)
    assert.ok(estado.error.includes('Fallo de conexión al backend'))
  })

  it('setPage(n) -> recarga con page=n (y resetea a 1 si cambia el filtro)', async () => {
    const urlsLlamadas = []
    const mockFetch = async (url) => {
      urlsLlamadas.push(url)
      return {
        ok: true,
        status: 200,
        json: async () => ({ items: cursosMock, total: 10, page: 1, page_size: 20 }),
      }
    }

    const gestor = crearGestorCursos({ fetchFn: mockFetch })
    await gestor.inicializacionPromise

    // Act 1: Cambiar de página con setPage(2)
    await gestor.setPage(2)

    // Assert 1: el estado pasa a page=2 y la URL solicitó page=2
    assert.strictEqual(gestor.getState().page, 2)
    assert.ok(urlsLlamadas[urlsLlamadas.length - 1].includes('page=2'))

    // Act 2: Modificar el filtro de búsqueda con setFiltro('python')
    await gestor.setFiltro('python')

    // Assert 2: la página se reseteó automáticamente a 1 y la URL incluye el filtro
    assert.strictEqual(gestor.getState().page, 1, 'Debe resetear a página 1 al cambiar el filtro')
    assert.strictEqual(gestor.getState().filtro, 'python')
    const ultimaUrl = urlsLlamadas[urlsLlamadas.length - 1]
    assert.ok(ultimaUrl.includes('page=1'), 'La URL solicitada debe pedir page=1')
    assert.ok(ultimaUrl.includes('q=python'), 'La URL debe incluir el parámetro de búsqueda')
  })

  it('refetch() -> recarga con parámetros actuales', async () => {
    let llamadas = 0
    const urlsLlamadas = []
    const mockFetch = async (url) => {
      llamadas++
      urlsLlamadas.push(url)
      return {
        ok: true,
        status: 200,
        json: async () => ({ items: cursosMock, total: 2, page: 2, page_size: 20 }),
      }
    }

    // Arrange: inicializado en página 2 y filtro 'react'
    const gestor = crearGestorCursos({
      initialPage: 2,
      initialFiltro: 'react',
      fetchFn: mockFetch,
    })
    await gestor.inicializacionPromise
    assert.strictEqual(llamadas, 1)

    // Act: ejecutar refetch
    await gestor.refetch()

    // Assert: se ejecutó una segunda llamada con los mismos parámetros
    assert.strictEqual(llamadas, 2)
    const urlRefetch = urlsLlamadas[1]
    assert.ok(urlRefetch.includes('page=2'))
    assert.ok(urlRefetch.includes('q=react'))
  })
})
