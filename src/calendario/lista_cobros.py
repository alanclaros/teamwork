import os
from utils.validators import validate_number_decimal
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
# settings de la app
from django.conf import settings
from django.http import HttpResponseRedirect
from django.apps import apps

# para los usuarios
from utils.permissions import current_date, current_periodo, get_user_permission_operation, get_permissions_user, next_periodo, previous_periodo, show_periodo
from datetime import datetime

# controlador
from controllers.SystemController import SystemController
import io
from django.http import FileResponse
from reportes.cobros.rptCobroRecibo import rptCobroRecibo


system_controller = SystemController()


@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_LISTA_COBROS, 'lista'), 'without_permission')
def lista_cobros_index(request):
    permisos = get_permissions_user(request.user, settings.MOD_LISTA_COBROS)

    user_perfil = None
    fecha_actual = None
    lista_recibos = []
    departamento = {'departamento_id': 0}

    try:
        user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=request.user)
        fecha_actual = datetime.now()

        if user_perfil.perfil_id.perfil_id == settings.PERFIL_DEPARTAMENTO:
            lista_recibos = system_controller.lista_recibos_id(fecha_actual, user_perfil)
            departamento = apps.get_model('departamentos', 'Departamentos').objects.get(departamento=user_perfil.user_id.username)

    except Exception as ex:
        context = {
            'type': 'warning',
            'title': 'Lista Recibos!',
            'description': 'Error al recuperar datos, ' + str(ex),
            'existe_error': 1
        }
        return render(request, 'partials/_alert_resultado.html', context)

    # operaciones
    if 'operation_x' in request.POST.keys():
        operation = request.POST['operation_x']
        if not operation in ['', 'mostrar_recibo']:
            return render(request, 'pages/without_permission.html', {})

        if operation == 'mostrar_recibo':
            try:

                id = request.POST['id']
                periodo_recibo = ''
                # verificamos que este entre los permitidos
                permitido = 'no'
                for recibo in lista_recibos:
                    if int(recibo['cobro_id']) == int(id):
                        permitido = 'si'
                        periodo_recibo = recibo['periodo']
                        break

                if permitido == 'si':
                    # mostramos recibo
                    try:
                        buffer = io.BytesIO()
                        rptCobroRecibo(buffer, request.user, int(id))

                        buffer.seek(0)
                        return FileResponse(buffer, filename='recibo' + periodo_recibo + '.pdf')

                    except Exception as ex:
                        print('error al imprimir: ', str(ex))
                        request.session['internal_error'] = str(ex)
                        request.session.modified = True
                        return render(request, 'pages/internal_error.html', {'error': str(ex)})
                else:
                    context = {
                        'type': 'warning',
                        'title': 'Lista Recibos!',
                        'description': 'No puede imprimir este recibo',
                        'existe_error': 1
                    }
                return render(request, 'partials/_alert_resultado.html', context)

            except Exception as ex:
                context = {
                    'type': 'warning',
                    'title': 'Lista Recibos!',
                    'description': 'Error al recuperar datos ' + str(ex),
                    'existe_error': 1
                }
                return render(request, 'partials/_alert_resultado.html', context)

    # verificamos mensajes
    if 'nuevo_mensaje' in request.session.keys():
        messages.add_message(request, messages.SUCCESS, request.session['nuevo_mensaje'])
        del request.session['nuevo_mensaje']
        request.session.modified = True

    # perfil de usuario
    print('asdfasd')
    context = {
        'permisos': permisos,
        'url_main': '',
        'js_file': 'lista_cobros',
        'autenticado': 'si',

        'activo': settings.STATUS_ACTIVO,
        'cobrado': settings.STATUS_COBRADO,
        'lista_recibos': lista_recibos,
        'departamento': departamento,

        'user_perfil': user_perfil,

        'module_x': settings.MOD_LISTA_COBROS,
        'module_x2': '',
        'module_x3': '',

        'operation_x': '',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }
    return render(request, 'calendario/lista_cobros.html', context)
