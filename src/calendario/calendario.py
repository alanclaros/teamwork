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
from calendario.models import Calendario

# para los usuarios
from utils.permissions import get_user_permission_operation, get_permissions_user, next_periodo, previous_periodo, show_periodo

# controlador
from controllers.calendario.CalendarioController import CalendarioController
from controllers.ListasController import ListasController


calendario_controller = CalendarioController()
lista_controller = ListasController()


@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_CALENDARIO, 'lista'), 'without_permission')
def calendario_index(request):
    permisos = get_permissions_user(request.user, settings.MOD_CALENDARIO)

    # operaciones
    if 'operation_x' in request.POST.keys():
        operation = request.POST['operation_x']
        if not operation in ['', 'registrar_actividad', 'confirmar_actividad', 'anular_actividad', 'anular_actividad_user']:
            return render(request, 'pages/without_permission.html', {})

        if operation == 'anular_actividad':
            try:
                user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=request.user)

                id = request.POST['id']
                if calendario_controller.anular_actividad(id, request.user):
                    context = {
                        'type': 'success',
                        'title': 'Calendario!',
                        'description': 'Se anulo la actividad correctamente',
                        'existe_error': 0
                    }
                    return render(request, 'partials/_alert_resultado.html', context)
                else:
                    context = {
                        'type': 'warning',
                        'title': 'Calendario!',
                        'description': 'Error al anular la actividad ' + calendario_controller.error_operation,
                        'existe_error': 1
                    }
                    return render(request, 'partials/_alert_resultado.html', context)

            except Exception as ex:
                context = {
                    'type': 'warning',
                    'title': 'Calendario!',
                    'description': 'Error al anular la actividad ' + str(ex),
                    'existe_error': 1
                }
                return render(request, 'partials/_alert_resultado.html', context)

        if operation == 'anular_actividad_user':
            try:
                user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=request.user)

                id = request.POST['id']
                dia = request.POST['dia']
                if calendario_controller.anular_actividad(id, request.user):
                    context = {
                        'type': 'success',
                        'title': 'Calendario!',
                        'description': 'Se anulo la actividad correctamente',
                        'existe_error': 0,
                        'id_error': '_' + dia
                    }
                    return render(request, 'partials/_alert_resultado.html', context)
                else:
                    context = {
                        'type': 'warning',
                        'title': 'Calendario!',
                        'description': 'Error al anular la actividad ' + calendario_controller.error_operation,
                        'existe_error': 1,
                        'id_error': '_' + dia
                    }
                    return render(request, 'partials/_alert_resultado.html', context)

            except Exception as ex:
                context = {
                    'type': 'warning',
                    'title': 'Calendario!',
                    'description': 'Error al anular la actividad ' + str(ex),
                    'existe_error': 1,
                    'id_error': '_' + dia
                }
                return render(request, 'partials/_alert_resultado.html', context)

        if operation == 'confirmar_actividad':
            try:
                user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=request.user)

                if user_perfil.perfil_id.perfil_id == settings.PERFIL_DEPARTAMENTO:
                    context = {
                        'type': 'danger',
                        'title': 'Calendario!',
                        'description': 'No tiene permiso para confirmar actividades',
                        'existe_error': 1
                    }
                    return render(request, 'partials/_alert_resultado.html', context)

                else:
                    id = request.POST['id']
                    if calendario_controller.confirmar_actividad(id, request.user):
                        context = {
                            'type': 'success',
                            'title': 'Calendario!',
                            'description': 'Se confirmo la actividad correctamente',
                            'existe_error': 0
                        }
                        return render(request, 'partials/_alert_resultado.html', context)
                    else:
                        context = {
                            'type': 'warning',
                            'title': 'Calendario!',
                            'description': 'Error al confirmar la actividad ' + calendario_controller.error_operation,
                            'existe_error': 1
                        }
                        return render(request, 'partials/_alert_resultado.html', context)

            except Exception as ex:
                context = {
                    'type': 'warning',
                    'title': 'Calendario!',
                    'description': 'Error al confirmar la actividad ' + str(ex),
                    'existe_error': 1
                }
                return render(request, 'partials/_alert_resultado.html', context)

        if operation == 'registrar_actividad':
            try:
                periodo_session = request.session[calendario_controller.modulo_session]['search_periodo']
                user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=request.user)

                if user_perfil.perfil_id.perfil_id == settings.PERFIL_DEPARTAMENTO:
                    if calendario_controller.solicitar_actividad(periodo_session, request, request.user):
                        context = {
                            'type': 'success',
                            'title': 'Calendario!',
                            'description': 'Se registro la solicitud correctamente',
                            'existe_error': 0
                        }
                        return render(request, 'partials/_alert_resultado.html', context)
                    else:
                        context = {
                            'type': 'warning',
                            'title': 'Calendario!',
                            'description': 'Error al registrar la actividad ' + calendario_controller.error_operation,
                            'existe_error': 1
                        }
                        return render(request, 'partials/_alert_resultado.html', context)

                else:
                    if calendario_controller.registrar_actividad(periodo_session, request, request.user):
                        context = {
                            'type': 'success',
                            'title': 'Calendario!',
                            'description': 'Se registro la actividad correctamente',
                            'existe_error': 0
                        }
                        return render(request, 'partials/_alert_resultado.html', context)
                    else:
                        context = {
                            'type': 'warning',
                            'title': 'Calendario!',
                            'description': 'Error al registrar la actividad ' + calendario_controller.error_operation,
                            'existe_error': 1
                        }
                        return render(request, 'partials/_alert_resultado.html', context)

            except Exception as ex:
                context = {
                    'type': 'warning',
                    'title': 'Calendario!',
                    'description': 'Error al registrar la actividad ' + str(ex),
                    'existe_error': 1
                }
                return render(request, 'partials/_alert_resultado.html', context)

        # if operation == 'save_data':
        #     try:
        #         periodo_session = request.session[lectura_controller.modulo_session]['search_periodo']
        #         if lectura_controller.save_data(periodo_session, request, request.user):
        #             messages.add_message(request, messages.SUCCESS, {'type': 'success', 'title': 'Lecturas!', 'description': 'Se registraron los datos correctamente'})
        #         else:
        #             messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Lecturas!',
        #                                                              'description': 'Error al registrar los datos, ' + lectura_controller.error_operation})
        #     except Exception as ex:
        #         messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Lecturas!', 'description': 'Error al registrar los datos, ' + str(ex)})

    # verificamos mensajes
    if 'nuevo_mensaje' in request.session.keys():
        messages.add_message(request, messages.SUCCESS, request.session['nuevo_mensaje'])
        del request.session['nuevo_mensaje']
        request.session.modified = True

    # datos por defecto
    calendario_lista = calendario_controller.index(request)
    # semana1 = calendario_lista[1]
    # print('semana1: ', semana1[0]['lista_actividades'][0]['actividad_codigo'])

    calendario_session = request.session[calendario_controller.modulo_session]
    periodo_actual = calendario_session['search_periodo']
    periodo_next = next_periodo(periodo_actual)
    periodo_ant = previous_periodo(periodo_actual)

    status_activo = calendario_controller.status_activo
    activo = calendario_controller.activo
    inactivo = calendario_controller.inactivo

    lista_actividades = lista_controller.get_lista_actividades(request.user, settings.MOD_CALENDARIO)
    lista_horas = lista_controller.get_horas()
    lista_minutos = lista_controller.get_minutos()

    user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=request.user)
    perfil_departamento = settings.PERFIL_DEPARTAMENTO

    departamento = {'departamento_id': -1}
    if user_perfil.perfil_id.perfil_id == perfil_departamento:
        departamento = apps.get_model('departamentos', 'Departamentos').objects.get(departamento=user_perfil.user_id.username)

    context = {
        'permisos': permisos,
        'url_main': '',
        'js_file': calendario_controller.modulo_session,
        'autenticado': 'si',

        'activo': activo,
        'inactivo': inactivo,

        'lista_actividades': lista_actividades,
        'lista_horas': lista_horas,
        'lista_minutos': lista_minutos,
        'user_perfil': user_perfil,
        'perfil_departamento': perfil_departamento,
        'departamento': departamento,

        'periodo_actual': periodo_actual,
        'periodo_next': periodo_next,
        'periodo_ant': periodo_ant,

        'columnas': calendario_controller.columnas,
        'calendario': calendario_lista,
        'session': calendario_session,

        'module_x': settings.MOD_CALENDARIO,
        'module_x2': '',
        'module_x3': '',

        'operation_x': '',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }
    return render(request, 'calendario/calendario.html', context)
