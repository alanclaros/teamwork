from utils.dates_functions import get_date_to_db
from django.apps.registry import Apps
from controllers.DefaultValues import DefaultValues
from django.conf import settings
from django.apps import apps

from django.db import transaction
from lecturas.models import Cobros, Lecturas

from utils.validators import validate_string, validate_number_int, validate_number_decimal
from utils.permissions import current_date, current_periodo, get_system_settings, next_periodo, previous_periodo, show_periodo

# conexion directa a la base de datos
from django.db import connection

from controllers.cajas.CajasIngresosController import CajasIngresosController
from controllers.cajas.CajasController import CajasController


class CobrosController(DefaultValues):
    def __init__(self):
        DefaultValues.__init__(self)
        self.modelo_name = 'Lecturas'
        self.modelo_id = 'lectura_id'
        self.modelo_app = 'lecturas'
        self.modulo_id = settings.MOD_COBROS

        # variables de session
        self.modulo_session = "cobros"
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

        self.variables_filtros_defecto['search_apellidos'] = ''
        self.variables_filtros_defecto['search_nombres'] = ''
        self.variables_filtros_defecto['search_departamento'] = ''
        self.variables_filtros_defecto['search_bloque'] = '0'
        self.variables_filtros_defecto['search_piso'] = '0'

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
        sql = "SELECT d.departamento_id, d.propietario_apellidos, d.propietario_nombres, d.departamento, d.codigo, d.metros2, b.bloque, p.piso, d.status_id "
        sql_count = "SELECT COUNT(*) AS cant "

        sql += "FROM departamentos d, bloques b, pisos p "
        sql += "WHERE d.bloque_id=b.bloque_id AND d.piso_id=p.piso_id "
        sql += sql_add

        sql_count += "FROM departamentos d, bloques b, pisos p "
        sql_count += "WHERE d.bloque_id=b.bloque_id AND d.piso_id=p.piso_id "
        sql_count += sql_add

        sql += "ORDER BY " + orden_enviar + " "

        # users perfiles lista
        users_perfil_lista = apps.get_model('permisos', 'UsersPerfiles').objects.filter(status_id=self.status_activo)

        # cantidad total de registros
        cantidad_registros = 0
        with connection.cursor() as cursor:
            cursor.execute(sql_count)
            row = cursor.fetchone()
            cantidad_registros = row[0]

        settings_sistema = get_system_settings()
        # costo_m3 = settings_sistema['costo_m3']
        # expensas_monto_m2 = settings_sistema['expensas_monto_m2']
        # costo_minimo = settings_sistema['costo_minimo']
        # unidad_minima_m3 = settings_sistema['unidad_minima_m3']
        cant_per_page = settings_sistema['cant_lista_cobranza']
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
                objeto['bloque'] = row[6]
                objeto['piso'] = row[7]
                objeto['status_id'] = row[8]

                # usuario del departamento
                user_id_dpto = 0
                for user_p in users_perfil_lista:
                    if user_p.user_id.username == objeto['departamento']:
                        user_id_dpto = user_p.user_id.id
                        break
                objeto['user_dpto_id'] = user_id_dpto

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

    def lista_deudas(self, departamento_id):
        """lista de las deudas del departamento"""
        try:
            departamento = apps.get_model('departamentos', 'Departamentos').objects.get(pk=int(departamento_id), status_id=self.status_activo)
            fecha_actual = current_date()
            periodo_actual = fecha_actual[0:4] + fecha_actual[5:7]

            # cobros pendientes
            lista_cobros = []
            cant_cobros = 5

            # recuperamos deuda o cobro del perido actual
            cobro_actual = apps.get_model('lecturas', 'Cobros').objects.get(departamento_id=departamento, periodo=periodo_actual)
            if cobro_actual:
                objeto = {}
                objeto['cobro_id'] = cobro_actual.cobro_id
                objeto['status_id'] = cobro_actual.status_id.status_id
                objeto['fecha_cobro'] = cobro_actual.fecha_cobro
                objeto['monto_bs'] = cobro_actual.monto_bs
                objeto['periodo'] = cobro_actual.periodo
                objeto['detalle'] = 'Cobranza ' + show_periodo(cobro_actual.periodo)
                lista_cobros.insert(0, objeto)
                cant_cobros = cant_cobros - 1

            # recuperamos las deudas pendientes, menores al periodo actual
            #ultimo_periodo = ''
            filtro_pendientes = {}
            filtro_pendientes['status_id'] = self.status_activo
            filtro_pendientes['departamento_id'] = departamento
            filtro_pendientes['periodo__lt'] = periodo_actual
            cobros_pendientes = apps.get_model('lecturas', 'Cobros').objects.filter(**filtro_pendientes).order_by('-periodo')
            for cobro in cobros_pendientes:
                objeto = {}
                objeto['cobro_id'] = cobro.cobro_id
                objeto['status_id'] = cobro.status_id.status_id
                objeto['fecha_cobro'] = cobro.fecha_cobro
                objeto['monto_bs'] = cobro.monto_bs
                objeto['periodo'] = cobro.periodo
                objeto['detalle'] = 'Cobranza ' + show_periodo(cobro.periodo)

                #ultimo_periodo = cobro.periodo
                lista_cobros.insert(0, objeto)
                cant_cobros = cant_cobros - 1

            # verificamos el ultimo periodo cobrado, menor al periodo actual
            ultimo_periodo = ''
            sql = f"SELECT MAX(periodo) AS maximo FROM cobros WHERE departamento_id='{departamento.departamento_id}' AND status_id='{self.cobrado}' AND periodo<'{periodo_actual}' "
            with connection.cursor() as cursor:
                cursor.execute(sql)
                row = cursor.fetchone()
                if row:
                    if row[0]:
                        ultimo_periodo = row[0]

            # completamos la lista
            bande_existe = 1
            while cant_cobros > 0 and bande_existe == 1 and ultimo_periodo != '':
                # # en caso de que pague adelantado algun mes y deje pendientes meses anteriores
                # sql = f"SELECT MAX(periodo) AS maximo FROM cobros WHERE departamento_id='{departamento.departamento_id}' AND status_id='{self.cobrado}' "
                # ultimo_periodo_cobrado = ''
                # with connection.cursor() as cursor:
                #     cursor.execute(sql)
                #     row = cursor.fetchone()
                #     if row:
                #         if row[0]:
                #             ultimo_periodo_cobrado = row[0]

                # if ultimo_periodo_cobrado != '':
                #     asd = 'asdf'

                # print('entra...')
                # recuperamos cobros realizados
                periodo_ant = ultimo_periodo
                cant_ant = apps.get_model('lecturas', 'Cobros').objects.filter(status_id=self.status_cobrado, departamento_id=departamento, periodo=periodo_ant).count()
                if cant_ant == 0:
                    # no existen mas periodos atras
                    bande_existe = 0
                else:
                    cobro_ant = apps.get_model('lecturas', 'Cobros').objects.get(status_id=self.status_cobrado, departamento_id=departamento, periodo=periodo_ant)
                    objeto = {}
                    objeto['cobro_id'] = cobro_ant.cobro_id
                    objeto['status_id'] = cobro_ant.status_id.status_id
                    objeto['fecha_cobro'] = cobro_ant.fecha_cobro
                    objeto['monto_bs'] = cobro_ant.monto_bs
                    objeto['periodo'] = cobro_ant.periodo
                    objeto['detalle'] = 'Cobranza ' + show_periodo(cobro_ant.periodo)
                    lista_cobros.insert(0, objeto)

                    cant_cobros = cant_cobros - 1
                    ultimo_periodo = previous_periodo(periodo_ant)

            # ordenamos la lista de periodos de menor a mayor
            if len(lista_cobros) > 0:
                nueva_lista = []
                for lcobro in lista_cobros:
                    posicion = 0
                    periodo_aux = lcobro['periodo']
                    for nuevo in nueva_lista:
                        if periodo_aux > nuevo['periodo']:
                            posicion = posicion+1

                    nueva_lista.insert(posicion, lcobro)

                lista_cobros = nueva_lista

            self.error_operation = ''
            return lista_cobros

        except Exception as ex:
            print('Error al recuperar datos periodo: ', str(ex))
            self.error_operation = 'Error al recuperar datos, ' + str(ex)
            return False

    def lista_detalles(self, cobro_id):
        """lista de los detalles por el periodo"""
        try:
            cobro = apps.get_model('lecturas', 'Cobros').objects.get(pk=int(cobro_id))
            # cobros pendientes
            lista_detalles = []
            cobros_detalles = apps.get_model('lecturas', 'CobrosDetalles').objects.filter(cobro_id=cobro).order_by('-lectura_id', 'cobro_cobro_mensual_id', 'cobro_cobro_manual_id')
            for detalle in cobros_detalles:
                objeto = {}
                objeto['detalle_id'] = detalle.cobro_detalle_id
                objeto['status_id'] = cobro.status_id.status_id
                objeto['detalle'] = detalle.detalle
                objeto['monto_bs'] = detalle.monto_bs

                lista_detalles.append(objeto)

            self.error_operation = ''
            return lista_detalles

        except Exception as ex:
            print('Error al recuperar datos periodo: ', str(ex))
            self.error_operation = 'Error al recuperar datos, ' + str(ex)
            return False

    def save_data(self, request, user):
        # armamos los datos
        try:
            cobros_cobrar = validate_string('lista cobros', request.POST['cobros_cobrar'])
            div_ids = cobros_cobrar.split(';')
            lista_ids_cobrar = []
            for id_cobrar in div_ids:
                lista_ids_cobrar.append(id_cobrar)

            # guardamos en la base de datos
            if self.save_data_db(lista_ids_cobrar, user):
                self.error_operation = ''
                return True
            else:
                return False

        except Exception as ex:
            self.error_operation = 'Error de datos, ' + str(ex)
            return False

    def save_data_db(self, lista_cobros, user):
        """guardamos en la base de datos"""
        try:
            user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=user)
            punto = apps.get_model('configuraciones', 'Puntos').objects.get(pk=user_perfil.punto_id)
            caja_controller = CajasController()
            ci_controller = CajasIngresosController()

            caja_lista = caja_controller.cash_active(current_date(), user, formato_ori='yyyy-mm-dd')

            if not caja_lista:
                self.error_operation = 'Debe tener una caja activa'
                return False

            # caja del usuario
            caja_usuario = caja_lista[0]

            with transaction.atomic():
                sid_ini = transaction.savepoint()

                # actualizamos el cobro, detalles, lecturas, cobros_cobros_mensuales, cobros_cobros_mensuales_detalles
                for cobro_id in lista_cobros:
                    fecha_cobro = get_date_to_db(fecha=current_date(), formato_ori='yyyy-mm-dd', formato='yyyy-mm-dd HH:ii:ss')

                    cobro = apps.get_model('lecturas', 'Cobros').objects.get(pk=int(cobro_id))
                    cobro.status_id = self.status_cobrado
                    cobro.fecha_cobro = fecha_cobro
                    cobro.user_perfil_id_cobro = user_perfil.user_perfil_id
                    cobro.punto_id = user_perfil.punto_id
                    cobro.caja_id = caja_usuario.caja_id
                    cobro.updated_at = 'now'
                    cobro.save()

                    sid_cobro = transaction.savepoint()

                    # detalles
                    cobros_detalles = apps.get_model('lecturas', 'CobrosDetalles').objects.filter(cobro_id=cobro)
                    for detalle in cobros_detalles:
                        if detalle.lectura_id > 0:
                            # actualizamos la lectura
                            lectura = apps.get_model('lecturas', 'Lecturas').objects.get(pk=detalle.lectura_id)
                            lectura.status_id = self.status_cobrado
                            lectura.fecha_cobro = fecha_cobro
                            lectura.user_perfil_id_cobro = user_perfil.user_perfil_id
                            lectura.punto_id = user_perfil.punto_id
                            lectura.caja_id = caja_usuario.caja_id
                            lectura.updated_at = 'now'
                            lectura.save()

                        if detalle.cobro_cobro_mensual_id > 0:
                            # actualizamos el cobro mensual
                            cobro_cobro_mensual = apps.get_model('lecturas', 'CobrosCobrosMensuales').objects.get(pk=detalle.cobro_cobro_mensual_id)
                            cobro_cobro_mensual.status_id = self.status_cobrado
                            cobro_cobro_mensual.fecha_cobro = fecha_cobro
                            cobro_cobro_mensual.user_perfil_id_cobro = user_perfil.user_perfil_id
                            cobro_cobro_mensual.punto_id = user_perfil.punto_id
                            cobro_cobro_mensual.caja_id = caja_usuario.caja_id
                            cobro_cobro_mensual.updated_at = 'now'
                            cobro_cobro_mensual.save()

                        if detalle.cobro_cobro_manual_id > 0:
                            # actualizamos el cobro manual
                            cobro_cobro_manual = apps.get_model('lecturas', 'CobrosCobrosManuales').objects.get(pk=detalle.cobro_cobro_manual_id)
                            cobro_cobro_manual.status_id = self.status_cobrado
                            cobro_cobro_manual.fecha_cobro = fecha_cobro
                            cobro_cobro_manual.user_perfil_id_cobro = user_perfil.user_perfil_id
                            cobro_cobro_manual.punto_id = user_perfil.punto_id
                            cobro_cobro_manual.caja_id = caja_usuario.caja_id
                            cobro_cobro_manual.updated_at = 'now'
                            cobro_cobro_manual.save()

                    sid_detalle = transaction.savepoint()

                    # ingreso a caja
                    datos_ingreso = {}
                    datos_ingreso['cobro_id'] = cobro.cobro_id
                    datos_ingreso['caja_id'] = caja_usuario
                    datos_ingreso['punto_id'] = punto
                    datos_ingreso['user_perfil_id'] = user_perfil
                    datos_ingreso['status_id'] = self.status_activo
                    datos_ingreso['fecha'] = fecha_cobro
                    datos_ingreso['concepto'] = 'Ingreso cobro: ' + str(cobro.cobro_id) + ", Dep : " + cobro.departamento_id.departamento + ", " + \
                        cobro.departamento_id.propietario_apellidos + " " + cobro.departamento_id.propietario_nombres
                    datos_ingreso['monto'] = cobro.monto_bs
                    datos_ingreso['created_at'] = 'now'
                    datos_ingreso['updated_at'] = 'now'

                    if ci_controller.add_db(**datos_ingreso):
                        sid_caja_ingreso = transaction.savepoint()
                    else:
                        transaction.savepoint_rollback(sid_detalle)
                        transaction.savepoint_rollback(sid_cobro)
                        transaction.savepoint_rollback(sid_ini)
                        self.error_operation = 'error al registrar el ingreso a caja'
                        return False

                transaction.savepoint_commit(sid_caja_ingreso)

            self.error_operation = ''
            return True

        except Exception as ex:
            self.error_operation = 'error de argumentos, ' + str(ex)
            print('ERROR cobros save, '+str(ex))
            return False

    def anular(self, request, user):
        # armamos los datos
        try:
            cobro_id = validate_number_int('cobro', request.POST['id_anula'])
            motivo_anula = validate_string('motivo anulacion', request.POST['motivo_anula'])
            datos_anulacion = {}
            datos_anulacion['cobro_id'] = cobro_id
            datos_anulacion['motivo_anula'] = motivo_anula

            # guardamos en la base de datos
            if self.anular_db(datos_anulacion, user):
                self.error_operation = ''
                return True
            else:
                return False

        except Exception as ex:
            self.error_operation = 'Error de datos, ' + str(ex)
            return False

    def anular_db(self, datos, user):
        try:
            cobro = apps.get_model('lecturas', 'Cobros').objects.get(pk=datos['cobro_id'])
            user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=user)
            motivo = datos['motivo_anula']
            #print('cobro..: ', cobro)

            with transaction.atomic():
                sid_ini = transaction.savepoint()

                # registramos los registros anulados
                cobro_anulado = apps.get_model('lecturas', 'CobrosAnulados').objects.create(
                    cobro_id=cobro.cobro_id, fecha_cobro=cobro.fecha_cobro, monto_bs=cobro.monto_bs,
                    periodo=cobro.periodo, observacion=cobro.observacion, user_perfil_id_cobro=cobro.user_perfil_id_cobro,
                    punto_id=cobro.punto_id, caja_id=cobro.caja_id, user_perfil_id_anula=user_perfil.user_perfil_id,
                    motivo_anula=motivo, departamento_id=cobro.departamento_id, status_id=self.status_anulado,
                    user_perfil_id=cobro.user_perfil_id,
                    created_at=cobro.created_at, updated_at=cobro.updated_at, deleted_at='now'
                )
                cobro_anulado.save()

                # detalles
                cobros_detalles = apps.get_model('lecturas', 'CobrosDetalles').objects.filter(cobro_id=cobro).order_by('cobro_detalle_id')
                for detalle in cobros_detalles:
                    cobro_detalle_anulado = apps.get_model('lecturas', 'CobrosDetallesAnulados').objects.create(
                        cobro_detalle_id=detalle.cobro_detalle_id, cobro_id=detalle.cobro_id.cobro_id,
                        lectura_id=detalle.lectura_id, cobro_cobro_mensual_id=detalle.cobro_cobro_mensual_id, cobro_cobro_manual_id=detalle.cobro_cobro_manual_id,
                        monto_bs=detalle.monto_bs, periodo=detalle.periodo, detalle=detalle.detalle,
                        observacion=detalle.observacion,
                        created_at=detalle.created_at, updated_at=detalle.updated_at, deleted_at='now'
                    )
                    cobro_detalle_anulado.save()

                    # verificamos lectura
                    if detalle.lectura_id > 0:
                        lectura = apps.get_model('lecturas', 'Lecturas').objects.get(pk=detalle.lectura_id)
                        lectura_anulado = apps.get_model('lecturas', 'LecturasAnulados').objects.create(
                            lectura_id=lectura.lectura_id,
                            periodo=lectura.periodo, lectura=lectura.lectura, costo_m3=lectura.costo_m3,
                            consumo=lectura.consumo, observacion=lectura.observacion, metros2=lectura.metros2,
                            costo_expensas_m2=lectura.costo_expensas_m2, total_expensas=lectura.total_expensas, fecha_cobro=lectura.fecha_cobro,
                            user_perfil_id_cobro=lectura.user_perfil_id_cobro, punto_id=lectura.punto_id, caja_id=lectura.caja_id,
                            user_perfil_id_anula=user_perfil.user_perfil_id, motivo_anula=motivo,
                            departamento_id=lectura.departamento_id, status_id=self.status_anulado, user_perfil_id=lectura.user_perfil_id,
                            created_at=lectura.created_at, updated_at=lectura.updated_at, deleted_at='now'
                        )
                        lectura_anulado.save()

                        lectura.status_id = self.status_activo
                        lectura.fecha_cobro = None
                        lectura.user_perfil_id_cobro = 0
                        lectura.punto_id = 0
                        lectura.caja_id = 0
                        lectura.updated_at = 'now'
                        lectura.save()

                    # cobro cobro mensual
                    if detalle.cobro_cobro_mensual_id > 0:
                        cc_mensual = apps.get_model('lecturas', 'CobrosCobrosMensuales').objects.get(pk=detalle.cobro_cobro_mensual_id)
                        cobro_cobro_mensual_anulado = apps.get_model('lecturas', 'CobrosCobrosMensualesAnulados').objects.create(
                            cobro_cobro_mensual_id=cc_mensual.cobro_cobro_mensual_id,
                            fecha_cobro=cc_mensual.fecha_cobro, monto_bs=cc_mensual.monto_bs, periodo=cc_mensual.periodo,
                            observacion=cc_mensual.observacion, user_perfil_id_cobro=cc_mensual.user_perfil_id_cobro, punto_id=cc_mensual.punto_id, caja_id=cc_mensual.caja_id,
                            cobro_mensual_id=cc_mensual.cobro_mensual_id, departamento_id=cc_mensual.departamento_id, status_id=self.status_anulado, user_perfil_id=cc_mensual.user_perfil_id,
                            user_perfil_id_anula=user_perfil.user_perfil_id, motivo_anula=motivo,
                            created_at=cc_mensual.created_at, updated_at=cc_mensual.updated_at, deleted_at='now'
                        )
                        cobro_cobro_mensual_anulado.save()

                        cc_mensual.status_id = self.status_activo
                        cc_mensual.fecha_cobro = None
                        cc_mensual.user_perfil_id_cobro = 0
                        cc_mensual.punto_id = 0
                        cc_mensual.caja_id = 0
                        cc_mensual.updated_at = 'now'
                        cc_mensual.save()

                    # cobro cobro manual
                    if detalle.cobro_cobro_manual_id > 0:
                        cc_manual = apps.get_model('lecturas', 'CobrosCobrosManuales').objects.get(pk=detalle.cobro_cobro_manual_id)
                        cobro_cobro_manual_anulado = apps.get_model('lecturas', 'CobrosCobrosManualesAnulados').objects.create(
                            cobro_cobro_manual_id=cc_manual.cobro_cobro_manual_id,
                            fecha_cobro=cc_manual.fecha_cobro, monto_bs=cc_manual.monto_bs, periodo=cc_manual.periodo,
                            observacion=cc_manual.observacion, user_perfil_id_cobro=cc_manual.user_perfil_id_cobro, punto_id=cc_manual.punto_id, caja_id=cc_manual.caja_id,
                            cobro_manual_id=cc_manual.cobro_manual_id, departamento_id=cc_manual.departamento_id, status_id=self.status_anulado, user_perfil_id=cc_manual.user_perfil_id,
                            user_perfil_id_anula=user_perfil.user_perfil_id, motivo_anula=motivo,
                            created_at=cc_manual.created_at, updated_at=cc_manual.updated_at, deleted_at='now'
                        )
                        cobro_cobro_manual_anulado.save()

                        cc_manual.status_id = self.status_activo
                        cc_manual.fecha_cobro = None
                        cc_manual.user_perfil_id_cobro = 0
                        cc_manual.punto_id = 0
                        cc_manual.caja_id = 0
                        cc_manual.updated_at = 'now'
                        cc_manual.save()

                # actualizamos el cobro
                cobro.status_id = self.status_activo
                cobro.fecha_cobro = None
                cobro.user_perfil_id_cobro = 0
                cobro.punto_id = 0
                cobro.caja_id = 0
                cobro.updated_at = 'now'
                cobro.save()

                sid_anulacion = transaction.savepoint()

                # anulamos el ingreso de caja
                caja_ingreso_cant = apps.get_model('cajas', 'CajasIngresos').objects.filter(cobro_id=cobro.cobro_id, status_id=self.status_activo).count()
                if caja_ingreso_cant == 0:
                    transaction.savepoint_rollback(sid_anulacion)
                    transaction.savepoint_rollback(sid_ini)
                    self.error_operation = 'No existe registro del ingreso'
                    return False

                caja_ingreso = apps.get_model('cajas', 'CajasIngresos').objects.get(cobro_id=cobro.cobro_id, status_id=self.status_activo)
                ci_controller = CajasIngresosController()

                campos_ingreso = {}
                campos_ingreso['status_id'] = self.status_anulado
                campos_ingreso['deleted_at'] = 'now'
                campos_ingreso['user_perfil_id_anula'] = user_perfil
                campos_ingreso['motivo_anula'] = motivo

                if ci_controller.delete_db(caja_ingreso.caja_ingreso_id, **campos_ingreso):
                    transaction.savepoint_commit(sid_anulacion)
                    self.error_operation = ''
                    return True
                else:
                    transaction.savepoint_rollback(sid_anulacion)
                    transaction.savepoint_rollback(sid_ini)
                    self.error_operation = 'Error al anular el ingreso'
                    return False

        except Exception as ex:
            self.error_operation = 'error de argumentos anular cobro, ' + str(ex)
            print('ERROR cobros anular, '+str(ex))
            return False

    def permission_print(self, user_perfil, module, id):
        """permission to print caja ingreso"""
        cobro = Cobros.objects.get(pk=id)

        puede_imprimir = False
        if user_perfil.perfil_id.perfil_id == settings.PERFIL_ADMIN:
            puede_imprimir = True

        if user_perfil.perfil_id.perfil_id == settings.PERFIL_SUPERVISOR:
            punto = apps.get_model('configuraciones', 'Puntos').objects.get(pk=user_perfil.punto_id)
            punto_cobro = apps.get_model('configuraciones', 'Puntos').objects.get(pk=cobro.punto_id)
            filtro_supervisor = {}
            filtro_supervisor['punto_id__sucursal_id'] = punto.sucursal_id
            filtro_supervisor['status_id'] = self.status_activo
            puntos_supervisor = apps.get_model('configuraciones', 'Puntos').objects.filter(**filtro_supervisor)

            for pu_su in puntos_supervisor:
                if pu_su.punto_id == punto:
                    puede_imprimir = True

        if user_perfil.perfil_id.perfil_id == settings.PERFIL_CAJERO:
            if cobro.punto_id == user_perfil.punto_id:
                puede_imprimir = True

        if not puede_imprimir:
            self.error_operation = "No tiene permiso para imprimir este recibo"

        return puede_imprimir
