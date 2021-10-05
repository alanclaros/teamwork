from utils.permissions import get_system_settings
from controllers.DefaultValues import DefaultValues
from django.conf import settings
from django.apps import apps

from utils.validators import validate_number_decimal, validate_number_int, validate_string
from configuraciones.models import CobrosMensuales


class CobrosMensualesController(DefaultValues):
    def __init__(self):
        DefaultValues.__init__(self)
        self.modelo_name = 'CobrosMensuales'
        self.modelo_id = 'cobro_mensual_id'
        self.modelo_app = 'configuraciones'
        self.modulo_id = settings.MOD_COBROS_MENSUALES

        # variables de session
        self.modulo_session = "cobros_mensuales"
        self.columnas.append('cobro_mensual')
        self.columnas.append('codigo')

        self.variables_filtros.append('search_cobro_mensual')
        self.variables_filtros.append('search_codigo')

        self.variables_filtros_defecto['search_cobro_mensual'] = ''
        self.variables_filtros_defecto['search_codigo'] = ''

        self.variable_page = "page"
        self.variable_page_defecto = "1"
        self.variable_order = "search_order"
        self.variable_order_value = self.columnas[0]
        self.variable_order_type = "search_order_type"

        # tablas donde se debe verificar para eliminar
        #self.modelos_eliminar = {'departamentos': 'Departamentos'}
        self.modelos_eliminar = {}

        # control del formulario
        self.control_form = "txt|1|S|cobro_mensual|Cobro Mensual"
        self.control_form += ";txt|1|S|codigo|Codigo"
        self.control_form += ";txt|1|S|monto_bs|Monto Bs"
        self.control_form += ";txt|1|S|monto_cobrar|Monto Cobrar"

    def index(self, request):
        DefaultValues.index(self, request)
        self.filtros_modulo.clear()
        # status
        self.filtros_modulo['status_id_id__in'] = [self.activo, self.inactivo]

        # cobro_mensual
        if self.variables_filtros_values['search_cobro_mensual'].strip() != "":
            self.filtros_modulo['cobro_mensual__icontains'] = self.variables_filtros_values['search_cobro_mensual'].strip()

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
        filtros['cobro_mensual__in'] = [nuevo_valor]
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
        save, add or modify cobro_mensual
        :param request: (object) request object
        :param type: (str) add or modify
        :return: True if success add else false
        """
        #print('type: ', type)
        try:
            cobro_mensual_txt = validate_string('cobro_mensual', request.POST['cobro_mensual'], remove_specials='yes')
            codigo_txt = validate_string('codigo', request.POST['codigo'], remove_specials='yes')
            monto_bs = validate_number_decimal('monto_bs', request.POST['monto_bs'])
            monto_cobrar = validate_number_decimal('monto_cobrar', request.POST['monto_cobrar'])
            id = validate_number_int('id', request.POST['id'], len_zero='yes')
            #user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=request.user)
            #print('user_perfil...:', user_perfil)

            if 'activo' in request.POST.keys():
                status_cobro_mensual = self.status_activo
            else:
                status_cobro_mensual = self.status_inactivo

            if not self.is_in_db(id, cobro_mensual_txt):
                if type == 'add':
                    cobro_mensual = CobrosMensuales.objects.create(cobro_mensual=cobro_mensual_txt, codigo=codigo_txt, monto_bs=monto_bs, monto_cobrar=monto_cobrar,
                                                                   status_id=status_cobro_mensual, created_at='now', updated_at='now')
                    cobro_mensual.save()
                    self.error_operation = ""
                    return True

                if type == 'modify':
                    cobro_mensual = CobrosMensuales.objects.get(pk=id)
                    cobro_mensual.cobro_mensual = cobro_mensual_txt
                    cobro_mensual.codigo = codigo_txt
                    cobro_mensual.monto_bs = monto_bs
                    cobro_mensual.monto_cobrar = monto_cobrar
                    cobro_mensual.status_id = status_cobro_mensual
                    #cobro_mensual.user_perfil_id = user_perfil
                    cobro_mensual.udpated_at = 'now'
                    cobro_mensual.save()
                    self.error_operation = ""
                    return True

                # default
                self.error_operation = 'operation no valid'
                return False

            else:
                self.error_operation = "Ya existe este cobro_mensual: " + cobro_mensual_txt
                return False

        except Exception as ex:
            if type == 'add':
                self.error_operation = "Error al agregar el cobro mensual, " + str(ex)
                return False

            if type == 'modify':
                self.error_operation = "Error al modificar el cobro mensual, " + str(ex)
                return False

            # default
            self.error_operation = 'db operation no valid'
            return False
