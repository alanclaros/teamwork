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
from controllers.configuraciones.SucursalesController import SucursalesController
from controllers.ListasController import ListasController

# modelo
from configuraciones.models import Sucursales

# controlador del modulo
sucursal_controller = SucursalesController()


# sucursales
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_SUCURSALES, 'lista'), 'without_permission')
def sucursales_index(request):
    permisos = get_permissions_user(request.user, settings.MOD_SUCURSALES)

    # operaciones
    if 'operation_x' in request.POST.keys():
        operation = request.POST['operation_x']
        if not operation in ['', 'add', 'modify', 'delete']:
            return render(request, 'pages/without_permission.html', {})

        if operation == 'add':
            respuesta = sucursales_add(request)
            if not type(respuesta) == bool:
                return respuesta

        if operation == 'modify':
            respuesta = sucursales_modify(request, request.POST['id'])
            if not type(respuesta) == bool:
                return respuesta

        if operation == 'delete':
            respuesta = sucursales_delete(request, request.POST['id'])
            if not type(respuesta) == bool:
                return respuesta

    # verificamos mensajes
    if 'nuevo_mensaje' in request.session.keys():
        messages.add_message(request, messages.SUCCESS, request.session['nuevo_mensaje'])
        del request.session['nuevo_mensaje']
        request.session.modified = True

    # datos por defecto

    sucursales_lista = sucursal_controller.index(request)
    sucursales_session = request.session[sucursal_controller.modulo_session]

    context = {
        'sucursales': sucursales_lista,
        'session': sucursales_session,
        'permisos': permisos,
        'url_main': '',
        'js_file': sucursal_controller.modulo_session,
        'autenticado': 'si',

        'columnas': sucursal_controller.columnas,

        'module_x': settings.MOD_SUCURSALES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': '',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/sucursales.html', context)


# sucursales add
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_SUCURSALES, 'adicionar'), 'without_permission')
def sucursales_add(request):
    # url modulo
    lista_controller = ListasController()

    # guardamos
    existe_error = False
    if 'add_x' in request.POST.keys():
        if sucursal_controller.save(request, type='add'):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Sucursales!', 'description': 'Se agrego la nueva sucursal: '+request.POST['sucursal']}
            request.session.modified = True
            return True
        else:
            # error al adicionar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Sucursales!', 'description': sucursal_controller.error_operation})

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(Sucursales, '', request, None, 'sucursal', 'codigo', 'email', 'empresa', 'direccion', 'ciudad', 'telefonos', 'actividad')
    else:
        db_tags = get_html_column(Sucursales, '', None, None, 'sucursal', 'codigo', 'email', 'empresa', 'direccion', 'ciudad', 'telefonos', 'actividad')

    # lista de ciudades
    ciudades_lista = lista_controller.get_lista_ciudades(request.user, settings.MOD_SUCURSALES)

    context = {
        'url_main': '',
        'db_tags': db_tags,
        'control_form': sucursal_controller.control_form,
        'js_file': sucursal_controller.modulo_session,
        'ciudades': ciudades_lista,
        'autenticado': 'si',

        'module_x': settings.MOD_SUCURSALES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'add',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/sucursales_form.html', context)


# sucursales modify
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_SUCURSALES, 'modificar'), 'without_permission')
def sucursales_modify(request, sucursal_id):
    # url modulo
    sucursal_check = apps.get_model('configuraciones', 'Sucursales').objects.filter(pk=sucursal_id)
    if not sucursal_check:
        return render(request, 'pages/without_permission.html', {})

    sucursal = apps.get_model('configuraciones', 'Sucursales').objects.get(pk=sucursal_id)
    lista_controller = ListasController()

    if sucursal.status_id not in [sucursal_controller.status_activo, sucursal_controller.status_inactivo]:
        return render(request, 'pages/without_permission.html', {})

    # guardamos
    existe_error = False
    if 'modify_x' in request.POST.keys():
        if sucursal_controller.save(request, type='modify'):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Sucursales!', 'description': 'Se modifico la sucursal: '+request.POST['sucursal']}
            request.session.modified = True
            return True
        else:
            # error al adicionar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Sucursales!', 'description': sucursal_controller.error_operation})

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(Sucursales, '', request, sucursal, 'sucursal', 'codigo', 'email', 'empresa', 'direccion', 'ciudad', 'telefonos', 'actividad')
    else:
        db_tags = get_html_column(Sucursales, '', None, sucursal, 'sucursal', 'codigo', 'email', 'empresa', 'direccion', 'ciudad', 'telefonos', 'actividad')

    # lista de ciudades
    ciudades_lista = lista_controller.get_lista_ciudades(request.user, settings.MOD_SUCURSALES)

    context = {
        'url_main': '',
        'sucursal': sucursal,
        'db_tags': db_tags,
        'control_form': sucursal_controller.control_form,
        'js_file': sucursal_controller.modulo_session,
        'ciudades': ciudades_lista,
        'status_active': sucursal_controller.activo,
        'autenticado': 'si',

        'module_x': settings.MOD_SUCURSALES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'modify',
        'operation_x2': '',
        'operation_x3': '',

        'id': sucursal_id,
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/sucursales_form.html', context)


# sucursales delete
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_SUCURSALES, 'eliminar'), 'without_permission')
def sucursales_delete(request, sucursal_id):
    # url modulo
    sucursal_check = Sucursales.objects.filter(pk=sucursal_id)
    if not sucursal_check:
        return render(request, 'pages/without_permission.html', {})

    sucursal = Sucursales.objects.get(pk=sucursal_id)
    lista_controller = ListasController()

    if sucursal.status_id not in [sucursal_controller.status_activo, sucursal_controller.status_inactivo]:
        return render(request, 'pages/without_permission.html', {})

    # confirma eliminacion
    existe_error = False
    if 'delete_x' in request.POST.keys():
        if sucursal_controller.can_delete('sucursal_id', sucursal_id, **sucursal_controller.modelos_eliminar) and sucursal_controller.delete(sucursal_id):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Sucursales!', 'description': 'Se elimino la sucursal: '+request.POST['sucursal']}
            request.session.modified = True
            return True
        else:
            # error al modificar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Sucursales!', 'description': sucursal_controller.error_operation})

    if sucursal_controller.can_delete('sucursal_id', sucursal_id, **sucursal_controller.modelos_eliminar):
        puede_eliminar = 1
    else:
        messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Sucursales!', 'description': 'No puede eliminar esta sucursal, ' + sucursal_controller.error_operation})
        puede_eliminar = 0

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(Sucursales, '', request, sucursal, 'sucursal', 'codigo', 'email', 'empresa', 'direccion', 'telefonos', 'actividad')
    else:
        db_tags = get_html_column(Sucursales, '', None, sucursal, 'sucursal', 'codigo', 'email', 'empresa', 'direccion', 'telefonos', 'actividad')

    # lista de ciudades
    ciudades_lista = lista_controller.get_lista_ciudades(request.user, settings.MOD_SUCURSALES)

    context = {
        'url_main': '',
        'sucursal': sucursal,
        'db_tags': db_tags,
        'control_form': sucursal_controller.control_form,
        'js_file': sucursal_controller.modulo_session,
        'puede_eliminar': puede_eliminar,
        'error_eliminar': sucursal_controller.error_operation,
        'ciudades': ciudades_lista,
        'status_active': sucursal_controller.activo,
        'autenticado': 'si',

        'module_x': settings.MOD_SUCURSALES,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'delete',
        'operation_x2': '',
        'operation_x3': '',

        'id': sucursal_id,
        'id2': '',
        'id3': '',
    }
    return render(request, 'configuraciones/sucursales_form.html', context)
