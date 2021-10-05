from reportlab.lib.pagesizes import letter
from reportlab.lib import pagesizes
from reportlab.lib.units import mm

# imagen
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.platypus import SimpleDocTemplate  # BaseDocTemplate, Frame, PageTemplate, NextPageTemplate, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# cabecera
from reportes.cabecera import cabecera

# modelos
from configuraciones.models import Puntos
from permisos.models import UsersPerfiles

# settings
from django.conf import settings

# utils
from utils.permissions import get_sucursal_settings, report_date, show_periodo

# clases
from controllers.reportes.ReportesController import ReportesController

import os

# tamanio de pagina
pagesize = pagesizes.portrait(pagesizes.letter)
RPT_SUCURSAL_ID = 0
DATO_CAJA = ''


def myFirstPage(canvas, doc):
    canvas.saveState()

    datosReporte = get_sucursal_settings(RPT_SUCURSAL_ID)
    datosReporte['titulo'] = 'Expensas ' + DATO_CAJA
    datosReporte['fecha_impresion'] = report_date()
    dir_img = os.path.join(settings.STATIC_ROOT, 'img/logo.png')
    datosReporte['logo'] = dir_img

    cabecera(canvas, **datosReporte)

    canvas.setFont('Times-Italic', 8)
    canvas.drawRightString(pagesize[0] - 15 * mm, 10 * mm, "pag. %d" % (doc.page,))

    canvas.restoreState()


def myLaterPages(canvas, doc):
    canvas.saveState()

    canvas.setFont('Times-Italic', 8)
    canvas.drawRightString(pagesize[0] - 15 * mm, 10 * mm, "pag. %d" % (doc.page,))
    canvas.restoreState()


def rptExpensas(buffer_pdf, usuario, bloque_id, piso_id, caja_id, periodo_ini, periodo_fin, anulados):
    # pdf
    #pdf = canvas.Canvas(buffer, pagesize=letter)

    # datos sucursal
    user_perfil = UsersPerfiles.objects.get(user_id=usuario)
    punto = Puntos.objects.get(pk=user_perfil.punto_id)
    sucursal_id_user = punto.sucursal_id.sucursal_id
    global RPT_SUCURSAL_ID
    RPT_SUCURSAL_ID = sucursal_id_user

    global DATO_CAJA
    if anulados == 'si':
        DATO_CAJA = 'Anulados'
    else:
        DATO_CAJA = ''

    styles = getSampleStyleSheet()

    style_fecha = ParagraphStyle('fecha',
                                 fontName="Helvetica-Bold",
                                 fontSize=10,
                                 parent=styles['Normal'],
                                 alignment=0,
                                 spaceAfter=2)

    style_caja = ParagraphStyle('caja',
                                fontName="Helvetica-BoldOblique",
                                fontSize=9,
                                parent=styles['Normal'],
                                alignment=0,
                                spaceAfter=5)

    doc = SimpleDocTemplate(buffer_pdf, pagesize=letter, leftMargin=10 * mm, rightMargin=10 * mm, topMargin=10 * mm, bottomMargin=15 * mm)

    """datos del reporte"""
    reporte_controller = ReportesController()
    datos_reporte = reporte_controller.datos_expensas(usuario, bloque_id, piso_id, caja_id, periodo_ini, periodo_fin, anulados)
    # print(datos_reporte)

    Story = []
    Story.append(Spacer(100*mm, 22*mm))
    fecha_reporte = 'Del: ' + show_periodo(periodo_ini) + ' Al: ' + show_periodo(periodo_fin)
    Story.append(Paragraph(fecha_reporte, style_fecha))
    # Story.append(tabla_datos)
    caja_id = 0
    datos_tabla = []
    data = []
    filas = 0
    total = 0
    bande = 0
    titulo_caja = ''

    for dato in datos_reporte:
        # caja
        if caja_id != dato['caja_id']:
            bande += 1
            # primera vuelta, no se cierra tabla
            if bande > 1:
                # cerramos tabla anterior y aniadimos
                if len(data) > 0:
                    datos_tabla = ['', '', '', '', '', 'Total: ', str(total) + ' Bs.']
                    data.append(datos_tabla)
                    num_cols = 7 - 1
                    align_right_from = 5

                    tabla_datos = Table(data, colWidths=[30*mm, 20*mm, 30*mm, 30*mm, 30*mm, 25*mm, 25*mm], repeatRows=1)
                    tabla_datos.setStyle(TableStyle([('BACKGROUND', (0, 0), (num_cols, 0), colors.Color(red=(204/255), green=(204/255), blue=(204/255))),
                                                     #('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                                                     ('ALIGN', (align_right_from, 0), (num_cols, filas+1), 'RIGHT'),
                                                     ('ALIGN', (align_right_from-1, filas+1), (align_right_from-1, filas+1), 'RIGHT'),
                                                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),

                                                     ('FONTSIZE', (0, 0), (num_cols, 0), 10),
                                                     ('FONTSIZE', (0, 1), (num_cols, filas+1), 9),
                                                     ('FONTNAME', (0, 0), (num_cols, 0), 'Helvetica'),
                                                     ('FONTNAME', (0, 1), (num_cols, filas+1), 'Helvetica'),
                                                     ('FONTNAME', (align_right_from-1, filas+1), (num_cols, filas+1), 'Helvetica-Bold'),
                                                     ('LEFTPADDING', (0, 0), (-1, -1), 2),
                                                     ('RIGHTPADDING', (0, 1), (-1, -1), 1),
                                                     ('VALIGN', (0, 1), (-1, -1), 'TOP'),
                                                     ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)]))
                    # aniadimos la tabla
                    Story.append(Paragraph(titulo_caja, style_caja))
                    Story.append(tabla_datos)
                    Story.append(Spacer(100*mm, 5*mm))

            # texto nombre de la caja
            titulo_caja = dato['caja']
            caja_id = dato['caja_id']

            # creamos tabla para esta caja
            data = []
            data.append(['Fecha', 'Periodo', 'Bloque', 'Piso', 'Dpto', 'Lectura', 'Expensas'])
            filas = 0
            total = 0

        # seguimos llenando de datos la tabla hasta cambiar de caja, sucursal o ciudad
        bloque = Paragraph(dato['bloque'])
        piso = Paragraph(dato['piso'])
        departamento = Paragraph(dato['departamento'])

        datos_tabla = [dato['fecha_cobro'], dato['periodo'], bloque, piso, departamento, str(dato['lectura']), str(dato['total_expensas'])]
        data.append(datos_tabla)
        filas += 1
        total += dato['total_expensas']

    # datos de la ultima tabla
    if len(data) > 0:
        datos_tabla = ['', '', '', '', '', 'Total: ', str(total) + ' Bs.']
        data.append(datos_tabla)
        num_cols = 7 - 1
        align_right_from = 5

        tabla_datos = Table(data, colWidths=[30*mm, 20*mm, 30*mm, 30*mm, 30*mm, 25*mm, 25*mm], repeatRows=1)
        tabla_datos.setStyle(TableStyle([('BACKGROUND', (0, 0), (num_cols, 0), colors.Color(red=(204/255), green=(204/255), blue=(204/255))),
                                         #('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                                         ('ALIGN', (align_right_from, 0), (num_cols, filas+1), 'RIGHT'),
                                         ('ALIGN', (align_right_from-1, filas+1), (align_right_from-1, filas+1), 'RIGHT'),
                                         ('GRID', (0, 0), (-1, -1), 0.5, colors.black),

                                         ('FONTSIZE', (0, 0), (num_cols, 0), 10),
                                         ('FONTSIZE', (0, 1), (num_cols, filas+1), 9),
                                         ('FONTNAME', (0, 0), (num_cols, 0), 'Helvetica'),
                                         ('FONTNAME', (0, 1), (num_cols, filas+1), 'Helvetica'),
                                         ('FONTNAME', (align_right_from-1, filas+1), (num_cols, filas+1), 'Helvetica-Bold'),
                                         ('LEFTPADDING', (0, 0), (-1, -1), 2),
                                         ('RIGHTPADDING', (0, 1), (-1, -1), 1),
                                         ('VALIGN', (0, 1), (-1, -1), 'TOP'),
                                         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)]))
        # aniadimos la tabla
        Story.append(Paragraph(titulo_caja, style_caja))
        Story.append(tabla_datos)

    doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)
