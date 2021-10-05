from decimal import Decimal
import os
from utils.validators import validate_number_decimal
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
# settings de la app
from django.conf import settings
from django.http import HttpResponseRedirect
from django.apps import apps

# propios
from lecturas.models import Lecturas

# para los usuarios
from utils.permissions import get_user_permission_operation, get_permissions_user, get_html_column, current_periodo, rango_periodos, show_periodo, get_system_settings

# controlador
from controllers.lecturas.AsignarCobrosManualesController import AsignarCobrosManualesController
from controllers.ListasController import ListasController


asignar_cm_controller = AsignarCobrosManualesController()
lista_controller = ListasController()


@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_ASIGNAR_COBROS_MANUALES, 'lista'), 'without_permission')
def asignar_cobros_manuales_index(request):
    permisos = get_permissions_user(request.user, settings.MOD_ASIGNAR_COBROS_MANUALES)

    # operaciones
    if 'operation_x' in request.POST.keys():
        operation = request.POST['operation_x']
        if not operation in ['', 'save_data']:
            return render(request, 'pages/without_permission.html', {})

        if operation == 'save_data':
            try:
                periodo_session = request.session[asignar_cm_controller.modulo_session]['search_periodo']
                if asignar_cm_controller.save_data(periodo_session, request, request.user):
                    messages.add_message(request, messages.SUCCESS, {'type': 'success', 'title': 'Asignar Cobros Manuales!', 'description': 'Se registraron los datos correctamente'})
                else:
                    messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Asignar Cobros Manuales!',
                                                                     'description': 'Error al registrar los datos, ' + asignar_cm_controller.error_operation})
            except Exception as ex:
                messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Asignar Cobros Manuales!', 'description': 'Error al registrar los datos, ' + str(ex)})

    # verificamos mensajes
    if 'nuevo_mensaje' in request.session.keys():
        messages.add_message(request, messages.SUCCESS, request.session['nuevo_mensaje'])
        del request.session['nuevo_mensaje']
        request.session.modified = True

    # datos por defecto
    lecturas_lista = asignar_cm_controller.index(request)
    lecturas_session = request.session[asignar_cm_controller.modulo_session]

    lista_bloques = lista_controller.get_lista_bloques(request.user, settings.MOD_ASIGNAR_COBROS_MANUALES)
    lista_pisos = lista_controller.get_lista_pisos(request.user, settings.MOD_ASIGNAR_COBROS_MANUALES)
    lista_cobros_manuales = lista_controller.get_lista_cobros_manuales(request.user, settings.MOD_ASIGNAR_COBROS_MANUALES)

    periodo_actual = current_periodo()
    lista_periodos = rango_periodos(periodo_actual)

    # verificamos si se registro en la tabla de cobros mensuales periodos
    periodo_session = lecturas_session['search_periodo']
    cantidad_cmp = apps.get_model('lecturas', 'CobrosMensualesPeriodos').objects.filter(periodo=periodo_session).count()
    #cantidad_cmp = 1

    # departamentos ids
    departamentos_ids = asignar_cm_controller.lista_departamentos_ids
    monto_cobro_manual = asignar_cm_controller.monto_cobro_manual
    request.session['asignar_cm_departamentos_ids'] = departamentos_ids
    request.session.modified = True
    #print('accc: ', departamentos_ids)

    status_cobrado = asignar_cm_controller.status_cobrado
    cobrado = asignar_cm_controller.cobrado

    context = {
        'departamentos_ids': departamentos_ids,
        'status_cobrado': status_cobrado,
        'cobrado': cobrado,
        'lista_cobros_manuales': lista_cobros_manuales,
        'monto_cobro_manual': monto_cobro_manual,

        'lecturas': lecturas_lista,
        'session': lecturas_session,
        'permisos': permisos,
        'url_main': '',
        'js_file': asignar_cm_controller.modulo_session,
        'autenticado': 'si',
        'bloques': lista_bloques,
        'pisos': lista_pisos,
        'periodo_actual': periodo_actual,
        'periodos': lista_periodos,

        'cantidad_cmp': cantidad_cmp,
        # 'lista_cmp': lista_cmp,
        'periodo_session': periodo_session,
        'periodo_session_show': show_periodo(periodo_session),

        'columnas': asignar_cm_controller.columnas,

        'module_x': settings.MOD_ASIGNAR_COBROS_MANUALES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': '',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }
    return render(request, 'lecturas/asignar_cobros_manuales.html', context)
