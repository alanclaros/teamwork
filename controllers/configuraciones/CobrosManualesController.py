from utils.permissions import get_system_settings
from controllers.DefaultValues import DefaultValues
from django.conf import settings
from django.apps import apps

from utils.validators import validate_number_decimal, validate_number_int, validate_string
from configuraciones.models import CobrosManuales


class CobrosManualesController(DefaultValues):
    def __init__(self):
        DefaultValues.__init__(self)
        self.modelo_name = 'CobrosManuales'
        self.modelo_id = 'cobro_manual_id'
        self.modelo_app = 'configuraciones'
        self.modulo_id = settings.MOD_COBROS_MANUALES

        # variables de session
        self.modulo_session = "cobros_manuales"
        self.columnas.append('cobro_manual')
        self.columnas.append('codigo')

        self.variables_filtros.append('search_cobro_manual')
        self.variables_filtros.append('search_codigo')

        self.variables_filtros_defecto['search_cobro_manual'] = ''
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
        self.control_form = "txt|1|S|cobro_manual|Cobro Manual"
        self.control_form += ";txt|1|S|codigo|Codigo"
        self.control_form += ";cbo|0|S|monto_porcentaje|"
        self.control_form += ";txt|1|S|monto_bs|Monto Bs"
        self.control_form += ";txt|1|S|porcentaje|Porcentaje"

    def index(self, request):
        DefaultValues.index(self, request)
        self.filtros_modulo.clear()
        # status
        self.filtros_modulo['status_id_id__in'] = [self.activo, self.inactivo]

        # cobro_manual
        if self.variables_filtros_values['search_cobro_manual'].strip() != "":
            self.filtros_modulo['cobro_manual__icontains'] = self.variables_filtros_values['search_cobro_manual'].strip()

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
        filtros['cobro_manual__in'] = [nuevo_valor]
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
        save, add or modify cobro_manual
        :param request: (object) request object
        :param type: (str) add or modify
        :return: True if success add else false
        """
        #print('type: ', type)
        try:
            cobro_manual_txt = validate_string('cobro manual', request.POST['cobro_manual'], remove_specials='yes')
            codigo_txt = validate_string('codigo', request.POST['codigo'], remove_specials='yes')
            monto_porcentaje = validate_string('monto porcentaje', request.POST['monto_porcentaje'], remove_specials='yes')
            monto_bs = validate_number_decimal('monto bs', request.POST['monto_bs'])
            porcentaje = validate_number_decimal('porcentaje', request.POST['porcentaje'])
            cobro_mensual_id = validate_number_int('cobro mensual', request.POST['cobro_mensual_id'], len_zero='yes')
            id = validate_number_int('id', request.POST['id'], len_zero='yes')

            if 'activo' in request.POST.keys():
                status_cobro_manual = self.status_activo
            else:
                status_cobro_manual = self.status_inactivo

            if not self.is_in_db(id, cobro_manual_txt):
                if type == 'add':
                    cobro_manual = CobrosManuales.objects.create(cobro_manual=cobro_manual_txt, codigo=codigo_txt, monto_porcentaje=monto_porcentaje, monto_bs=monto_bs,
                                                                 porcentaje=porcentaje, cobro_mensual_id=cobro_mensual_id, status_id=status_cobro_manual, created_at='now', updated_at='now')
                    cobro_manual.save()
                    self.error_operation = ""
                    return True

                if type == 'modify':
                    cobro_manual = CobrosManuales.objects.get(pk=id)
                    cobro_manual.cobro_manual = cobro_manual_txt
                    cobro_manual.codigo = codigo_txt
                    cobro_manual.monto_porcentaje = monto_porcentaje
                    cobro_manual.monto_bs = monto_bs
                    cobro_manual.porcentaje = porcentaje
                    cobro_manual.cobro_mensual_id = cobro_mensual_id
                    cobro_manual.status_id = status_cobro_manual
                    cobro_manual.udpated_at = 'now'
                    cobro_manual.save()
                    self.error_operation = ""
                    return True

                # default
                self.error_operation = 'operation no valid'
                return False

            else:
                self.error_operation = "Ya existe este cobro manual: " + cobro_manual_txt
                return False

        except Exception as ex:
            if type == 'add':
                self.error_operation = "Error al agregar el cobro manual, " + str(ex)
                return False

            if type == 'modify':
                self.error_operation = "Error al modificar el cobro manual, " + str(ex)
                return False

            # default
            self.error_operation = 'db operation no valid'
            return False
