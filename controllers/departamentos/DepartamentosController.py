from controllers.DefaultValues import DefaultValues
from django.conf import settings
from django.apps import apps

from django.db import transaction
from departamentos.models import Departamentos

# password
from django.contrib.auth.hashers import make_password

from utils.validators import validate_string, validate_number_int, validate_number_decimal, validate_email


class DepartamentosController(DefaultValues):
    def __init__(self):
        DefaultValues.__init__(self)
        self.modelo_name = 'Departamentos'
        self.modelo_id = 'departamento_id'
        self.modelo_app = 'departamentos'
        self.modulo_id = settings.MOD_DEPARTAMENTOS

        # variables de session
        self.modulo_session = "departamentos"
        self.columnas.append('propietario_apellidos')
        self.columnas.append('propietario_nombres')
        self.columnas.append('departamento')

        self.variables_filtros.append('search_apellidos')
        self.variables_filtros.append('search_nombres')
        self.variables_filtros.append('search_ci_nit')
        self.variables_filtros.append('search_departamento')

        self.variables_filtros_defecto['search_apellidos'] = ''
        self.variables_filtros_defecto['search_nombres'] = ''
        self.variables_filtros_defecto['search_ci_nit'] = ''
        self.variables_filtros_defecto['search_departamento'] = ''

        self.variable_page = "page"
        self.variable_page_defecto = "1"
        self.variable_order = "search_order"
        self.variable_order_value = self.columnas[0]
        self.variable_order_type = "search_order_type"
        self.variable_order_type_value = 'ASC'

        # tablas donde se debe verificar para eliminar
        self.modelos_eliminar = {}

        # control del formulario
        self.control_form = "txt|3|S|propietario_apellidos|Apellidos Propietario"
        self.control_form += ";txt|2|S|propietario_nombres|Nombres Propietario"
        self.control_form += ";txt|2|S|propietario_fonos|Telefonos Propietario"
        self.control_form += ";cbo|0|S|bloque_id|Bloque"
        self.control_form += ";cbo|0|S|piso_id|Piso"
        self.control_form += ";txt|1|S|departamento|Departamento"
        self.control_form += ";txt|1|S|codigo|Codigo"
        self.control_form += ";txt|2|S|metros2|Metros 2"
        #self.control_form += "txt|2|S|ci_nit|"

    def index(self, request):
        DefaultValues.index(self, request)
        self.filtros_modulo.clear()
        # status
        self.filtros_modulo['status_id_id__in'] = [self.activo, self.inactivo]
        # apellidos
        if self.variables_filtros_values['search_apellidos'].strip() != "":
            self.filtros_modulo['propietario_apellidos__icontains'] = self.variables_filtros_values['search_apellidos'].strip()
        # nombres
        if self.variables_filtros_values['search_nombres'].strip() != "":
            self.filtros_modulo['propietario_nombres__icontains'] = self.variables_filtros_values['search_nombres'].strip()
        # ci_nit
        if self.variables_filtros_values['search_ci_nit'].strip() != "":
            self.filtros_modulo['propietario_ci_nit__icontains'] = self.variables_filtros_values['search_ci_nit'].strip()
        # departamento
        if self.variables_filtros_values['search_departamento'].strip() != "":
            self.filtros_modulo['departamento__icontains'] = self.variables_filtros_values['search_departamento'].strip()

        # paginacion, paginas y definiendo el LIMIT *,*
        self.pagination()
        # asigamos la paginacion a la session
        request.session[self.modulo_session]['pages_list'] = self.pages_list

        # recuperamos los datos
        return self.get_list()

    def is_in_db(self, id, nuevo_valor):
        """verificamos si existe en la base de datos"""
        if nuevo_valor == '':
            # dejamos guardar sin nit
            return False

        modelo = apps.get_model(self.modelo_app, self.modelo_name)
        filtros = {}
        filtros['status_id_id__in'] = [self.activo, self.inactivo]
        filtros['departamento__iexact'] = nuevo_valor

        if id:
            cantidad = modelo.objects.filter(**filtros).exclude(pk=id).count()
        else:
            cantidad = modelo.objects.filter(**filtros).count()

        # si no existe
        if cantidad > 0:
            return True

        return False

    def save(self, request, type='add'):
        """aniadimos un nuevo departamento"""
        try:
            propietario_apellidos_txt = validate_string('propietario apellidos', request.POST['propietario_apellidos'], remove_specials='yes')
            propietario_nombres_txt = validate_string('propietario nombres', request.POST['propietario_nombres'], remove_specials='yes')
            propietario_fonos_txt = validate_string('propietario telefonos', request.POST['propietario_fonos'], remove_specials='yes')
            propietario_ci_nit_txt = validate_string('propietario ci/nit', request.POST['propietario_ci_nit'], remove_specials='yes')
            propietario_email_txt = validate_email('propietario email', request.POST['propietario_email'], len_zero='yes')

            copropietario_apellidos_txt = validate_string('copropietario apellidos', request.POST['copropietario_apellidos'], remove_specials='yes', len_zero='yes')
            copropietario_nombres_txt = validate_string('copropietario nombres', request.POST['copropietario_nombres'], remove_specials='yes', len_zero='yes')
            copropietario_fonos_txt = validate_string('copropietario telefonos', request.POST['copropietario_fonos'], remove_specials='yes', len_zero='yes')
            copropietario_ci_nit_txt = validate_string('copropietario ci/nit', request.POST['copropietario_ci_nit'], remove_specials='yes', len_zero='yes')
            copropietario_email_txt = validate_email('copropietario email', request.POST['copropietario_email'], len_zero='yes')

            departamento_txt = validate_string('departamento', request.POST['departamento'], remove_specials='yes')
            departamento_txt = departamento_txt.replace(' ', '')
            codigo_txt = validate_string('codigo', request.POST['codigo'], remove_specials='yes')
            metros2_txt = validate_number_decimal('metros 2', request.POST['metros2'])
            bloque_id = validate_number_int('bloque', request.POST['bloque_id'])
            piso_id = validate_number_int('piso', request.POST['piso_id'])
            id = validate_number_int('id', request.POST['id'], len_zero='yes')

            # verificamos duplicidad departamento
            if not self.is_in_db(id, departamento_txt):
                # activo
                if 'activo' in request.POST.keys():
                    status_departamento = self.status_activo
                else:
                    status_departamento = self.status_inactivo

                # punto
                usuario = request.user
                usuario_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=usuario)

                datos = {}
                datos['type'] = type
                datos['id'] = id
                datos['propietario_apellidos'] = propietario_apellidos_txt
                datos['propietario_nombres'] = propietario_nombres_txt
                datos['propietario_ci_nit'] = propietario_ci_nit_txt
                datos['propietario_fonos'] = propietario_fonos_txt
                datos['propietario_email'] = propietario_email_txt
                datos['copropietario_apellidos'] = copropietario_apellidos_txt
                datos['copropietario_nombres'] = copropietario_nombres_txt
                datos['copropietario_ci_nit'] = copropietario_ci_nit_txt
                datos['copropietario_fonos'] = copropietario_fonos_txt
                datos['copropietario_email'] = copropietario_email_txt

                datos['departamento'] = departamento_txt
                datos['codigo'] = codigo_txt
                datos['metros2'] = metros2_txt
                datos['bloque_id'] = apps.get_model('departamentos', 'Bloques').objects.get(pk=bloque_id)
                datos['piso_id'] = apps.get_model('departamentos', 'Pisos').objects.get(pk=piso_id)

                datos['created_at'] = 'now'
                datos['updated_at'] = 'now'
                datos['user_perfil_id'] = usuario_perfil
                datos['status_id'] = status_departamento

                if self.save_db(**datos):
                    self.error_operation = ""
                    return True
                else:
                    return False
            else:
                self.error_operation = "Ya existe este departamento: " + departamento_txt
                return False

        except Exception as ex:
            if type == 'add':
                self.error_operation = "Error al agregar departamento, " + str(ex)
            if type == 'modify':
                self.error_operation = "Error al modificar departamento, " + str(ex)
            return False

    def save_db(self, **datos):
        """base de datos"""
        if not self.is_in_db(datos['id'], datos['departamento']):
            if not datos['type'] in ['add', 'modify']:
                self.error_operation = 'Operation no valid'
                return False

            try:
                with transaction.atomic():
                    campos_add = {}
                    campos_add['propietario_apellidos'] = datos['propietario_apellidos']
                    campos_add['propietario_nombres'] = datos['propietario_nombres']
                    campos_add['propietario_ci_nit'] = datos['propietario_ci_nit']
                    campos_add['propietario_fonos'] = datos['propietario_fonos']
                    campos_add['propietario_email'] = datos['propietario_email']
                    campos_add['copropietario_apellidos'] = datos['copropietario_apellidos']
                    campos_add['copropietario_nombres'] = datos['copropietario_nombres']
                    campos_add['copropietario_ci_nit'] = datos['copropietario_ci_nit']
                    campos_add['copropietario_fonos'] = datos['copropietario_fonos']
                    campos_add['copropietario_email'] = datos['copropietario_email']

                    campos_add['bloque_id'] = datos['bloque_id']
                    campos_add['piso_id'] = datos['piso_id']
                    campos_add['departamento'] = datos['departamento'].replace(' ', '')
                    campos_add['codigo'] = datos['codigo']
                    campos_add['metros2'] = datos['metros2']

                    campos_add['created_at'] = datos['created_at']
                    campos_add['updated_at'] = datos['updated_at']
                    campos_add['user_perfil_id'] = datos['user_perfil_id']
                    campos_add['status_id'] = datos['status_id']

                    if datos['type'] == 'add':
                        departamento_add = Departamentos.objects.create(**campos_add)
                        departamento_add.save()

                        status_django_user = 0
                        if datos['status_id'] == self.status_activo:
                            status_django_user = 1

                        password_user = make_password(datos['propietario_ci_nit'])
                        user = apps.get_model('auth', 'User')
                        usuario = user.objects.create(first_name=datos['propietario_nombres'], last_name=datos['propietario_apellidos'],
                                                      username=datos['departamento'], password=password_user, email=datos['propietario_email'], is_active=status_django_user)
                        usuario.save()

                        # relaciones y permisos
                        perfil = apps.get_model('permisos', 'Perfiles').objects.get(pk=settings.PERFIL_DEPARTAMENTO)
                        user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.create(user_id=usuario, perfil_id=perfil, punto_id=1,
                                                                                                 caja_id=0, notificacion=1, status_id=datos['status_id'], created_at='now', updated_at='now')
                        user_perfil.save()
                        # usuarios modulos
                        apps.get_model('permisos', 'UsersModulos').objects.filter(user_perfil_id=user_perfil).delete()
                        lista_modulos = apps.get_model('permisos', 'Modulos').objects.all()
                        for modulo in lista_modulos:
                            if modulo.modulo_id == settings.MOD_CALENDARIO or modulo.modulo_id == settings.MOD_LISTA_COBROS:
                                if modulo.modulo_id == settings.MOD_CALENDARIO:
                                    user_modulo = apps.get_model('permisos', 'UsersModulos').objects.create(
                                        modulo_id=modulo, user_perfil_id=user_perfil, enabled=1, adicionar=1,
                                        modificar=0, eliminar=1, anular=0, imprimir=0, permiso=0
                                    )
                                    user_modulo.save()
                                if modulo.modulo_id == settings.MOD_LISTA_COBROS:
                                    user_modulo = apps.get_model('permisos', 'UsersModulos').objects.create(
                                        modulo_id=modulo, user_perfil_id=user_perfil, enabled=1, adicionar=0,
                                        modificar=0, eliminar=0, anular=0, imprimir=0, permiso=0
                                    )
                                    user_modulo.save()
                            else:
                                user_modulo = apps.get_model('permisos', 'UsersModulos').objects.create(
                                    modulo_id=modulo, user_perfil_id=user_perfil, enabled=0, adicionar=0,
                                    modificar=0, eliminar=0, anular=0, imprimir=0, permiso=0
                                )
                                user_modulo.save()

                    if datos['type'] == 'modify':
                        departamento = Departamentos.objects.get(pk=datos['id'])

                        # recuperamos el usuario del departamento
                        usuario = apps.get_model('auth', 'User').objects.get(username=departamento.departamento)

                        departamento.propietario_apellidos = datos['propietario_apellidos']
                        departamento.propietario_nombres = datos['propietario_nombres']
                        departamento.propietario_ci_nit = datos['propietario_ci_nit']
                        departamento.propietario_fonos = datos['propietario_fonos']
                        departamento.propietario_email = datos['propietario_email']
                        departamento.copropietario_apellidos = datos['copropietario_apellidos']
                        departamento.copropietario_nombres = datos['copropietario_nombres']
                        departamento.copropietario_ci_nit = datos['copropietario_ci_nit']
                        departamento.copropietario_fonos = datos['copropietario_fonos']
                        departamento.copropietario_email = datos['copropietario_email']

                        departamento.bloque_id = datos['bloque_id']
                        departamento.piso_id = datos['piso_id']
                        departamento.departamento = datos['departamento']
                        departamento.codigo = datos['codigo']
                        departamento.metros2 = datos['metros2']

                        departamento.updated_at = datos['updated_at']
                        departamento.status_id = datos['status_id']
                        departamento.save()

                        status_django_user = 0
                        if datos['status_id'] == self.status_activo:
                            status_django_user = 1

                        # user perfil
                        user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=usuario)
                        # actualizamos
                        usuario.first_name = datos['propietario_nombres']
                        usuario.last_name = datos['propietario_apellidos']
                        usuario.email = datos['propietario_email']
                        #print('user name..: ', datos['departamento'])
                        usuario.username = datos['departamento']
                        usuario.is_active = status_django_user

                        #password_user = make_password(datos['propietario_ci_nit'])
                        #usuario.password = password_user

                        usuario.save()
                        #print('usuario....', usuario, ' ...id: ', usuario.id)

                        user_perfil.status_id = datos['status_id']
                        user_perfil.save()

                self.error_operation = ''
                return True

            except Exception as ex:
                self.error_operation = 'error de argumentos, ' + str(ex)
                if datos['type'] == 'add':
                    print('ERROR departmentos add, '+str(ex))
                if datos['type'] == 'modify':
                    print('ERROR departmentos modify, '+str(ex))
                return False
        else:
            self.error_operation = "Ya existe este departamento: " + datos['departamento']
            return False

    def delete(self, id):
        """eliminamos"""
        try:
            with transaction.atomic():
                # departamento
                departamento = Departamentos.objects.get(pk=id)

                # usuario
                modelo = apps.get_model('auth', 'User')
                objeto = modelo.objects.get(username=departamento.departamento)
                objeto.is_active = False
                objeto.save()

                # usuario perfil
                usuario_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=objeto)
                usuario_perfil.status_id = self.status_eliminado
                usuario_perfil.deleted_at = 'now'
                usuario_perfil.save()

                departamento.status_id = self.status_eliminado
                departamento.deleted_at = 'now'
                departamento.save()

                self.error_operation = ''
                return True

        except Exception as ex:
            self.error_operation = "Error al eliminar el usuario, " + str(ex)
            return False
