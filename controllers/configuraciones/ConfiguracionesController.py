from django.conf import settings
from django.apps import apps

from controllers.DefaultValues import DefaultValues
# from configuraciones.models import Configuraciones
# from status.models import Status

from utils.validators import validate_number_int, validate_number_decimal, validate_string
from utils.dates_functions import get_date_to_db


class ConfiguracionesController(DefaultValues):
    def __init__(self):
        DefaultValues.__init__(self)
        self.modelo_name = 'Configuraciones'
        self.modelo_id = 'configuracion_id'
        self.modelo_app = 'configuraciones'
        self.modulo_id = settings.MOD_CONFIGURACIONES_SISTEMA

        # variables de session
        self.modulo_session = "configuraciones"

        # paginas session
        self.variable_page = "ss_page"
        self.variable_page_defecto = "1"

        # control del formulario
        self.control_form = "txt|1|S|cant_per_page|Cantidad por Pagina"
        self.control_form += ";txt|1|S|cant_lista_cobranza|Cantidad lista Cobranza"
        self.control_form += ";txt|1|S|costo_m3|Costo M3"
        self.control_form += ";txt|1|S|costo_minimo|Costo Minimo"
        self.control_form += ";txt|1|S|unidad_minima_m3|Unidad Minima M3"
        self.control_form += ";txt|1|S|expensas_monto_m2|Expensas Monto M2"

    def index(self, request):
        DefaultValues.index(self, request)
        self.filtros_modulo.clear()

        modelo = apps.get_model(self.modelo_app, self.modelo_name)
        retorno = modelo.objects.get(pk=1)

        return retorno

    def add(self, request):
        """aniadimos"""
        pass

    def save(self, request, type='modify'):
        """modificamos"""
        try:
            cant_per_page = validate_number_int('cantidad pagina', request.POST['cant_per_page'])
            cant_lista_cobranza = validate_number_int('cantidad lista cobranza', request.POST['cant_lista_cobranza'])
            usar_fecha_servidor = validate_string('usar_fecha_servidor', request.POST['usar_fecha_servidor'], remove_specials='yes')
            fecha_sistema = get_date_to_db(fecha=request.POST['fecha_sistema'].strip(), formato_ori='dd-MMM-yyyy', formato='yyyy-mm-dd')
            costo_m3 = validate_number_decimal('costo m3', request.POST['costo_m3'])
            costo_minimo = validate_number_decimal('costo minimo', request.POST['costo_minimo'])
            unidad_minima_m3 = validate_number_decimal('Unidad minima m3', request.POST['unidad_minima_m3'])
            expensas_monto_m2 = validate_number_decimal('Expensas monto M2', request.POST['expensas_monto_m2'])

            configuracion = apps.get_model('configuraciones', 'Configuraciones').objects.get(pk=1)
            configuracion.cant_per_page = cant_per_page
            configuracion.cant_lista_cobranza = cant_lista_cobranza
            configuracion.usar_fecha_servidor = usar_fecha_servidor
            configuracion.fecha_sistema = fecha_sistema
            configuracion.costo_m3 = costo_m3
            configuracion.costo_minimo = costo_minimo
            configuracion.unidad_minima_m3 = unidad_minima_m3
            configuracion.expensas_monto_m2 = expensas_monto_m2
            configuracion.usar_fecha_servidor = usar_fecha_servidor
            configuracion.save()
            return True

        except Exception as ex:
            self.error_operation = "Error al actualizar los datos, " + str(ex)
            return False
