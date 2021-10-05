from controllers.DefaultValues import DefaultValues
from django.conf import settings
from django.apps import apps

from utils.validators import validate_number_int, validate_string


class ActividadesController(DefaultValues):
    def __init__(self):
        DefaultValues.__init__(self)
        self.modelo_name = 'Actividades'
        self.modelo_id = 'actividad_id'
        self.modelo_app = 'calendario'
        self.modulo_id = settings.MOD_ACTIVIDADES

        # variables de session
        self.modulo_session = "actividades"
        self.columnas.append('actividad')
        self.columnas.append('codigo')

        self.variables_filtros.append('search_actividad')
        self.variables_filtros.append('search_codigo')

        self.variables_filtros_defecto['search_actividad'] = ''
        self.variables_filtros_defecto['search_codigo'] = ''

        self.variable_page = "page"
        self.variable_page_defecto = "1"
        self.variable_order = "search_order"
        self.variable_order_value = self.columnas[0]
        self.variable_order_type = "search_order_type"

        # tablas donde se debe verificar para eliminar
        self.modelos_eliminar = {'calendario': 'Calendario'}

        # control del formulario
        self.control_form = "txt|2|S|actividad|Actividad"
        self.control_form += ";txt|2|S|codigo|Codigo"
        self.control_form += ";txt|6|S|color_hex|Color Hexadecimal"
        self.control_form += ";txt|6|S|color_txt|Color Texto"

    def index(self, request):
        DefaultValues.index(self, request)
        self.filtros_modulo.clear()
        # status
        self.filtros_modulo['status_id_id__in'] = [self.activo, self.inactivo]

        # actividad
        if self.variables_filtros_values['search_actividad'].strip() != "":
            self.filtros_modulo['actividad__icontains'] = self.variables_filtros_values['search_actividad'].strip()

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
        filtros['actividad__in'] = [nuevo_valor]
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
        save, add or modify actividad
        :param request: (object) request object
        :param type: (str) add or modify
        :return: True if success add else false
        """
        #print('type: ', type)
        try:
            actividad_txt = validate_string('actividad', request.POST['actividad'], remove_specials='yes')
            codigo_txt = validate_string('codigo', request.POST['codigo'], remove_specials='yes')
            color_hex_txt = validate_string('color hex', request.POST['color_hex'], remove_specials='yes')
            color_texto_txt = validate_string('color texto', request.POST['color_txt'], remove_specials='yes')
            id = validate_number_int('id', request.POST['id'], len_zero='yes')
            user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=request.user)

            if 'activo' in request.POST.keys():
                status_actividad = self.status_activo
            else:
                status_actividad = self.status_inactivo

            if not self.is_in_db(id, actividad_txt):
                if type == 'add':
                    actividad = apps.get_model('calendario', 'Actividades').objects.create(actividad=actividad_txt,
                                                                                           codigo=codigo_txt, color_hex=color_hex_txt, color_txt=color_texto_txt, user_perfil_id=user_perfil, status_id=status_actividad, created_at='now', updated_at='now')
                    actividad.save()
                    self.error_operation = ""
                    return True

                if type == 'modify':
                    actividad = apps.get_model('calendario', 'Actividades').objects.get(pk=id)
                    actividad.actividad = actividad_txt
                    actividad.codigo = codigo_txt
                    actividad.color_hex = color_hex_txt
                    actividad.color_txt = color_texto_txt
                    actividad.status_id = status_actividad
                    actividad.user_perfil_id = user_perfil
                    actividad.udpated_at = 'now'
                    actividad.save()
                    self.error_operation = ""
                    return True

                # default
                self.error_operation = 'operation no valid'
                return False

            else:
                self.error_operation = "Ya existe esta actividad: " + actividad_txt
                return False

        except Exception as ex:
            if type == 'add':
                self.error_operation = "Error al agregar la actividad, " + str(ex)
                return False

            if type == 'modify':
                self.error_operation = "Error al modificar la actividad, " + str(ex)
                return False

            # default
            self.error_operation = 'db operation no valid'
            return False
