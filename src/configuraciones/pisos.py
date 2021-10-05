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
from controllers.configuraciones.PisosController import PisosController
from departamentos.models import Pisos

# controlador del modulo
piso_controller = PisosController()


# pisos
# pisos
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_PISOS, 'lista'), 'without_permission')
def pisos_index(request):
    permisos = get_permissions_user(request.user, settings.MOD_PISOS)

    # operaciones
    if 'operation_x' in request.POST.keys():
        operation = request.POST['operation_x']
        if not operation in ['', 'add', 'modify', 'delete']:
            return render(request, 'pages/without_permission.html', {})

        if operation == 'add':
            respuesta = pisos_add(request)
            if not type(respuesta) == bool:
                return respuesta

        if operation == 'modify':
            respuesta = pisos_modify(request, request.POST['id'])
            if not type(respuesta) == bool:
                return respuesta

        if operation == 'delete':
            respuesta = pisos_delete(request, request.POST['id'])
            if not type(respuesta) == bool:
                return respuesta

    # verificamos mensajes
    if 'nuevo_mensaje' in request.session.keys():
        messages.add_message(request, messages.SUCCESS, request.session['nuevo_mensaje'])
        del request.session['nuevo_mensaje']
        request.session.modified = True

    # datos por defecto
    pisos_lista = piso_controller.index(request)
    #print('pisos_lista: ', pisos_lista)
    pisos_session = request.session[piso_controller.modulo_session]

    context = {
        'pisos': pisos_lista,
        'session': pisos_session,
        'permisos': permisos,
        'url_main': '',
        'js_file': piso_controller.modulo_session,
        'autenticado': 'si',

        'columnas': piso_controller.columnas,

        'module_x': settings.MOD_PISOS,
        'module_x2': '',
        'module_x3': '',

        'operation_x': '',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/pisos.html', context)


# pisos add
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_PISOS, 'adicionar'), 'without_permission')
def pisos_add(request):

    # guardamos
    existe_error = False
    if 'add_x' in request.POST.keys():
        if piso_controller.save(request, type='add'):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Pisos!', 'description': 'Se agrego el nuevo piso: '+request.POST['piso']}
            request.session.modified = True
            return True
        else:
            # error al adicionar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Pisos!', 'description': piso_controller.error_operation})

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(Pisos, '', request, None, 'piso', 'codigo')
    else:
        db_tags = get_html_column(Pisos, '', None, None, 'piso', 'codigo')

    context = {
        'url_main': '',
        'db_tags': db_tags,
        'control_form': piso_controller.control_form,
        'js_file': piso_controller.modulo_session,
        'autenticado': 'si',

        'module_x': settings.MOD_PISOS,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'add',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/pisos_form.html', context)


# pisos modify
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_PISOS, 'modificar'), 'without_permission')
def pisos_modify(request, piso_id):
    # url modulo
    piso_check = Pisos.objects.filter(pk=piso_id)
    if not piso_check:
        return render(request, 'pages/without_permission.html', {})

    piso = Pisos.objects.get(pk=piso_id)

    if piso.status_id not in [piso_controller.status_activo, piso_controller.status_inactivo]:
        return render(request, 'pages/without_permission.html', {})

    # guardamos
    existe_error = False
    if 'modify_x' in request.POST.keys():
        if piso_controller.save(request, type='modify'):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Pisos!', 'description': 'Se modifico el piso: '+request.POST['piso']}
            request.session.modified = True
            return True
        else:
            # error al adicionar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Pisos!', 'description': piso_controller.error_operation})

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(Pisos, '', request, piso, 'piso', 'codigo')
    else:
        db_tags = get_html_column(Pisos, '', None, piso, 'piso', 'codigo')

    context = {
        'url_main': '',
        'piso': piso,
        'db_tags': db_tags,
        'control_form': piso_controller.control_form,
        'js_file': piso_controller.modulo_session,
        'status_active': piso_controller.activo,
        'autenticado': 'si',

        'module_x': settings.MOD_PISOS,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'modify',
        'operation_x2': '',
        'operation_x3': '',

        'id': piso_id,
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/pisos_form.html', context)


# pisos delete
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_PISOS, 'eliminar'), 'without_permission')
def pisos_delete(request, piso_id):
    # url modulo
    piso_check = Pisos.objects.filter(pk=piso_id)
    if not piso_check:
        return render(request, 'pages/without_permission.html', {})

    piso = Pisos.objects.get(pk=piso_id)

    if piso.status_id not in [piso_controller.status_activo, piso_controller.status_inactivo]:
        return render(request, 'pages/without_permission.html', {})

    # confirma eliminacion
    existe_error = False
    if 'delete_x' in request.POST.keys():
        if piso_controller.can_delete('piso_id', piso_id, **piso_controller.modelos_eliminar) and piso_controller.delete(piso_id):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Pisos!', 'description': 'Se elimino el piso: '+request.POST['piso']}
            request.session.modified = True
            return True
        else:
            # error al modificar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Pisos!', 'description': piso_controller.error_operation})

    if piso_controller.can_delete('piso_id', piso_id, **piso_controller.modelos_eliminar):
        puede_eliminar = 1
    else:
        messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Pisos!', 'description': 'No puede eliminar este piso, ' + piso_controller.error_operation})
        puede_eliminar = 0

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(Pisos, '', request, piso, 'piso', 'codigo')
    else:
        db_tags = get_html_column(Pisos, '', None, piso, 'piso', 'codigo')

    context = {
        'url_main': '',
        'piso': piso,
        'db_tags': db_tags,
        'control_form': piso_controller.control_form,
        'js_file': piso_controller.modulo_session,
        'puede_eliminar': puede_eliminar,
        'error_eliminar': piso_controller.error_operation,
        'status_active': piso_controller.activo,
        'autenticado': 'si',

        'module_x': settings.MOD_PISOS,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'delete',
        'operation_x2': '',
        'operation_x3': '',

        'id': piso_id,
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/pisos_form.html', context)
