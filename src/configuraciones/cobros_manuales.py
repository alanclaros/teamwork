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
from controllers.configuraciones.CobrosManualesController import CobrosManualesController
from controllers.ListasController import ListasController
from configuraciones.models import CobrosManuales

# controlador del modulo
cobro_manual_controller = CobrosManualesController()
lista_controller = ListasController()

# cobros manuales
# cobros manuales


@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_COBROS_MANUALES, 'lista'), 'without_permission')
def cobros_manuales_index(request):
    permisos = get_permissions_user(request.user, settings.MOD_COBROS_MANUALES)

    # operaciones
    if 'operation_x' in request.POST.keys():
        operation = request.POST['operation_x']
        if not operation in ['', 'add', 'modify', 'delete']:
            return render(request, 'pages/without_permission.html', {})

        if operation == 'add':
            respuesta = cobros_manuales_add(request)
            if not type(respuesta) == bool:
                return respuesta

        if operation == 'modify':
            respuesta = cobros_manuales_modify(request, request.POST['id'])
            if not type(respuesta) == bool:
                return respuesta

        if operation == 'delete':
            respuesta = cobros_manuales_delete(request, request.POST['id'])
            if not type(respuesta) == bool:
                return respuesta

    # verificamos mensajes
    if 'nuevo_mensaje' in request.session.keys():
        messages.add_message(request, messages.SUCCESS, request.session['nuevo_mensaje'])
        del request.session['nuevo_mensaje']
        request.session.modified = True

    # datos por defecto
    cobros_manuales_lista = cobro_manual_controller.index(request)
    #print('cobros_manuales_lista: ', cobros_manuales_lista)
    cobros_manuales_session = request.session[cobro_manual_controller.modulo_session]

    context = {
        'cobros_manuales': cobros_manuales_lista,
        'session': cobros_manuales_session,
        'permisos': permisos,
        'url_main': '',
        'js_file': cobro_manual_controller.modulo_session,
        'autenticado': 'si',

        'columnas': cobro_manual_controller.columnas,

        'module_x': settings.MOD_COBROS_MANUALES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': '',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/cobros_manuales.html', context)


# cobros_manuales add
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_COBROS_MANUALES, 'adicionar'), 'without_permission')
def cobros_manuales_add(request):

    # guardamos
    existe_error = False
    if 'add_x' in request.POST.keys():
        if cobro_manual_controller.save(request, type='add'):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Cobros Manuales!', 'description': 'Se agrego el nuevo cobro manual: '+request.POST['cobro_manual']}
            request.session.modified = True
            return True
        else:
            # error al adicionar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Cobros Manuales!', 'description': cobro_manual_controller.error_operation})

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(CobrosManuales, '', request, None, 'cobro_manual', 'codigo', 'monto_bs', 'porcentaje')
    else:
        db_tags = get_html_column(CobrosManuales, '', None, None, 'cobro_manual', 'codigo', 'monto_bs', 'porcentaje')

    # lista cobros mensuales
    cobros_mensuales = lista_controller.get_lista_cobros_mensuales(request.user, settings.MOD_COBROS_MANUALES)

    context = {
        'url_main': '',
        'db_tags': db_tags,
        'control_form': cobro_manual_controller.control_form,
        'js_file': cobro_manual_controller.modulo_session,
        'autenticado': 'si',
        'cobros_mensuales': cobros_mensuales,

        'module_x': settings.MOD_COBROS_MANUALES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'add',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/cobros_manuales_form.html', context)


# cobros manuales modify
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_COBROS_MANUALES, 'modificar'), 'without_permission')
def cobros_manuales_modify(request, cobro_manual_id):
    # url modulo
    cobro_manual_check = CobrosManuales.objects.filter(pk=cobro_manual_id)
    if not cobro_manual_check:
        return render(request, 'pages/without_permission.html', {})

    cobro_manual = CobrosManuales.objects.get(pk=cobro_manual_id)

    if cobro_manual.status_id not in [cobro_manual_controller.status_activo, cobro_manual_controller.status_inactivo]:
        return render(request, 'pages/without_permission.html', {})

    # guardamos
    existe_error = False
    if 'modify_x' in request.POST.keys():
        if cobro_manual_controller.save(request, type='modify'):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Cobros Manuales!', 'description': 'Se modifico el cobro manual: '+request.POST['cobro_manual']}
            request.session.modified = True
            return True
        else:
            # error al adicionar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Cobros Manuales!', 'description': cobro_manual_controller.error_operation})

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(CobrosManuales, '', request, cobro_manual, 'cobro_manual', 'codigo', 'monto_bs', 'porcentaje')
    else:
        db_tags = get_html_column(CobrosManuales, '', None, cobro_manual, 'cobro_manual', 'codigo', 'monto_bs', 'porcentaje')

    # lista cobros mensuales
    cobros_mensuales = lista_controller.get_lista_cobros_mensuales(request.user, settings.MOD_COBROS_MANUALES)

    context = {
        'url_main': '',
        'cobro_manual': cobro_manual,
        'db_tags': db_tags,
        'control_form': cobro_manual_controller.control_form,
        'js_file': cobro_manual_controller.modulo_session,
        'status_active': cobro_manual_controller.activo,
        'autenticado': 'si',
        'cobros_mensuales': cobros_mensuales,

        'module_x': settings.MOD_COBROS_MANUALES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'modify',
        'operation_x2': '',
        'operation_x3': '',

        'id': cobro_manual_id,
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/cobros_manuales_form.html', context)


# cobros manuales delete
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_COBROS_MANUALES, 'eliminar'), 'without_permission')
def cobros_manuales_delete(request, cobro_manual_id):
    # url modulo
    cobro_manual_check = CobrosManuales.objects.filter(pk=cobro_manual_id)
    if not cobro_manual_check:
        return render(request, 'pages/without_permission.html', {})

    cobro_manual = CobrosManuales.objects.get(pk=cobro_manual_id)

    if cobro_manual.status_id not in [cobro_manual_controller.status_activo, cobro_manual_controller.status_inactivo]:
        return render(request, 'pages/without_permission.html', {})

    # confirma eliminacion
    existe_error = False
    if 'delete_x' in request.POST.keys():
        if cobro_manual_controller.can_delete('cobro_manual_id', cobro_manual_id, **cobro_manual_controller.modelos_eliminar) and cobro_manual_controller.delete(cobro_manual_id):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Cobros Manuales!', 'description': 'Se elimino el cobro manual: '+request.POST['cobro_manual']}
            request.session.modified = True
            return True
        else:
            # error al modificar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Cobros Manuales!', 'description': cobro_manual_controller.error_operation})

    if cobro_manual_controller.can_delete('cobro_manual_id', cobro_manual_id, **cobro_manual_controller.modelos_eliminar):
        puede_eliminar = 1
    else:
        messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Cobros Manuales!', 'description': 'No puede eliminar este cobro manual, ' + cobro_manual_controller.error_operation})
        puede_eliminar = 0

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(CobrosManuales, '', request, cobro_manual, 'cobro_manual', 'codigo', 'monto_bs', 'porcentaje')
    else:
        db_tags = get_html_column(CobrosManuales, '', None, cobro_manual, 'cobro_manual', 'codigo', 'monto_bs', 'porcentaje')

    # lista cobros mensuales
    cobros_mensuales = lista_controller.get_lista_cobros_mensuales(request.user, settings.MOD_COBROS_MANUALES)

    context = {
        'url_main': '',
        'cobro_manual': cobro_manual,
        'db_tags': db_tags,
        'control_form': cobro_manual_controller.control_form,
        'js_file': cobro_manual_controller.modulo_session,
        'puede_eliminar': puede_eliminar,
        'error_eliminar': cobro_manual_controller.error_operation,
        'status_active': cobro_manual_controller.activo,
        'autenticado': 'si',
        'cobros_mensuales': cobros_mensuales,

        'module_x': settings.MOD_COBROS_MANUALES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'delete',
        'operation_x2': '',
        'operation_x3': '',

        'id': cobro_manual_id,
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/cobros_manuales_form.html', context)
