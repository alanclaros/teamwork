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
from controllers.configuraciones.CobrosMensualesController import CobrosMensualesController
from controllers.ListasController import ListasController
from configuraciones.models import CobrosMensuales

# controlador del modulo
cobro_mensual_controller = CobrosMensualesController()
lista_controller = ListasController()


# cobros mensuales
# cobros mensuales
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_COBROS_MENSUALES, 'lista'), 'without_permission')
def cobros_mensuales_index(request):
    permisos = get_permissions_user(request.user, settings.MOD_COBROS_MENSUALES)

    # operaciones
    if 'operation_x' in request.POST.keys():
        operation = request.POST['operation_x']
        if not operation in ['', 'add', 'modify', 'delete']:
            return render(request, 'pages/without_permission.html', {})

        if operation == 'add':
            respuesta = cobros_mensuales_add(request)
            if not type(respuesta) == bool:
                return respuesta

        if operation == 'modify':
            respuesta = cobros_mensuales_modify(request, request.POST['id'])
            if not type(respuesta) == bool:
                return respuesta

        if operation == 'delete':
            respuesta = cobros_mensuales_delete(request, request.POST['id'])
            if not type(respuesta) == bool:
                return respuesta

    # verificamos mensajes
    if 'nuevo_mensaje' in request.session.keys():
        messages.add_message(request, messages.SUCCESS, request.session['nuevo_mensaje'])
        del request.session['nuevo_mensaje']
        request.session.modified = True

    # datos por defecto
    cobros_mensuales_lista = cobro_mensual_controller.index(request)
    #print('cobros_mensuales_lista: ', cobros_mensuales_lista)
    cobros_mensuales_session = request.session[cobro_mensual_controller.modulo_session]

    context = {
        'cobros_mensuales': cobros_mensuales_lista,
        'session': cobros_mensuales_session,
        'permisos': permisos,
        'url_main': '',
        'js_file': cobro_mensual_controller.modulo_session,
        'autenticado': 'si',

        'columnas': cobro_mensual_controller.columnas,

        'module_x': settings.MOD_COBROS_MENSUALES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': '',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/cobros_mensuales.html', context)


# cobros_mensuales add
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_COBROS_MENSUALES, 'adicionar'), 'without_permission')
def cobros_mensuales_add(request):

    # guardamos
    existe_error = False
    if 'add_x' in request.POST.keys():
        if cobro_mensual_controller.save(request, type='add'):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Cobros Mensuales!', 'description': 'Se agrego el nuevo cobro mensual: '+request.POST['cobro_mensual']}
            request.session.modified = True
            return True
        else:
            # error al adicionar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Cobros Mensuales!', 'description': cobro_mensual_controller.error_operation})

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(CobrosMensuales, '', request, None, 'cobro_mensual', 'codigo', 'monto_bs', 'monto_cobrar')
    else:
        db_tags = get_html_column(CobrosMensuales, '', None, None, 'cobro_mensual', 'codigo', 'monto_bs', 'monto_cobrar')

    # cantidad de departamentos
    numero_departamentos = lista_controller.get_cantidad_departamentos(request.user, settings.MOD_COBROS_MENSUALES)

    context = {
        'url_main': '',
        'db_tags': db_tags,
        'control_form': cobro_mensual_controller.control_form,
        'js_file': cobro_mensual_controller.modulo_session,
        'autenticado': 'si',

        'numero_departamentos': numero_departamentos,

        'module_x': settings.MOD_COBROS_MENSUALES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'add',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/cobros_mensuales_form.html', context)


# cobros mensuales modify
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_COBROS_MENSUALES, 'modificar'), 'without_permission')
def cobros_mensuales_modify(request, cobro_mensual_id):
    # url modulo
    cobro_mensual_check = CobrosMensuales.objects.filter(pk=cobro_mensual_id)
    if not cobro_mensual_check:
        return render(request, 'pages/without_permission.html', {})

    cobro_mensual = CobrosMensuales.objects.get(pk=cobro_mensual_id)

    if cobro_mensual.status_id not in [cobro_mensual_controller.status_activo, cobro_mensual_controller.status_inactivo]:
        return render(request, 'pages/without_permission.html', {})

    # guardamos
    existe_error = False
    if 'modify_x' in request.POST.keys():
        if cobro_mensual_controller.save(request, type='modify'):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Cobros Mensuales!', 'description': 'Se modifico el cobro mensual: '+request.POST['cobro_mensual']}
            request.session.modified = True
            return True
        else:
            # error al adicionar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Cobros Mensuales!', 'description': cobro_mensual_controller.error_operation})

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(CobrosMensuales, '', request, cobro_mensual, 'cobro_mensual', 'codigo', 'monto_bs', 'monto_cobrar')
    else:
        db_tags = get_html_column(CobrosMensuales, '', None, cobro_mensual, 'cobro_mensual', 'codigo', 'monto_bs', 'monto_cobrar')

    # cantidad de departamentos
    numero_departamentos = lista_controller.get_cantidad_departamentos(request.user, settings.MOD_COBROS_MENSUALES)
    if numero_departamentos > 0:
        monto_dividido = round(cobro_mensual.monto_bs/numero_departamentos, 2)
    else:
        monto_dividido = 0

    context = {
        'url_main': '',
        'cobro_mensual': cobro_mensual,
        'db_tags': db_tags,
        'numero_departamentos': numero_departamentos,
        'monto_dividido': monto_dividido,
        'control_form': cobro_mensual_controller.control_form,
        'js_file': cobro_mensual_controller.modulo_session,
        'status_active': cobro_mensual_controller.activo,
        'autenticado': 'si',

        'module_x': settings.MOD_COBROS_MENSUALES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'modify',
        'operation_x2': '',
        'operation_x3': '',

        'id': cobro_mensual_id,
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/cobros_mensuales_form.html', context)


# cobros mensuales delete
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_COBROS_MENSUALES, 'eliminar'), 'without_permission')
def cobros_mensuales_delete(request, cobro_mensual_id):
    # url modulo
    cobro_mensual_check = CobrosMensuales.objects.filter(pk=cobro_mensual_id)
    if not cobro_mensual_check:
        return render(request, 'pages/without_permission.html', {})

    cobro_mensual = CobrosMensuales.objects.get(pk=cobro_mensual_id)

    if cobro_mensual.status_id not in [cobro_mensual_controller.status_activo, cobro_mensual_controller.status_inactivo]:
        return render(request, 'pages/without_permission.html', {})

    # confirma eliminacion
    existe_error = False
    if 'delete_x' in request.POST.keys():
        if cobro_mensual_controller.can_delete('cobro_mensual_id', cobro_mensual_id, **cobro_mensual_controller.modelos_eliminar) and cobro_mensual_controller.delete(cobro_mensual_id):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Cobros Mensuales!', 'description': 'Se elimino el cobro mensual: '+request.POST['cobro_mensual']}
            request.session.modified = True
            return True
        else:
            # error al modificar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Cobros Mensuales!', 'description': cobro_mensual_controller.error_operation})

    if cobro_mensual_controller.can_delete('cobro_mensual_id', cobro_mensual_id, **cobro_mensual_controller.modelos_eliminar):
        puede_eliminar = 1
    else:
        messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Cobros Mensuales!', 'description': 'No puede eliminar este cobro_mensual, ' + cobro_mensual_controller.error_operation})
        puede_eliminar = 0

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(CobrosMensuales, '', request, cobro_mensual, 'cobro_mensual', 'codigo', 'monto_bs', 'monto_cobrar')
    else:
        db_tags = get_html_column(CobrosMensuales, '', None, cobro_mensual, 'cobro_mensual', 'codigo', 'monto_bs', 'monto_cobrar')

    context = {
        'url_main': '',
        'cobro_mensual': cobro_mensual,
        'db_tags': db_tags,
        'control_form': cobro_mensual_controller.control_form,
        'js_file': cobro_mensual_controller.modulo_session,
        'puede_eliminar': puede_eliminar,
        'error_eliminar': cobro_mensual_controller.error_operation,
        'status_active': cobro_mensual_controller.activo,
        'autenticado': 'si',

        'module_x': settings.MOD_COBROS_MENSUALES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'delete',
        'operation_x2': '',
        'operation_x3': '',

        'id': cobro_mensual_id,
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/cobros_mensuales_form.html', context)
