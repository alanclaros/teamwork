from datetime import datetime
from utils.dates_functions import get_date_show
from django.apps.registry import apps
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib import pagesizes
# from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm

from reportlab.pdfbase.pdfmetrics import stringWidth

# imagen
from reportlab.platypus import Paragraph, Spacer, Image, Table, TableStyle
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# cabecera
from reportes.cabecera import cabecera

# modelos
from configuraciones.models import Puntos
from permisos.models import UsersPerfiles
from lecturas.models import Cobros, CobrosDetalles

# settings
from django.conf import settings

# utils
#from utils.dates_functions import get_date_report, get_date_show
from utils.permissions import get_sucursal_settings, previous_periodo, show_periodo, report_date

from reportlab.platypus import PageBreak

import os

# tamanio de pagina
pagesize = pagesizes.portrait(pagesizes.letter)
RPT_SUCURSAL_ID = 0
RPT_DPTO = ''
RPT_PERIODO = 'periodo'
RPT_EXPENSAS = '0.00'
RPT_NOMBRE = 'nombres'
RPT_ANULADO = ''
RPT_FECHA_IMPRESION = ''

color_fondo_aviso = [255/255, 255/255, 125/255]
color_borde_aviso = [128/255, 128/255, 128/255]
color_txt_aviso = [255/255, 0/255, 0/255]
color_txt_pendiente = [255/255, 0/255, 0/255]
color_txt_cobrar = [0/255, 128/255, 128/255]
color_fondo_cabecera = [215/255, 215/255, 215/255]
color_txt_nota = [0/255, 64/255, 128/255]


def myFirstPage(canvas, doc):
    canvas.saveState()

    datosReporte = get_sucursal_settings(RPT_SUCURSAL_ID)
    datosReporte['titulo'] = datosReporte['empresa']
    datosReporte['fecha_impresion'] = RPT_FECHA_IMPRESION
    dir_img = os.path.join(settings.STATIC_ROOT, 'img/logo.png')
    datosReporte['logo'] = dir_img

    # para horizontal
    # posicionY = 207
    # cabecera(canvas, posY=posicionY, **datosReporte)

    # vertical
    #cabecera(canvas=canvas, **datosReporte)

    posY = 270.5
    altoTxt = 13
    canvas.drawImage(datosReporte['logo'], 2*mm, (posY-14.5)*mm, width=50, height=50)
    canvas.setStrokeColorRGB(color_borde_aviso[0], color_borde_aviso[1], color_borde_aviso[2])
    canvas.setFillColorRGB(color_fondo_aviso[0], color_fondo_aviso[1], color_fondo_aviso[2])
    canvas.rect(19*mm, 245*mm, 190*mm, 15*mm, fill=1)

    textobject = canvas.beginText()
    textobject.setTextOrigin(5*mm, posY*mm)
    textobject.setFont("Helvetica", 12)
    # color del texto
    textobject.setFillColorRGB(0, 0, 0)

    # # empresa
    # textobject.textOut(datosReporte['empresa'])
    # # direccion
    # textobject.setFont("Helvetica", 11)
    # textobject.moveCursor(0, altoTxt)
    # textobject.textOut(datosReporte['direccion'])
    # # ciudad
    # textobject.setFont("Helvetica", 10)
    # textobject.moveCursor(0, altoTxt)
    # textobject.textOut(datosReporte['ciudad'])
    # # telefonos
    # textobject.moveCursor(0, altoTxt)
    # textobject.textOut(datosReporte['telefonos'])
    # # actividad
    # textobject.setFont("Helvetica-Oblique", 8)
    # textobject.moveCursor(0, altoTxt)
    # textobject.textOut(datosReporte['actividad'])

    # titulo
    textobject.setFont("Helvetica-Bold", 12)
    textobject.moveCursor(220, 0)
    textobject.textOut(datosReporte['titulo'])

    # aviso de cobranza
    textobject.setFont("Helvetica", 11)
    textobject.moveCursor(30, 25)
    textobject.textOut('AVISO DE COBRANZA')
    # fecha recibo
    textobject.setFont("Helvetica", 10)
    textobject.moveCursor(230, 0)
    textobject.textOut(datosReporte['fecha_impresion'])

    # color del texto
    textobject.setTextOrigin(60, 720)
    textobject.setFont("Helvetica", 10)
    textobject.setFillColorRGB(color_txt_aviso[0], color_txt_aviso[1], color_txt_aviso[2])
    #textobject.moveCursor(-30-175, 22)
    textobject.textOut('EL DEPOSITO DEBE REALIZARCE A NOMBRE DE: ALEJANDRA JIMENEZ IRIARTE Y/O JAIME TORREZ MOLINA')
    # cuenta
    textobject.moveCursor(210, 18)
    textobject.textOut('BCP: 301-51408948-3-12')

    # departamento, periodo, nombres apellidos
    textobject.setFillColorRGB(0, 0, 0)
    textobject.moveCursor(-210, 20)
    textobject.setFont("Helvetica-Bold", 11)
    textobject.textOut('Dpto: ')
    textobject.setFont("Helvetica", 11)
    textobject.moveCursor(35, 0)
    textobject.textOut(RPT_DPTO)

    # periodo
    textobject.moveCursor(80, 0)
    textobject.setFont("Helvetica-Bold", 11)
    textobject.textOut('Periodo: ')
    textobject.setFont("Helvetica", 11)
    textobject.moveCursor(50, 0)
    textobject.textOut(RPT_PERIODO)

    # expensas
    textobject.moveCursor(220, 0)
    textobject.setFont("Helvetica-Bold", 11)
    textobject.textOut('Expensas: ')
    textobject.setFont("Helvetica", 11)
    textobject.moveCursor(60, 0)
    textobject.setFillColorRGB(color_txt_cobrar[0], color_txt_cobrar[1], color_txt_cobrar[2])
    textobject.textOut(RPT_EXPENSAS)

    # nombre
    textobject.moveCursor(-461.5, 16)
    textobject.setFillColorRGB(0, 0, 0)
    textobject.setFont("Helvetica-Bold", 11)
    textobject.textOut('Nombre: ')
    textobject.setFont("Helvetica", 11)
    textobject.moveCursor(51, 0)
    textobject.textOut(RPT_NOMBRE)

    # anulado
    if RPT_ANULADO != '':
        textobject.setTextOrigin(14*mm, 230*mm)
        textobject.setFont("Helvetica-Bold", 11)
        textobject.textOut('Anulado: ')
        textobject.setFont("Helvetica", 11)
        textobject.moveCursor(54, 0)
        textobject.textOut(RPT_ANULADO)

    # output
    canvas.drawText(textobject)

    # pie de pagina
    # canvas.setFont('Times-Italic', 8)
    # canvas.drawRightString(pagesize[0] - 15 * mm, 10 * mm, "pag. %d" % (doc.page,))

    canvas.restoreState()


def myLaterPages(canvas, doc):
    canvas.saveState()

    canvas.setFont('Times-Italic', 8)
    canvas.drawRightString(pagesize[0] - 15 * mm, 10 * mm, "pag. %d" % (doc.page,))
    canvas.restoreState()


def rptCobroRecibo(buffer_pdf, usuario, cobro_id):

    #print('cobro id..: ', cobro_id)
    # datos sucursal
    user_perfil = UsersPerfiles.objects.get(user_id=usuario)
    punto = Puntos.objects.get(pk=user_perfil.punto_id)
    sucursal_id_user = punto.sucursal_id.sucursal_id
    global RPT_SUCURSAL_ID
    RPT_SUCURSAL_ID = sucursal_id_user

    # verificando si es el perfil departamento el que imprimir
    global RPT_FECHA_IMPRESION
    if user_perfil.perfil_id.perfil_id == settings.PERFIL_DEPARTAMENTO:
        RPT_FECHA_IMPRESION = get_date_show(datetime.now(), formato='dd-MMM-yyyy HH:ii')
    else:
        RPT_FECHA_IMPRESION = report_date()

    # print('111111')
    # colores
    # color_fondo_aviso = colors.Color(red=)

    # registros
    cobro = Cobros.objects.get(pk=cobro_id)
    filtro_cobro = {}
    filtro_cobro['cobro_id'] = cobro
    filtro_cobro['lectura_id'] = 0
    detalles = CobrosDetalles.objects.filter(**filtro_cobro).order_by('cobro_cobro_mensual_id', 'cobro_cobro_manual_id')
    filtro_cobro = {}
    filtro_cobro['cobro_id'] = cobro
    filtro_cobro['lectura_id__gt'] = 0
    detalle_lectura = CobrosDetalles.objects.filter(**filtro_cobro).first()
    lectura_cobro = apps.get_model('lecturas', 'Lecturas').objects.get(pk=detalle_lectura.lectura_id)
    # print('22222')
    # verificamos si esta anulado
    dato_anulado = ''
    if cobro.status_id.status_id == settings.STATUS_ANULADO:
        user_perfil_anula = apps.get_model('permisos', 'UsersPerfiles').objects.get(pk=cobro.user_perfil_id_anula)
        usuario_anula = user_perfil_anula.user_id
        motivo_anula = cobro.motivo_anula
        dato_anulado = usuario_anula.username + ', ' + motivo_anula

    global RPT_DPTO, RPT_PERIODO, RPT_EXPENSAS, RPT_NOMBRE, RPT_ANULADO
    RPT_DPTO = cobro.departamento_id.departamento
    RPT_PERIODO = show_periodo(cobro.periodo)
    #RPT_FECHA = '/N' if cobro.fecha_cobro is None else get_date_show(fecha=cobro.fecha_cobro, formato='dd-MMM-yyyy HH:ii')
    RPT_EXPENSAS = str(lectura_cobro.total_expensas) + ' Bs.'
    RPT_NOMBRE = cobro.departamento_id.propietario_nombres + ' ' + cobro.departamento_id.propietario_apellidos
    RPT_ANULADO = dato_anulado

    styles = getSampleStyleSheet()
    # personalizamos
    style_tabla_datos = ParagraphStyle('tabla_datos',
                                       fontName="Helvetica",
                                       fontSize=8,
                                       parent=styles['Normal'],
                                       alignment=0,
                                       spaceAfter=0)

    # style nota
    style_nota = ParagraphStyle('style_nota',
                                fontName="Helvetica-Bold",
                                fontSize=9,
                                parent=styles['Normal'],
                                alignment=0,
                                spaceAfter=0,
                                leftIndent=30,
                                textColor=colors.Color(color_txt_nota[0], color_txt_nota[1], color_txt_nota[2])
                                )

    # style leyenda
    style_leyenda = ParagraphStyle('style_nota',
                                   fontName="Helvetica",
                                   fontSize=10,
                                   parent=styles['Normal'],
                                   alignment=0,
                                   spaceAfter=0,
                                   leftIndent=30,
                                   textColor=colors.Color(color_txt_nota[0], color_txt_nota[1], color_txt_nota[2])
                                   )

    # hoja vertical
    doc = SimpleDocTemplate(buffer_pdf, pagesize=letter, leftMargin=10 * mm, rightMargin=10 * mm, topMargin=10 * mm, bottomMargin=15 * mm)

    # armamos
    Story = []
    if RPT_ANULADO == '':
        Story.append(Spacer(100*mm, 36*mm))
    else:
        Story.append(Spacer(100*mm, 41*mm))

    # tabla de evolucion de consumo
    data_consumo = []
    data_consumo.append(['Evolucion del Consumo de Agua', '', ''])
    data_consumo.append(['Periodo', 'Lectura', 'Consumo'])
    filas_consumo = 1

    dato_consumo = [show_periodo(lectura_cobro.periodo), lectura_cobro.lectura, lectura_cobro.consumo]
    data_consumo.append(dato_consumo)
    filas_consumo += 1

    # aniadimos las 3 ultimas lecturas
    cant_lecturas = 3
    periodo_actual = previous_periodo(lectura_cobro.periodo)
    #print('periodo actual..: ', periodo_actual)
    bande = 1
    while cant_lecturas > 0 and bande == 1:
        lectura_ant_cant = apps.get_model('lecturas', 'Lecturas').objects.filter(departamento_id=lectura_cobro.departamento_id, periodo=periodo_actual).count()
        #print('lectura cant: ', lectura_ant_cant)
        if lectura_ant_cant == 0:
            bande = 0
        else:
            lectura_ant = apps.get_model('lecturas', 'Lecturas').objects.get(departamento_id=lectura_cobro.departamento_id, periodo=periodo_actual)
            dato_consumo = [show_periodo(lectura_ant.periodo), lectura_ant.lectura, lectura_ant.consumo]
            data_consumo.insert(2, dato_consumo)

            periodo_actual = previous_periodo(lectura_ant.periodo)
            cant_lecturas = cant_lecturas - 1
            filas_consumo += 1

    tabla_consumo = Table(data_consumo, colWidths=[25*mm, 25*mm, 25*mm], repeatRows=1)
    num_cols = 2
    align_right_from = 1

    tabla_consumo.setStyle(TableStyle([('BACKGROUND', (0, 0), (num_cols, 1), colors.Color(red=color_fondo_cabecera[0], green=color_fondo_cabecera[1], blue=color_fondo_cabecera[2])),

                                       ('ALIGN', (0, 0), (num_cols, 0), 'CENTER'),
                                       ('ALIGN', (align_right_from, 1), (num_cols, filas_consumo), 'RIGHT'),

                                       ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                                       ('SPAN', (0, 0), (num_cols, 0)),

                                       ('FONTSIZE', (0, 0), (num_cols, 1), 9),
                                       ('FONTSIZE', (0, 2), (num_cols, filas_consumo), 8),

                                       ('FONTNAME', (0, 0), (num_cols, 1), 'Helvetica'),
                                       ('FONTNAME', (0, 2), (num_cols, filas_consumo), 'Helvetica'),

                                       ('LEFTPADDING', (0, 0), (-1, -1), 2),
                                       ('RIGHTPADDING', (0, 0), (-1, -1), 1),
                                       ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                       ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                                       ('TEXTCOLOR', (num_cols, filas_consumo), (num_cols, filas_consumo), colors.Color(red=color_txt_cobrar[0], green=color_txt_cobrar[1], blue=color_txt_cobrar[2]))
                                       ]))

    # tabla de detalle
    datos_detalle = []
    data_detalle = []
    data_detalle.append(['Detalle', 'Monto'])
    filas = 0
    total_detalles = 0

    # cargamos los registros
    for det in detalles:
        detalle_txt = Paragraph(det.detalle, style_tabla_datos)
        datos_detalle = [detalle_txt, det.monto_bs]
        total_detalles += det.monto_bs

        data_detalle.append(datos_detalle)
        filas += 1

    # total
    data_detalle.append(['Total ' + show_periodo(cobro.periodo) + ' Bs. : ', cobro.monto_bs])
    filas += 1

    # deudas pendientes, anteriores al periodo de cobro
    status_activo = apps.get_model('status', 'Status').objects.get(pk=settings.STATUS_ACTIVO)
    data_detalle.append(['Deudas Pendientes', ''])
    filtro_pendiente = {}
    filtro_pendiente['status_id'] = status_activo
    filtro_pendiente['departamento_id'] = cobro.departamento_id
    filtro_pendiente['periodo__lt'] = cobro.periodo
    cobros_pendientes = apps.get_model('lecturas', 'Cobros').objects.filter(**filtro_pendiente).order_by('periodo')
    filas_deudas = filas + 1
    total_deudas = 0
    for cp in cobros_pendientes:
        datos_detalle = [show_periodo(cp.periodo), cp.monto_bs]
        data_detalle.append(datos_detalle)
        filas_deudas += 1
        total_deudas += cp.monto_bs
    data_detalle.append(['Total Deudas Pendientes Bs. : ', total_deudas])
    filas_deudas += 1

    # total a depositar
    data_detalle.append(['Total A DEPOSITAR Bs. : ', total_deudas + cobro.monto_bs])
    #filas_deudas += 1

    tabla_detalle = Table(data_detalle, colWidths=[100*mm, 18*mm], repeatRows=1)
    num_cols = 1
    align_right_from = 1

    tabla_detalle.setStyle(TableStyle([('BACKGROUND', (0, 0), (num_cols, 0), colors.Color(red=color_fondo_cabecera[0], green=color_fondo_cabecera[1], blue=color_fondo_cabecera[2])),
                                       ('ALIGN', (align_right_from, 0), (num_cols, filas), 'RIGHT'),
                                       ('ALIGN', (align_right_from-1, filas), (align_right_from-1, filas), 'RIGHT'),

                                       ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                                       ('FONTSIZE', (0, 0), (num_cols, 0), 9),
                                       ('FONTSIZE', (0, 1), (num_cols, filas), 8),
                                       ('FONTNAME', (0, 0), (num_cols, 0), 'Helvetica'),
                                       ('FONTNAME', (0, 1), (num_cols, filas), 'Helvetica'),
                                       ('FONTNAME', (0, filas), (num_cols, filas), 'Helvetica-Bold'),
                                       ('LEFTPADDING', (0, 0), (-1, -1), 2),
                                       ('RIGHTPADDING', (0, 1), (-1, -1), 1),
                                       ('VALIGN', (0, 1), (-1, -1), 'TOP'),
                                       ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                                       ('TEXTCOLOR', (num_cols, filas), (num_cols, filas), colors.Color(red=color_txt_cobrar[0], green=color_txt_cobrar[1], blue=color_txt_cobrar[2])),

                                       # deudas pendientes
                                       ('SPAN', (0, filas+1), (num_cols, filas+1)),
                                       ('BACKGROUND', (0, filas+1), (num_cols, filas+1), colors.Color(red=color_fondo_cabecera[0], green=color_fondo_cabecera[1], blue=color_fondo_cabecera[2])),
                                       ('FONTSIZE', (0, filas+1), (num_cols, filas+1), 9),
                                       ('FONTSIZE', (0, filas+2), (num_cols, filas_deudas), 8),
                                       ('FONTNAME', (0, filas+1), (num_cols, filas_deudas), 'Helvetica'),
                                       ('ALIGN', (align_right_from, filas+2), (num_cols, filas_deudas), 'RIGHT'),
                                       ('ALIGN', (0, filas_deudas), (0, filas_deudas), 'RIGHT'),
                                       ('FONTNAME', (num_cols, filas_deudas), (num_cols, filas_deudas), 'Helvetica-Bold'),
                                       ('TEXTCOLOR', (num_cols, filas_deudas), (num_cols, filas_deudas), colors.Color(red=0, green=0, blue=0) if total_deudas ==
                                        0 else colors.Color(red=color_txt_pendiente[0], green=color_txt_pendiente[1], blue=color_txt_pendiente[2])),

                                       # total a depositar
                                       ('ALIGN', (0, filas_deudas+1), (1, filas_deudas+1), 'RIGHT'),
                                       ('FONTSIZE', (0, filas_deudas+1), (1, filas_deudas+1), 9),
                                       ('FONTNAME', (0, filas_deudas+1), (1, filas_deudas+1), 'Helvetica-Bold'),
                                       ('TEXTCOLOR', (1, filas_deudas+1), (1, filas_deudas+1), colors.Color(red=color_txt_cobrar[0], green=color_txt_cobrar[1], blue=color_txt_cobrar[2])),
                                       ]))

    # tabla contenedora
    datos_tabla = [tabla_consumo, tabla_detalle]
    data = []
    data.append(datos_tabla)
    tabla_datos = Table(data, colWidths=[80*mm, 120*mm], repeatRows=1)
    tabla_datos.setStyle(TableStyle([('BACKGROUND', (0, 0), (1, 0), colors.Color(red=(255/255), green=(255/255), blue=(255/255))),
                                     ('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                     #('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                                     ('FONTSIZE', (0, 0), (1, 0), 9),
                                     ('FONTNAME', (0, 0), (1, 0), 'Helvetica'),
                                     ('LEFTPADDING', (0, 0), (-1, -1), 1),
                                     ('RIGHTPADDING', (0, 0), (-1, -1), 1),
                                     ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                     ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)]))
    # aniadimos la tabla
    Story.append(tabla_datos)

    # nota
    Story.append(Spacer(100*mm, 3*mm))
    nota = "NOTA: Debe ser cancelado hasta fecha 15 de cada mes, caso contrario se aplicara la multa correspondiente"
    p_nota = Paragraph(nota, style_nota)
    Story.append(p_nota)

    # leyenda
    leyenda = "SE RECOMIENDA NO DESPERDICIAR EL AGUA, VERIFICAR EL CIERRE DE GRIFOS E INODOROS"
    p_leyenda = Paragraph(leyenda, style_leyenda)
    Story.append(p_leyenda)

    # # tabla
    # datos_tabla = []
    # data = []

    # data.append(['Detalle', 'Monto'])

    # filas = 0
    # total = 0

    # # cargamos los registros
    # for det in detalles:
    #     detalle_txt = Paragraph(det.detalle, style_tabla_datos)
    #     datos_tabla = [detalle_txt, det.monto_bs]

    #     data.append(datos_tabla)
    #     filas += 1

    # tabla_datos = Table(data, colWidths=[80*mm, 20*mm], repeatRows=1)
    # num_cols = 1
    # align_right_from = 1

    # tabla_datos.setStyle(TableStyle([('BACKGROUND', (0, 0), (num_cols, 0), colors.Color(red=(204/255), green=(204/255), blue=(204/255))),
    #                                  ('ALIGN', (align_right_from, 0), (num_cols, filas), 'RIGHT'),
    #                                  ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    #                                  ('FONTSIZE', (0, 0), (num_cols, 0), 9),
    #                                  ('FONTSIZE', (0, 1), (num_cols, filas), 8),
    #                                  ('FONTNAME', (0, 0), (num_cols, 0), 'Helvetica'),
    #                                  ('FONTNAME', (0, 1), (num_cols, filas), 'Helvetica'),
    #                                  ('FONTNAME', (0, filas), (num_cols, filas), 'Helvetica-Bold'),
    #                                  ('LEFTPADDING', (0, 0), (-1, -1), 2),
    #                                  ('RIGHTPADDING', (0, 1), (-1, -1), 1),
    #                                  ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    #                                  ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)]))
    # # aniadimos la tabla
    # Story.append(tabla_datos)

    # creamos
    doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)
