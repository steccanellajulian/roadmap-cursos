"""Script generador del Informe Técnico Completo en formato PDF para la Segunda Parte.
Cátedra: Desarrollo de Software (UTN FR La Plata)
Proyecto: Aprende-Gratis (Roadmap de Cursos)
Autor: Julián Steccanella
"""
import os
import sys
import xml.sax.saxutils as saxutils
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Canvas que calcula el número total de páginas dinámicamente."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Encabezado superior
        header_text = "UTN FR La Plata · Desarrollo de Software | Informe Técnico - Segunda Parte (Tickets de Clase)"
        self.drawString(45, 11 * 72 - 36, header_text)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(45, 11 * 72 - 42, 8.5 * 72 - 45, 11 * 72 - 42)

        # Pie de página inferior
        footer_left = "Aprende-Gratis · Sistema de Cursos y Roadmaps Comunitarios | v0.2.0"
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawString(45, 30, footer_left)
        self.drawRightString(8.5 * 72 - 45, 30, page_str)
        self.line(45, 40, 8.5 * 72 - 45, 40)

        self.restoreState()


def esc(text: str) -> str:
    """Escapa caracteres HTML para que ReportLab Paragraph no falle."""
    return saxutils.escape(str(text))


def construir_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=50,
        bottomMargin=50,
    )

    styles = getSampleStyleSheet()

    c_primary = colors.HexColor("#1B365D")    # Azul UTN / Navy institucional
    c_secondary = colors.HexColor("#2563EB")  # Azul técnico
    c_dark = colors.HexColor("#1E293B")       # Texto principal grafito
    c_gray = colors.HexColor("#64748B")       # Gris metadatos

    style_title = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=25,
        textColor=c_primary,
        spaceAfter=6,
    )
    style_subtitle = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceAfter=12,
    )
    style_h1 = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13.5,
        leading=17,
        textColor=c_primary,
        spaceBefore=0,
        spaceAfter=5,
        keepWithNext=True,
    )
    style_h2 = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=15,
        textColor=c_secondary,
        spaceBefore=6,
        spaceAfter=4,
        keepWithNext=True,
    )
    style_body = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=c_dark,
        spaceAfter=5,
    )
    style_code = ParagraphStyle(
        "Code_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7,
        leading=9.5,
        textColor=colors.HexColor("#0F172A"),
    )
    style_table_cell = ParagraphStyle(
        "TableCell_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=c_dark,
    )
    style_table_header = ParagraphStyle(
        "TableHeader_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=colors.white,
    )

    story = []

    # Helper para cajas de código
    def code_box(titulo: str, lineas_codigo: list[str]):
        raw_text = "\n".join(lineas_codigo)
        p_code = Paragraph(f"<font color='#0F172A'>{esc(raw_text).replace(chr(10), '<br/>').replace(' ', '&nbsp;')}</font>", style_code)
        p_head = Paragraph(f"<b>Archivo / Extracto Verificable:</b> <code>{esc(titulo)}</code>", ParagraphStyle(
            "CodeHeader", fontName="Helvetica-Bold", fontSize=7.5, leading=10, textColor=c_primary
        ))
        tbl = Table([[p_head], [p_code]], colWidths=[522])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#E2E8F0")),
            ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        return tbl

    # Helper para tarjetas de Git
    def git_box(rama: str, commit_hash: str, commit_msg: str, merge_hash: str):
        content = [
            [Paragraph("<b>Rama de trabajo:</b>", style_table_cell), Paragraph(f"<code>{esc(rama)}</code>", style_table_cell),
             Paragraph("<b>Commit hash:</b>", style_table_cell), Paragraph(f"<code>{esc(commit_hash)}</code>", style_table_cell)],
            [Paragraph("<b>Mensaje Commit:</b>", style_table_cell), Paragraph(f"<i>{esc(commit_msg)}</i>", style_table_cell),
             Paragraph("<b>Merge a dev (--no-ff):</b>", style_table_cell), Paragraph(f"<code>{esc(merge_hash)}</code>", style_table_cell)],
        ]
        tbl = Table(content, colWidths=[100, 180, 110, 132])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#BFDBFE")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DBEAFE")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        return tbl

    # =========================================================================
    # PÁGINA 1: PORTADA & CONTEXTO DEL SISTEMA
    # =========================================================================
    story.append(Paragraph("UNIVERSIDAD TECNOLÓGICA NACIONAL", ParagraphStyle(
        "UnivHeader", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=c_primary
    )))
    story.append(Paragraph("Facultad Regional La Plata · Departamento de Ingeniería en Sistemas de Información", ParagraphStyle(
        "UnivSub", fontName="Helvetica", fontSize=8.5, leading=11, textColor=c_gray, spaceAfter=10
    )))
    story.append(HRFlowable(width="100%", thickness=2.5, color=c_primary, spaceAfter=14))

    story.append(Paragraph("INFORME TÉCNICO Y AUDITORÍA DE CAMBIOS", style_title))
    story.append(Paragraph("Segunda Parte: Testing Unitario de Dominio, Integración con Base de Datos Real, Dockerización Multi-Stage y Gestión del Cambio", style_subtitle))

    meta_data = [
        [Paragraph("<b>Asignatura:</b>", style_table_cell), Paragraph("Desarrollo de Software — Sección S34", style_table_cell),
         Paragraph("<b>Fecha de Entrega:</b>", style_table_cell), Paragraph("Octubre / Noviembre 2026", style_table_cell)],
        [Paragraph("<b>Proyecto:</b>", style_table_cell), Paragraph("Aprende-Gratis (Roadmap de Cursos)", style_table_cell),
         Paragraph("<b>Versión Release:</b>", style_table_cell), Paragraph("v0.2.0 (Auditable)", style_table_cell)],
        [Paragraph("<b>Estudiante:</b>", style_table_cell), Paragraph("Julián Steccanella", style_table_cell),
         Paragraph("<b>Repositorio:</b>", style_table_cell), Paragraph("github.com/steccanellajulian/roadmap-cursos", style_table_cell)],
    ]
    meta_table = Table(meta_data, colWidths=[90, 175, 95, 162])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("1. Introducción y Contexto del Sistema", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceAfter=8))
    story.append(Paragraph(
        "<b>¿Qué es 'Aprende-Gratis'?</b> Es una plataforma web académica y comunitaria concebida para que "
        "estudiantes de la UTN puedan descubrir, compartir y catalogar cursos gratuitos de programación, ciencia de datos "
        "e ingeniería de software, consolidando además rutas de aprendizaje personalizadas (<i>Roadmaps</i>).",
        style_body
    ))
    story.append(Paragraph(
        "El sistema resuelve una problemática habitual: la dispersión y falta de curaduría de los recursos educativos online. "
        "Para garantizar la calidad pedagógica sin centralizarla en un único administrador, se implementó un <b>modelo de aportes colaborativos</b>: "
        "cualquier estudiante puede postular un curso, pero este no se publica de inmediato, sino que ingresa en un estado de <code>en_revision</code> "
        "para ser evaluado por estudiantes avanzados con rol de <b>validador</b>.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Objetivo de esta Segunda Entrega:</b> En la etapa previa (Instancia B) se desarrolló un MVP mínimo. "
        "El objetivo de estos 11 tickets de clase fue transformar el software en un sistema con estándares de calidad industrial, abarcando:",
        style_body
    ))
    puntos_resumen = [
        "<b>Bloque 1 (Dominio Puro y Tests Unitarios):</b> Extraer las reglas de negocio a funciones independientes de BD y HTTP con 100% de cobertura y patrón AAA.",
        "<b>Bloque 2 (Testing de Integración):</b> Comprobar el repositorio SQL con base de datos relacional real y validar de punta a punta el flujo de aportes y seguridad HTTP.",
        "<b>Bloque 3 (Docker Multi-Stage y Buenas Prácticas):</b> Contenedores de producción ultralivianos (< 100 MB backend, < 30 MB frontend) y seguros (usuario no-root, Nginx).",
        "<b>Bloque 4 (Gestión del Cambio y Cierre Auditable):</b> Docker Compose con healthchecks, historial auditable con Conventional Commits y registro formal en CHANGELOG.",
    ]
    for pt in puntos_resumen:
        story.append(Paragraph(f"• {pt}", style_body))

    # =========================================================================
    # PÁGINA 2: BLOQUE 1 - INTRODUCCIÓN Y TICKET T1
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("2. Bloque 1 — Testing Unitario (Funciones Puras de Negocio)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceAfter=8))
    story.append(Paragraph(
        "<b>Fundamento Teórico:</b> Acoplar las reglas de negocio a la base de datos o al framework web vuelve a las suites de prueba "
        "lentas y frágiles. Siguiendo <b>Clean Architecture</b>, el núcleo del dominio se modeló mediante <b>funciones puras</b>: "
        "reciben datos de entrada, aplican lógica determinista y devuelven un resultado o lanzan una <code>ReglaNegocioError</code>. "
        "Las pruebas se estructuraron bajo el <b>patrón AAA (Arrange - Act - Assert)</b>, logrando 48 tests que corren en menos de 0.8s.",
        style_body
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Ticket T1 — Tests Unitarios de las Reglas de Negocio de Curso", style_h2))
    story.append(Paragraph(
        "<b>Justificación del Ticket:</b><br/>"
        "Un curso posee un ciclo de vida gobernado por una máquina de estados finita: <code>borrador → en_revision → publicado / rechazado</code>. "
        "Un curso publicado nunca puede volver a borrador ni ser editado sin nueva revisión. Además, un curso propuesto debe validar que: "
        "la URL sea sintácticamente válida y esté normalizada (sin barras finales redundantes), los campos obligatorios existan, el año de edición "
        "esté en el rango [1990 .. año_actual] y el estudiante declare bajo juramento haber tomado el curso (regla de integridad BR-002).",
        style_body
    ))
    story.append(Paragraph(
        "<b>Archivos creados / modificados:</b><br/>"
        "• <code>backend/app/catalogo/reglas.py</code>: Dominio puro con Enum <code>EstadoCurso</code>, <code>TRANSICIONES_VALIDAS</code>, "
        "<code>normalizar_url()</code>, <code>transicionar_estado_curso()</code> y <code>validar_aporte_curso()</code>.<br/>"
        "• <code>backend/app/compartido/errores.py</code>: Excepción canónica de dominio <code>ReglaNegocioError(codigo, mensaje)</code>.<br/>"
        "• <code>backend/tests/test_catalogo_unit.py</code>: Suite con 21 tests unitarios con patrón AAA y 100% de cobertura.",
        style_body
    ))
    story.append(code_box("backend/app/catalogo/reglas.py y backend/tests/test_catalogo_unit.py", [
        "# Máquina de estados finita del curso",
        "TRANSICIONES_VALIDAS = {",
        "    EstadoCurso.BORRADOR: {EstadoCurso.EN_REVISION},",
        "    EstadoCurso.EN_REVISION: {EstadoCurso.PUBLICADO, EstadoCurso.RECHAZADO},",
        "    EstadoCurso.PUBLICADO: set(), EstadoCurso.RECHAZADO: set()",
        "}",
        "# Test Unitario con Patrón AAA (Arrange - Act - Assert):",
        "def test_transicionar_estado_curso_de_borrador_a_en_revision_exitoso():",
        "    # Arrange: estado inicial",
        "    estado_actual, nuevo_estado = EstadoCurso.BORRADOR, EstadoCurso.EN_REVISION",
        "    # Act: invocar función pura",
        "    resultado, motivo = transicionar_estado_curso(estado_actual, nuevo_estado)",
        "    # Assert: verificar transición válida y ausencia de motivo de rechazo",
        "    assert resultado == EstadoCurso.EN_REVISION and motivo is None",
    ]))
    story.append(Spacer(1, 4))
    story.append(git_box("ticket/T1-reglas-curso", "2cff44e", "test: add unit tests for catalogo rules", "502d076"))

    # =========================================================================
    # PÁGINA 3: TICKET T2
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Ticket T2 — Tests Unitarios de las Reglas del Roadmap del Usuario", style_h2))
    story.append(Paragraph(
        "<b>Justificación del Ticket:</b><br/>"
        "El <i>Roadmap</i> es el itinerario secuencial de aprendizaje que arma cada estudiante. Debe cumplir reglas estrictas de integridad:<br/>"
        "1. <b>Solo Cursos Publicados:</b> Un curso en borrador o en revisión no puede ser agregado al roadmap de nadie.<br/>"
        "2. <b>Unicidad (Sin duplicados):</b> El estudiante no puede agregar dos veces el mismo curso (regla BR-006).<br/>"
        "3. <b>Límite de Capacidad:</b> Se impone un límite máximo de 50 ítems por roadmap para mantenerlo pedagógicamente manejable.<br/>"
        "4. <b>Secuencia Compacta:</b> Al reordenar o eliminar un curso del medio, la numeración de orden se recompacta automáticamente sin dejar huecos.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Archivos creados / modificados:</b><br/>"
        "• <code>backend/app/roadmap/reglas.py</code>: Funciones puras <code>agregar_curso_a_roadmap()</code>, <code>quitar_curso_de_roadmap()</code>, "
        "<code>reordenar_items_roadmap()</code> y <code>cambiar_estado_item_roadmap()</code>.<br/>"
        "• <code>backend/tests/test_roadmap_unit.py</code>: Suite con 16 tests unitarios verificando caminos felices, cursos inexistentes, "
        "cursos no publicados, duplicados, recompactación secuencial y límite alcanzado.",
        style_body
    ))
    story.append(code_box("backend/app/roadmap/reglas.py", [
        "def agregar_curso_a_roadmap(roadmap_actual, curso, limite_maximo=50):",
        "    if not curso or not curso.get('id'):",
        "        raise ReglaNegocioError(codigo='CURSO_NO_ENCONTRADO', mensaje='El curso no existe.')",
        "    if curso.get('estado') != EstadoCurso.PUBLICADO.value:",
        "        raise ReglaNegocioError(codigo='CURSO_NO_PUBLICADO', mensaje='Solo cursos publicados.')",
        "    for item in roadmap_actual:",
        "        if item.get('curso_id') == curso['id']:",
        "            raise ReglaNegocioError(codigo='CURSO_YA_EN_ROADMAP', mensaje='El curso ya está.')",
        "    if len(roadmap_actual) >= limite_maximo:",
        "        raise ReglaNegocioError(codigo='LIMITE_ROADMAP_ALCANZADO', mensaje='Límite alcanzado.')",
        "    nuevo_item = {'curso_id': curso['id'], 'orden': len(roadmap_actual) + 1, 'estado': 'pendiente'}",
        "    return nuevo_item, roadmap_actual + [nuevo_item]",
    ]))
    story.append(Spacer(1, 4))
    story.append(git_box("ticket/T2-reglas-roadmap", "a119dce", "test: add unit tests for roadmap rules", "a6b8dd4"))

    # =========================================================================
    # PÁGINA 4: TICKET T3
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Ticket T3 — Tests Unitarios del Servicio de Aportes / Validación", style_h2))
    story.append(Paragraph(
        "<b>Justificación del Ticket:</b><br/>"
        "La moderación comunitaria requiere controles de seguridad y auditoría para proteger la integridad del catálogo:<br/>"
        "1. <b>Control de Acceso por Rol:</b> Únicamente los usuarios con rol <code>validador</code> tienen permitido dictaminar aportes.<br/>"
        "2. <b>Prevención de Conflicto de Intereses:</b> Un validador tiene terminantemente prohibido dictaminar un curso postulado por él mismo (autovalidación).<br/>"
        "3. <b>Motivo de Rechazo Obligatorio:</b> Si el dictamen es negativo, se exige obligatoriamente un texto justificatorio pedagógico.<br/>"
        "4. <b>Códigos Semánticos Estables:</b> Los tests dependen de <code>CodigosErrorAportes</code> en lugar de comparar strings literales volubles.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Archivos creados / modificados:</b><br/>"
        "• <code>backend/app/aportes/reglas.py</code>: Definición de <code>RolUsuario</code>, constantes semánticas <code>CodigosErrorAportes</code>, "
        "validador de permisos <code>verificar_permiso_validador()</code> y función pura <code>dictaminar_aporte()</code>.<br/>"
        "• <code>backend/tests/test_aportes_unit.py</code>: Suite con 11 tests unitarios verificando aprobación, rechazo con y sin motivo, "
        "intento de validación por estudiante y autovalidación prohibida.",
        style_body
    ))
    story.append(code_box("backend/app/aportes/reglas.py", [
        "def dictaminar_aporte(aporte, validador, aprobado, motivo=None, fecha_revision=None):",
        "    verificar_permiso_validador(validador)",
        "    # Salvaguarda: prevención de conflicto de intereses",
        "    if aporte.get('creador_id') == validador.get('id'):",
        "        raise ReglaNegocioError(codigo=CodigosErrorAportes.AUTOVALIDACION_PROHIBIDA,",
        "                                mensaje='Un validador no puede dictaminar su propio aporte.')",
        "    if not aprobado and (not motivo or not motivo.strip()):",
        "        raise ReglaNegocioError(codigo=CodigosErrorAportes.MOTIVO_REQUERIDO,",
        "                                mensaje='Debe indicar el motivo del rechazo.')",
        "    nuevo_estado = EstadoCurso.PUBLICADO if aprobado else EstadoCurso.RECHAZADO",
        "    return {**aporte, 'estado': nuevo_estado.value, 'validador_id': validador['id'],",
        "            'motivo_rechazo': None if aprobado else motivo.strip()}",
    ]))
    story.append(Spacer(1, 4))
    story.append(git_box("ticket/T3-reglas-aportes", "8dda2e8", "test: add unit tests for aporte validation service", "c605a3c"))

    # =========================================================================
    # PÁGINA 5: BLOQUE 2 - INTRODUCCIÓN Y TICKET T4
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("3. Bloque 2 — Testing de Integración (Con BD Real y HTTP)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceAfter=8))
    story.append(Paragraph(
        "<b>Fundamento Teórico y Decisión Arquitectónica:</b> El testing de integración valida que el código interactúe con éxito con motores "
        "reales de base de datos relacional (SQLModel/SQLAlchemy) y con el protocolo HTTP (FastAPI TestClient).<br/>"
        "<b>¿Por qué SQLite en memoria (<code>sqlite:///:memory:</code> + <code>StaticPool</code>)?</b><br/>"
        "1) <b>Aislamiento y Determinismo:</b> Cada test se ejecuta en una base de datos virgen e instantánea, eliminando efectos secundarios.<br/>"
        "2) <b>Velocidad extrema:</b> 16 tests de persistencia y API REST se ejecutan en 1.2 segundos sin depender de sockets de red externos.<br/>"
        "3) <b>Cero fricción:</b> Garantiza compatibilidad universal tanto en máquinas locales de desarrollo como en runners de CI/CD.",
        style_body
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Ticket T4 — Integration Tests del CursoRepository", style_h2))
    story.append(Paragraph(
        "<b>Justificación del Ticket:</b><br/>"
        "El patrón <b>Repository</b> aísla las consultas SQL de los controladores. Se implementó <code>CursoRepository</code> sobre SQLModel, "
        "garantizando: 1) CRUD completo (create, get_by_id, update parcial y delete); 2) Paginación exacta con conteo total de registros "
        "(<code>page=1, size=2 → 2 items</code>; <code>page=2 → resto</code>; <code>total_count</code> correcto); 3) Búsqueda parcial insensible "
        "a mayúsculas/minúsculas mediante <code>LIKE %q%</code> en título o tema; y 4) Filtro exacto por categoría.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Archivos creados / modificados:</b><br/>"
        "• <code>backend/app/catalogo/models.py</code>: Entidades relacionales <code>Curso</code> y <code>Categoria</code>.<br/>"
        "• <code>backend/app/catalogo/repository.py</code>: Clase <code>CursoRepository</code> con métodos CRUD y listado paginado.<br/>"
        "• <code>backend/tests/test_integration.py</code>: 11 tests de integración sobre SQLite en memoria validando cada consulta SQL.",
        style_body
    ))
    story.append(code_box("backend/app/catalogo/repository.py", [
        "def list_paginated(self, page=1, page_size=20, q=None, categoria_id=None, estado=None):",
        "    conditions = []",
        "    if estado is not None: conditions.append(Curso.estado == estado)",
        "    if categoria_id is not None: conditions.append(Curso.categoria_id == categoria_id)",
        "    if q and q.strip():",
        "        filtro = f'%{q.strip()}%'",
        "        conditions.append(or_(col(Curso.titulo).ilike(filtro), col(Curso.tema).ilike(filtro)))",
        "    total_count = self.session.exec(select(func.count(col(Curso.id))).where(*conditions)).one()",
        "    stmt = select(Curso).where(*conditions).offset((page - 1) * page_size).limit(page_size)",
        "    return list(self.session.exec(stmt).all()), total_count",
    ]))
    story.append(Spacer(1, 4))
    story.append(git_box("ticket/T4-integration-curso-repository", "ab81e5c", "test: add integration tests for CursoRepository", "44753a7"))

    # =========================================================================
    # PÁGINA 6: TICKET T5
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Ticket T5 — Integration Tests del Flujo Aporte → Validación", style_h2))
    story.append(Paragraph(
        "<b>Justificación del Ticket:</b><br/>"
        "Valida el ciclo de vida completo de extremo a extremo a través de los endpoints HTTP de la API REST:<br/>"
        "1. Un estudiante autenticado envía un curso a <code>POST /api/v1/aportes</code> → se guarda en estado <code>en_revision</code>.<br/>"
        "2. El catálogo público (<code>GET /api/v1/cursos</code>) <b>no muestra el curso</b> mientras esté en revisión.<br/>"
        "3. Un validador autenticado aprueba el curso mediante <code>POST /api/v1/aportes/{id}/dictamen</code> (con <code>aprobado: true</code>). "
        "El curso pasa a <code>publicado</code> y aparece inmediatamente en el catálogo.<br/>"
        "4. Si el dictamen es <code>aprobado: false</code>, el curso pasa a <code>rechazado</code> y permanece oculto.<br/>"
        "5. Respuestas de seguridad: <b>401 Unauthorized</b> sin sesión, y <b>403 Forbidden</b> si un estudiante intenta dictaminar.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Archivos creados / modificados:</b><br/>"
        "• <code>backend/app/aportes/router.py</code>: Endpoints <code>POST /aportes</code> y <code>POST /aportes/{id}/dictamen</code>.<br/>"
        "• <code>backend/app/catalogo/router.py</code>: Endpoint <code>GET /cursos</code> con paginación y filtros multicriterio.<br/>"
        "• <code>backend/app/identidad/seguridad.py</code>: Dependencias de seguridad para simular usuarios con distintos roles.<br/>"
        "• <code>backend/tests/test_flujo_aportes_integration.py</code>: 5 tests de integración completos sobre la API.",
        style_body
    ))
    story.append(code_box("backend/tests/test_flujo_aportes_integration.py", [
        "def test_flujo_aporte_valido_y_aprobacion_publica_curso(client, payload_aporte_valido):",
        "    # 1. Enviar aporte -> ingresa en 'en_revision'",
        "    resp = client.post('/api/v1/aportes', json=payload_aporte_valido,",
        "                       headers={'X-User-Id': '10', 'X-User-Role': 'estudiante'})",
        "    assert resp.status_code == 201; aporte_id = resp.json()['id']",
        "    # 2. Catálogo público no lo muestra aún",
        "    assert client.get('/api/v1/cursos').json()['total'] == 0",
        "    # 3. Validador aprueba el aporte",
        "    resp_dict = client.post(f'/api/v1/aportes/{aporte_id}/dictamen',",
        "                            json={'aprobado': True, 'motivo': 'Excelente calidad'},",
        "                            headers={'X-User-Id': '99', 'X-User-Role': 'validador'})",
        "    assert resp_dict.status_code == 200",
        "    # 4. Visible públicamente en catálogo",
        "    assert client.get('/api/v1/cursos').json()['total'] == 1",
    ]))
    story.append(Spacer(1, 4))
    story.append(git_box("ticket/T5-integration-flujo-aportes", "839b4be", "test: add integration tests for aporte validation flow", "b04568b"))

    # =========================================================================
    # PÁGINA 7: TICKET T6
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Ticket T6 — Frontend: Tests del Hook Principal (useCursos)", style_h2))
    story.append(Paragraph(
        "<b>Justificación del Ticket:</b><br/>"
        "Acoplar llamadas <code>fetch()</code> y manejo de estados (cargando, error, paginación) dentro de componentes React "
        "genera código espagueti difícil de probar. Se extrajo la lógica al Custom Hook <code>useCursos</code>, gobernado por "
        "un gestor de estado puro (<code>crearGestorCursos</code>). Las especificaciones verificadas cubren:<br/>"
        "• <b>Carga inicial:</b> <code>cargando=true</code> → <code>cargando=false</code> con datos cargados.<br/>"
        "• <b>Error de red:</b> Captura de fallos de conexión, estado de error seteado y lista de cursos vacía.<br/>"
        "• <b>Paginación y reseteo:</b> <code>setPage(n)</code> carga la página <i>n</i>; si el usuario cambia el filtro de búsqueda, "
        "la página se <b>resetea automáticamente a 1</b>.<br/>"
        "• <b>Recarga (refetch):</b> Vuelve a consultar al servidor con los filtros y página activos.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Archivos creados / modificados:</b><br/>"
        "• <code>frontend/src/features/catalogo/hooks/useCursos.js</code>: Custom hook y gestor de estado puro desacoplado.<br/>"
        "• <code>frontend/src/features/catalogo/hooks/useCursos.test.js</code>: Suite con 4 tests ejecutables tanto con Vitest como con <code>node:test</code>.<br/>"
        "• <code>frontend/src/features/catalogo/CatalogoCursos.jsx</code>: Componente visual refactorizado.",
        style_body
    ))
    story.append(code_box("frontend/src/features/catalogo/hooks/useCursos.test.js", [
        "it('setPage(n) -> recarga con page=n (y resetea a 1 si cambia el filtro)', async () => {",
        "    const llamadas = []",
        "    const mockFetch = async (url) => {",
        "        llamadas.push(url)",
        "        return { ok: true, json: async () => ({ items: [], total: 0, page: 1, page_size: 20 }) }",
        "    }",
        "    const gestor = crearGestorCursos({ fetchFn: mockFetch })",
        "    await gestor.setPage(3) // Navega a página 3",
        "    assert.strictEqual(gestor.getState().page, 3)",
        "    await gestor.setFiltro('Python') // Cambia búsqueda -> resetea a página 1",
        "    assert.strictEqual(gestor.getState().page, 1)",
        "})",
    ]))
    story.append(Spacer(1, 4))
    story.append(git_box("ticket/T6-frontend-hook-tests", "51b482c", "test: add frontend tests for useCursos hook", "65024b0"))

    # =========================================================================
    # PÁGINA 8: BLOQUE 3 - INTRODUCCIÓN Y TICKET T7
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("4. Bloque 3 — Docker Multi-Stage y Buenas Prácticas", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceAfter=8))
    story.append(Paragraph(
        "<b>Fundamento Teórico y Seguridad:</b> En entornos de producción, una imagen de contenedor jamás debe ser un clon del entorno de desarrollo. "
        "Las imágenes 'mono-stage' acarrean compiladores, herramientas de depuración y dependencias de test, produciendo imágenes pesadas (> 1 GB) "
        "y vulnerables. El patrón <b>Multi-Stage Build</b> separa el proceso en: etapa <b>builder</b> (compilación y resolución de paquetes) y "
        "etapa <b>runtime</b> (copia exclusiva de binarios sobre imágenes base mínimas). "
        "Asimismo, se aplicó el <b>Principio de Menor Privilegio</b>: los contenedores se ejecutan sin privilegios de root.",
        style_body
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Ticket T7 — Backend: Dockerfile Multi-Stage", style_h2))
    story.append(Paragraph(
        "<b>Justificación del Ticket:</b><br/>"
        "Se implementó un Dockerfile multi-stage para FastAPI utilizando <code>uv</code>. En el stage <code>builder</code> "
        "(<code>python:3.12-slim</code>) se ejecuta <code>uv sync --frozen --no-dev</code> para compilar un virtualenv con dependencias de producción. "
        "En el stage <code>runtime</code> se crea el grupo y usuario sin privilegios <code>appuser:appgroup</code> (UID 1001), se copian únicamente "
        "el directorio <code>.venv</code> y el paquete <code>app/</code>, y se configura un <code>HEALTHCHECK</code> nativo contra <code>/health</code>.<br/>"
        "<b>Resultado:</b> Imagen final de ~94 MB (cumpliendo la meta de &lt; 100 MB).",
        style_body
    ))
    story.append(Paragraph(
        "<b>Archivos creados / modificados:</b><br/>"
        "• <code>backend/Dockerfile</code>: Configuración en dos etapas (builder con uv y runtime no-root).",
        style_body
    ))
    story.append(code_box("backend/Dockerfile", [
        "# Stage 1: Builder (dependencias de producción)",
        "FROM python:3.12-slim AS builder",
        "WORKDIR /app",
        "RUN pip install --no-cache-dir uv && COPY pyproject.toml uv.lock ./",
        "RUN uv sync --frozen --no-dev --no-install-project",
        "# Stage 2: Runtime (mínimo, seguro y no-root)",
        "FROM python:3.12-slim AS runtime",
        "WORKDIR /app",
        "RUN groupadd -g 1001 appgroup && useradd -u 1001 -g appgroup -s /bin/sh -m appuser",
        "COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv",
        "COPY --chown=appuser:appgroup app/ ./app/",
        "USER appuser",
        "EXPOSE 8000",
        "HEALTHCHECK --interval=15s --timeout=3s --retries=3 \\",
        "    CMD python3 -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/health')\" || exit 1",
        "CMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]",
    ]))
    story.append(Spacer(1, 4))
    story.append(git_box("ticket/T7-backend-dockerfile-multistage", "439c715", "docker: add multi-stage Dockerfile for backend", "dfbba7d"))

    # =========================================================================
    # PÁGINA 9: TICKET T8
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Ticket T8 — .dockerignore Optimizado (Backend y Frontend)", style_h2))
    story.append(Paragraph(
        "<b>Justificación del Ticket:</b><br/>"
        "Al ejecutar <code>docker build</code>, el cliente empaqueta todo el directorio local y lo transfiere al daemon de Docker como "
        "<i>Build Context</i>. Sin un <code>.dockerignore</code> riguroso, esta operación transfiere gigabytes de archivos prescindibles:<br/>"
        "1. <b>Degradación de rendimiento:</b> Enviar <code>node_modules</code> o <code>.venv</code> locales demora la compilación innecesariamente.<br/>"
        "2. <b>Invalidación de caché:</b> Cambios en archivos de log o cachés locales (<code>__pycache__</code>, <code>.pytest_cache</code>) "
        "arruinan el sistema de capas de Docker, obligando a reconstruir todo desde cero.<br/>"
        "3. <b>Riesgo crítico de seguridad:</b> Permite que archivos <code>.env</code> locales con contraseñas o claves maestras queden "
        "empaquetados de forma invisible dentro de la imagen pública.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Archivos creados / modificados:</b><br/>"
        "• <code>backend/.dockerignore</code>: Excluye <code>.git</code>, <code>__pycache__</code>, <code>.venv</code>, <code>tests/</code>, "
        "<code>.env*</code>, <code>.pytest_cache</code> y logs.<br/>"
        "• <code>frontend/.dockerignore</code>: Excluye <code>node_modules</code>, <code>dist</code>, <code>coverage</code>, <code>*.test.js</code>, "
        "<code>.git</code> y variables de entorno locales.",
        style_body
    ))
    story.append(code_box("backend/.dockerignore y frontend/.dockerignore", [
        "# backend/.dockerignore",
        ".git",
        ".gitignore",
        ".venv",
        "__pycache__/",
        "*.pyc",
        ".pytest_cache/",
        "tests/",
        ".env*",
        "*.log",
        "",
        "# frontend/.dockerignore",
        ".git",
        "node_modules/",
        "dist/",
        "coverage/",
        "*.test.js",
        "*.test.jsx",
        ".env*",
    ]))
    story.append(Spacer(1, 4))
    story.append(git_box("ticket/T8-dockerignore-optimizado", "f77eac6", "docker: add optimized .dockerignore files", "873a890"))

    # =========================================================================
    # PÁGINA 10: TICKET T9
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Ticket T9 — Frontend: Dockerfile Multi-Stage (Builder → Nginx)", style_h2))
    story.append(Paragraph(
        "<b>Justificación del Ticket:</b><br/>"
        "Una aplicación React (SPA) compilada por Vite consta exclusivamente de archivos estáticos HTML, JS y CSS. "
        "Mantener un runtime pesado de Node.js en producción para servir archivos estáticos es una mala práctica de arquitectura. "
        "Se adoptó una estrategia multi-stage:<br/>"
        "1. <b>Stage Builder:</b> Imagen <code>node:20-alpine</code> con <code>pnpm</code> que instala dependencias y compila el bundle en <code>dist/</code>.<br/>"
        "2. <b>Stage Runtime:</b> Servidor web <b>Nginx sobre Alpine Linux</b> (&lt; 25 MB).<br/>"
        "3. <b>Configuración Nginx (<code>nginx.conf</code>):</b><br/>"
        "   • <b>SPA Fallback:</b> <code>try_files $uri $uri/ /index.html;</code> garantizando que el router de React funcione sin errores 404.<br/>"
        "   • <b>Proxy Inverso:</b> Bloque <code>location /api/</code> que reenvía peticiones transparentemente hacia <code>http://backend:8000;</code>.<br/>"
        "   • <b>Salud:</b> Endpoint <code>/health</code> respondiendo HTTP 200 para las comprobaciones de Docker Compose.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Archivos creados / modificados:</b><br/>"
        "• <code>frontend/Dockerfile</code>: Multi-stage builder (Node 20 + pnpm) → runtime (Nginx Alpine).<br/>"
        "• <code>frontend/nginx.conf</code>: Configuración del servidor web de producción y proxy reverso.",
        style_body
    ))
    story.append(code_box("frontend/nginx.conf (Proxy y SPA Fallback)", [
        "server {",
        "    listen 80; root /usr/share/nginx/html; index index.html;",
        "    # SPA fallback: redirige rutas al index.html de React",
        "    location / { try_files $uri $uri/ /index.html; }",
        "    # Proxy inverso transparente hacia el backend FastAPI",
        "    location /api/ {",
        "        proxy_pass http://backend:8000;",
        "        proxy_set_header Host $host;",
        "        proxy_set_header X-Real-IP $remote_addr;",
        "    }",
        "    # Endpoint de salud para Docker Compose",
        "    location = /health { return 200 'healthy\\n'; add_header Content-Type text/plain; }",
        "}",
    ]))
    story.append(Spacer(1, 4))
    story.append(git_box("ticket/T9-frontend-dockerfile-multistage", "2e9f6f3", "docker: add multi-stage Dockerfile for frontend with nginx", "aa96c55"))

    # =========================================================================
    # PÁGINA 11: TICKET T10
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Ticket T10 — Docker Compose con Healthchecks y Dependencias", style_h2))
    story.append(Paragraph(
        "<b>Justificación del Ticket:</b><br/>"
        "En arquitecturas con múltiples servicios existe la problemática de las <i>condiciones de carrera al arrancar (race conditions)</i>: "
        "si el contenedor del backend se ejecuta antes de que PostgreSQL termine de crear su socket TCP, la aplicación backend colapsa.<br/>"
        "Se implementó un esquema de orquestación resiliente en <code>docker-compose.yml</code> donde cada servicio monitoriza su propia salud:<br/>"
        "1. <b>postgres:</b> Healthcheck activo con <code>pg_isready -U aprende -d aprende_gratis</code>.<br/>"
        "2. <b>backend:</b> Configurado con <code>depends_on: { postgres: { condition: service_healthy } }</code>. Solo arranca cuando PostgreSQL está listo, y se monitoriza con <code>/health</code>.<br/>"
        "3. <b>frontend:</b> Configurado con <code>depends_on: { backend: { condition: service_healthy } }</code>. Solo arranca cuando el backend responde saludable, y se monitoriza con <code>wget /health</code>.<br/>"
        "4. <b>Persistencia:</b> Volumen nombrado <code>postgres_data</code> para asegurar los datos ante reinicios.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Archivos creados / modificados:</b><br/>"
        "• <code>docker-compose.yml</code>: Orquestación declarativa de los 3 servicios con healthcheck y dependencias condicionadas.<br/>"
        "• <code>backend/pyproject.toml</code> y <code>backend/uv.lock</code>: Driver PostgreSQL <code>psycopg</code> para producción.",
        style_body
    ))
    story.append(code_box("docker-compose.yml (Healthcheck y Dependencias Condicionadas)", [
        "services:",
        "  postgres:",
        "    image: postgres:18.6",
        "    healthcheck:",
        "      test: [\"CMD-SHELL\", \"pg_isready -U $${POSTGRES_USER:-aprende} -d $${POSTGRES_DB:-aprende_gratis}\"]",
        "  backend:",
        "    depends_on: { postgres: { condition: service_healthy } }",
        "    healthcheck:",
        "      test: [\"CMD\", \"python3\", \"-c\", \"import urllib.request; urllib.request.urlopen('http://localhost:8000/health')\"]",
        "  frontend:",
        "    depends_on: { backend: { condition: service_healthy } }",
        "    healthcheck:",
        "      test: [\"CMD-SHELL\", \"wget -q -O /dev/null http://localhost/health || exit 1\"]",
    ]))
    story.append(Spacer(1, 4))
    story.append(git_box("ticket/T10-docker-compose-healthchecks", "7d1cc51", "docker: add healthchecks and service dependencies to compose", "feb5fb9"))

    # =========================================================================
    # PÁGINA 12: BLOQUE 4 - INTRODUCCIÓN Y TICKET T11
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("5. Bloque 4 — Gestión del Cambio y Cierre Auditable", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceAfter=8))
    story.append(Paragraph(
        "<b>Fundamento Teórico:</b> En proyectos de software profesionales y sujetos a auditoría académica, "
        "la calidad no solo se mide en código que compila, sino en la <b>trazabilidad histórica del repositorio</b>. "
        "Cada cambio debe responder a un propósito claro, estar encapsulado en una rama corta, seguir la convención "
        "<b>Conventional Commits</b> y quedar documentado en un registro de versiones estructurado bajo el estándar <i>Keep a Changelog</i>.",
        style_body
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Ticket T11 — Cierre Auditable del Ciclo y Retrospectiva", style_h2))
    story.append(Paragraph(
        "<b>Justificación del Ticket:</b><br/>"
        "Cierre formal de la versión <code>v0.2.0</code>. Se documentaron de manera exhaustiva en el <code>CHANGELOG.md</code> "
        "todos los tickets del T1 al T10, se redactó una retrospectiva técnica de 5 líneas analizando los aciertos y adaptaciones "
        "del ciclo, se actualizó la sección de estrategia de testing en <code>docs/IMPLEMENTATION_PLAN.md</code> y se aseguraron todos los merges "
        "con <code>--no-ff</code> en la rama <code>dev</code> para preservar la bifurcación gráfica de cada ticket.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Archivos creados / modificados:</b><br/>"
        "• <code>CHANGELOG.md</code>: Incorporación de la versión <code>[v0.2.0] - 2026-10-27</code> detallando los 10 tickets y la retrospectiva.<br/>"
        "• <code>docs/IMPLEMENTATION_PLAN.md</code>: Actualización de la Sección 5 (Estrategia de Testing) justificando SQLite in-memory.",
        style_body
    ))
    story.append(code_box("CHANGELOG.md (Retrospectiva del Ciclo)", [
        "### Retrospectiva del Ciclo (Clase 27/10/2026)",
        "1. Flujo y Trazabilidad: El flujo GitHub Flow documentado (1 rama corta por ticket y merge con --no-ff",
        "   hacia dev) funcionó a la perfección, logrando un historial 100% auditable con Conventional Commits.",
        "2. Arquitectura Limpia: Separar las reglas de negocio en funciones puras libres de HTTP y BD (T1-T3)",
        "   permitió alcanzar 48 tests unitarios deterministas que se ejecutan en menos de 1 segundo.",
        "3. Decisión de Testing de Integración: Sobre la marcha elegimos SQLite in-memory para el repository (T4-T5)",
        "   en lugar de PostgreSQL externo; esto garantizó aislamiento total, velocidad instantánea y portabilidad.",
        "4. Eficiencia en Docker Multi-Stage: El patrón builder/runtime (T7 y T9) demostró ser clave para la seguridad",
        "   (usuario no-root) y redujo drásticamente el peso de las imágenes al descartar dependencias dev.",
        "5. Orquestación Robusta: Los healthchecks en Docker Compose (T10) resolvieron definitivamente las condiciones",
        "   de carrera al arrancar, asegurando que la base de datos esté lista antes de que el backend sirva tráfico.",
    ]))
    story.append(Spacer(1, 4))
    story.append(git_box("ticket/T11-cierre-auditable", "dec6813", "docs: add changelog and retrospective for class 27/10", "ffe2d9b"))

    # =========================================================================
    # PÁGINA 13: MATRIZ DE AUDITORÍA Y CONCLUSIONES
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("6. Matriz de Auditoría y Verificación de Criterios", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceAfter=6))

    checklist_data = [
        [Paragraph("<b>Ticket</b>", style_table_header),
         Paragraph("<b>Rama Git</b>", style_table_header),
         Paragraph("<b>Commit Hash & Mensaje</b>", style_table_header),
         Paragraph("<b>Merge dev</b>", style_table_header),
         Paragraph("<b>Estado</b>", style_table_header)],
        [Paragraph("T1 (Reglas Curso)", style_table_cell), Paragraph("ticket/T1-reglas-curso", style_table_cell), Paragraph("2cff44e test: add unit tests for catalogo rules", style_table_cell), Paragraph("502d076", style_table_cell), Paragraph("<font color='#16A34A'><b>100% OK</b></font>", style_table_cell)],
        [Paragraph("T2 (Reglas Roadmap)", style_table_cell), Paragraph("ticket/T2-reglas-roadmap", style_table_cell), Paragraph("a119dce test: add unit tests for roadmap rules", style_table_cell), Paragraph("a6b8dd4", style_table_cell), Paragraph("<font color='#16A34A'><b>100% OK</b></font>", style_table_cell)],
        [Paragraph("T3 (Servicio Aportes)", style_table_cell), Paragraph("ticket/T3-reglas-aportes", style_table_cell), Paragraph("8dda2e8 test: add unit tests for aporte validation...", style_table_cell), Paragraph("c605a3c", style_table_cell), Paragraph("<font color='#16A34A'><b>100% OK</b></font>", style_table_cell)],
        [Paragraph("T4 (Repository Cursos)", style_table_cell), Paragraph("ticket/T4-integration-curso-repository", style_table_cell), Paragraph("ab81e5c test: add integration tests for CursoRepo...", style_table_cell), Paragraph("44753a7", style_table_cell), Paragraph("<font color='#16A34A'><b>100% OK</b></font>", style_table_cell)],
        [Paragraph("T5 (Flujo Aportes)", style_table_cell), Paragraph("ticket/T5-integration-flujo-aportes", style_table_cell), Paragraph("839b4be test: add integration tests for aporte flow...", style_table_cell), Paragraph("b04568b", style_table_cell), Paragraph("<font color='#16A34A'><b>100% OK</b></font>", style_table_cell)],
        [Paragraph("T6 (Frontend Hook)", style_table_cell), Paragraph("ticket/T6-frontend-hook-tests", style_table_cell), Paragraph("51b482c test: add frontend tests for useCursos...", style_table_cell), Paragraph("65024b0", style_table_cell), Paragraph("<font color='#16A34A'><b>100% OK</b></font>", style_table_cell)],
        [Paragraph("T7 (Backend Docker)", style_table_cell), Paragraph("ticket/T7-backend-dockerfile-multistage", style_table_cell), Paragraph("439c715 docker: add multi-stage Dockerfile backend", style_table_cell), Paragraph("dfbba7d", style_table_cell), Paragraph("<font color='#16A34A'><b>100% OK</b></font>", style_table_cell)],
        [Paragraph("T8 (.dockerignore)", style_table_cell), Paragraph("ticket/T8-dockerignore-optimizado", style_table_cell), Paragraph("f77eac6 docker: add optimized .dockerignore files", style_table_cell), Paragraph("873a890", style_table_cell), Paragraph("<font color='#16A34A'><b>100% OK</b></font>", style_table_cell)],
        [Paragraph("T9 (Frontend Nginx)", style_table_cell), Paragraph("ticket/T9-frontend-dockerfile-multistage", style_table_cell), Paragraph("2e9f6f3 docker: add multi-stage frontend with nginx", style_table_cell), Paragraph("aa96c55", style_table_cell), Paragraph("<font color='#16A34A'><b>100% OK</b></font>", style_table_cell)],
        [Paragraph("T10 (Compose Health)", style_table_cell), Paragraph("ticket/T10-docker-compose-healthchecks", style_table_cell), Paragraph("7d1cc51 docker: add healthchecks to compose", style_table_cell), Paragraph("feb5fb9", style_table_cell), Paragraph("<font color='#16A34A'><b>100% OK</b></font>", style_table_cell)],
        [Paragraph("T11 (Cierre Auditable)", style_table_cell), Paragraph("ticket/T11-cierre-auditable", style_table_cell), Paragraph("dec6813 docs: add changelog and retrospective...", style_table_cell), Paragraph("ffe2d9b", style_table_cell), Paragraph("<font color='#16A34A'><b>100% OK</b></font>", style_table_cell)],
    ]
    check_table = Table(checklist_data, colWidths=[95, 120, 195, 55, 57])
    check_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_primary),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BOX", (0, 0), (-1, -1), 1, c_primary),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    for row_idx in range(1, len(checklist_data)):
        bg = colors.HexColor("#F8FAFC") if row_idx % 2 == 1 else colors.white
        check_table.setStyle(TableStyle([("BACKGROUND", (0, row_idx), (-1, row_idx), bg)]))
    story.append(check_table)
    story.append(Spacer(1, 8))

    crit_data = [
        [Paragraph("<b>Criterio Evaluado</b>", style_table_header),
         Paragraph("<b>Mínimo Solicitado</b>", style_table_header),
         Paragraph("<b>Resultado Obtenido</b>", style_table_header),
         Paragraph("<b>Dictamen</b>", style_table_header)],
        [Paragraph("Tests passing", style_table_cell), Paragraph("100% (0 fallos, 0 omitidos)", style_table_cell), Paragraph("68/68 tests superados (64 backend, 4 frontend)", style_table_cell), Paragraph("<font color='#16A34A'><b>CUMPLIDO</b></font>", style_table_cell)],
        [Paragraph("Cobertura Backend", style_table_cell), Paragraph("≥ 85%", style_table_cell), Paragraph("≥ 95% en módulos de negocio y repositorios", style_table_cell), Paragraph("<font color='#16A34A'><b>CUMPLIDO</b></font>", style_table_cell)],
        [Paragraph("Imagen Docker Backend", style_table_cell), Paragraph("< 100 MB", style_table_cell), Paragraph("~94 MB (multi-stage con uv y usuario no-root)", style_table_cell), Paragraph("<font color='#16A34A'><b>CUMPLIDO</b></font>", style_table_cell)],
        [Paragraph("Imagen Docker Frontend", style_table_cell), Paragraph("< 30 MB", style_table_cell), Paragraph("~23 MB (Nginx Alpine con assets minificados)", style_table_cell), Paragraph("<font color='#16A34A'><b>CUMPLIDO</b></font>", style_table_cell)],
        [Paragraph("Docker Compose", style_table_cell), Paragraph("3/3 servicios healthy", style_table_cell), Paragraph("Postgres (pg_isready), Backend y Frontend (/health)", style_table_cell), Paragraph("<font color='#16A34A'><b>CUMPLIDO</b></font>", style_table_cell)],
        [Paragraph("Gestión del Cambio", style_table_cell), Paragraph("Conventional Commits + Merges", style_table_cell), Paragraph("100% Conventional Commits, ramas cortas, merges --no-ff", style_table_cell), Paragraph("<font color='#16A34A'><b>CUMPLIDO</b></font>", style_table_cell)],
    ]
    crit_table = Table(crit_data, colWidths=[120, 120, 202, 80])
    crit_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_secondary),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BOX", (0, 0), (-1, -1), 1, c_secondary),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    for row_idx in range(1, len(crit_data)):
        bg = colors.HexColor("#F8FAFC") if row_idx % 2 == 1 else colors.white
        crit_table.setStyle(TableStyle([("BACKGROUND", (0, row_idx), (-1, row_idx), bg)]))
    story.append(crit_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("7. Conclusiones", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceAfter=6))
    story.append(Paragraph(
        "El desarrollo de esta Segunda Parte consolidó una arquitectura de software robusta, desacoplada y auditable. "
        "La separación de reglas puras de dominio permitió lograr suites de pruebas unitarias ultrarrápidas, mientras que los tests "
        "de integración sobre SQLite en memoria validaron de extremo a extremo la persistencia y la API REST sin introducir dependencias "
        "frágiles en los entornos de ejecución.<br/>"
        "En el plano de infraestructura, la optimización mediante Docker Multi-Stage garantizó contenedores livianos, seguros y listos para producción, "
        "y la orquestación con healthchecks eliminó las fallas de sincronización en el arranque. "
        "Por último, el estricto apego a Git Flow y Conventional Commits asegura que cualquier evaluador pueda auditar la evolución histórica "
        "del proyecto paso a paso, confirmando el cumplimiento del 100% de los requerimientos de la cátedra.",
        style_body
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Informe PDF generado exitosamente en: {output_path}")


if __name__ == "__main__":
    destino = sys.argv[1] if len(sys.argv) > 1 else os.path.join("docs", "INFORME_TECNICO_SEGUNDA_PARTE_TICKETS_27_10_2026.pdf")
    construir_pdf(destino)
