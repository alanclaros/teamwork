from utils.permissions import get_system_settings
from controllers.DefaultValues import DefaultValues
from django.conf import settings
from django.apps import apps

from utils.validators import validate_number_int, validate_string
from departamentos.models import Pisos


class PisosController(DefaultValues):
    def __init__(self):
        DefaultValues.__init__(self)
        self.modelo_name = 'Pisos'
        self.modelo_id = 'piso_id'
        self.modelo_app = 'departamentos'
        self.modulo_id = settings.MOD_PISOS

        # variables de session
        self.modulo_session = "pisos"
        self.columnas.append('piso')
        self.columnas.append('codigo')

        self.variables_filtros.append('search_piso')
        self.variables_filtros.append('search_codigo')

        self.variables_filtros_defecto['search_piso'] = ''
        self.variables_filtros_defecto['search_codigo'] = ''

        self.variable_page = "page"
        self.variable_page_defecto = "1"
        self.variable_order = "search_order"
        self.variable_order_value = self.columnas[0]
        self.variable_order_type = "search_order_type"

        # tablas donde se debe verificar para eliminar
        self.modelos_eliminar = {'departamentos': 'Departamentos'}

        # control del formulario
        self.control_form = "txt|1|S|piso|Piso"
        self.control_form += ";txt|1|S|codigo|Codigo"

    def index(self, request):
        DefaultValues.index(self, request)
        self.filtros_modulo.clear()
        # status
        self.filtros_modulo['status_id_id__in'] = [self.activo, self.inactivo]

        # piso
        if self.variables_filtros_values['search_piso'].strip() != "":
            self.filtros_modulo['piso__icontains'] = self.variables_filtros_values['search_piso'].strip()

        # codigo
        if self.variables_filtros_values['search_codigo'].strip() != "":
            self.filtros_modulo['codigo__icontains'] = self.variables_filtros_values['search_codigo'].strip()

        # paginacion, paginas y definiendo el LIMIT *,*
        self.pagination()
        # asigamos la paginacion a la session
        request.session[self.modulo_session]['pages_list'] = self.pages_list

        # recuperamos los datos
        return self.get_list()

    def is_in_db(self, id, nuevo_valor):
        """verificamos si existe en la base de datos"""
        modelo = apps.get_model(self.modelo_app, self.modelo_name)
        filtros = {}
        filtros['status_id_id__in'] = [self.activo, self.inactivo]
        filtros['piso__in'] = [nuevo_valor]
        if id > 0:
            cantidad = modelo.objects.filter(**filtros).exclude(pk=id).count()
        else:
            cantidad = modelo.objects.filter(**filtros).count()

        # si no existe
        if cantidad > 0:
            return True

        return False

    def save(self, request, type='add'):
        """
        save, add or modify piso
        :param request: (object) request object
        :param type: (str) add or modify
        :return: True if success add else false
        """
        #print('type: ', type)
        try:
            piso_txt = validate_string('piso', request.POST['piso'], remove_specials='yes')
            codigo_txt = validate_string('codigo', request.POST['codigo'], remove_specials='yes')
            id = validate_number_int('id', request.POST['id'], len_zero='yes')
            user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=request.user)

            if 'activo' in request.POST.keys():
                status_piso = self.status_activo
            else:
                status_piso = self.status_inactivo

            if not self.is_in_db(id, piso_txt):
                if type == 'add':
                    piso = Pisos.objects.create(piso=piso_txt, codigo=codigo_txt, user_perfil_id=user_perfil,
                                                status_id=status_piso, created_at='now', updated_at='now')
                    piso.save()
                    self.error_operation = ""
                    return True

                if type == 'modify':
                    piso = Pisos.objects.get(pk=id)
                    piso.piso = piso_txt
                    piso.codigo = codigo_txt
                    piso.status_id = status_piso
                    piso.user_perfil_id = user_perfil
                    piso.udpated_at = 'now'
                    piso.save()
                    self.error_operation = ""
                    return True

                # default
                self.error_operation = 'operation no valid'
                return False

            else:
                self.error_operation = "Ya existe este piso: " + piso_txt
                return False

        except Exception as ex:
            if type == 'add':
                self.error_operation = "Error al agregar el piso, " + str(ex)
                return False

            if type == 'modify':
                self.error_operation = "Error al modificar el piso, " + str(ex)
                return False

            # default
            self.error_operation = 'db operation no valid'
            return False
