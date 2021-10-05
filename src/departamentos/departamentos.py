import os
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
# settings de la app
from django.conf import settings
from django.http import HttpResponseRedirect
from django.apps import apps

# propios
from departamentos.models import Departamentos

# para los usuarios
from utils.permissions import get_user_permission_operation, get_permissions_user, get_html_column

# controlador
from controllers.departamentos.DepartamentosController import DepartamentosController
from controllers.ListasController import ListasController


departamento_controller = DepartamentosController()
lista_controller = ListasController()


@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_DEPARTAMENTOS, 'lista'), 'without_permission')
def departamentos_index(request):
    permisos = get_permissions_user(request.user, settings.MOD_DEPARTAMENTOS)

    # operaciones
    if 'operation_x' in request.POST.keys():
        operation = request.POST['operation_x']
        if not operation in ['', 'add', 'modify', 'delete']:
            return render(request, 'pages/without_permission.html', {})

        if operation == 'add':
            respuesta = departamentos_add(request)
            if not type(respuesta) == bool:
                return respuesta

        if operation == 'modify':
            respuesta = departamentos_modify(request, request.POST['id'])
            if not type(respuesta) == bool:
                return respuesta

        if operation == 'delete':
            respuesta = departamentos_delete(request, request.POST['id'])
            if not type(respuesta) == bool:
                return respuesta

    # verificamos mensajes
    if 'nuevo_mensaje' in request.session.keys():
        messages.add_message(request, messages.SUCCESS, request.session['nuevo_mensaje'])
        del request.session['nuevo_mensaje']
        request.session.modified = True

    # datos por defecto
    departamentos_lista = departamento_controller.index(request)
    # print(Ciudades)
    departamentos_session = request.session[departamento_controller.modulo_session]
    # print(zonas_session)
    context = {
        'departamentos': departamentos_lista,
        'session': departamentos_session,
        'permisos': permisos,
        'url_main': '',
        'js_file': departamento_controller.modulo_session,
        'autenticado': 'si',

        'columnas': departamento_controller.columnas,

        'module_x': settings.MOD_DEPARTAMENTOS,
        'module_x2': '',
        'module_x3': '',

        'operation_x': '',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }
    return render(request, 'departamentos/departamentos.html', context)


# departamentos add
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_DEPARTAMENTOS, 'adicionar'), 'without_permission')
def departamentos_add(request):

    # guardamos
    existe_error = False
    if 'add_x' in request.POST.keys():
        if departamento_controller.save(request, type='add'):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Departamentos!', 'description': 'Se agrego el nuevo departamento: '+request.POST['departamento']}
            request.session.modified = True
            return True
        else:
            # error al adicionar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Departamentos!', 'description': departamento_controller.error_operation})

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(Departamentos, 'propietario_email,copropietario_apellidos,copropietario_nombres,copropietario_email,copropietario_fonos,copropietario_ci_nit', request, None, 'propietario_apellidos', 'propietario_nombres',
                                  'propietario_ci_nit', 'propietario_email', 'propietario_fonos', 'copropietario_apellidos', 'copropietario_nombres', 'copropietario_ci_nit', 'copropietario_email', 'copropietario_fonos', 'departamento', 'codigo', 'metros2')
    else:
        db_tags = get_html_column(Departamentos, 'propietario_email,copropietario_apellidos,copropietario_nombres,copropietario_email,copropietario_fonos,copropietario_ci_nit', None, None, 'propietario_apellidos', 'propietario_nombres',
                                  'propietario_ci_nit', 'propietario_email', 'propietario_fonos', 'copropietario_apellidos', 'copropietario_nombres', 'copropietario_ci_nit', 'copropietario_email', 'copropietario_fonos', 'departamento', 'codigo', 'metros2')

    bloques_lista = lista_controller.get_lista_bloques(request.user, settings.MOD_BLOQUES)
    pisos_lista = lista_controller.get_lista_pisos(request.user, settings.MOD_PISOS)

    context = {
        'url_main': '',
        'operation_x': 'add',
        'db_tags': db_tags,
        'control_form': departamento_controller.control_form,
        'js_file': departamento_controller.modulo_session,
        'autenticado': 'si',
        'bloques': bloques_lista,
        'pisos': pisos_lista,
        'columnas': departamento_controller.columnas,

        'module_x': settings.MOD_DEPARTAMENTOS,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'add',
        'operation_x2': '',
        'operation_x3': '',

        'id': '',
        'id2': '',
        'id3': '',
    }
    return render(request, 'departamentos/departamentos_form.html', context)


# departamentos modify
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_DEPARTAMENTOS, 'modificar'), 'without_permission')
def departamentos_modify(request, departamento_id):
    departamento_check = apps.get_model('departamentos', 'Departamentos').objects.filter(pk=departamento_id)
    if not departamento_check:
        return render(request, 'pages/without_permission.html', {})

    departamento = Departamentos.objects.get(pk=departamento_id)

    if departamento.status_id not in [departamento_controller.status_activo, departamento_controller.status_inactivo]:
        return render(request, 'pages/without_permission.html', {})

    # guardamos
    existe_error = False
    if 'modify_x' in request.POST.keys():
        if departamento_controller.save(request, type='modify'):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Departamentos!', 'description': 'Se modifico el departamento: '+request.POST['departamento']}
            request.session.modified = True
            return True
        else:
            # error al adicionar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Departamentos!', 'description': departamento_controller.error_operation})

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(Departamentos, 'propietario_email,copropietario_apellidos,copropietario_nombres,copropietario_email,copropietario_fonos,copropietario_ci_nit', request, departamento, 'propietario_apellidos', 'propietario_nombres',
                                  'propietario_ci_nit', 'propietario_email', 'propietario_fonos', 'copropietario_apellidos', 'copropietario_nombres', 'copropietario_ci_nit', 'copropietario_email', 'copropietario_fonos', 'departamento', 'codigo', 'metros2')
    else:
        db_tags = get_html_column(Departamentos, 'propietario_email,copropietario_apellidos,copropietario_nombres,copropietario_email,copropietario_fonos,copropietario_ci_nit', None, departamento, 'propietario_apellidos', 'propietario_nombres',
                                  'propietario_ci_nit', 'propietario_email', 'propietario_fonos', 'copropietario_apellidos', 'copropietario_nombres', 'copropietario_ci_nit', 'copropietario_email', 'copropietario_fonos', 'departamento', 'codigo', 'metros2')

    bloques_lista = lista_controller.get_lista_bloques(request.user, settings.MOD_BLOQUES)
    pisos_lista = lista_controller.get_lista_pisos(request.user, settings.MOD_PISOS)

    context = {
        'url_main': '',
        'operation_x': 'modify',
        'departamento': departamento,
        'status_active': departamento_controller.activo,
        'db_tags': db_tags,
        'control_form': departamento_controller.control_form,
        'js_file': departamento_controller.modulo_session,
        'autenticado': 'si',
        'bloques': bloques_lista,
        'pisos': pisos_lista,

        'module_x': settings.MOD_DEPARTAMENTOS,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'modify',
        'operation_x2': '',
        'operation_x3': '',

        'id': departamento_id,
        'id2': '',
        'id3': '',
    }
    return render(request, 'departamentos/departamentos_form.html', context)


# departamentos delete
@user_passes_test(lambda user: get_user_permission_operation(user, settings.MOD_DEPARTAMENTOS, 'eliminar'), 'without_permission')
def departamentos_delete(request, departamento_id):
    departamento_check = apps.get_model('departamentos', 'Departamentos').objects.filter(pk=departamento_id)
    if not departamento_check:
        return render(request, 'pages/without_permission.html', {})

    departamento = get_object_or_404(Departamentos, pk=departamento_id)

    # confirma eliminacion
    existe_error = False
    if 'delete_x' in request.POST.keys():
        if departamento_controller.can_delete('departamento_id', departamento_id, **departamento_controller.modelos_eliminar) and departamento_controller.delete(departamento_id):
            request.session['nuevo_mensaje'] = {'type': 'success', 'title': 'Departamentos!', 'description': 'Se elimino el departamento: '+request.POST['departamento']}
            request.session.modified = True
            return True
        else:
            # error al modificar
            existe_error = True
            messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Departamentos!', 'description': departamento_controller.error_operation})

    if departamento_controller.can_delete('departamento_id', departamento_id, **departamento_controller.modelos_eliminar):
        puede_eliminar = 1
    else:
        messages.add_message(request, messages.SUCCESS, {'type': 'warning', 'title': 'Departamentos!', 'description': 'No puede eliminar este ciente, ' + departamento_controller.error_operation})
        puede_eliminar = 0

    # restricciones de columna
    if existe_error:
        db_tags = get_html_column(Departamentos, 'propietario_email,copropietario_apellidos,copropietario_nombres,copropietario_email,copropietario_fonos,copropietario_ci_nit', request, departamento, 'propietario_apellidos', 'propietario_nombres',
                                  'propietario_ci_nit', 'propietario_email', 'propietario_fonos', 'copropietario_apellidos', 'copropietario_nombres', 'copropietario_ci_nit', 'copropietario_email', 'copropietario_fonos', 'departamento', 'codigo', 'metros2')
    else:
        db_tags = get_html_column(Departamentos, 'propietario_email,copropietario_apellidos,copropietario_nombres,copropietario_email,copropietario_fonos,copropietario_ci_nit', None, departamento, 'propietario_apellidos', 'propietario_nombres',
                                  'propietario_ci_nit', 'propietario_email', 'propietario_fonos', 'copropietario_apellidos', 'copropietario_nombres', 'copropietario_ci_nit', 'copropietario_email', 'copropietario_fonos', 'departamento', 'codigo', 'metros2')

    bloques_lista = lista_controller.get_lista_bloques(request.user, settings.MOD_BLOQUES)
    pisos_lista = lista_controller.get_lista_pisos(request.user, settings.MOD_PISOS)

    context = {
        'url_main': '',
        'operation_x': 'delete',
        'departamento': departamento,
        'db_tags': db_tags,
        'control_form': departamento_controller.control_form,
        'js_file': departamento_controller.modulo_session,
        'puede_eliminar': puede_eliminar,
        'error_eliminar': departamento_controller.error_operation,
        'autenticado': 'si',
        'status_active': departamento_controller.activo,
        'bloques': bloques_lista,
        'pisos': pisos_lista,

        'module_x': settings.MOD_DEPARTAMENTOS,
        'module_x2': '',
        'module_x3': '',

        'operation_x': 'delete',
        'operation_x2': '',
        'operation_x3': '',

        'id': departamento_id,
        'id2': '',
        'id3': '',
    }
    return render(request, 'departamentos/departamentos_form.html', context)
