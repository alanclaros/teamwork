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
from controllers.configuraciones.BloquesController import BloquesController
from departamentos.models import Bloques

# controlador del modulo
bloque_controller = BloquesController()


# bloques
# bloques
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_BLOQUES, 'lista'), 'without_permission')
def bloques_index(request):
    permisos = get_permissions_user(request.user, settings.MOD_BLOQUES)

    # operaciones
    if 'operation_x' in request.POST.keys():
        operation = request.POST['operation_x']
        if not operation in ['', 'add', 'modify', 'delete']:
            return render(request, 'pages/without_permission.html', {})

        if operation == 'add':
            respuesta = bloques_add(request)
            if not type(respuesta) == bool:
                return respuesta

        if operation == 'modify':
            respuesta = bloques_modify(request, request.POST['id'])
            if not type(respuesta) == bool:
                return respuesta

        if operation == 'delete':
            respuesta = bloques_delete(request, request.POST['id'])
            if not type(respuesta) == bool:
                return respuesta

    # verificamos mensajes
    if 'nuevo_mensaje' in request.session.keys():
        messages.add_message(request, messages.SUCCESS, request.session['nuevo_mensaje'])
        del request.session['nuevo_mensaje']
        request.session.modified = True

    # datos por defecto
    bloques_lista = bloque_controller.index(request)
    #print('bloques_lista: ', bloques_lista)
    bloques_session = request.session[bloque_controller.modulo_session]

    context = {
        'bloques': bloques_lista,
        'session': bloques_session,
        'permisos': permisos,
        'url_main': '',
        'js_file': bloque_controller.modulo_session,
        'autenticado': 'si',

        'columnas': bloque_controller.columnas,

        'module_x': settings.MOD_BLOQUES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': '',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/bloques.html', context)


# bloques add
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_BLOQUES, 'adicionar'), 'without_permission')
def bloques_add(request):

    # guardamos
    existe_error = False
    if 'add_x' in request.POST.keys():
        if bloque_controller.save(request, type='add'):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Bloques!', 'description': 'Se agrego el nuevo bloque: '+request.POST['bloque']}
            request.session.modified = True
            return True
        else:
            # error al adicionar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Bloques!', 'description': bloque_controller.error_operation})

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(Bloques, 'ubicacion', request, None, 'bloque', 'codigo', 'ubicacion')
    else:
        db_tags = get_html_column(Bloques, 'ubicacion', None, None, 'bloque', 'codigo', 'ubicacion')

    context = {
        'url_main': '',
        'db_tags': db_tags,
        'control_form': bloque_controller.control_form,
        'js_file': bloque_controller.modulo_session,
        'autenticado': 'si',

        'module_x': settings.MOD_BLOQUES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'add',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/bloques_form.html', context)


# bloques modify
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_BLOQUES, 'modificar'), 'without_permission')
def bloques_modify(request, bloque_id):
    # url modulo
    bloque_check = Bloques.objects.filter(pk=bloque_id)
    if not bloque_check:
        return render(request, 'pages/without_permission.html', {})

    bloque = Bloques.objects.get(pk=bloque_id)

    if bloque.status_id not in [bloque_controller.status_activo, bloque_controller.status_inactivo]:
        return render(request, 'pages/without_permission.html', {})

    # guardamos
    existe_error = False
    if 'modify_x' in request.POST.keys():
        if bloque_controller.save(request, type='modify'):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Bloques!', 'description': 'Se modifico el bloque: '+request.POST['bloque']}
            request.session.modified = True
            return True
        else:
            # error al adicionar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Bloques!', 'description': bloque_controller.error_operation})

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(Bloques, 'ubicacion', request, bloque, 'bloque', 'codigo', 'ubicacion')
    else:
        db_tags = get_html_column(Bloques, 'ubicacion', None, bloque, 'bloque', 'codigo', 'ubicacion')

    context = {
        'url_main': '',
        'bloque': bloque,
        'db_tags': db_tags,
        'control_form': bloque_controller.control_form,
        'js_file': bloque_controller.modulo_session,
        'status_active': bloque_controller.activo,
        'autenticado': 'si',

        'module_x': settings.MOD_BLOQUES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'modify',
        'operation_x2': '',
        'operation_x3': '',

        'id': bloque_id,
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/bloques_form.html', context)


# bloques delete
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_BLOQUES, 'eliminar'), 'without_permission')
def bloques_delete(request, bloque_id):
    # url modulo
    bloque_check = Bloques.objects.filter(pk=bloque_id)
    if not bloque_check:
        return render(request, 'pages/without_permission.html', {})

    bloque = Bloques.objects.get(pk=bloque_id)

    if bloque.status_id not in [bloque_controller.status_activo, bloque_controller.status_inactivo]:
        return render(request, 'pages/without_permission.html', {})

    # confirma eliminacion
    existe_error = False
    if 'delete_x' in request.POST.keys():
        if bloque_controller.can_delete('bloque_id', bloque_id, **bloque_controller.modelos_eliminar) and bloque_controller.delete(bloque_id):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Bloques!', 'description': 'Se elimino bloque: '+request.POST['bloque']}
            request.session.modified = True
            return True
        else:
            # error al modificar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Bloques!', 'description': bloque_controller.error_operation})

    if bloque_controller.can_delete('bloque_id', bloque_id, **bloque_controller.modelos_eliminar):
        puede_eliminar = 1
    else:
        messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Bloques!', 'description': 'No puede eliminar este bloque, ' + bloque_controller.error_operation})
        puede_eliminar = 0

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(Bloques, 'ubicacion', request, bloque, 'bloque', 'codigo', 'ubicacion')
    else:
        db_tags = get_html_column(Bloques, 'ubicacion', None, bloque, 'bloque', 'codigo', 'ubicacion')

    context = {
        'url_main': '',
        'bloque': bloque,
        'db_tags': db_tags,
        'control_form': bloque_controller.control_form,
        'js_file': bloque_controller.modulo_session,
        'puede_eliminar': puede_eliminar,
        'error_eliminar': bloque_controller.error_operation,
        'status_active': bloque_controller.activo,
        'autenticado': 'si',

        'module_x': settings.MOD_BLOQUES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'delete',
        'operation_x2': '',
        'operation_x3': '',

        'id': bloque_id,
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/bloques_form.html', context)
