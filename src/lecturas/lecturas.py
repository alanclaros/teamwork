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
from controllers.lecturas.LecturasController import LecturasController
from controllers.ListasController import ListasController


lectura_controller = LecturasController()
lista_controller = ListasController()


@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_LECTURAS, 'lista'), 'without_permission')
def lecturas_index(request):
    permisos = get_permissions_user(request.user, settings.MOD_LECTURAS)

    # operaciones
    if 'operation_x' in request.POST.keys():
        operation = request.POST['operation_x']
        if not operation in ['', 'save_data_periodo', 'save_data']:
            return render(request, 'pages/without_permission.html', {})

        if operation == 'save_data_periodo':
            try:
                periodo_session = request.session[lectura_controller.modulo_session]['search_periodo']
                cobros_mens = apps.get_model('configuraciones', 'CobrosMensuales').objects.filter(status_id=lectura_controller.status_activo)
                # vaciamos antes de insertar
                cobros_mensuales_periodo = apps.get_model('lecturas', 'CobrosMensualesPeriodos').objects.filter(periodo=periodo_session)
                cobros_mensuales_periodo.delete()
                user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=request.user)

                for co_mens in cobros_mens:
                    nombre = 'cobro_mensual_' + str(co_mens.cobro_mensual_id)
                    if nombre in request.POST.keys():
                        monto_cobrar = validate_number_decimal('monto cobrar', request.POST['monto_cobrar_'+str(co_mens.cobro_mensual_id)])
                        cmp_add = apps.get_model('lecturas', 'CobrosMensualesPeriodos').objects.create(
                            periodo=periodo_session, monto_bs=monto_cobrar, cobro_mensual_id=co_mens, status_id=lectura_controller.status_activo, user_perfil_id=user_perfil
                        )
                        cmp_add.save()

                #messages.add_message(request, messages.SUCCESS, {'type': 'success', 'title': 'Lecturas!', 'description': 'Se registraron los cobros mensuales para todos los departamentos'})

                if lectura_controller.save_cobros_mensuales_periodo(periodo_session, request.user):
                    messages.add_message(request, messages.SUCCESS, {'type': 'success', 'title': 'Lecturas!', 'description': 'Se registraron los cobros mensuales para todos los departamentos'})
                else:
                    messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Lecturas!',
                                         'description': 'Error al registrar los cobros mensuales para el periodo, ' + lectura_controller.error_operation})

            except Exception as ex:
                messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Lecturas!', 'description': 'Error al registrar los cobros mensuales para el periodo, ' + str(ex)})

        if operation == 'save_data':
            try:
                periodo_session = request.session[lectura_controller.modulo_session]['search_periodo']
                if lectura_controller.save_data(periodo_session, request, request.user):
                    messages.add_message(request, messages.SUCCESS, {'type': 'success', 'title': 'Lecturas!', 'description': 'Se registraron los datos correctamente'})
                else:
                    messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Lecturas!',
                                                                     'description': 'Error al registrar los datos, ' + lectura_controller.error_operation})
            except Exception as ex:
                messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Lecturas!', 'description': 'Error al registrar los datos, ' + str(ex)})

    # verificamos mensajes
    if 'nuevo_mensaje' in request.session.keys():
        messages.add_message(request, messages.SUCCESS, request.session['nuevo_mensaje'])
        del request.session['nuevo_mensaje']
        request.session.modified = True

    # datos por defecto
    lecturas_lista = lectura_controller.index(request)
    lecturas_session = request.session[lectura_controller.modulo_session]

    lista_bloques = lista_controller.get_lista_bloques(request.user, settings.MOD_LECTURAS)
    lista_pisos = lista_controller.get_lista_pisos(request.user, settings.MOD_LECTURAS)
    lista_cobros_manuales = lista_controller.get_lista_cobros_manuales(request.user, settings.MOD_LECTURAS)
    cobros_manuales_ids = ""
    for aux_lcm in lista_cobros_manuales:
        cobros_manuales_ids += str(aux_lcm.cobro_manual_id) + ";"
    if len(cobros_manuales_ids) > 0:
        cobros_manuales_ids = cobros_manuales_ids[0:len(cobros_manuales_ids)-1]

    periodo_actual = current_periodo()
    lista_periodos = rango_periodos(periodo_actual)

    # verificamos si se registro en la tabla de cobros mensuales periodos
    periodo_session = lecturas_session['search_periodo']
    cantidad_cmp = apps.get_model('lecturas', 'CobrosMensualesPeriodos').objects.filter(periodo=periodo_session).count()
    #cantidad_cmp = 1
    aux_lista_cobros_mensuales = lista_controller.get_lista_cobros_mensuales(request.user, settings.MOD_LECTURAS)
    lista_cmp = apps.get_model('lecturas', 'CobrosMensualesPeriodos').objects.filter(periodo=periodo_session).order_by('cobro_mensual_id__cobro_mensual')
    lista_cobros_mensuales = []
    for aux_lcm in aux_lista_cobros_mensuales:
        objeto = {}
        objeto['cobro_mensual_id'] = aux_lcm.cobro_mensual_id
        objeto['cobro_mensual'] = aux_lcm.cobro_mensual
        objeto['monto_cobrar'] = aux_lcm.monto_cobrar
        objeto['status_id'] = aux_lcm.status_id
        objeto['cobro_mensual_periodo_id'] = 0
        # verificamos si ya tiene un registro
        for aux_cmp in lista_cmp:
            if aux_cmp.cobro_mensual_id == aux_lcm:
                objeto['monto_cobrar'] = aux_cmp.monto_bs
                objeto['cobro_mensual_periodo_id'] = aux_cmp.cobro_mensual_periodo_id

        lista_cobros_mensuales.append(objeto)

    cm_ids = ''
    for cm in aux_lista_cobros_mensuales:
        cm_ids += str(cm.cobro_mensual_id) + ';'

    if len(cm_ids) > 0:
        cm_ids = cm_ids[0:len(cm_ids)-1]

    # cantidad cobros mensuales para el periodo
    cantidad_cm_periodo = lectura_controller.cantidad_cobros_mensuales(periodo_session)
    #cantidad_cm_periodo= 1

    settings_sistema = get_system_settings()
    costo_m3 = settings_sistema['costo_m3']
    expensas_monto_m2 = settings_sistema['expensas_monto_m2']
    costo_minimo = settings_sistema['costo_minimo']
    unidad_minima_m3 = settings_sistema['unidad_minima_m3']

    # departamentos ids
    departamentos_ids = lectura_controller.lista_departamentos_ids
    request.session['departamentos_ids'] = departamentos_ids
    request.session.modified = True
    #print('accc: ', departamentos_ids)

    status_cobrado = lectura_controller.status_cobrado
    cobrado = lectura_controller.cobrado

    context = {
        'costo_m3': costo_m3,
        'expensas_monto_m2': expensas_monto_m2,
        'costo_minimo': costo_minimo,
        'unidad_minima_m3': unidad_minima_m3,

        'departamentos_ids': departamentos_ids,
        'status_cobrado': status_cobrado,
        'cobrado': cobrado,

        'lecturas': lecturas_lista,
        'session': lecturas_session,
        'permisos': permisos,
        'url_main': '',
        'js_file': lectura_controller.modulo_session,
        'autenticado': 'si',
        'bloques': lista_bloques,
        'pisos': lista_pisos,
        'periodo_actual': periodo_actual,
        'periodos': lista_periodos,
        'cobros_mensuales_ids': cm_ids,
        'cobros_manuales_ids': cobros_manuales_ids,

        'cantidad_cmp': cantidad_cmp,
        'lista_cobros_mensuales': lista_cobros_mensuales,
        # 'lista_cmp': lista_cmp,
        'periodo_session': periodo_session,
        'periodo_session_show': show_periodo(periodo_session),
        'cantidad_cm_periodo': cantidad_cm_periodo,

        'columnas': lectura_controller.columnas,

        'module_x': settings.MOD_LECTURAS,
        'module_x2': '',
        'module_x3': '',

        'operation_x': '',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }
    return render(request, 'lecturas/lecturas.html', context)
