from utils.dates_functions import add_months_datetime, get_calendario, get_date_to_db
from controllers.DefaultValues import DefaultValues
from django.conf import settings
from django.apps import apps

from django.db import transaction
from calendario.models import Calendario

from utils.validators import validate_string, validate_number_int
from utils.permissions import current_date, fecha_periodo
from datetime import datetime

# conexion directa a la base de datos
from django.db import connection


class CalendarioController(DefaultValues):
    def __init__(self):
        DefaultValues.__init__(self)
        self.modelo_name = 'Calendario'
        self.modelo_id = 'calendario_id'
        self.modelo_app = 'calendario'
        self.modulo_id = settings.MOD_CALENDARIO

        # variables de session
        self.modulo_session = "calendario"
        self.columnas.append('departamento')

        self.variables_filtros.append('search_departamento')
        self.variables_filtros.append('search_periodo')
        self.variables_filtros.append('search_actividad')

        self.variables_filtros_defecto['search_departamento'] = ''
        self.variables_filtros_defecto['search_actividad'] = '0'

        anio = '20' + str(datetime.now().year) if len(str(datetime.now().year)) == 2 else str(datetime.now().year)
        mes = '0' + str(datetime.now().month) if len(str(datetime.now().month)) == 1 else str(datetime.now().month)
        self.variables_filtros_defecto['search_periodo'] = anio + mes

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

    def index(self, request):
        DefaultValues.index(self, request)
        self.filtros_modulo.clear()
        #sql_add = f"AND c.status_id in ('{self.activo}','{self.inactivo}', '{self.anulado}') "
        sql_add = f"AND c.status_id in ('{self.activo}','{self.inactivo}') "
        # status
        self.filtros_modulo['status_id_id__in'] = [self.activo, self.inactivo]

        user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=request.user)

        # actividad
        actividad_search = self.variables_filtros_values['search_actividad'].strip()
        if actividad_search != '0':
            sql_add = f"AND c.actividad_id='{actividad_search}' "

        # periodo del calendario
        calendario = []
        # if self.variables_filtros_values['search_periodo'].strip() != "":
        periodo = self.variables_filtros_values['search_periodo'].strip()
        anio = periodo[0:4]
        mes = periodo[4:6]
        calendario = get_calendario(mes, anio)

        fecha_ini = fecha_periodo(periodo, '01')
        fecha_ini = get_date_to_db(fecha=fecha_ini, formato_ori='yyyy-mm-dd', formato='yyyy-mm-dd HH:ii:ss', tiempo='00:00:00')
        fecha_fin = add_months_datetime(fecha=fecha_ini, formato_ori='yyyy-mm-dd HH:ii:ss', meses=1, formato='yyyy-mm-dd HH:ii:ss')
        sql_add += f"AND c.fecha_actividad_ini>='{fecha_ini}' AND c.fecha_actividad_ini<'{fecha_fin}' "
        #print('sql_add: ', sql_add)

        # departamento
        depa = self.variables_filtros_values['search_departamento'].strip()
        if depa != "":
            sql_add += f"AND d.departamento LIKE '%{depa}%' "

        # lista de todos los usuarios
        users_perfiles_lista = apps.get_model('permisos', 'UsersPerfiles').objects.filter(status_id=self.status_activo)

        # lista del calendario
        sql = "SELECT c.calendario_id, c.fecha_actividad_ini, c.fecha_actividad_fin, c.fecha_reserva, c.user_perfil_id_reserva, "
        sql += "c.fecha_confirma, c.user_perfil_id_confirma, c.fecha_anula, c.user_perfil_id_anula, c.motivo_anula, "
        sql += "c.detalle, c.observacion, c.status_id, a.actividad, a.codigo, a.color_hex, d.departamento, d.codigo AS departamento_codigo, "
        sql += "d.departamento_id, a.color_txt "
        sql += "FROM calendario c INNER JOIN actividades a ON c.actividad_id=a.actividad_id "
        sql += "LEFT JOIN departamentos d ON c.departamento_id=d.departamento_id "
        sql += "WHERE c.calendario_id>0 "
        sql += sql_add

        sql += "ORDER BY a.actividad, c.fecha_actividad_ini, c.fecha_reserva "
        #print('sql: ', sql)

        retorno = []
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()

            # recorremos todos los dias del calendario
            semana_add = []

            for semana in calendario:
                for dia_semana in semana:
                    objeto_dia = {}
                    objeto_dia['posicion'] = dia_semana['posicion']
                    objeto_dia['dia'] = dia_semana['dia']
                    objeto_dia['nombre'] = dia_semana['nombre']
                    objeto_dia['existe'] = dia_semana['existe']

                    if objeto_dia['existe'] == 1:
                        #print('dia: ', objeto_dia['dia'])
                        # dia valido, vemos las actividades
                        para_dia = str(objeto_dia['dia'])
                        if len(para_dia) == 1:
                            para_dia = '0' + para_dia

                        fecha_dia = anio + '-' + mes + '-' + para_dia
                        lista_actividades = []
                        #print('fecha dia: ', fecha_dia)

                        for row in rows:
                            aux_fecha = get_date_to_db(fecha=row[1], formato_ori='yyyy-mm-dd HH:ii:ss', formato='yyyy-mm-dd HH:ii:ss')  # fecha actividad ini
                            div_aux = aux_fecha.split(' ')
                            fecha_calendario = div_aux[0]
                            hora_calendario = div_aux[1]
                            #print('hora calendario: ', hora_calendario)
                            # fecha fin calendario
                            aux_fecha = get_date_to_db(fecha=row[2], formato_ori='yyyy-mm-dd HH:ii:ss', formato='yyyy-mm-dd HH:ii:ss')  # fecha actividad ini
                            div_aux = aux_fecha.split(' ')
                            fecha_calendario_fin = div_aux[0]
                            hora_calendario_fin = div_aux[1]
                            #print('fecha calendario: ', fecha_calendario, ' ..fecha dia: ', fecha_dia)

                            if fecha_dia == fecha_calendario:
                                # actividad para el dia
                                actividad = {}
                                actividad['calendario_id'] = row[0]
                                actividad['hora_ini'] = hora_calendario[0:5]
                                actividad['hora_fin'] = hora_calendario_fin[0:5]
                                actividad['fecha_reserva'] = row[3]
                                actividad['user_perfil_id_reserva'] = row[4]
                                actividad['fecha_confirma'] = row[5]
                                actividad['user_perfil_id_confirma'] = row[6]
                                actividad['fecha_anula'] = row[7]
                                actividad['user_perfil_id_anula'] = row[8]
                                actividad['motivo_anula'] = row[9]
                                actividad['detalle'] = row[10]
                                actividad['observacion'] = row[11]
                                actividad['status_id'] = row[12]
                                actividad['actividad'] = row[13]
                                actividad['actividad_codigo'] = row[14]
                                actividad['color_hex'] = row[15]
                                actividad['departamento'] = row[16]
                                actividad['departamento_codigo'] = row[17]
                                actividad['departamento_id'] = row[18]
                                actividad['color_txt'] = row[19]

                                # user id del departamento
                                user_id_dpto = 0
                                for us_perfil in users_perfiles_lista:
                                    if actividad['departamento'] == us_perfil.user_id.username:
                                        user_id_dpto = us_perfil.user_id.id
                                        break
                                actividad['user_id_dpto'] = user_id_dpto

                                #print('actividad: ', actividad)
                                lista_actividades.append(actividad)

                        objeto_dia['lista_actividades'] = lista_actividades
                        semana_add.append(objeto_dia)
                    else:
                        objeto_dia['lista_actividades'] = []
                        semana_add.append(objeto_dia)

                # termina el for de semana
                retorno.append(semana_add)
                semana_add = []
            # termina el for calendario
            # retorno.append(semana_add)

        # return calendario
        #print('retorno: ', retorno)
        return retorno

    def registrar_actividad(self, periodo, request, user):
        # armamos los datos
        try:
            hora_ini = validate_string('hora inicio', request.POST['hora_ini'])
            minuto_ini = validate_string('minutos inicio', request.POST['minuto_ini'])
            hora_fin = validate_string('hora fin', request.POST['hora_fin'])
            minuto_fin = validate_string('minutos fin', request.POST['minuto_fin'])
            actividad_id = validate_number_int('actividad', request.POST['actividad'])
            aux_dia = validate_number_int('dia', request.POST['dia'])
            #departamento_id = validate_number_int('departamento', request.POST['departamento'], len_zero='yes')
            # registro directo por un usuario que no es departamento
            departamento_id = 0
            detalle = validate_string('detalle', request.POST['detalle'], len_zero='yes')

            dia = str(aux_dia)
            if len(dia) == 1:
                dia = "0" + dia

            actividad = apps.get_model('calendario', 'Actividades').objects.get(pk=actividad_id)
            # if departamento_id > 0:
            #     departamento = apps.get_model('departamentos', 'Departamento').objects.get(pk=departamento_id)

            user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=user)

            fecha_inicio = periodo[0:4] + '-' + periodo[4:6] + '-' + dia + ' ' + hora_ini + ':' + minuto_ini + ':00'
            fecha_fin = periodo[0:4] + '-' + periodo[4:6] + '-' + dia + ' ' + hora_fin + ':' + minuto_fin + ':00'
            # verificamos que no exista actividad confirmada en este rango
            sql = f"SELECT COUNT(*) AS cant FROM calendario WHERE fecha_actividad_ini>='{fecha_inicio}' AND fecha_actividad_ini<'{fecha_fin}' AND actividad_id='{actividad_id}' AND status_id='{self.activo}' "
            cant = 0
            with connection.cursor() as cursor:
                cursor.execute(sql)
                row = cursor.fetchone()
                cant = row[0]
                if cant == 0:
                    sql = f"SELECT COUNT(*) AS cant FROM calendario WHERE fecha_actividad_fin>'{fecha_inicio}' AND fecha_actividad_fin<='{fecha_fin}' AND actividad_id='{actividad_id}' AND status_id='{self.activo}' "
                    with connection.cursor() as cursor2:
                        cursor2.execute(sql)
                        row2 = cursor2.fetchone()
                        cant = row2[0]

            if cant > 0:
                self.error_operation = "Ya existen actividades en este rango de fecha para la actividad : " + actividad.actividad
                return False

            # guardamos en la base de datos
            calendario_add = apps.get_model('calendario', 'Calendario').objects.create(
                fecha_actividad_ini=fecha_inicio, fecha_actividad_fin=fecha_fin, departamento_id=departamento_id,
                user_perfil_id_reserva=user_perfil.user_perfil_id, fecha_reserva='now', detalle=detalle,
                user_perfil_id_confirma=user_perfil.user_perfil_id, fecha_confirma='now',
                actividad_id=actividad, status_id=self.status_activo,
                created_at='now', updated_at='now'
            )
            calendario_add.save()

            self.error_operation = ''
            return True

        except Exception as ex:
            self.error_operation = 'Error de datos, ' + str(ex)
            return False

    def solicitar_actividad(self, periodo, request, user):
        # armamos los datos
        try:
            hora_ini = validate_string('hora inicio', request.POST['hora_ini'])
            minuto_ini = validate_string('minutos inicio', request.POST['minuto_ini'])
            hora_fin = validate_string('hora fin', request.POST['hora_fin'])
            minuto_fin = validate_string('minutos fin', request.POST['minuto_fin'])
            actividad_id = validate_number_int('actividad', request.POST['actividad'])
            aux_dia = validate_number_int('dia', request.POST['dia'])
            detalle = validate_string('detalle', request.POST['detalle'], len_zero='yes')

            user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=user)
            departamento = apps.get_model('departamentos', 'Departamentos').objects.get(departamento=user_perfil.user_id.username)
            departamento_id = departamento.departamento_id
            actividad = apps.get_model('calendario', 'Actividades').objects.get(pk=actividad_id)

            dia = str(aux_dia)
            if len(dia) == 1:
                dia = "0" + dia

            fecha_inicio = periodo[0:4] + '-' + periodo[4:6] + '-' + dia + ' ' + hora_ini + ':' + minuto_ini + ':00'
            fecha_fin = periodo[0:4] + '-' + periodo[4:6] + '-' + dia + ' ' + hora_fin + ':' + minuto_fin + ':00'
            # verificamos que no exista actividad confirmada en este rango
            sql = f"SELECT COUNT(*) AS cant FROM calendario WHERE fecha_actividad_ini>='{fecha_inicio}' AND fecha_actividad_ini<'{fecha_fin}' AND actividad_id='{actividad_id}' AND status_id='{self.activo}' "
            cant = 0
            with connection.cursor() as cursor:
                cursor.execute(sql)
                row = cursor.fetchone()
                cant = row[0]
                if cant == 0:
                    sql = f"SELECT COUNT(*) AS cant FROM calendario WHERE fecha_actividad_fin>'{fecha_inicio}' AND fecha_actividad_fin<='{fecha_fin}' AND actividad_id='{actividad_id}' AND status_id='{self.activo}' "
                    with connection.cursor() as cursor2:
                        cursor2.execute(sql)
                        row2 = cursor2.fetchone()
                        cant = row2[0]

            if cant > 0:
                self.error_operation = "Ya existen actividades en este rango de fecha para la actividad : " + actividad.actividad
                return False

            # guardamos en la base de datos
            calendario_add = apps.get_model('calendario', 'Calendario').objects.create(
                fecha_actividad_ini=fecha_inicio, fecha_actividad_fin=fecha_fin, departamento_id=departamento_id,
                user_perfil_id_reserva=user_perfil.user_perfil_id, fecha_reserva='now', detalle=detalle,
                actividad_id=actividad, status_id=self.status_inactivo,
                created_at='now', updated_at='now'
            )
            calendario_add.save()

            self.error_operation = ''
            return True

        except Exception as ex:
            self.error_operation = 'Error de datos, ' + str(ex)
            return False

    def confirmar_actividad(self, id, user):
        # armamos los datos
        try:
            calendario_id = validate_number_int('calendario id', id)
            calendario = apps.get_model('calendario', 'Calendario').objects.get(pk=calendario_id)
            fecha_inicio = get_date_to_db(fecha=calendario.fecha_actividad_ini, formato_ori='yyyy-mm-dd HH:ii:ss', formato='yyyy-mm-dd HH:ii:ss')
            fecha_fin = get_date_to_db(fecha=calendario.fecha_actividad_fin, formato_ori='yyyy-mm-dd HH:ii:ss', formato='yyyy-mm-dd HH:ii:ss')

            user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=user)

            # verificamos que no exista actividad confirmada en este rango
            sql = f"SELECT COUNT(*) AS cant FROM calendario WHERE fecha_actividad_ini>='{fecha_inicio}' AND fecha_actividad_ini<'{fecha_fin}' AND actividad_id='{calendario.actividad_id.actividad_id}' AND status_id='{self.activo}' "
            cant = 0
            with connection.cursor() as cursor:
                cursor.execute(sql)
                row = cursor.fetchone()
                cant = row[0]
                if cant == 0:
                    sql = f"SELECT COUNT(*) AS cant FROM calendario WHERE fecha_actividad_fin>'{fecha_inicio}' AND fecha_actividad_fin<='{fecha_fin}' AND actividad_id='{calendario.actividad_id.actividad_id}' AND status_id='{self.activo}' "
                    with connection.cursor() as cursor2:
                        cursor2.execute(sql)
                        row2 = cursor2.fetchone()
                        cant = row2[0]

            if cant > 0:
                self.error_operation = "Ya existen actividades en este rango de fecha para la actividad : " + calendario.actividad_id.actividad
                return False

            # actualizamos en la base de datos
            calendario.user_perfil_id_confirma = user_perfil.user_perfil_id
            calendario.fecha_confirma = 'now'
            calendario.updated_at = 'now'
            calendario.status_id = self.status_activo
            calendario.save()

            self.error_operation = ''
            return True

        except Exception as ex:
            self.error_operation = 'Error de datos, ' + str(ex)
            return False

    def anular_actividad(self, id, user):
        # armamos los datos
        try:
            calendario_id = validate_number_int('calendario id', id)
            calendario = apps.get_model('calendario', 'Calendario').objects.get(pk=calendario_id)
            fecha_inicio = get_date_to_db(fecha=calendario.fecha_actividad_ini, formato_ori='yyyy-mm-dd HH:ii:ss', formato='yyyy-mm-dd HH:ii:ss')
            fecha_fin = get_date_to_db(fecha=calendario.fecha_actividad_fin, formato_ori='yyyy-mm-dd HH:ii:ss', formato='yyyy-mm-dd HH:ii:ss')

            user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=user)
            #self.error_operation = 'asdfa'
            # return False

            # verificamos si es usuario departamento, solo puede eliminar sus actividades
            if user_perfil.perfil_id.perfil_id == settings.PERFIL_DEPARTAMENTO:
                departamento = apps.get_model('departamentos', 'Departamentos').objects.get(pk=calendario.departamento_id)
                if user_perfil.user_id.username != departamento.departamento:
                    self.error_operation = 'Solo puede eliminar sus actividades'
                    return False

            # actualizamos en la base de datos
            calendario.user_perfil_id_anula = user_perfil.user_perfil_id
            calendario.fecha_anula = 'now'
            calendario.deleted_at = 'now'
            calendario.status_id = self.status_anulado
            calendario.motivo_anula = ''
            calendario.save()

            self.error_operation = ''
            return True

        except Exception as ex:
            self.error_operation = 'Error de datos, ' + str(ex)
            return False
