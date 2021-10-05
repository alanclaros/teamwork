#from configuraciones.views import usuarios_modify
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from django.apps import apps
from django.conf import settings
from django.contrib import messages

# utils
from utils.permissions import get_user_permission_operation, get_permissions_user, get_html_column

# clases
from controllers.configuraciones.ActividadesController import ActividadesController
from calendario.models import Actividades

# controlador del modulo
actividad_controller = ActividadesController()


# actividades
# actividades
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_ACTIVIDADES, 'lista'), 'without_permission')
def actividades_index(request):
    permisos = get_permissions_user(request.user, settings.MOD_ACTIVIDADES)

    # operaciones
    if 'operation_x' in request.POST.keys():
        operation = request.POST['operation_x']
        if not operation in ['', 'add', 'modify', 'delete']:
            return render(request, 'pages/without_permission.html', {})

        if operation == 'add':
            respuesta = actividades_add(request)
            if not type(respuesta) == bool:
                return respuesta

        if operation == 'modify':
            respuesta = actividades_modify(request, request.POST['id'])
            if not type(respuesta) == bool:
                return respuesta

        if operation == 'delete':
            respuesta = actividades_delete(request, request.POST['id'])
            if not type(respuesta) == bool:
                return respuesta

    # verificamos mensajes
    if 'nuevo_mensaje' in request.session.keys():
        messages.add_message(request, messages.SUCCESS, request.session['nuevo_mensaje'])
        del request.session['nuevo_mensaje']
        request.session.modified = True

    # datos por defecto
    actividades_lista = actividad_controller.index(request)
    #print('actividades_lista: ', actividades_lista)
    actividades_session = request.session[actividad_controller.modulo_session]

    context = {
        'actividades': actividades_lista,
        'session': actividades_session,
        'permisos': permisos,
        'url_main': '',
        'js_file': actividad_controller.modulo_session,
        'autenticado': 'si',

        'columnas': actividad_controller.columnas,

        'module_x': settings.MOD_ACTIVIDADES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': '',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/actividades.html', context)


# actividades add
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_ACTIVIDADES, 'adicionar'), 'without_permission')
def actividades_add(request):

    # guardamos
    existe_error = False
    if 'add_x' in request.POST.keys():
        if actividad_controller.save(request, type='add'):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Actividades!', 'description': 'Se agrego la nueva actividad: '+request.POST['actividad']}
            request.session.modified = True
            return True
        else:
            # error al adicionar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Actividades!', 'description': actividad_controller.error_operation})

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(Actividades, '', request, None, 'actividad', 'codigo', 'color_hex', 'color_txt')
    else:
        db_tags = get_html_column(Actividades, '', None, None, 'actividad', 'codigo', 'color_hex', 'color_txt')

    context = {
        'url_main': '',
        'db_tags': db_tags,
        'control_form': actividad_controller.control_form,
        'js_file': actividad_controller.modulo_session,
        'autenticado': 'si',

        'module_x': settings.MOD_ACTIVIDADES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'add',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/actividades_form.html', context)


# actividades modify
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_ACTIVIDADES, 'modificar'), 'without_permission')
def actividades_modify(request, actividad_id):
    # url modulo
    actividad_check = Actividades.objects.filter(pk=actividad_id)
    if not actividad_check:
        return render(request, 'pages/without_permission.html', {})

    actividad = Actividades.objects.get(pk=actividad_id)

    if actividad.status_id not in [actividad_controller.status_activo, actividad_controller.status_inactivo]:
        return render(request, 'pages/without_permission.html', {})

    # guardamos
    existe_error = False
    if 'modify_x' in request.POST.keys():
        if actividad_controller.save(request, type='modify'):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Actividades!', 'description': 'Se modifico la actividad: '+request.POST['actividad']}
            request.session.modified = True
            return True
        else:
            # error al adicionar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Actividades!', 'description': actividad_controller.error_operation})

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(Actividades, '', request, actividad, 'actividad', 'codigo', 'color_hex', 'color_txt')
    else:
        db_tags = get_html_column(Actividades, '', None, actividad, 'actividad', 'codigo', 'color_hex', 'color_txt')

    context = {
        'url_main': '',
        'actividad': actividad,
        'db_tags': db_tags,
        'control_form': actividad_controller.control_form,
        'js_file': actividad_controller.modulo_session,
        'status_active': actividad_controller.activo,
        'autenticado': 'si',

        'module_x': settings.MOD_ACTIVIDADES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'modify',
        'operation_x2': '',
        'operation_x3': '',

        'id': actividad_id,
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/actividades_form.html', context)


# actividades delete
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_ACTIVIDADES, 'eliminar'), 'without_permission')
def actividades_delete(request, actividad_id):
    # url modulo
    actividad_check = Actividades.objects.filter(pk=actividad_id)
    if not actividad_check:
        return render(request, 'pages/without_permission.html', {})

    actividad = Actividades.objects.get(pk=actividad_id)

    if actividad.status_id not in [actividad_controller.status_activo, actividad_controller.status_inactivo]:
        return render(request, 'pages/without_permission.html', {})

    # confirma eliminacion
    existe_error = False
    if 'delete_x' in request.POST.keys():
        if actividad_controller.can_delete('actividad_id', actividad_id, **actividad_controller.modelos_eliminar) and actividad_controller.delete(actividad_id):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Actividades!', 'description': 'Se elimino actividad: '+request.POST['actividad']}
            request.session.modified = True
            return True
        else:
            # error al modificar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Actividades!', 'description': actividad_controller.error_operation})

    if actividad_controller.can_delete('actividad_id', actividad_id, **actividad_controller.modelos_eliminar):
        puede_eliminar = 1
    else:
        messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Actividades!', 'description': 'No puede eliminar esta actividad, ' + actividad_controller.error_operation})
        puede_eliminar = 0

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(Actividades, '', request, actividad, 'actividad', 'codigo', 'color_hex', 'color_txt')
    else:
        db_tags = get_html_column(Actividades, '', None, actividad, 'actividad', 'codigo', 'color_hex', 'color_txt')

    context = {
        'url_main': '',
        'actividad': actividad,
        'db_tags': db_tags,
        'control_form': actividad_controller.control_form,
        'js_file': actividad_controller.modulo_session,
        'puede_eliminar': puede_eliminar,
        'error_eliminar': actividad_controller.error_operation,
        'status_active': actividad_controller.activo,
        'autenticado': 'si',

        'module_x': settings.MOD_ACTIVIDADES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'delete',
        'operation_x2': '',
        'operation_x3': '',

        'id': actividad_id,
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/actividades_form.html', context)
