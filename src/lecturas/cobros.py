from decimal import Decimal
import os
from utils.validators import validate_number_decimal, validate_number_int
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
# settings de la app
from django.conf import settings
from django.http import HttpResponseRedirect
from django.apps import apps

# propios
#from lecturas.models import Cobros, Lecturas

# para los usuarios
from utils.permissions import current_date, get_user_permission_operation, get_permissions_user, get_html_column, current_periodo, rango_periodos, show_periodo, get_system_settings

# controlador
from controllers.lecturas.CobrosController import CobrosController
from controllers.ListasController import ListasController
from controllers.cajas.CajasController import CajasController

import io
from django.http import FileResponse

from reportes.cobros.rptCobroRecibo import rptCobroRecibo

cobro_controller = CobrosController()
caja_controller = CajasController()
lista_controller = ListasController()


@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_COBROS, 'lista'), 'without_permission')
def cobros_index(request):
    permisos = get_permissions_user(request.user, settings.MOD_COBROS)

    # operaciones
    if 'operation_x' in request.POST.keys():
        operation = request.POST['operation_x']

        if not operation in ['', 'data_periodos', 'data_detalles', 'save_data', 'anular', 'imprimir_cobro', 'imprimir_todo']:
            return render(request, 'pages/without_permission.html', {})

        if operation == 'imprimir_cobro':
            if permisos.imprimir:
                try:
                    user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=request.user)
                    if not cobro_controller.permission_print(user_perfil, settings.MOD_COBROS, int(request.POST['id'].strip())):
                        return render(request, 'pages/without_permission.html', {})

                    buffer = io.BytesIO()
                    rptCobroRecibo(buffer, request.user, int(request.POST['id']))

                    buffer.seek(0)
                    return FileResponse(buffer, filename='cobro_recibo.pdf')

                except Exception as ex:
                    print('error al imprimir: ', str(ex))
                    request.session['internal_error'] = str(ex)
                    request.session.modified = True
                    return render(request, 'pages/internal_error.html', {'error': str(ex)})

            else:
                return render(request, 'pages/without_permission.html', {})

        if operation == 'anular':
            if permisos.anular:
                if cobro_controller.anular(request, request.user):
                    messages.add_message(request, messages.SUCCESS, {'type': 'success', 'title': 'Cobros!', 'description': 'Se anulo el cobro correctamente'})
                else:
                    messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Cobros!', 'description': 'Error al anular el cobro, ' + cobro_controller.error_operation})
            else:
                messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Cobros!', 'description': 'No tiene permisos de anulacion'})

            # volvemos a cargar los datos del periodo
            respuesta = cobros_periodos(request)
            if not type(respuesta) == bool:
                return respuesta
            else:
                return render(request, 'pages/internal_error.html', {'error': cobro_controller.error_operation})

        if operation == 'save_data':
            if cobro_controller.save_data(request, request.user):
                messages.add_message(request, messages.SUCCESS, {'type': 'success', 'title': 'Cobros!', 'description': 'Se registro el cobro correctamente'})
            else:
                messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Cobros!', 'description': 'Error al registrar el cobro, ' + cobro_controller.error_operation})

            # volvemos a cargar los datos del periodo
            respuesta = cobros_periodos(request)
            if not type(respuesta) == bool:
                return respuesta
            else:
                return render(request, 'pages/internal_error.html', {'error': cobro_controller.error_operation})

        if operation == 'data_periodos':
            respuesta = cobros_periodos(request)
            if not type(respuesta) == bool:
                return respuesta

        if operation == 'data_detalles':
            respuesta = cobros_detalles(request)
            if not type(respuesta) == bool:
                return respuesta

        # if operation == 'save_data':
        #     try:
        #         if cobro_controller.save_data(request, request.user):
        #             messages.add_message(request, messages.SUCCESS, {'type': 'success', 'title': 'Cobros!', 'description': 'Se registraron los datos correctamente'})
        #         else:
        #             messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Cobros!',
        #                                                              'description': 'Error al registrar los datos, ' + cobro_controller.error_operation})
        #     except Exception as ex:
        #         messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Cobros!', 'description': 'Error al registrar los datos, ' + str(ex)})

    # verificamos mensajes
    if 'nuevo_mensaje' in request.session.keys():
        messages.add_message(request, messages.SUCCESS, request.session['nuevo_mensaje'])
        del request.session['nuevo_mensaje']
        request.session.modified = True

    # datos por defecto
    lecturas_lista = cobro_controller.index(request)
    lecturas_session = request.session[cobro_controller.modulo_session]

    lista_bloques = lista_controller.get_lista_bloques(request.user, settings.MOD_COBROS)
    lista_pisos = lista_controller.get_lista_pisos(request.user, settings.MOD_COBROS)

    # departamentos ids
    departamentos_ids = cobro_controller.lista_departamentos_ids
    request.session['departamentos_ids'] = departamentos_ids
    request.session.modified = True

    status_cobrado = cobro_controller.status_cobrado
    cobrado = cobro_controller.cobrado

    fecha_actual = current_date()

    context = {
        'departamentos_ids': departamentos_ids,
        'status_cobrado': status_cobrado,
        'cobrado': cobrado,
        'fecha_actual': fecha_actual,

        'lecturas': lecturas_lista,
        'session': lecturas_session,
        'permisos': permisos,
        'url_main': '',
        'js_file': cobro_controller.modulo_session,
        'autenticado': 'si',
        'bloques': lista_bloques,
        'pisos': lista_pisos,

        'columnas': cobro_controller.columnas,

        'module_x': settings.MOD_COBROS,
        'module_x2': '',
        'module_x3': '',

        'operation_x': '',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }
    return render(request, 'lecturas/cobros.html', context)


# cobros periodos
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_COBROS, 'adicionar'), 'without_permission')
def cobros_periodos(request):
    try:
        permisos = get_permissions_user(request.user, settings.MOD_COBROS)

        # recuperamos las deudas pendientes del departamento
        id = validate_number_int('id', request.POST['id'])
        lista_cobros = cobro_controller.lista_deudas(id)

        # cobros ids
        lista_cobros_ids = ""
        for cobro in lista_cobros:
            lista_cobros_ids += str(cobro['cobro_id']) + ";"
        if len(lista_cobros_ids) > 0:
            lista_cobros_ids = lista_cobros_ids[0:len(lista_cobros_ids)-1]

        cobrado = cobro_controller.cobrado

        # verificamos si tiene caja activa
        caja_lista = caja_controller.cash_active(current_date(), request.user, formato_ori='yyyy-mm-dd')
        tiene_caja = 0
        if caja_lista:
            tiene_caja = 1

        context = {
            'url_main': '',
            'permisos': permisos,
            'autenticado': 'si',
            'lista_cobros': lista_cobros,
            'cobrado': cobrado,
            'lista_cobros_ids': lista_cobros_ids,
            'tiene_caja': tiene_caja,

            'module_x': settings.MOD_COBROS,
            'module_x2': '',
            'module_x3': '',

            'operation_x': 'periodos',
            'operation_x2': '',
            'operation_x3': '',

            'id': '',
            'id2': '',
            'id3': '',
        }

        return render(request, 'lecturas/cobros_periodos.html', context)

    except Exception as ex:
        return render(request, 'pages/internal_error.html', {'error': str(ex)})


# cobros detalles
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_COBROS, 'adicionar'), 'without_permission')
def cobros_detalles(request):
    try:
        # recuperamos las deudas pendientes del departamento
        id = validate_number_int('id', request.POST['id'])
        lista_detalles = cobro_controller.lista_detalles(id)

        cobrado = cobro_controller.cobrado

        context = {
            'url_main': '',
            'autenticado': 'si',
            'detalles': lista_detalles,
            'cobrado': cobrado,

            'module_x': settings.MOD_COBROS,
            'module_x2': '',
            'module_x3': '',

            'operation_x': 'detalles',
            'operation_x2': '',
            'operation_x3': '',

            'id': '',
            'id2': '',
            'id3': '',
        }
        return render(request, 'lecturas/cobros_detalles.html', context)

    except Exception as ex:
        return render(request, 'pages/internal_error.html', {'error': str(ex)})
