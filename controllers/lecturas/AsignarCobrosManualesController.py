from controllers.ListasController import ListasController
from controllers.DefaultValues import DefaultValues
from django.conf import settings
from django.apps import apps

from django.db import transaction

from utils.validators import validate_string, validate_number_int, validate_number_decimal
from utils.permissions import current_periodo, get_system_settings, previous_periodo, show_periodo

# conexion directa a la base de datos
from django.db import connection

from controllers.lecturas.LecturasController import LecturasController


class AsignarCobrosManualesController(DefaultValues):
    def __init__(self):
        DefaultValues.__init__(self)
        self.modelo_name = 'Lecturas'
        self.modelo_id = 'lectura_id'
        self.modelo_app = 'lecturas'
        self.modulo_id = settings.MOD_ASIGNAR_COBROS_MANUALES

        # variables de session
        self.modulo_session = "asignar_cobros_manuales"
        self.columnas.append('departamento')
        self.columnas.append('propietario_apellidos')
        self.columnas.append('propietario_nombres')
        self.columnas.append('b.bloque')
        self.columnas.append('p.piso')

        self.variables_filtros.append('search_apellidos')
        self.variables_filtros.append('search_nombres')
        self.variables_filtros.append('search_departamento')
        self.variables_filtros.append('search_bloque')
        self.variables_filtros.append('search_piso')
        self.variables_filtros.append('search_periodo')
        self.variables_filtros.append('search_cobro_manual')

        self.variables_filtros_defecto['search_apellidos'] = ''
        self.variables_filtros_defecto['search_nombres'] = ''
        self.variables_filtros_defecto['search_departamento'] = ''
        self.variables_filtros_defecto['search_bloque'] = '0'
        self.variables_filtros_defecto['search_piso'] = '0'
        self.variables_filtros_defecto['search_periodo'] = current_periodo()

        # lista de cobros manuales
        lista_cobros_manuales = apps.get_model('configuraciones', 'CobrosManuales').objects.filter(status_id=self.status_activo).order_by('cobro_manual')
        if lista_cobros_manuales:
            primer_cobro = lista_cobros_manuales.first().cobro_manual_id
        else:
            primer_cobro = '0'

        self.variables_filtros_defecto['search_cobro_manual'] = primer_cobro

        self.variable_page = "page"
        self.variable_page_defecto = "1"
        self.variable_order = "search_order"
        self.variable_order_value = self.columnas[0]
        self.variable_order_type = "search_order_type"
        self.variable_order_type_value = 'ASC'

        # tablas donde se debe verificar para eliminar
        self.modelos_eliminar = {}

        # control del formulario
        self.control_form = ""
        # solo de lecturas
        self.lista_departamentos_ids = ""
        self.monto_cobro_manual = 0

    def index(self, request):
        DefaultValues.index(self, request)
        self.filtros_modulo.clear()
        sql_add = f"AND d.status_id='{self.activo}' "
        # status
        self.filtros_modulo['status_id_id__in'] = [self.activo]

        # periodo
        self.filtros_modulo['periodo'] = self.variables_filtros_values['search_periodo']

        # apellidos
        if self.variables_filtros_values['search_apellidos'].strip() != "":
            self.filtros_modulo['departamento_id__propietario_apellidos__icontains'] = self.variables_filtros_values['search_apellidos'].strip()
            sql_add += f"AND d.propietario_apellidos LIKE '%{self.variables_filtros_values['search_apellidos'].strip()}%' "

        # nombres
        if self.variables_filtros_values['search_nombres'].strip() != "":
            self.filtros_modulo['departamento_id__propietario_nombres__icontains'] = self.variables_filtros_values['search_nombres'].strip()
            sql_add += f"AND d.propietario_nombres LIKE '%{self.variables_filtros_values['search_nombres'].strip()}%' "

        # departamento
        if self.variables_filtros_values['search_departamento'].strip() != "":
            self.filtros_modulo['departamento_id__departamento__icontains'] = self.variables_filtros_values['search_departamento'].strip()
            sql_add += f"AND d.departamento LIKE '%{self.variables_filtros_values['search_departamento'].strip()}%' "

        # bloque
        if self.variables_filtros_values['search_bloque'].strip() != "0":
            self.filtros_modulo['departamento_id__bloque_id__bloque_id'] = self.variables_filtros_values['search_bloque'].strip()
            sql_add += f"AND d.bloque_id='{self.variables_filtros_values['search_bloque'].strip()}' "

        # piso
        if self.variables_filtros_values['search_piso'].strip() != "0":
            self.filtros_modulo['departamento_id__piso_id__piso_id'] = self.variables_filtros_values['search_piso'].strip()
            sql_add += f"AND d.piso_id='{self.variables_filtros_values['search_piso'].strip()}' "

        # orden
        orden_enviar = ''
        if self.variable_order_value != '':
            orden_enviar = self.variable_order_value
            if self.variable_order_type_value != '':
                orden_enviar = orden_enviar + ' ' + self.variable_order_type_value

        # lista de departamentos
        sql = "SELECT d.departamento_id, d.propietario_apellidos, d.propietario_nombres, d.departamento, d.codigo, d.metros2, b.bloque, p.piso "
        sql_count = "SELECT COUNT(*) AS cant "

        sql += "FROM departamentos d, bloques b, pisos p "
        sql += "WHERE d.bloque_id=b.bloque_id AND d.piso_id=p.piso_id "
        sql += sql_add

        sql_count += "FROM departamentos d, bloques b, pisos p "
        sql_count += "WHERE d.bloque_id=b.bloque_id AND d.piso_id=p.piso_id "
        sql_count += sql_add

        sql += "ORDER BY " + orden_enviar + " "

        # cantidad total de registros
        cantidad_registros = 0
        with connection.cursor() as cursor:
            cursor.execute(sql_count)
            row = cursor.fetchone()
            cantidad_registros = row[0]

        settings_sistema = get_system_settings()
        cant_per_page = settings_sistema['cant_per_page']
        self.pages_list = []
        cant_total = cantidad_registros
        j = 1
        i = 0
        while i < cant_total:
            self.pages_list.append(j)
            i = i + cant_per_page
            j += 1
            # if j > 15:
            #     break

        self.pages_limit_botton = (int(self.variable_page_val) - 1) * cant_per_page
        self.pages_limit_top = cant_per_page

        # limit para el sql
        sql += f"LIMIT {self.pages_limit_botton},{self.pages_limit_top} "
        retorno = []
        aux_lista_departamentos_ids = ""
        # lista de cobros manuales
        lista_cobros_manuales = apps.get_model('configuraciones', 'CobrosManuales').objects.filter(status_id=self.status_activo).order_by('cobro_manual')
        #lista_cobros_mensuales = apps.get_model('configuraciones', 'CobrosMensuales').objects.filter(status_id=self.status_activo).order_by('cobro_mensual')
        lista_cobros_mensuales_periodo = apps.get_model('lecturas', 'CobrosMensualesPeriodos').objects.filter(status_id=self.status_activo, periodo=self.variables_filtros_values['search_periodo'])

        # nombre y monto del cobro manual por defecto
        cobro_manual_id_cobrar = self.variables_filtros_values['search_cobro_manual']
        nombre_cobro_manual = ""
        monto_cobro_manual = 0
        if int(cobro_manual_id_cobrar) != 0:
            for cobro_manual in lista_cobros_manuales:
                if cobro_manual.cobro_manual_id == int(cobro_manual_id_cobrar):
                    nombre_cobro_manual = cobro_manual.cobro_manual
                    if cobro_manual.monto_porcentaje == 'monto':
                        monto_cobro_manual = cobro_manual.monto_bs
                    else:
                        # porcentaje
                        if cobro_manual.cobro_mensual_id != 0 and cobro_manual.porcentaje > 0:
                            # verificamos si existe la tabla de cobros mensuales periodos
                            existe = 0
                            for lcmp in lista_cobros_mensuales_periodo:
                                if lcmp.cobro_mensual_id.cobro_mensual_id == cobro_manual.cobro_mensual_id:
                                    existe = 1
                                    monto_cobro_manual = (cobro_manual.porcentaje / 100) * lcmp.monto_bs

                            if existe == 0:
                                # recuperamos el monto del cobro mensual
                                cobro_mensual = apps.get_model('configuraciones', 'CobrosMensuales').objects.get(pk=int(cobro_manual.cobro_mensual_id))
                                monto_cobro_manual = (cobro_manual.porcentaje / 100) * cobro_mensual.monto_cobrar
                        else:
                            monto_cobro_manual = 0

        monto_cobro_manual = round(monto_cobro_manual, 2)
        self.monto_cobro_manual = monto_cobro_manual
        #print('nombre: ', nombre_cobro_manual, ' ..monto: ', monto_cobro_manual)

        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                total_cobro = 0
                objeto = {}
                objeto['departamento_id'] = row[0]
                aux_lista_departamentos_ids += str(objeto['departamento_id']) + ";"

                objeto['apellidos'] = row[1]
                objeto['nombres'] = row[2]
                objeto['departamento'] = row[3]
                objeto['codigo'] = row[4]
                objeto['metros2'] = row[5]
                objeto['bloque'] = row[6]
                objeto['piso'] = row[7]
                objeto['periodo'] = self.variables_filtros_values['search_periodo']
                objeto['cobro_manual_id'] = cobro_manual_id_cobrar

                # cobros
                sql_cobro = "SELECT cobro_id, fecha_cobro, monto_bs, status_id "
                sql_cobro += f"FROM cobros c WHERE c.departamento_id='{objeto['departamento_id']}' AND c.periodo='{objeto['periodo']}' "
                with connection.cursor() as cursor_cobro:
                    cursor_cobro.execute(sql_cobro)
                    row_cobro = cursor_cobro.fetchone()
                    if row_cobro:
                        objeto['cobro_id'] = row_cobro[0]
                        objeto['fecha_cobro'] = row_cobro[1]
                        objeto['monto_bs'] = row_cobro[2]
                        objeto['status_id'] = row_cobro[3]
                    else:
                        objeto['cobro_id'] = 0
                        objeto['fecha_cobro'] = ''
                        objeto['monto_bs'] = 0
                        objeto['status_id'] = self.activo

                # cobros manuales para el periodo
                sql_cobro = "SELECT ccm.cobro_cobro_manual_id, ccm.monto_bs, cm.cobro_manual_id, cm.cobro_manual "
                sql_cobro += f"FROM cobros_cobros_manuales ccm, cobros_manuales cm WHERE ccm.cobro_manual_id=cm.cobro_manual_id "
                sql_cobro += f"AND ccm.departamento_id='{objeto['departamento_id']}' AND ccm.periodo='{objeto['periodo']}' AND ccm.cobro_manual_id='{cobro_manual_id_cobrar}' "
                sql_cobro += "ORDER BY cm.cobro_manual "
                #print('sql cobro: ', sql_cobro)

                with connection.cursor() as cursor_cobro:
                    cursor_cobro.execute(sql_cobro)
                    row_cobro = cursor_cobro.fetchone()
                    if row_cobro:
                        objeto['cobro_cobro_manual_id'] = row_cobro[0]
                        objeto['monto_bs_manual'] = row_cobro[1]
                        objeto['cobro_manual'] = row_cobro[3]
                    else:
                        objeto['cobro_cobro_manual_id'] = 0
                        objeto['monto_bs_manual'] = monto_cobro_manual
                        objeto['cobro_manual'] = nombre_cobro_manual

                retorno.append(objeto)

        # asigamos la paginacion a la session
        request.session[self.modulo_session]['pages_list'] = self.pages_list
        # asignamos departamentos ids
        if len(aux_lista_departamentos_ids) > 0:
            aux_lista_departamentos_ids = aux_lista_departamentos_ids[0:len(aux_lista_departamentos_ids)-1]
        self.lista_departamentos_ids = aux_lista_departamentos_ids

        # recuperamos los datos
        #print('retorno: ', retorno)
        return retorno

    def save_data(self, periodo, request, user):
        # verificamos el periodo
        cant_cm_periodo = apps.get_model('lecturas', 'CobrosMensualesPeriodos').objects.filter(
            status_id=self.status_activo, periodo=periodo
        ).count()
        if cant_cm_periodo == 0:
            self.error_operation = "No existen registros de cobros mensuales para el periodo"
            return False

        #cobros_manuales = apps.get_model('configuraciones', 'CobrosManuales').objects.filter(status_id=self.status_activo).order_by('cobro_manual')

        # armamos los datos
        try:
            #departamentos_ids = self.lista_departamentos_ids
            departamentos_ids = request.session['asignar_cm_departamentos_ids']
            cobro_manual = apps.get_model('configuraciones', 'CobrosManuales').objects.get(pk=int(request.POST['cobro_manual_id']))
            todos_departamentos = validate_number_int('todos departamentos', request.POST['todos_departamentos'])
            monto_cobro_manual = validate_number_decimal('monto cobro manual', request.POST['monto_cobro_manual'])
            lista_dep = []

            if todos_departamentos == 1:
                lista_departamentos = apps.get_model('departamentos', 'Departamentos').objects.filter(status_id=self.status_activo).order_by('departamento_id')

                for dep in lista_departamentos:
                    objeto = {}
                    objeto['departamento_id'] = dep
                    objeto['periodo'] = periodo
                    objeto['user'] = user
                    objeto['lectura'] = 0
                    objeto['metros2'] = 0
                    objeto['costo_expensas'] = 0
                    objeto['total_expensas'] = 0
                    objeto['costo_m3'] = 0
                    objeto['consumo'] = 0
                    # cobros mensuales
                    lista_mensuales = []
                    objeto['lista_mensuales'] = lista_mensuales
                    # cobros manuales
                    lista_manuales = []
                    obj_manual = {}
                    obj_manual['cobro_manual_id'] = cobro_manual
                    obj_manual['monto_bs'] = monto_cobro_manual
                    obj_manual['add_cobro_manual'] = 1
                    obj_manual['remove_cobro_manual'] = 0

                    lista_manuales.append(obj_manual)
                    objeto['lista_manuales'] = lista_manuales

                    objeto['update_lectura'] = 0
                    objeto['update_cobros_mensuales'] = 0
                    objeto['update_cobros_manuales'] = 0
                    objeto['add_remove_cobro_manual'] = 1

                    lista_dep.append(objeto)

            else:
                # departamentos seleccionados
                div_dep = departamentos_ids.split(';')

                for dep in div_dep:
                    objeto = {}
                    objeto['departamento_id'] = apps.get_model('departamentos', 'Departamentos').objects.get(departamento_id=int(dep), status_id=self.status_activo)
                    objeto['periodo'] = periodo
                    objeto['user'] = user
                    objeto['lectura'] = 0
                    objeto['metros2'] = 0
                    objeto['costo_expensas'] = 0
                    objeto['total_expensas'] = 0
                    objeto['costo_m3'] = 0
                    objeto['consumo'] = 0

                    # cobros mensuales
                    lista_mensuales = []
                    objeto['lista_mensuales'] = lista_mensuales

                    # cobros manuales
                    lista_manuales = []
                    obj_manual = {}
                    obj_manual['cobro_manual_id'] = cobro_manual
                    obj_manual['monto_bs'] = validate_number_decimal('monto bs', request.POST['monto_bs_manual_' + str(dep)])
                    if 'chk_cobro_manual_'+dep in request.POST.keys():
                        obj_manual['add_cobro_manual'] = 1
                        obj_manual['remove_cobro_manual'] = 0
                    else:
                        obj_manual['add_cobro_manual'] = 0
                        obj_manual['remove_cobro_manual'] = 1

                    lista_manuales.append(obj_manual)
                    objeto['lista_manuales'] = lista_manuales

                    objeto['update_lectura'] = 0
                    objeto['update_cobros_mensuales'] = 0
                    objeto['update_cobros_manuales'] = 0
                    objeto['add_remove_cobro_manual'] = 1

                    lista_dep.append(objeto)

            # guardamos en la base de datos
            lectura_controller = LecturasController()
            if lectura_controller.save_data_db(lista_dep, user):
                self.error_operation = ''
                return True
            else:
                self.error_operation = 'Error lista controller, ' + lectura_controller.error_operation
                return False

        except Exception as ex:
            self.error_operation = 'Error de datos, ' + str(ex)
            return False
