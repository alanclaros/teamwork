from app.settings import PRODUCTOS_LBL_LOTE
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import pagesizes
#from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm

from datetime import datetime

# imagen
from reportlab.platypus import Paragraph, Spacer, Image, Table, TableStyle
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# cabecera
from reportes.cabecera import cabecera

# modelos
from configuraciones.models import Puntos, Sucursales
from permisos.models import UsersPerfiles

# settings
from django.conf import settings

# utils
from utils.permissions import get_sucursal_settings
from utils.dates_functions import get_date_system, get_date_show, get_date_report

# clases
from controllers.reportes.ReportesController import ReportesController


import os
import copy

# tamanio de pagina
pagesize = pagesizes.portrait(pagesizes.letter)
RPT_SUCURSAL_ID = 0
DATO_CAJA = ''


def myFirstPage(canvas, doc):
    canvas.saveState()

    datosReporte = get_sucursal_settings(RPT_SUCURSAL_ID)
    datosReporte['titulo'] = 'Pedido Productos ' + DATO_CAJA
    datosReporte['fecha_impresion'] = get_date_report()
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


def rptPedidosProductos(buffer_pdf, usuario, ciudad_id, sucursal_id, almacen_id, fecha_ini, fecha_fin, anulados):
    # pdf
    #pdf = canvas.Canvas(buffer, pagesize=letter)

    # datos sucursal
    user_perfil = UsersPerfiles.objects.get(user_id=usuario)
    #permisos = get_permisos_usuario(usuario, settings.MOD_REPORTES)
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
    # personalizamos
    style_ciudad = ParagraphStyle('ciudad',
                                  fontName="Helvetica-Bold",
                                  fontSize=12,
                                  parent=styles['Normal'],
                                  alignment=1,
                                  spaceAfter=10)

    style_sucursal = ParagraphStyle('sucursal',
                                    fontName="Helvetica-Bold",
                                    fontSize=10,
                                    parent=styles['Normal'],
                                    alignment=0,
                                    spaceAfter=2)

    style_almacen = ParagraphStyle('almacen',
                                   fontName="Helvetica-BoldOblique",
                                   fontSize=9,
                                   parent=styles['Normal'],
                                   alignment=0,
                                   spaceAfter=5)

    # styles.add(ParagraphStyle(fontName='SimSun', name='SimSun', leading=20, fontSize=12))

    # style_ciudad = copy.deepcopy(styles['Normal'])
    # style_ciudad
    # style_ciudad.normal.fontName = 'Helvetica-Bold'
    # style_ciudad.normal.fontSize = 12

    doc = SimpleDocTemplate(buffer_pdf, pagesize=letter, leftMargin=10 * mm, rightMargin=10 * mm, topMargin=10 * mm, bottomMargin=15 * mm)

    """datos del reporte"""
    reporte_controller = ReportesController()
    datos_reporte = reporte_controller.datos_pedido_productos(usuario, ciudad_id, sucursal_id, almacen_id, fecha_ini, fecha_fin, anulados)
    # print(datos_reporte)

    Story = []
    Story.append(Spacer(100*mm, 22*mm))
    fecha_reporte = 'Del: ' + fecha_ini + ' Al: ' + fecha_fin
    Story.append(Paragraph(fecha_reporte, style_almacen))
    # Story.append(tabla_datos)
    ciudad_actual = ''
    sucursal_actual = ''
    codigo_moneda = ''
    almacen_id = ''
    datos_tabla = []
    data = []
    filas = 0
    total = 0
    bande = 0
    titulo_almacen = ''

    for dato in datos_reporte:

        # almacen
        if almacen_id != dato['almacen']:
            bande += 1
            # primera vuelta, no se cierra tabla
            if bande > 1:
                # cerramos tabla anterior y aniadimos
                if len(data) > 0:
                    #datos_tabla = ['', 'Total: ', str(total) + ' ' + codigo_moneda]
                    # data.append(datos_tabla)

                    if settings.PRODUCTOS_USAR_FECHAS and settings.PRODUCTOS_USAR_LOTE:
                        tabla_datos = Table(data, colWidths=[50*mm, 65*mm, 22*mm, 22*mm, 22*mm, 15*mm], repeatRows=1)
                        num_cols = 6-1
                        align_from_right = 5
                    else:
                        if not settings.PRODUCTOS_USAR_FECHAS and not settings.PRODUCTOS_USAR_LOTE:
                            tabla_datos = Table(data, colWidths=[181*mm, 15*mm], repeatRows=1)
                            num_cols = 2-1
                            align_from_right = 1
                        else:
                            if settings.PRODUCTOS_USAR_LOTE:
                                tabla_datos = Table(data, colWidths=[83*mm, 83*mm, 15*mm, 15*mm], repeatRows=1)
                                num_cols = 4-1
                                align_from_right = 3

                    tabla_datos.setStyle(TableStyle([('BACKGROUND', (0, 0), (num_cols, 0), colors.Color(red=(204/255), green=(204/255), blue=(204/255))),
                                                     ('ALIGN', (align_from_right, 0), (num_cols, filas+1), 'RIGHT'),
                                                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                                                     ('FONTSIZE', (0, 0), (num_cols, 0), 10),
                                                     ('FONTSIZE', (0, 1), (-1, -1), 9),
                                                     ('FONTNAME', (0, 0), (num_cols, 0), 'Helvetica'),
                                                     ('FONTNAME', (0, 1), (num_cols, filas), 'Helvetica'),
                                                     ('LEFTPADDING', (0, 0), (-1, -1), 2),
                                                     ('RIGHTPADDING', (0, 1), (-1, -1), 1),
                                                     ('VALIGN', (0, 1), (-1, -1), 'TOP'),
                                                     ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)]))
                    # aniadimos la tabla
                    Story.append(Paragraph(titulo_almacen, style_almacen))
                    Story.append(tabla_datos)
                    Story.append(Spacer(100*mm, 5*mm))

            # texto nombre de la caja
            #Story.append(Paragraph(dato['punto'] + ' - ' + dato['caja'], style_punto))
            titulo_almacen = dato['almacen']
            almacen_id = dato['almacen']

            # creamos tabla para esta caja
            data = []

            if settings.PRODUCTOS_USAR_FECHAS and settings.PRODUCTOS_USAR_LOTE:
                data.append(['Linea', 'Producto', 'F.Elab.', 'F.Venc.', 'Lote', 'Cant'])
            else:
                if not settings.PRODUCTOS_USAR_FECHAS and not settings.PRODUCTOS_USAR_LOTE:
                    data.append(['Insumo', 'Cant'])
                else:
                    if settings.PRODUCTOS_USAR_LOTE:
                        data.append(['Linea', 'Producto', settings.PRODUCTOS_LBL_LOTE, 'Cant'])

            filas = 0
            total = 0

            # datos
            # datos_tabla = [dato['fecha'], dato['concepto'], str(dato['monto']) + ' ' + str(dato['tipo_moneda_id'])]
            # data.append(datos_tabla)
            # filas += 1
            # total += dato['monto']

        # seguimos llenando de datos la tabla hasta cambiar de caja, sucursal o ciudad
        linea = Paragraph(dato['linea'])
        producto = Paragraph(dato['producto'])

        if settings.PRODUCTOS_USAR_FECHAS and settings.PRODUCTOS_USAR_LOTE:
            datos_tabla = [linea, producto, dato['fecha_elaboracion'], dato['fecha_vencimiento'], dato['lote'], str(dato['cantidad'])]
        else:
            if not settings.PRODUCTOS_USAR_FECHAS and not settings.PRODUCTOS_USAR_LOTE:
                datos_tabla = [producto, str(dato['cantidad'])]
            else:
                if settings.PRODUCTOS_USAR_LOTE:
                    datos_tabla = [linea, producto, dato['lote'], str(dato['cantidad'])]

        data.append(datos_tabla)
        filas += 1
        #total += dato['monto']

        # codigo moneda para los totales
        # if codigo_moneda != dato['tipo_moneda']:
        #     codigo_moneda = dato['tipo_moneda']

        # titulo de ciudad, despues que se terminen las tablas
        if ciudad_actual != dato['ciudad']:
            Story.append(Paragraph(dato['ciudad'], style_ciudad))
            ciudad_actual = dato['ciudad']

        # titulo sucursal despues que se termine de dibujar las tablas
        if sucursal_actual != dato['sucursal']:
            Story.append(Paragraph(dato['sucursal'], style_sucursal))
            sucursal_actual = dato['sucursal']

    # datos de la ultima tabla
    if len(data) > 0:
        # datos_tabla = ['', 'Total: ', str(total) + ' ' + codigo_moneda]
        # data.append(datos_tabla)

        if settings.PRODUCTOS_USAR_FECHAS and settings.PRODUCTOS_USAR_LOTE:
            tabla_datos = Table(data, colWidths=[50*mm, 65*mm, 22*mm, 22*mm, 22*mm, 15*mm], repeatRows=1)
            num_cols = 6-1
            align_from_right = 5
        else:
            if not settings.PRODUCTOS_USAR_FECHAS and not settings.PRODUCTOS_USAR_LOTE:
                tabla_datos = Table(data, colWidths=[83*mm, 98*mm, 15*mm], repeatRows=1)
                num_cols = 2-1
                align_from_right = 1
            else:
                if settings.PRODUCTOS_USAR_LOTE:
                    tabla_datos = Table(data, colWidths=[83*mm, 83*mm, 15*mm, 15*mm], repeatRows=1)
                    num_cols = 4-1
                    align_from_right = 3

        tabla_datos.setStyle(TableStyle([('BACKGROUND', (0, 0), (num_cols, 0), colors.Color(red=(204/255), green=(204/255), blue=(204/255))),
                                         ('ALIGN', (align_from_right, 0), (num_cols, filas+1), 'RIGHT'),
                                         ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                                         ('FONTSIZE', (0, 0), (num_cols, 0), 10),
                                         ('FONTSIZE', (0, 1), (-1, -1), 9),
                                         ('FONTNAME', (0, 0), (num_cols, 0), 'Helvetica'),
                                         ('FONTNAME', (0, 1), (num_cols, filas), 'Helvetica'),
                                         ('LEFTPADDING', (0, 0), (-1, -1), 2),
                                         ('RIGHTPADDING', (0, 1), (-1, -1), 1),
                                         ('VALIGN', (0, 1), (-1, -1), 'TOP'),
                                         ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)]))
        # aniadimos la tabla
        Story.append(Paragraph(titulo_almacen, style_almacen))
        Story.append(tabla_datos)

    doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)
