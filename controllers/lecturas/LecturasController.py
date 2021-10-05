from controllers.DefaultValues import DefaultValues
from django.conf import settings
from django.apps import apps

from django.db import transaction
from lecturas.models import Lecturas

from utils.validators import validate_string, validate_number_int, validate_number_decimal
from utils.permissions import current_periodo, get_system_settings, previous_periodo, show_periodo

# conexion directa a la base de datos
from django.db import connection


class LecturasController(DefaultValues):
    def __init__(self):
        DefaultValues.__init__(self)
        self.modelo_name = 'Lecturas'
        self.modelo_id = 'lectura_id'
        self.modelo_app = 'lecturas'
        self.modulo_id = settings.MOD_LECTURAS

        # variables de session
        self.modulo_session = "lecturas"
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

        self.variables_filtros_defecto['search_apellidos'] = ''
        self.variables_filtros_defecto['search_nombres'] = ''
        self.variables_filtros_defecto['search_departamento'] = ''
        self.variables_filtros_defecto['search_bloque'] = '0'
        self.variables_filtros_defecto['search_piso'] = '0'
        self.variables_filtros_defecto['search_periodo'] = current_periodo()

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
        costo_m3 = settings_sistema['costo_m3']
        expensas_monto_m2 = settings_sistema['expensas_monto_m2']
        costo_minimo = settings_sistema['costo_minimo']
        unidad_minima_m3 = settings_sistema['unidad_minima_m3']
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
        # lista de cobros mensuales y manuales
        lista_cobros_mensuales = apps.get_model('configuraciones', 'CobrosMensuales').objects.filter(status_id=self.status_activo).order_by('cobro_mensual')
        lista_cobros_mensuales_periodo = apps.get_model('lecturas', 'CobrosMensualesPeriodos').objects.filter(status_id=self.status_activo, periodo=self.variables_filtros_values['search_periodo'])

        lista_cobros_manuales = apps.get_model('configuraciones', 'CobrosManuales').objects.filter(status_id=self.status_activo).order_by('cobro_manual')

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

                # datos de la lectura
                sql_lectura = "SELECT l.lectura_id, l.lectura, l.costo_m3, l.consumo, l.fecha_cobro, l.status_id, l.metros2, l.costo_expensas_m2, total_expensas "
                sql_lectura += f"FROM lecturas l WHERE l.departamento_id='{row[0]}' AND l.periodo='{objeto['periodo']}' "
                # print(sql_lectura)
                with connection.cursor() as cursor_lectura:
                    cursor_lectura.execute(sql_lectura)
                    row_lectura = cursor_lectura.fetchone()
                    if row_lectura:
                        objeto['lectura_id'] = row_lectura[0]
                        objeto['lectura'] = row_lectura[1]
                        objeto['costo_m3'] = row_lectura[2]
                        objeto['consumo'] = row_lectura[3]
                        objeto['lectura_metros2'] = row_lectura[6]
                        objeto['costo_expensas_m2'] = row_lectura[7]
                        objeto['total_expensas'] = row_lectura[8]
                    else:
                        objeto['lectura_id'] = 0
                        objeto['lectura'] = 0
                        objeto['costo_m3'] = costo_m3
                        objeto['consumo'] = 0
                        objeto['lectura_metros2'] = objeto['metros2']
                        objeto['costo_expensas_m2'] = expensas_monto_m2
                        objeto['total_expensas'] = round(expensas_monto_m2 * objeto['metros2'], 2)
                # sumamos el cobro
                total_cobro = total_cobro + objeto['consumo'] + objeto['total_expensas']
                #print('total cobro: ', total_cobro, ' ..consumo: ', objeto['consumo'], ' ...expensas: ', objeto['total_expensas'])

                # lectura anterior
                periodo_ant = previous_periodo(objeto['periodo'])
                sql_lectura = "SELECT l.lectura_id, l.lectura "
                sql_lectura += f"FROM lecturas l WHERE l.departamento_id='{row[0]}' AND l.periodo='{periodo_ant}' "
                with connection.cursor() as cursor_lectura:
                    cursor_lectura.execute(sql_lectura)
                    row_lectura = cursor_lectura.fetchone()
                    if row_lectura:
                        objeto['lectura_anterior'] = row_lectura[1]
                    else:
                        objeto['lectura_anterior'] = 0

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

                # cobros mensuales
                sql_cobro = "SELECT ccm.cobro_cobro_mensual_id, ccm.monto_bs, cm.cobro_mensual_id, cm.cobro_mensual "
                sql_cobro += f"FROM cobros_cobros_mensuales ccm, cobros_mensuales cm WHERE ccm.cobro_mensual_id=cm.cobro_mensual_id AND ccm.departamento_id='{objeto['departamento_id']}' AND ccm.periodo='{objeto['periodo']}' "
                sql_cobro += "ORDER BY cm.cobro_mensual "
                #print('sql cobro: ', sql_cobro)
                lista_cmen = []
                total_mensuales = 0
                with connection.cursor() as cursor_cobro:
                    cursor_cobro.execute(sql_cobro)
                    rows_cobro = cursor_cobro.fetchall()

                    # segun la lista de cobros mensuales
                    for co_me in lista_cobros_mensuales:
                        existe = 0
                        objeto_cobro = {}
                        for row_cobro in rows_cobro:
                            if co_me.cobro_mensual_id == row_cobro[2]:
                                existe = 1
                                objeto_cobro['cobro_cobro_mensual_id'] = row_cobro[0]
                                objeto_cobro['monto_bs'] = row_cobro[1]
                                total_mensuales = total_mensuales + objeto_cobro['monto_bs']
                        if existe == 0:
                            # buscamos en la lista del periodo
                            existe_periodo = 0
                            for cmp in lista_cobros_mensuales_periodo:
                                if cmp.cobro_mensual_id == co_me:
                                    existe_periodo = 1
                                    objeto_cobro['cobro_cobro_mensual_id'] = 0
                                    objeto_cobro['monto_bs'] = cmp.monto_bs

                            if existe_periodo == 0:
                                objeto_cobro['cobro_cobro_mensual_id'] = 0
                                objeto_cobro['monto_bs'] = co_me.monto_cobrar

                        # datos
                        objeto_cobro['cobro_mensual_id'] = co_me.cobro_mensual_id
                        objeto_cobro['cobro_mensual'] = co_me.cobro_mensual
                        lista_cmen.append(objeto_cobro)

                objeto['lista_cobros_mensuales'] = lista_cmen
                objeto['total_mensuales'] = total_mensuales
                #print('lista mensuales..: ', lista_cmen)
                # sumamos el cobro
                total_cobro = total_cobro + objeto['total_mensuales']

                # cobros manuales
                sql_cobro = "SELECT ccm.cobro_cobro_manual_id, ccm.monto_bs, cm.cobro_manual_id, cm.cobro_manual "
                sql_cobro += f"FROM cobros_cobros_manuales ccm, cobros_manuales cm WHERE ccm.cobro_manual_id=cm.cobro_manual_id AND ccm.departamento_id='{objeto['departamento_id']}' AND ccm.periodo='{objeto['periodo']}' "
                sql_cobro += "ORDER BY cm.cobro_manual "
                lista_cman = []
                total_manuales = 0
                with connection.cursor() as cursor_cobro:
                    cursor_cobro.execute(sql_cobro)
                    rows_cobro = cursor_cobro.fetchall()

                    # segun la lista de cobros manuales
                    for co_ma in lista_cobros_manuales:
                        existe = 0
                        objeto_cobro = {}
                        for row_cobro in rows_cobro:
                            if co_ma.cobro_manual_id == row_cobro[2]:
                                existe = 1
                                objeto_cobro['cobro_cobro_manual_id'] = row_cobro[0]
                                objeto_cobro['monto_bs'] = row_cobro[1]
                                total_manuales = total_manuales + objeto_cobro['monto_bs']
                        if existe == 0:
                            objeto_cobro['cobro_cobro_manual_id'] = 0
                            if co_ma.monto_porcentaje == 'monto':
                                objeto_cobro['monto_bs'] = co_ma.monto_bs
                            else:
                                # buscamos el monto del cobro mensual asignado
                                aux_valor = 0
                                for aux_cm in lista_cobros_mensuales:
                                    if aux_cm.cobro_mensual_id == co_ma.cobro_mensual_id:
                                        aux_valor = aux_cm.monto_cobrar
                                if co_ma.porcentaje > 0:
                                    objeto_cobro['monto_bs'] = round((co_ma.porcentaje / 100) * aux_valor, 2)
                                else:
                                    objeto_cobro['monto_bs'] = 0

                        # datos
                        objeto_cobro['monto_porcentaje'] = co_ma.monto_porcentaje
                        objeto_cobro['porcentaje'] = co_ma.porcentaje
                        objeto_cobro['cobro_mensual_id'] = co_ma.cobro_mensual_id

                        objeto_cobro['cobro_manual_id'] = co_ma.cobro_manual_id
                        objeto_cobro['cobro_manual'] = co_ma.cobro_manual
                        lista_cman.append(objeto_cobro)

                    # for row_cobro in rows_cobro:
                    #     objeto_cobro = {}
                    #     objeto_cobro['cobro_cobro_manual_id'] = row_cobro[0]
                    #     objeto_cobro['monto_bs'] = row_cobro[1]
                    #     objeto_cobro['cobro_manual_id'] = row_cobro[2]
                    #     objeto_cobro['cobro_manual'] = row_cobro[3]
                    #     lista_cman.append(objeto_cobro)
                    #     total_manuales = total_manuales + objeto_cobro['monto_bs']

                #print('lista manuales..: ', lista_cman)
                objeto['lista_cobros_manuales'] = lista_cman
                objeto['total_manuales'] = total_manuales
                # sumamos el cobro
                total_cobro = total_cobro + objeto['total_manuales']

                objeto['monto_bs'] = total_cobro
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

    def cantidad_cobros_mensuales(self, periodo):
        """cantidad de cobros mensuales en estado cobrado"""
        sql = f"SELECT COUNT(*) AS cant FROM cobros_cobros_mensuales WHERE status_id='{self.cobrado}' and periodo='{periodo}' "
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchone()
            cantidad = row[0]

        return cantidad

    def save_cobros_mensuales_periodo(self, periodo, user):
        """cobros mensuales para todos los departamentos"""
        try:
            cant_cm_periodo = apps.get_model('lecturas', 'CobrosMensualesPeriodos').objects.filter(
                status_id=self.status_activo, periodo=periodo
            ).count()
            if cant_cm_periodo == 0:
                self.error_operation = "No existen registros de cobros mensuales para el periodo"
                return False

            user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=user)
            # lista de departamentos
            lista_dep = apps.get_model('departamentos', 'Departamentos').objects.filter(status_id=self.status_activo)
            cm_periodo = apps.get_model('lecturas', 'CobrosMensualesPeriodos').objects.filter(status_id=self.status_activo, periodo=periodo)

            for dep in lista_dep:
                # borramos sus cobros mensuales para el periodo y dpto
                # si es que no tiene cobros "estado cobrado" para esa fecha
                cant_cobro_realizado = apps.get_model('lecturas', 'CobrosCobrosMensuales').objects.filter(periodo=periodo, departamento_id=dep, status_id=self.status_cobrado).count()
                if cant_cobro_realizado == 0:
                    # vaciamos
                    apps.get_model('lecturas', 'CobrosCobrosMensuales').objects.filter(periodo=periodo, departamento_id=dep).delete()
                    for cmp in cm_periodo:
                        cmp_add = apps.get_model('lecturas', 'CobrosCobrosMensuales').objects.create(
                            monto_bs=cmp.monto_bs, periodo=periodo, observacion='', cobro_mensual_id=cmp.cobro_mensual_id, departamento_id=dep,
                            status_id=self.status_activo, user_perfil_id=user_perfil,
                            created_at='now', updated_at='now'
                        )
                        cmp_add.save()

            self.error_operation = ''
            return True

        except Exception as ex:
            print('error cmp: ', str(ex))
            self.error_operation = 'Error al guardar los cobros mensuales para los departamentos ' + str(ex)
            return False

    def save_data(self, periodo, request, user):
        # verificamos el periodo
        cant_cm_periodo = apps.get_model('lecturas', 'CobrosMensualesPeriodos').objects.filter(
            status_id=self.status_activo, periodo=periodo
        ).count()
        if cant_cm_periodo == 0:
            self.error_operation = "No existen registros de cobros mensuales para el periodo"
            return False

        cobros_mensuales = apps.get_model('configuraciones', 'CobrosMensuales').objects.filter(status_id=self.status_activo).order_by('cobro_mensual')
        cobros_manuales = apps.get_model('configuraciones', 'CobrosManuales').objects.filter(status_id=self.status_activo).order_by('cobro_manual')

        # armamos los datos
        try:
            #departamentos_ids = self.lista_departamentos_ids
            departamentos_ids = request.session['departamentos_ids']
            #print('request: ', request)
            div_dep = departamentos_ids.split(';')
            lista_dep = []
            for dep in div_dep:
                if not 'lectura_' + dep in request.POST.keys():
                    self.error_operation = 'Debe llenar los datos de lecturas'
                    return False

                lectura = request.POST['lectura_'+dep].strip()
                if lectura == '':
                    self.error_operation = 'Debe llenar los datos de lecturas'
                    return False

                objeto = {}
                objeto['departamento_id'] = apps.get_model('departamentos', 'Departamentos').objects.get(departamento_id=int(dep), status_id=self.status_activo)
                objeto['periodo'] = periodo
                objeto['user'] = user
                objeto['lectura'] = validate_number_decimal('lectura', lectura)
                objeto['metros2'] = validate_number_decimal('metros2', request.POST['metros2_'+dep])
                objeto['costo_expensas'] = validate_number_decimal('costo expensas', request.POST['costo_expensas_'+dep])
                objeto['total_expensas'] = validate_number_decimal('total expensas', request.POST['total_expensas_'+dep])
                objeto['costo_m3'] = validate_number_decimal('costo m3', request.POST['costo_m3_'+dep])
                objeto['consumo'] = validate_number_decimal('consumo', request.POST['consumo_'+dep])

                # cobros mensuales
                lista_mensuales = []
                for co_men in cobros_mensuales:
                    if 'me_chk_' + dep + '_' + str(co_men.cobro_mensual_id) in request.POST.keys():
                        val_men = validate_number_decimal('monto mensual', request.POST['me_val_'+dep+'_'+str(co_men.cobro_mensual_id)])
                        obj_mensual = {}
                        obj_mensual['cobro_mensual_id'] = co_men
                        obj_mensual['monto_bs'] = val_men
                        lista_mensuales.append(obj_mensual)
                objeto['lista_mensuales'] = lista_mensuales

                # cobros manuales
                lista_manuales = []
                for co_man in cobros_manuales:
                    if 'ma_chk_' + dep + '_' + str(co_man.cobro_manual_id) in request.POST.keys():
                        val_man = validate_number_decimal('monto manual', request.POST['ma_val_'+dep+'_'+str(co_man.cobro_manual_id)])
                        obj_manual = {}
                        obj_manual['cobro_manual_id'] = co_man
                        obj_manual['monto_bs'] = val_man
                        obj_manual['add_cobro_manual'] = 1
                        obj_manual['remove_cobro_manual'] = 0
                        lista_manuales.append(obj_manual)
                objeto['lista_manuales'] = lista_manuales

                objeto['update_lectura'] = 1
                objeto['update_cobros_mensuales'] = 1
                objeto['update_cobros_manuales'] = 1
                objeto['add_remove_cobro_manual'] = 0

                lista_dep.append(objeto)

            # guardamos en la base de datos
            if self.save_data_db(lista_dep, user):
                self.error_operation = ''
                return True
            else:
                return False

        except Exception as ex:
            self.error_operation = 'Error de datos, ' + str(ex)
            return False

    def save_data_db(self, lista_dep, user):
        """guardamos en la base de datos"""
        try:
            with transaction.atomic():
                user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=user)
                #cobros_mensuales = apps.get_model('configuraciones', 'CobrosMensuales').objects.filter(status_id=self.status_activo).order_by('cobro_mensual')
                #cobros_manuales = apps.get_model('configuraciones', 'CobrosManuales').objects.filter(status_id=self.status_activo).order_by('cobro_manual')

                # recorremos los departamentos
                for dep in lista_dep:
                    periodo = dep['periodo']
                    departamento = dep['departamento_id']
                    # verificamos su registro en la tabla cobros y lecturas
                    cant_cobro = apps.get_model('lecturas', 'Cobros').objects.filter(departamento_id=departamento, periodo=periodo).count()
                    if cant_cobro > 0:
                        cobro = apps.get_model('lecturas', 'Cobros').objects.get(departamento_id=departamento, periodo=periodo)
                    else:
                        cobro = apps.get_model('lecturas', 'Cobros').objects.create(
                            monto_bs=0, periodo=periodo, departamento_id=departamento, status_id=self.status_activo,
                            created_at='now', updated_at='now',
                            user_perfil_id=user_perfil
                        )
                        cobro.save()

                    total_cobro = 0
                    if cobro.status_id == self.status_cobrado:
                        # estados cobrados no se modifican
                        continue

                    # eliminamos los detalles del cobro
                    detalles = apps.get_model('lecturas', 'CobrosDetalles').objects.filter(cobro_id=cobro)
                    if detalles:
                        detalles.delete()

                    if dep['update_lectura'] == 1:
                        cant_lectura = apps.get_model('lecturas', 'Lecturas').objects.filter(departamento_id=departamento, periodo=periodo).count()
                        if cant_lectura > 0:
                            lectura = apps.get_model('lecturas', 'Lecturas').objects.get(departamento_id=departamento, periodo=periodo)
                            lectura.lectura = dep['lectura']
                            lectura.costo_m3 = dep['costo_m3']
                            lectura.consumo = dep['consumo']
                            lectura.metros2 = dep['metros2']
                            lectura.costo_expensas_m2 = dep['costo_expensas']
                            lectura.total_expensas = dep['total_expensas']
                            lectura.updated_at = 'now'
                            lectura.save()
                        else:
                            lectura = apps.get_model('lecturas', 'Lecturas').objects.create(
                                periodo=periodo, lectura=dep['lectura'], costo_m3=dep['costo_m3'], consumo=dep['consumo'], metros2=dep['metros2'],
                                costo_expensas_m2=dep['costo_expensas'], total_expensas=dep['total_expensas'],
                                created_at='now', updated_at='now',
                                departamento_id=departamento, status_id=self.status_activo, user_perfil_id=user_perfil
                            )
                            lectura.save()
                    else:
                        lectura = apps.get_model('lecturas', 'Lecturas').objects.get(departamento_id=departamento, periodo=periodo)

                    # total cobro
                    total_cobro = total_cobro + lectura.consumo + lectura.total_expensas

                    # insertamos el detalle
                    detalle_add = apps.get_model('lecturas', 'CobrosDetalles').objects.create(
                        lectura_id=lectura.lectura_id, cobro_cobro_mensual_id=0, cobro_cobro_manual_id=0, monto_bs=lectura.consumo + lectura.total_expensas, periodo=periodo,
                        detalle='lectura mes: ' + show_periodo(periodo), observacion='',
                        created_at='now', updated_at='now', cobro_id=cobro
                    )
                    detalle_add.save()

                    # cobros mensuales
                    if dep['update_cobros_mensuales'] == 1:
                        # borramos todos los cobros mensuales para el periodo y departamento
                        cm_delete = apps.get_model('lecturas', 'CobrosCobrosMensuales').objects.filter(periodo=periodo, departamento_id=departamento)
                        cm_delete.delete()
                        # segun los cobros mensuales
                        for co_men in dep['lista_mensuales']:
                            ccm_add = apps.get_model('lecturas', 'CobrosCobrosMensuales').objects.create(
                                monto_bs=co_men['monto_bs'], cobro_mensual_id=co_men['cobro_mensual_id'], periodo=periodo,
                                departamento_id=departamento, status_id=self.status_activo, user_perfil_id=user_perfil,
                                created_at='now', updated_at='now'
                            )
                            ccm_add.save()

                    # insertamos el detalle de cobros mensuales
                    # recuperamos los cobros mensuales
                    lista_ccm = apps.get_model('lecturas', 'CobrosCobrosMensuales').objects.filter(departamento_id=departamento, periodo=periodo)
                    for ccm in lista_ccm:
                        detalle_add = apps.get_model('lecturas', 'CobrosDetalles').objects.create(
                            lectura_id=0, cobro_cobro_mensual_id=ccm.cobro_cobro_mensual_id, cobro_cobro_manual_id=0, monto_bs=ccm.monto_bs, periodo=periodo,
                            detalle=ccm.cobro_mensual_id.cobro_mensual + ' : ' + show_periodo(periodo), observacion='',
                            created_at='now', updated_at='now', cobro_id=cobro
                        )
                        detalle_add.save()
                        total_cobro = total_cobro + ccm.monto_bs

                    # cobros manuales
                    if dep['update_cobros_manuales'] == 1:
                        # borramos todos los cobros manuales para el periodo y departamento
                        cm_delete = apps.get_model('lecturas', 'CobrosCobrosManuales').objects.filter(periodo=periodo, departamento_id=departamento)
                        cm_delete.delete()
                        # segun los cobros manuales
                        for co_man in dep['lista_manuales']:
                            ccm_add = apps.get_model('lecturas', 'CobrosCobrosManuales').objects.create(
                                monto_bs=co_man['monto_bs'], cobro_manual_id=co_man['cobro_manual_id'], periodo=periodo,
                                departamento_id=departamento, status_id=self.status_activo, user_perfil_id=user_perfil,
                                created_at='now', updated_at='now'
                            )
                            ccm_add.save()

                    else:
                        if dep['add_remove_cobro_manual'] == 1:
                            # solo actualizamos o añadimos los manuales
                            for co_man in dep['lista_manuales']:
                                if co_man['add_cobro_manual'] == 1:
                                    # verificamos si ya existe
                                    cant_co_man = apps.get_model('lecturas', 'CobrosCobrosManuales').objects.filter(periodo=periodo, departamento_id=departamento, cobro_manual_id=co_man['cobro_manual_id']).count()
                                    if cant_co_man == 0:
                                        # creamos
                                        co_man_db = apps.get_model('lecturas', 'CobrosCobrosManuales').objects.create(
                                            periodo=periodo, departamento_id=departamento, cobro_manual_id=co_man['cobro_manual_id'],
                                            status_id=self.status_activo, user_perfil_id=user_perfil,
                                            monto_bs=co_man['monto_bs'], created_at='now', updated_at='now'
                                        )
                                        co_man_db.save()
                                    else:
                                        # actualizamos
                                        co_man_db = apps.get_model('lecturas', 'CobrosCobrosManuales').objects.get(
                                            periodo=periodo, departamento_id=departamento, cobro_manual_id=co_man['cobro_manual_id']
                                        )
                                        co_man_db.monto_bs = co_man['monto_bs']
                                        co_man_db.updated_at = 'now'
                                        co_man_db.save()

                                if co_man['remove_cobro_manual'] == 1:
                                    cant_co_man = apps.get_model('lecturas', 'CobrosCobrosManuales').objects.filter(periodo=periodo, departamento_id=departamento, cobro_manual_id=co_man['cobro_manual_id']).count()
                                    if cant_co_man > 0:
                                        # eliminamos
                                        co_man_db = apps.get_model('lecturas', 'CobrosCobrosManuales').objects.get(
                                            periodo=periodo, departamento_id=departamento, cobro_manual_id=co_man['cobro_manual_id']
                                        )
                                        co_man_db.delete()

                    # insertamos el detalle
                    lista_ccm = apps.get_model('lecturas', 'CobrosCobrosManuales').objects.filter(departamento_id=departamento, periodo=periodo)
                    for ccm in lista_ccm:
                        detalle_add = apps.get_model('lecturas', 'CobrosDetalles').objects.create(
                            lectura_id=0, cobro_cobro_mensual_id=0, cobro_cobro_manual_id=ccm.cobro_cobro_manual_id, monto_bs=ccm.monto_bs, periodo=periodo,
                            detalle=ccm.cobro_manual_id.cobro_manual + ' : ' + show_periodo(periodo), observacion='',
                            created_at='now', updated_at='now', cobro_id=cobro
                        )
                        detalle_add.save()
                        total_cobro = total_cobro + ccm.monto_bs

                    # actualizamos el total
                    cobro.monto_bs = total_cobro
                    cobro.save()

            self.error_operation = ''
            return True

        except Exception as ex:
            self.error_operation = 'error de argumentos, ' + str(ex)
            print('ERROR lecturas save, '+str(ex))
            return False
