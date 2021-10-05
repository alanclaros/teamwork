from utils.permissions import get_system_settings
from controllers.DefaultValues import DefaultValues
from django.conf import settings
from django.apps import apps

from utils.validators import validate_number_int, validate_string


class BloquesController(DefaultValues):
    def __init__(self):
        DefaultValues.__init__(self)
        self.modelo_name = 'Bloques'
        self.modelo_id = 'bloque_id'
        self.modelo_app = 'departamentos'
        self.modulo_id = settings.MOD_BLOQUES

        # variables de session
        self.modulo_session = "bloques"
        self.columnas.append('bloque')
        self.columnas.append('codigo')

        self.variables_filtros.append('search_bloque')
        self.variables_filtros.append('search_codigo')

        self.variables_filtros_defecto['search_bloque'] = ''
        self.variables_filtros_defecto['search_codigo'] = ''

        self.variable_page = "page"
        self.variable_page_defecto = "1"
        self.variable_order = "search_order"
        self.variable_order_value = self.columnas[0]
        self.variable_order_type = "search_order_type"

        # tablas donde se debe verificar para eliminar
        self.modelos_eliminar = {'departamentos': 'Departamentos'}

        # control del formulario
        self.control_form = "txt|2|S|bloque|Bloque"
        self.control_form += ";txt|2|S|codigo|Codigo"

    def index(self, request):
        DefaultValues.index(self, request)
        self.filtros_modulo.clear()
        # status
        self.filtros_modulo['status_id_id__in'] = [self.activo, self.inactivo]

        # bloque
        if self.variables_filtros_values['search_bloque'].strip() != "":
            self.filtros_modulo['bloque__icontains'] = self.variables_filtros_values['search_bloque'].strip()

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
        filtros['bloque__in'] = [nuevo_valor]
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
        save, add or modify bloque
        :param request: (object) request object
        :param type: (str) add or modify
        :return: True if success add else false
        """
        #print('type: ', type)
        try:
            bloque_txt = validate_string('bloque', request.POST['bloque'], remove_specials='yes')
            codigo_txt = validate_string('codigo', request.POST['codigo'], remove_specials='yes')
            ubicacion_txt = validate_string('ubicacion', request.POST['ubicacion'], remove_specials='yes', len_zero='yes')
            id = validate_number_int('id', request.POST['id'], len_zero='yes')
            user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=request.user)

            if 'activo' in request.POST.keys():
                status_bloque = self.status_activo
            else:
                status_bloque = self.status_inactivo

            if not self.is_in_db(id, bloque_txt):
                if type == 'add':
                    bloque = apps.get_model('departamentos', 'Bloques').objects.create(bloque=bloque_txt,
                                                                                       codigo=codigo_txt, ubicacion=ubicacion_txt, user_perfil_id=user_perfil, status_id=status_bloque, created_at='now', updated_at='now')
                    bloque.save()
                    self.error_operation = ""
                    return True

                if type == 'modify':
                    bloque = apps.get_model('departamentos', 'Bloques').objects.get(pk=id)
                    bloque.bloque = bloque_txt
                    bloque.codigo = codigo_txt
                    bloque.ubicacion = ubicacion_txt
                    bloque.status_id = status_bloque
                    bloque.user_perfil_id = user_perfil
                    bloque.udpated_at = 'now'
                    bloque.save()
                    self.error_operation = ""
                    return True

                # default
                self.error_operation = 'operation no valid'
                return False

            else:
                self.error_operation = "Ya existe este bloque: " + bloque_txt
                return False

        except Exception as ex:
            if type == 'add':
                self.error_operation = "Error al agregar el bloque, " + str(ex)
                return False

            if type == 'modify':
                self.error_operation = "Error al modificar el bloque, " + str(ex)
                return False

            # default
            self.error_operation = 'db operation no valid'
            return False
