from utils.permissions import show_periodo
from utils.dates_functions import get_date_show
from django.db import connection
from permisos.models import UsersPerfiles
from django.shortcuts import render

from django.conf import settings
from django.contrib.auth.models import User
# password
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib import messages
# reverse
from django.urls import reverse
from django.apps import apps
from controllers.SystemController import SystemController

# configuraciones
from src.configuraciones.configuraciones import configuraciones_index
from src.configuraciones.bloques import bloques_index
from src.configuraciones.pisos import pisos_index
from src.configuraciones.cobros_mensuales import cobros_mensuales_index
from src.configuraciones.cobros_manuales import cobros_manuales_index
from src.configuraciones.sucursales import sucursales_index
from src.configuraciones.puntos import puntos_index
from src.configuraciones.usuarios import usuarios_index

# cajas
from src.cajas.cajas_iniciar import cajas_iniciar_index
from src.cajas.cajas_iniciar_recibir import cajas_iniciar_recibir_index
from src.cajas.cajas_entregar import cajas_entregar_index
from src.cajas.cajas_entregar_recibir import cajas_entregar_recibir_index
from src.cajas.cajas_movimientos import cajas_movimientos_index
from src.cajas.cajas_ingresos import cajas_ingresos_index
from src.cajas.cajas_egresos import cajas_egresos_index

# departamentos
from src.departamentos.departamentos import departamentos_index

# lecturas
from src.lecturas.lecturas import lecturas_index
from src.lecturas.asignar_cobros_manuales import asignar_cobros_manuales_index
from src.lecturas.cobros import cobros_index

# actividades
from src.configuraciones.actividades import actividades_index
from src.calendario.calendario import calendario_index

# reportes
from src.reportes.reportes import reportes_index
# recibos
from src.calendario.lista_cobros import lista_cobros_index


def index(request):
    """pagina index"""

    if 'module_x' in request.POST.keys():
        module_id = int(request.POST['module_x'])

        # # cambiar password
        if module_id == 1000:
            return cambiar_password(request)

        if module_id == settings.MOD_CONFIGURACIONES_SISTEMA:
            return configuraciones_index(request)

        if module_id == settings.MOD_BLOQUES:
            return bloques_index(request)

        if module_id == settings.MOD_PISOS:
            return pisos_index(request)

        if module_id == settings.MOD_COBROS_MENSUALES:
            return cobros_mensuales_index(request)

        if module_id == settings.MOD_COBROS_MANUALES:
            return cobros_manuales_index(request)

        if module_id == settings.MOD_SUCURSALES:
            return sucursales_index(request)

        if module_id == settings.MOD_PUNTOS:
            return puntos_index(request)

        if module_id == settings.MOD_USUARIOS:
            return usuarios_index(request)

        # cajas
        # cajas
        if module_id == settings.MOD_INICIAR_CAJA:
            return cajas_iniciar_index(request)

        if module_id == settings.MOD_INICIAR_CAJA_RECIBIR:
            return cajas_iniciar_recibir_index(request)

        if module_id == settings.MOD_ENTREGAR_CAJA:
            return cajas_entregar_index(request)

        if module_id == settings.MOD_ENTREGAR_CAJA_RECIBIR:
            return cajas_entregar_recibir_index(request)

        if module_id == settings.MOD_CAJAS_INGRESOS:
            return cajas_ingresos_index(request)

        if module_id == settings.MOD_CAJAS_EGRESOS:
            return cajas_egresos_index(request)

        if module_id == settings.MOD_CAJAS_MOVIMIENTOS:
            return cajas_movimientos_index(request)

        # departamentos
        if module_id == settings.MOD_DEPARTAMENTOS:
            return departamentos_index(request)

        # lecturas
        if module_id == settings.MOD_LECTURAS:
            return lecturas_index(request)

        # asignar cobros manuales
        if module_id == settings.MOD_ASIGNAR_COBROS_MANUALES:
            return asignar_cobros_manuales_index(request)

        # cobros
        if module_id == settings.MOD_COBROS:
            return cobros_index(request)

        # actividades
        if module_id == settings.MOD_ACTIVIDADES:
            return actividades_index(request)

        # calendario
        if module_id == settings.MOD_CALENDARIO:
            return calendario_index(request)

        # reportes
        if module_id == settings.MOD_REPORTES:
            return reportes_index(request)

        # lista cobros
        if module_id == settings.MOD_LISTA_COBROS:
            return lista_cobros_index(request)

        context = {
            'module_id': module_id,
        }

        return render(request, 'pages/nada.html', context)

    #system_controller = SystemController()

    usuario = request.user
    #print('usuario: ', usuario)
    id_usuario = usuario.id
    if id_usuario:
        autenticado = 'si'
    else:
        autenticado = 'no'
        usuario = {}

    #print('autenticado..', autenticado)
    # webpush
    webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
    vapid_key = webpush_settings.get('VAPID_PUBLIC_KEY')

    url_empresa = settings.SUB_URL_EMPRESA

    # usuarios del sistema para la notificacion
    status_activo = apps.get_model('status', 'Status').objects.get(pk=1)
    filtro_usuarios = {}
    filtro_usuarios['status_id'] = status_activo
    filtro_usuarios['perfil_id__perfil_id__in'] = [settings.PERFIL_ADMIN, settings.PERFIL_SUPERVISOR, settings.PERFIL_CAJERO]
    filtro_usuarios['notificacion'] = 1

    usuarios_notificacion = apps.get_model('permisos', 'UsersPerfiles').objects.filter(**filtro_usuarios).order_by('user_perfil_id')
    lista_notificacion = ''
    for usuario_notif in usuarios_notificacion:
        lista_notificacion += str(usuario_notif.user_id.id) + '|'

    if len(lista_notificacion) > 0:
        lista_notificacion = lista_notificacion[0:len(lista_notificacion)-1]

    if settings.SUB_URL_EMPRESA != '':
        url_push = '/' + settings.SUB_URL_EMPRESA + '/send_push'
    else:
        url_push = '/send_push'

    context = {
        'autenticado': autenticado,
        'url_notificacion': 'url_notificacion',
        'pagina_inicio': 'si',
        'user': usuario,
        'vapid_key': vapid_key,
        'url_empresa': url_empresa,
        'lista_notificacion': lista_notificacion,
        'url_webpush': url_push,
    }

    return render(request, 'pages/index.html', context)

# cambio de password


def cambiar_password(request):
    """cambio de password de los usuarios"""
    usuario = request.user
    id_usuario = usuario.id
    if id_usuario:
        autenticado = 'si'
    else:
        autenticado = 'no'
        return render(request, 'pages/without_permission.html')

    # por defecto
    usuario_actual = User.objects.get(pk=request.user.id)
    usuario_perfil = UsersPerfiles.objects.get(user_id=usuario_actual)

    if 'operation_x' in request.POST.keys():
        operation = request.POST['operation_x']
        # busqueda cliente por ci
        if operation == 'add':
            # verificamos
            error = 0
            password = request.POST['actual'].strip()
            nuevo = request.POST['nuevo'].strip()
            nuevo2 = request.POST['nuevo2'].strip()

            if error == 0 and nuevo == '' and nuevo2 == '':
                error = 1
                messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Usuario!', 'description': 'Debe llenar su nuevo password y su repeticion'})

            if error == 0 and not check_password(password, usuario_actual.password):
                #print('db ', usuario_actual.password)
                #print('puso ', password)
                error = 1
                messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Usuario!', 'description': 'Error en su password'})

            if error == 0 and nuevo != nuevo2:
                error = 1
                messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Usuario!', 'description': 'La repeticion de su password no coincide'})

            if error == 0 and len(nuevo) < 6:
                error = 1
                messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Usuario!', 'description': 'Su nuevo password debe tener al menos 6 letras'})

            if error == 0:
                # actualizamos
                usuario_actual.password = make_password(nuevo)
                usuario_actual.save()
                messages.add_message(request, messages.SUCCESS, {'type': 'success', 'title': 'Usuario!', 'description': 'Su nuevo password se cambio correctamente'})

    context = {
        'autenticado': autenticado,
        'usuario_actual': usuario_actual,

        'module_x': 1000,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'add',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }

    return render(request, 'pages/cambiar_password.html', context)


def reemplazar_codigo_html(cadena):
    retorno = cadena
    retorno = retorno.replace('&', "&#38;")
    retorno = retorno.replace('#', "&#35;")

    retorno = retorno.replace("'", "&#39;")
    retorno = retorno.replace('"', "&#34;")
    retorno = retorno.replace('á', "&#225;")
    retorno = retorno.replace('é', "&#233;")
    retorno = retorno.replace('í', "&#237;")
    retorno = retorno.replace('ó', "&#243;")
    retorno = retorno.replace('ú', "&#250;")
    retorno = retorno.replace('Á', "&#193;")
    retorno = retorno.replace('É', "&#201;")
    retorno = retorno.replace('Í', "&#205;")
    retorno = retorno.replace('Ó', "&#211;")
    retorno = retorno.replace('Ú', "&#218;")
    retorno = retorno.replace('!', "&#33;")

    retorno = retorno.replace('$', "&#36;")
    retorno = retorno.replace('%', "&#37;")
    retorno = retorno.replace('*', "&#42;")
    retorno = retorno.replace('+', "&#43;")
    retorno = retorno.replace('-', "&#45;")
    retorno = retorno.replace('', "")
    retorno = retorno.replace('', "")
    retorno = retorno.replace('', "")
    retorno = retorno.replace('', "")
    retorno = retorno.replace('', "")
    retorno = retorno.replace('', "")

    return retorno


# notificaciones para el usuario
def notificaciones_pagina(request):
    #context = {'abc': 'asdd'}
    # return render(request, 'pages/nada.html', context)

    usuario = request.user
    id_usuario = usuario.id
    if id_usuario:
        autenticado = 'si'
    else:
        autenticado = 'no'

    if autenticado == 'no':
        context = {
            'cantidad': 0,
            'cantidad_rojos': 0,
            'notificaciones': {},
            'autenticado': autenticado,
        }
        return render(request, 'pages/notificaciones_pagina.html', context)

    try:
        user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=request.user)
        #punto = apps.get_model('configuraciones', 'Puntos').objects.get(pk=user_perfil.punto_id)
        #sucursal = apps.get_model('configuraciones', 'Sucursales').objects.get(pk=punto.sucursal_id.sucursal_id)

        lista_notificaciones = []
        cantidad = 0
        cantidad_rojos = 0
        cantidad_normal = 0

        if user_perfil.perfil_id.perfil_id == settings.PERFIL_DEPARTAMENTO:
            departamento = apps.get_model('departamentos', 'Departamentos').objects.get(departamento=user_perfil.user_id.username)
            # mostramos las solicitudes de reserva que hizo
            sql = "SELECT c.calendario_id, c.fecha_actividad_ini, c.fecha_actividad_fin, c.detalle, a.actividad FROM calendario c, actividades a "
            sql += f"WHERE c.actividad_id=a.actividad_id AND c.departamento_id='{departamento.departamento_id}' AND c.status_id='{settings.STATUS_INACTIVO}' "
            sql += "ORDER BY c.fecha_actividad_ini "
            with connection.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    objeto = {}
                    objeto['tabla_id'] = row[0]
                    objeto['tipo'] = 'calendario'

                    fecha_ini = get_date_show(fecha=row[1], formato='dd-MMM-yyyy HH:ii')
                    aux_fin = str(row[2])
                    div_aux = aux_fin.split(' ')
                    hora_fin = div_aux[1][0:5]

                    objeto['descripcion'] = row[4] + ', ' + fecha_ini + '-' + hora_fin
                    objeto['url'] = 'calendario'

                    lista_notificaciones.append(objeto)
                    cantidad_normal += 1
                    cantidad += 1

            # mostramos deudas pendientes
            sql = "SELECT c.cobro_id, c.periodo, c.monto_bs FROM cobros c "
            sql += f"WHERE c.departamento_id='{departamento.departamento_id}' AND c.status_id='{settings.STATUS_ACTIVO}' "
            sql += "ORDER BY c.periodo "
            with connection.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    objeto = {}
                    objeto['tabla_id'] = row[0]
                    objeto['tipo'] = 'cobros'
                    objeto['descripcion'] = 'Recibo ' + show_periodo(row[1]) + ', ' + str(row[2]) + " Bs."
                    objeto['url'] = 'lista_cobros'

                    lista_notificaciones.append(objeto)
                    cantidad_rojos += 1
                    cantidad += 1

        else:
            # mostramos las solicitudes de reserva que hicieron los departamentos
            sql = "SELECT c.calendario_id, c.fecha_actividad_ini, c.fecha_actividad_fin, c.detalle, a.actividad, d.departamento FROM calendario c, actividades a, departamentos d "
            sql += f"WHERE c.actividad_id=a.actividad_id AND c.departamento_id=d.departamento_id AND c.status_id='{settings.STATUS_INACTIVO}' "
            sql += "ORDER BY c.fecha_actividad_ini "
            with connection.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    objeto = {}
                    objeto['tabla_id'] = row[0]
                    objeto['tipo'] = 'calendario'

                    fecha_ini = get_date_show(fecha=row[1], formato='dd-MMM-yyyy HH:ii')
                    aux_fin = str(row[2])
                    div_aux = aux_fin.split(' ')
                    hora_fin = div_aux[1][0:5]

                    objeto['descripcion'] = row[4] + '(' + row[5] + '), ' + fecha_ini + '-' + hora_fin
                    objeto['url'] = 'calendario'

                    lista_notificaciones.append(objeto)
                    cantidad += 1
                    cantidad_normal += 1

        # context para el html
        context = {
            'notificaciones': lista_notificaciones,
            'cantidad': cantidad,
            'cantidad_rojos': cantidad_rojos,
            'cantidad_normal': cantidad_normal,
            'autenticado': autenticado,
        }

        return render(request, 'pages/notificaciones_pagina.html', context)

    except Exception as e:
        print('ERROR ' + str(e))
        context = {
            'cantidad': 0,
            'cantidad_rojos': 0,
            'notificaciones': {},
            'autenticado': autenticado,
        }
        return render(request, 'pages/notificaciones_pagina.html', context)
