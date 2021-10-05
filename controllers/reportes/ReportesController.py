from django.conf import settings
from django.apps import apps
from datetime import datetime
import random

from configuraciones.models import TiposMonedas, Puntos, Cajas, Sucursales
from cajas.models import CajasOperaciones
from permisos.models import UsersPerfiles

from status.models import Status

from decimal import Decimal

# modelo del usuario de django
from django.contrib.auth.models import User

from utils.permissions import get_permissions_user, show_periodo
from utils.dates_functions import get_date_to_db, get_date_show

from django.db import transaction

# clases
from controllers.DefaultValues import DefaultValues

# conexion directa a la base de datos
from django.db import connection


class ReportesController(DefaultValues):
    def __init__(self):
        DefaultValues.__init__(self)
        self.reporte_id = ''
        self.error_operation = ''
        self.modulo_session = 'reportes'

    def lista_cajas_sucursal(self, user):
        """lista de cajas por sucursal"""
        status_activo = Status.objects.get(pk=self.activo)
        user_perfil = UsersPerfiles.objects.get(user_id=user)
        punto = Puntos.objects.get(pk=user_perfil.punto_id)

        permisos = get_permissions_user(user, settings.MOD_REPORTES)

        filtros = {}
        # usuarios con permiso de superadmin
        if permisos.permiso:
            filtros['status_id'] = status_activo
            lista_cajas = Cajas.objects.select_related('punto_id').select_related('punto_id__sucursal_id').select_related('punto_id__sucursal_id__ciudad_id').filter(
                **filtros).order_by('punto_id__sucursal_id__ciudad_id__ciudad', 'punto_id__sucursal_id__sucursal', 'punto_id__punto', 'caja')

        else:
            # admin
            if user_perfil.perfil_id.perfil_id == self.perfil_admin:
                filtros['status_id'] = status_activo
                filtros['punto_id__sucursal_id'] = punto.sucursal_id
            # normal
            else:
                filtros['status_id'] = status_activo
                filtros['punto_id'] = punto

            lista_cajas = Cajas.objects.select_related('punto_id').filter(**filtros).order_by('punto_id__punto', 'caja')

        return lista_cajas

    def lista_almacenes_sucursal(self, user):
        """lista de almacenes por sucursal"""
        status_activo = Status.objects.get(pk=self.activo)
        user_perfil = UsersPerfiles.objects.get(user_id=user)
        punto = Puntos.objects.get(pk=user_perfil.punto_id)

        permisos = get_permissions_user(user, settings.MOD_REPORTES)

        filtros = {}
        # usuarios con permiso de superadmin
        if permisos.permiso:
            filtros['status_id'] = status_activo
            lista_almacenes = Almacenes.objects.select_related('sucursal_id').select_related('sucursal_id__ciudad_id').filter(
                **filtros).order_by('sucursal_id__ciudad_id__ciudad', 'sucursal_id__sucursal', 'almacen')

        else:
            # admin
            if user_perfil.perfil_id.perfil_id == self.perfil_admin:
                filtros['status_id'] = status_activo
                filtros['sucursal_id'] = punto.sucursal_id
                lista_almacenes = Almacenes.objects.select_related('sucursal_id').filter(**filtros).order_by('sucursal_id__sucursal', 'almacen')
            # normal
            else:
                # almacen del punto
                almacen_punto_lista = PuntosAlmacenes.objects.filter(punto_id=punto, status_id=status_activo).order_by('almacen_id')
                if almacen_punto_lista:
                    almacen_punto = almacen_punto_lista.first()
                    filtros['status_id'] = status_activo
                    filtros['sucursal_id'] = punto.sucursal_id
                    filtros['almacen_id'] = almacen_punto.almacen_id.almacen_id
                    lista_almacenes = Almacenes.objects.select_related('sucursal_id').filter(**filtros).order_by('sucursal_id__sucursal', 'almacen')
                else:
                    lista_almacenes = []

        return lista_almacenes

    def lista_puntos_sucursal(self, user):
        """lista de puntos por sucursal"""
        status_activo = Status.objects.get(pk=self.activo)
        user_perfil = UsersPerfiles.objects.get(user_id=user)
        punto = Puntos.objects.get(pk=user_perfil.punto_id)

        permisos = get_permissions_user(user, settings.MOD_REPORTES)

        filtros = {}
        # usuarios con permiso de superadmin
        if permisos.permiso:
            filtros['status_id'] = status_activo
            lista_puntos = Puntos.objects.select_related('sucursal_id').select_related('sucursal_id__ciudad_id').filter(
                **filtros).order_by('sucursal_id__ciudad_id__ciudad', 'sucursal_id__sucursal', 'punto')

        else:
            # admin
            if user_perfil.perfil_id.perfil_id == self.perfil_admin:
                filtros['status_id'] = status_activo
                filtros['sucursal_id'] = punto.sucursal_id
            # normal
            else:
                filtros['status_id'] = status_activo
                filtros['punto_id'] = punto.punto_id

            lista_puntos = Puntos.objects.select_related('sucursal_id').filter(**filtros).order_by('punto')

        return lista_puntos

    def verificar_permiso(self, usuario, caja_id=0):
        """verificando que solo vea reportes que le corresponden"""
        permisos = get_permissions_user(usuario, settings.MOD_REPORTES)
        status_activo = Status.objects.get(pk=self.activo)
        user_perfil = UsersPerfiles.objects.get(user_id=usuario)
        punto = Puntos.objects.get(pk=user_perfil.punto_id)

        if caja_id != 0:
            # control de cajas
            filtros = {}
            if permisos.permiso:
                filtros['status_id'] = status_activo
                lista_cajas = Cajas.objects.select_related('punto_id').select_related('punto_id__sucursal_id').select_related('punto_id__sucursal_id__ciudad_id').filter(
                    **filtros).order_by('punto_id__sucursal_id__ciudad_id__ciudad', 'punto_id__sucursal_id__sucursal', 'punto_id__punto', 'caja')
            else:
                if user_perfil.perfil_id.perfil_id == self.perfil_admin or user_perfil.perfil_id.perfil_id == self.perfil_supervisor:
                    filtros['status_id'] = status_activo
                    filtros['punto_id__sucursal_id'] = punto.sucursal_id
                else:
                    filtros['status_id'] = status_activo
                    filtros['punto_id'] = punto

                lista_cajas = Cajas.objects.select_related('punto_id').filter(**filtros).order_by('punto_id__punto', 'caja')

        for caja in lista_cajas:
            if caja.caja_id == caja_id:
                return True

        return False

    def datos_arqueo_caja(self, caja_id, fecha):
        """reporte de arqueo de caja"""
        try:
            # recuperamos todas las operaciones de caja, empezando inicio de caja
            caja = Cajas.objects.get(pk=caja_id)
            inicio_caja = 0
            fecha_inicio_caja = get_date_show(fecha=fecha, formato_ori='yyyy-mm-dd', formato='dd-MMM-yyyy HH:ii')

            cajaFecha = CajasOperaciones.objects.filter(caja_id=caja, fecha=fecha)

            if cajaFecha:
                CajaF = cajaFecha.first()
                inicio_caja = CajaF.monto_apertura
                fecha_inicio_caja = get_date_show(CajaF.created_at, formato='dd-MMM-yyyy HH:ii')

            # estado activo
            estado_activo = self.activo
            fecha_ini = get_date_to_db(fecha=fecha, formato_ori='yyyy-mm-dd', formato='yyyy-mm-dd HH:ii:ss', tiempo='00:00:00')
            fecha_fin = get_date_to_db(fecha=fecha, formato_ori='yyyy-mm-dd', formato='yyyy-mm-dd HH:ii:ss', tiempo='23:59:59')
            datos_arqueo = []
            datos_arqueo.append({'caja_operacion': 0, 'fecha': fecha_inicio_caja, 'concepto': 'apertura de caja', 'monto': inicio_caja})

            msql = f"SELECT ci.caja_ingreso_id AS caja_operacion, ci.fecha, ci.monto, ci.concepto, 'ingreso' AS tipo_operacion FROM cajas_ingresos ci WHERE ci.caja_id ={caja_id} AND ci.status_id={estado_activo} "
            msql += f"AND ci.fecha>='{fecha_ini}' AND ci.fecha<='{fecha_fin}' "
            msql += f"UNION SELECT ce.caja_egreso_id AS caja_operacion, ce.fecha, ce.monto, ce.concepto, 'egreso' AS tipo_operacion FROM cajas_egresos ce WHERE ce.caja_id ={caja_id} AND ce.status_id={estado_activo} "
            msql += f"AND ce.fecha>='{fecha_ini}' AND ce.fecha<='{fecha_fin}' "
            msql += f"ORDER BY fecha "

            with connection.cursor() as cursor:
                cursor.execute(msql)
                rows = cursor.fetchall()
                for row in rows:
                    # print('row: ', row[0])
                    if row[4] == 'ingreso':
                        datos_arqueo.append({'caja_operacion': row[0], 'fecha': get_date_show(fecha=row[1], formato='dd-MMM-yyyy HH:ii'), 'monto': row[2], 'concepto': row[3]})
                    else:
                        datos_arqueo.append({'caja_operacion': row[0], 'fecha': get_date_show(fecha=row[1], formato='dd-MMM-yyyy HH:ii'), 'monto': 0-row[2], 'concepto': row[3]})

            # print(datos_arqueo)
            return datos_arqueo

        except Exception as e:
            self.error_operation = "Error al recuperar datos"
            print('ERROR ' + str(e))
            return False

    def get_codigo_moneda(self, lista_tipos, tipo_moneda_id):
        """devuelve el codigo de la moneda"""
        for tipo in lista_tipos:
            if tipo.tipo_moneda_id == tipo_moneda_id:
                return tipo.codigo

        return ''

    def get_punto_txt(self, lista_puntos, punto_id):
        """devuelve el nombre del punto con su id"""
        for punto in lista_puntos:
            if punto.punto_id == punto_id:
                return punto.punto

        return ''

    def get_caja_txt(self, lista_cajas, caja_id):
        """devuelve el nombre de la caja con su id"""
        for caja in lista_cajas:
            if caja.caja_id == caja_id:
                return caja.caja

        return ''

    def get_ciudad_txt_from_sucursal(self, lista_sucursales, sucursal_id):
        for sucursal in lista_sucursales:
            if sucursal.sucursal_id == sucursal_id:
                return sucursal.ciudad_id.ciudad

        return ''

    def datos_ingreso_caja(self, usuario, ciudad_id, sucursal_id, caja_id, fecha_ini, fecha_fin, anulados):
        """datos de ingresos de caja"""
        try:
            tipos_monedas = TiposMonedas.objects.all()

            fecha1 = get_date_to_db(fecha=fecha_ini, formato_ori='dd-MMM-yyyy', formato='yyyy-mm-dd HH:ii:ss', tiempo='00:00:00')
            fecha2 = get_date_to_db(fecha=fecha_fin, formato_ori='dd-MMM-yyyy', formato='yyyy-mm-dd HH:ii:ss', tiempo='23:59:59')

            user_perfil = UsersPerfiles.objects.get(user_id=usuario)
            permisos = get_permissions_user(usuario, settings.MOD_REPORTES)
            punto = Puntos.objects.get(pk=user_perfil.punto_id)
            sucursal_id_user = punto.sucursal_id.sucursal_id

            sql_add = f"AND ci.fecha>='{fecha1}' AND ci.fecha<='{fecha2}' "

            if ciudad_id != 0:
                sql_add += f"AND ciu.ciudad_id='{ciudad_id}' "

            if sucursal_id != 0:
                sql_add += f"AND su.sucursal_id='{sucursal_id}' "

            if caja_id != 0:
                sql_add += f"AND ca.caja_id='{caja_id}' "

            # if anulados == 'si':
            #     sql_add += f"AND ci.status_id='{self.anulado}' "
            # else:
            #     sql_add += f"AND ci.status_id='{self.activo}' "

            if not permisos.permiso:
                if user_perfil.perfil_id.perfil_id == self.perfil_admin or user_perfil.perfil_id.perfil_id == self.perfil_supervisor:
                    sql_add += f"AND su.sucursal_id='{sucursal_id_user}' "
                else:
                    sql_add += f"AND pu.punto_id='{punto.punto_id}' "

            if anulados == 'si':
                # left join con usuarios para los anulados
                sql = "SELECT ciu.ciudad, su.sucursal, pu.punto, ca.caja, ci.caja_ingreso_id, ci.fecha, ci.concepto, ci.monto, ca.caja_id, ca.tipo_moneda_id, ci.user_perfil_id_anula, ci.motivo_anula "
                sql += "FROM cajas_ingresos ci INNER JOIN puntos pu ON ci.punto_id=pu.punto_id INNER JOIN cajas ca ON ci.caja_id=ca.caja_id INNER JOIN sucursales su ON pu.sucursal_id=su.sucursal_id "
                sql += "INNER JOIN ciudades ciu ON su.ciudad_id=ciu.ciudad_id "
                sql += f"WHERE ci.status_id='{self.anulado}' "
            else:
                # sql sin anulados
                sql = "SELECT ciu.ciudad, su.sucursal, pu.punto, ca.caja, ci.caja_ingreso_id, ci.fecha, ci.concepto, ci.monto, ca.caja_id, ca.tipo_moneda_id "
                sql += "FROM cajas_ingresos ci, puntos pu, cajas ca, sucursales su, ciudades ciu "
                sql += f"WHERE ci.status_id='{self.activo}' AND ci.punto_id=pu.punto_id AND ci.caja_id=ca.caja_id AND pu.sucursal_id=su.sucursal_id AND su.ciudad_id=ciu.ciudad_id "

            # toda la consulta
            sql += sql_add + " ORDER BY ciu.ciudad, su.sucursal, pu.punto, ci.caja_id, ci.fecha "
            # print(sql)

            datos_ingreso = []
            with connection.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    anulacion_dato = ''
                    if anulados == 'si':
                        anulacion_dato = ', ' + str(row[10]) + ', ' + str(row[11])
                    # print('row: ', row[0])
                    datos_ingreso.append({'ciudad': row[0],
                                          'sucursal': row[1],
                                          'punto': row[2],
                                          'caja': row[3],
                                          'operacion': row[4],
                                          'fecha': get_date_show(fecha=row[5], formato='dd-MMM-yyyy HH:ii'),
                                          'concepto': row[6] + anulacion_dato,
                                          'monto': row[7],
                                          'caja_id': row[8],
                                          'estado_txt': 'anulado' if anulados == 'si' else 'activo',
                                          'tipo_moneda': self.get_codigo_moneda(tipos_monedas, row[9])})

            # print('datos_ingreso...', datos_ingreso)
            return datos_ingreso

        except Exception as e:
            self.error_operation = "Error al recuperar datos"
            print('ERROR ' + str(e))
            return False

    def datos_egreso_caja(self, usuario, ciudad_id, sucursal_id, caja_id, fecha_ini, fecha_fin, anulados):
        """datos de egresos de caja"""
        try:
            tipos_monedas = TiposMonedas.objects.all()

            fecha1 = get_date_to_db(fecha=fecha_ini, formato_ori='dd-MMM-yyyy', formato='yyyy-mm-dd HH:ii:ss', tiempo='00:00:00')
            fecha2 = get_date_to_db(fecha=fecha_fin, formato_ori='dd-MMM-yyyy', formato='yyyy-mm-dd HH:ii:ss', tiempo='23:59:59')

            user_perfil = UsersPerfiles.objects.get(user_id=usuario)
            permisos = get_permissions_user(usuario, settings.MOD_REPORTES)
            punto = Puntos.objects.get(pk=user_perfil.punto_id)
            sucursal_id_user = punto.sucursal_id.sucursal_id

            sql_add = f"AND ci.fecha>='{fecha1}' AND ci.fecha<='{fecha2}' "

            if ciudad_id != 0:
                sql_add += f"AND ciu.ciudad_id='{ciudad_id}' "

            if sucursal_id != 0:
                sql_add += f"AND su.sucursal_id='{sucursal_id}' "

            if caja_id != 0:
                sql_add += f"AND ca.caja_id='{caja_id}' "

            # if anulados == 'si':
            #     sql_add += f"AND ci.status_id='{self.anulado}' "
            # else:
            #     sql_add += f"AND ci.status_id='{self.activo}' "

            if not permisos.permiso:
                if user_perfil.perfil_id.perfil_id == self.perfil_admin or user_perfil.perfil_id.perfil_id == self.perfil_supervisor:
                    sql_add += f"AND su.sucursal_id='{sucursal_id_user}' "
                else:
                    sql_add += f"AND pu.punto_id='{punto.punto_id}' "

            if anulados == 'si':
                # left join con usuarios para los anulados
                sql = "SELECT ciu.ciudad, su.sucursal, pu.punto, ca.caja, ci.caja_egreso_id, ci.fecha, ci.concepto, ci.monto, ca.caja_id, ca.tipo_moneda_id, ci.user_perfil_id_anula, ci.motivo_anula "
                sql += "FROM cajas_egresos ci INNER JOIN puntos pu ON ci.punto_id=pu.punto_id INNER JOIN cajas ca ON ci.caja_id=ca.caja_id INNER JOIN sucursales su ON pu.sucursal_id=su.sucursal_id "
                sql += "INNER JOIN ciudades ciu ON su.ciudad_id=ciu.ciudad_id "
                sql += f"WHERE ci.status_id='{self.anulado}' "
            else:
                # sql sin anulados
                sql = "SELECT ciu.ciudad, su.sucursal, pu.punto, ca.caja, ci.caja_egreso_id, ci.fecha, ci.concepto, ci.monto, ca.caja_id, ca.tipo_moneda_id "
                sql += "FROM cajas_egresos ci, puntos pu, cajas ca, sucursales su, ciudades ciu "
                sql += f"WHERE ci.status_id='{self.activo}' AND ci.punto_id=pu.punto_id AND ci.caja_id=ca.caja_id AND pu.sucursal_id=su.sucursal_id AND su.ciudad_id=ciu.ciudad_id "

            # sql = "SELECT ciu.ciudad, su.sucursal, pu.punto, ca.caja, ci.caja_egreso_id, ci.fecha, ci.concepto, ci.monto, ca.caja_id, ca.tipo_moneda_id "
            # sql += "FROM cajas_egresos ci, puntos pu, cajas ca, sucursales su, ciudades ciu "
            # sql += "WHERE ci.punto_id=pu.punto_id AND ci.caja_id=ca.caja_id AND pu.sucursal_id=su.sucursal_id AND su.ciudad_id=ciu.ciudad_id "

            # toda la consulta
            sql += sql_add + " ORDER BY ciu.ciudad, su.sucursal, pu.punto, ci.caja_id, ci.fecha "

            datos_egreso = []
            with connection.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    # print('row: ', row[0])
                    anulacion_dato = ''
                    if anulados == 'si':
                        anulacion_dato = ', ' + str(row[10]) + ', ' + str(row[11])

                    datos_egreso.append({'ciudad': row[0],
                                         'sucursal': row[1],
                                         'punto': row[2],
                                         'caja': row[3],
                                         'operacion': row[4],
                                         'fecha': get_date_show(fecha=row[5], formato='dd-MMM-yyyy HH:ii'),
                                         'concepto': row[6] + anulacion_dato,
                                         'monto': row[7],
                                         'caja_id': row[8],
                                         'estado_txt': 'anulado' if anulados == 'si' else 'activo',
                                         'tipo_moneda': self.get_codigo_moneda(tipos_monedas, row[9])})

            # print(datos_egreso)
            return datos_egreso

        except Exception as e:
            self.error_operation = "Error al recuperar datos"
            print('ERROR ' + str(e))
            return False

    def datos_movimientos_caja(self, usuario, ciudad_id, sucursal_id, caja_id, fecha_ini, fecha_fin, anulados):
        """datos de egresos de caja"""
        try:
            tipos_monedas = TiposMonedas.objects.all()

            fecha1 = get_date_to_db(fecha=fecha_ini, formato_ori='dd-MMM-yyyy', formato='yyyy-mm-dd HH:ii:ss', tiempo='00:00:00')
            fecha2 = get_date_to_db(fecha=fecha_fin, formato_ori='dd-MMM-yyyy', formato='yyyy-mm-dd HH:ii:ss', tiempo='23:59:59')

            user_perfil = UsersPerfiles.objects.get(user_id=usuario)
            permisos = get_permissions_user(usuario, settings.MOD_REPORTES)
            punto = Puntos.objects.get(pk=user_perfil.punto_id)
            sucursal_id_user = punto.sucursal_id.sucursal_id

            sql_add = f"AND cm.fecha>='{fecha1}' AND cm.fecha<='{fecha2}' "

            if ciudad_id != 0:
                sql_add += f"AND ciu.ciudad_id='{ciudad_id}' "

            if sucursal_id != 0:
                sql_add += f"AND su.sucursal_id='{sucursal_id}' "

            if caja_id != 0:
                sql_add += f"AND c1.caja_id='{caja_id}' "

            # if anulados == 'si':
            #     sql_add += f"AND ci.status_id='{self.anulado}' "
            # else:
            #     sql_add += f"AND ci.status_id='{self.activo}' "

            if not permisos.permiso:
                if user_perfil.perfil_id.perfil_id == self.perfil_admin or user_perfil.perfil_id.perfil_id == self.perfil_supervisor:
                    sql_add += f"AND su.sucursal_id='{sucursal_id_user}' "
                else:
                    sql_add += f"AND pu.punto_id='{punto.punto_id}' "

            if anulados == 'si':
                sql = 'SELECT ciu.ciudad, su.sucursal, cm.fecha, cm.concepto, cm.monto, c1.caja, p1.punto, c2.caja, p2.punto, cm.tipo_moneda_id, c1.caja_id, cm.status_id, cm.user_perfil_id_anula, cm.motivo_anula '
            else:
                sql = 'SELECT ciu.ciudad, su.sucursal, cm.fecha, cm.concepto, cm.monto, c1.caja, p1.punto, c2.caja, p2.punto, cm.tipo_moneda_id, c1.caja_id, cm.status_id '
            sql += 'FROM cajas_movimientos cm INNER JOIN cajas c1 ON cm.caja1_id=c1.caja_id '
            sql += 'INNER JOIN cajas c2 ON cm.caja2_id=c2.caja_id '
            sql += 'INNER JOIN puntos p1 ON c1.punto_id=p1.punto_id '
            sql += 'INNER JOIN puntos p2 ON c2.punto_id=p2.punto_id '
            sql += 'INNER JOIN sucursales su ON p1.sucursal_id=su.sucursal_id '
            sql += 'INNER JOIN ciudades ciu ON su.ciudad_id=ciu.ciudad_id '
            if anulados == 'si':
                sql += f"WHERE cm.status_id='{self.anulado}' "
            else:
                sql += f"WHERE cm.status_id IN('{self.movimiento_caja}','{self.movimiento_caja_recibe}') "

            # toda la consulta
            sql += sql_add + " ORDER BY ciu.ciudad, su.sucursal, p1.punto, c1.caja, cm.fecha "
            print(sql)

            datos_movimiento = []
            with connection.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    # print('row: ', row[0])
                    anulacion_dato = ''
                    if anulados == 'si':
                        anulacion_dato = ', ' + str(row[12]) + ', ' + str(row[13])

                    if row[11] == self.movimiento_caja_recibe:
                        datos_movimiento.append({'ciudad': row[0],
                                                 'sucursal': row[1],
                                                 'fecha': get_date_show(fecha=row[2], formato='dd-MMM-yyyy HH:ii'),
                                                 'concepto': row[3] + anulacion_dato,
                                                 'monto': row[4],
                                                 'caja1': row[5],
                                                 'punto1': row[6],
                                                 'caja2': row[7],
                                                 'punto2': row[8],
                                                 'estado_txt': 'anulado-recibe' if anulados == 'si' else 'recibe',
                                                 'tipo_moneda': self.get_codigo_moneda(tipos_monedas, row[9]),
                                                 'caja1_id': row[10]})
                    else:
                        datos_movimiento.append({'ciudad': row[0],
                                                 'sucursal': row[1],
                                                 'fecha': get_date_show(fecha=row[2], formato='dd-MMM-yyyy HH:ii'),
                                                 'concepto': row[3] + anulacion_dato,
                                                 'monto': row[4],
                                                 'caja1': row[5],
                                                 'punto1': row[6],
                                                 'caja2': '',
                                                 'punto2': '',
                                                 'estado_txt': 'anulado-envia' if anulados == 'si' else 'envia',
                                                 'tipo_moneda': self.get_codigo_moneda(tipos_monedas, row[9]),
                                                 'caja1_id': row[10]})

            # print(datos_movimiento)
            return datos_movimiento

        except Exception as e:
            self.error_operation = "Error al recuperar datos"
            print('ERROR ' + str(e))
            return False

    def datos_cobros(self, usuario, bloque_id, piso_id, caja_id, fecha_ini, fecha_fin, anulados):
        """datos de cobros"""
        try:
            fecha1 = get_date_to_db(fecha=fecha_ini, formato_ori='dd-MMM-yyyy', formato='yyyy-mm-dd HH:ii:ss', tiempo='00:00:00')
            fecha2 = get_date_to_db(fecha=fecha_fin, formato_ori='dd-MMM-yyyy', formato='yyyy-mm-dd HH:ii:ss', tiempo='23:59:59')

            lista_user_perfil = UsersPerfiles.objects.filter(status_id=self.status_activo)

            sql_add = f"AND c.fecha_cobro>='{fecha1}' AND c.fecha_cobro<='{fecha2}' "

            if bloque_id != 0:
                sql_add += f"AND b.bloque_id='{bloque_id}' "

            if piso_id != 0:
                sql_add += f"AND pi.piso_id='{piso_id}' "

            if caja_id != 0:
                sql_add += f"AND ca.caja_id='{caja_id}' "

            if anulados == 'si':
                sql = "SELECT c.monto_bs, c.periodo, c.fecha_cobro, ca.caja, b.bloque, pi.piso, d.departamento, c.user_perfil_id_anula, c.motivo_anula, ca.caja_id "
                sql += "FROM cobros_anulados c, cajas ca, departamentos d, bloques b, pisos pi "
                sql += "WHERE c.caja_id=ca.caja_id AND c.departamento_id=d.departamento_id AND d.bloque_id=b.bloque_id AND d.piso_id=pi.piso_id "
                sql_add += f"AND c.status_id='{self.anulado}' "
                sql += sql_add
            else:
                sql = "SELECT c.monto_bs, c.periodo, c.fecha_cobro, ca.caja, b.bloque, pi.piso, d.departamento, c.user_perfil_id_anula, c.motivo_anula, ca.caja_id "
                sql += "FROM cobros c, cajas ca, departamentos d, bloques b, pisos pi "
                sql += "WHERE c.caja_id=ca.caja_id AND c.departamento_id=d.departamento_id AND d.bloque_id=b.bloque_id AND d.piso_id=pi.piso_id "
                sql_add += f"AND c.status_id='{self.cobrado}' "
                sql += sql_add

            # toda la consulta
            sql += " ORDER BY ca.caja, c.fecha_cobro "
            # print(sql)

            datos_cobros = []
            with connection.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    anulacion_dato = ''
                    if anulados == 'si':
                        anulacion_dato = ""
                        for user_perfil in lista_user_perfil:
                            if user_perfil.user_perfil_id == row[7]:
                                anulacion_dato += user_perfil.user_id.username
                                break

                        anulacion_dato += ', ' + str(row[8])
                    # print('row: ', row[0])
                    datos_cobros.append({'caja': row[3],
                                         'monto_bs': row[0],
                                         'periodo': show_periodo(row[1]),
                                         'fecha_cobro': get_date_show(fecha=row[2], formato='dd-MMM-yyyy HH:ii'),
                                         'bloque': row[4],
                                         'piso': row[5],
                                         'departamento': row[6],
                                         'anulacion': anulacion_dato,
                                         'caja_id': row[9]
                                         })

            # print('datos_cobros...', datos_cobros)
            return datos_cobros

        except Exception as e:
            self.error_operation = "Error al recuperar datos"
            print('ERROR ' + str(e))
            return False

    def datos_cobros_mensuales(self, usuario, bloque_id, piso_id, caja_id, fecha_ini, fecha_fin, anulados, cobro_mensual_id):
        """datos de cobros"""
        try:
            fecha1 = get_date_to_db(fecha=fecha_ini, formato_ori='dd-MMM-yyyy', formato='yyyy-mm-dd HH:ii:ss', tiempo='00:00:00')
            fecha2 = get_date_to_db(fecha=fecha_fin, formato_ori='dd-MMM-yyyy', formato='yyyy-mm-dd HH:ii:ss', tiempo='23:59:59')

            lista_user_perfil = UsersPerfiles.objects.filter(status_id=self.status_activo)

            sql_add = f"AND c.fecha_cobro>='{fecha1}' AND c.fecha_cobro<='{fecha2}' "

            if bloque_id != 0:
                sql_add += f"AND b.bloque_id='{bloque_id}' "

            if piso_id != 0:
                sql_add += f"AND pi.piso_id='{piso_id}' "

            if caja_id != 0:
                sql_add += f"AND ca.caja_id='{caja_id}' "

            if cobro_mensual_id != 0:
                sql_add += f"AND cm.cobro_mensual_id='{cobro_mensual_id}' "

            if anulados == 'si':
                sql = "SELECT c.monto_bs, c.periodo, c.fecha_cobro, ca.caja, b.bloque, pi.piso, d.departamento, c.user_perfil_id_anula, c.motivo_anula, ca.caja_id, cm.cobro_mensual "
                sql += "FROM cobros_cobros_mensuales_anulados c, cobros_mensuales cm, cajas ca, departamentos d, bloques b, pisos pi "
                sql += "WHERE c.cobro_mensual_id=cm.cobro_mensual_id AND c.caja_id=ca.caja_id AND c.departamento_id=d.departamento_id AND d.bloque_id=b.bloque_id AND d.piso_id=pi.piso_id "
                sql_add += f"AND c.status_id='{self.anulado}' "
                sql += sql_add
            else:
                sql = "SELECT c.monto_bs, c.periodo, c.fecha_cobro, ca.caja, b.bloque, pi.piso, d.departamento, c.user_perfil_id_anula, c.motivo_anula, ca.caja_id, cm.cobro_mensual "
                sql += "FROM cobros_cobros_mensuales c, cobros_mensuales cm, cajas ca, departamentos d, bloques b, pisos pi "
                sql += "WHERE c.cobro_mensual_id=cm.cobro_mensual_id AND c.caja_id=ca.caja_id AND c.departamento_id=d.departamento_id AND d.bloque_id=b.bloque_id AND d.piso_id=pi.piso_id "
                sql_add += f"AND c.status_id='{self.cobrado}' "
                sql += sql_add

            # toda la consulta
            sql += " ORDER BY ca.caja, c.fecha_cobro, cm.cobro_mensual "
            # print(sql)

            datos_cobros = []
            with connection.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    anulacion_dato = ''
                    if anulados == 'si':
                        anulacion_dato = ""
                        for user_perfil in lista_user_perfil:
                            if user_perfil.user_perfil_id == row[7]:
                                anulacion_dato += user_perfil.user_id.username
                                break

                        anulacion_dato += ', ' + str(row[8])
                    # print('row: ', row[0])
                    datos_cobros.append({'caja': row[3],
                                         'monto_bs': row[0],
                                         'periodo': show_periodo(row[1]),
                                         'fecha_cobro': get_date_show(fecha=row[2], formato='dd-MMM-yyyy HH:ii'),
                                         'bloque': row[4],
                                         'piso': row[5],
                                         'departamento': row[6],
                                         'anulacion': anulacion_dato,
                                         'caja_id': row[9],
                                         'cobro_mensual': row[10]
                                         })

            # print('datos_cobros...', datos_cobros)
            return datos_cobros

        except Exception as e:
            self.error_operation = "Error al recuperar datos"
            print('ERROR ' + str(e))
            return False

    def datos_cobros_manuales(self, usuario, bloque_id, piso_id, caja_id, fecha_ini, fecha_fin, anulados, cobro_manual_id):
        """datos de cobros"""
        try:
            fecha1 = get_date_to_db(fecha=fecha_ini, formato_ori='dd-MMM-yyyy', formato='yyyy-mm-dd HH:ii:ss', tiempo='00:00:00')
            fecha2 = get_date_to_db(fecha=fecha_fin, formato_ori='dd-MMM-yyyy', formato='yyyy-mm-dd HH:ii:ss', tiempo='23:59:59')

            lista_user_perfil = UsersPerfiles.objects.filter(status_id=self.status_activo)

            sql_add = f"AND c.fecha_cobro>='{fecha1}' AND c.fecha_cobro<='{fecha2}' "

            if bloque_id != 0:
                sql_add += f"AND b.bloque_id='{bloque_id}' "

            if piso_id != 0:
                sql_add += f"AND pi.piso_id='{piso_id}' "

            if caja_id != 0:
                sql_add += f"AND ca.caja_id='{caja_id}' "

            if cobro_manual_id != 0:
                sql_add += f"AND cm.cobro_manual_id='{cobro_manual_id}' "

            if anulados == 'si':
                sql = "SELECT c.monto_bs, c.periodo, c.fecha_cobro, ca.caja, b.bloque, pi.piso, d.departamento, c.user_perfil_id_anula, c.motivo_anula, ca.caja_id, cm.cobro_manual "
                sql += "FROM cobros_cobros_manuales_anulados c, cobros_manuales cm, cajas ca, departamentos d, bloques b, pisos pi "
                sql += "WHERE c.cobro_manual_id=cm.cobro_manual_id AND c.caja_id=ca.caja_id AND c.departamento_id=d.departamento_id AND d.bloque_id=b.bloque_id AND d.piso_id=pi.piso_id "
                sql_add += f"AND c.status_id='{self.anulado}' "
                sql += sql_add
            else:
                sql = "SELECT c.monto_bs, c.periodo, c.fecha_cobro, ca.caja, b.bloque, pi.piso, d.departamento, c.user_perfil_id_anula, c.motivo_anula, ca.caja_id, cm.cobro_manual "
                sql += "FROM cobros_cobros_manuales c, cobros_manuales cm, cajas ca, departamentos d, bloques b, pisos pi "
                sql += "WHERE c.cobro_manual_id=cm.cobro_manual_id AND c.caja_id=ca.caja_id AND c.departamento_id=d.departamento_id AND d.bloque_id=b.bloque_id AND d.piso_id=pi.piso_id "
                sql_add += f"AND c.status_id='{self.cobrado}' "
                sql += sql_add

            # toda la consulta
            sql += " ORDER BY ca.caja, c.fecha_cobro, cm.cobro_manual "
            # print(sql)

            datos_cobros = []
            with connection.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    anulacion_dato = ''
                    if anulados == 'si':
                        anulacion_dato = ""
                        for user_perfil in lista_user_perfil:
                            if user_perfil.user_perfil_id == row[7]:
                                anulacion_dato += user_perfil.user_id.username
                                break

                        anulacion_dato += ', ' + str(row[8])
                    # print('row: ', row[0])
                    datos_cobros.append({'caja': row[3],
                                         'monto_bs': row[0],
                                         'periodo': show_periodo(row[1]),
                                         'fecha_cobro': get_date_show(fecha=row[2], formato='dd-MMM-yyyy HH:ii'),
                                         'bloque': row[4],
                                         'piso': row[5],
                                         'departamento': row[6],
                                         'anulacion': anulacion_dato,
                                         'caja_id': row[9],
                                         'cobro_manual': row[10]
                                         })

            # print('datos_cobros...', datos_cobros)
            return datos_cobros

        except Exception as e:
            self.error_operation = "Error al recuperar datos"
            print('ERROR ' + str(e))
            return False

    def datos_lecturas(self, usuario, bloque_id, piso_id, caja_id, periodo_ini, periodo_fin, anulados):
        """datos de cobros"""
        try:
            lista_user_perfil = UsersPerfiles.objects.filter(status_id=self.status_activo)

            #sql_add = f"AND l.periodo>='{periodo_ini}' AND l.periodo<='{periodo_fin}' "
            sql_add = ""

            if bloque_id != 0:
                sql_add += f"AND b.bloque_id='{bloque_id}' "

            if piso_id != 0:
                sql_add += f"AND pi.piso_id='{piso_id}' "

            if caja_id != 0:
                sql_add += f"AND ca.caja_id='{caja_id}' "

            if anulados == 'si':
                sql = "SELECT l.consumo, l.periodo, l.fecha_cobro, ca.caja, b.bloque, pi.piso, d.departamento, l.user_perfil_id_anula, l.motivo_anula, ca.caja_id, l.lectura "
                sql += "FROM lecturas_anulados l, cajas ca, departamentos d, bloques b, pisos pi "
                sql += f"WHERE l.periodo>='{periodo_ini}' AND l.periodo<='{periodo_fin}' AND l.caja_id=ca.caja_id AND l.departamento_id=d.departamento_id AND d.bloque_id=b.bloque_id AND d.piso_id=pi.piso_id "
                sql_add += f"AND l.status_id='{self.anulado}' "
                sql += sql_add
            else:
                sql = "SELECT l.consumo, l.periodo, l.fecha_cobro, ca.caja, b.bloque, pi.piso, d.departamento, l.user_perfil_id_anula, l.motivo_anula, ca.caja_id, l.lectura "
                sql += "FROM lecturas l, cajas ca, departamentos d, bloques b, pisos pi "
                sql += f"WHERE l.periodo>='{periodo_ini}' AND l.periodo<='{periodo_fin}' AND l.caja_id=ca.caja_id AND l.departamento_id=d.departamento_id AND d.bloque_id=b.bloque_id AND d.piso_id=pi.piso_id "
                sql_add += f"AND l.status_id='{self.cobrado}' "
                sql += sql_add

            # toda la consulta
            sql += " ORDER BY ca.caja, l.fecha_cobro, l.periodo "
            # print(sql)

            datos_cobros = []
            with connection.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    anulacion_dato = ''
                    if anulados == 'si':
                        anulacion_dato = ""
                        for user_perfil in lista_user_perfil:
                            if user_perfil.user_perfil_id == row[7]:
                                anulacion_dato += user_perfil.user_id.username
                                break

                        anulacion_dato += ', ' + str(row[8])
                    #print('row: ', row[1], '  mostrar: ', show_periodo(row[1]))
                    datos_cobros.append({'caja': row[3],
                                         'consumo': row[0],
                                         'periodo': show_periodo(row[1]),
                                         'fecha_cobro': get_date_show(fecha=row[2], formato='dd-MMM-yyyy HH:ii'),
                                         'bloque': row[4],
                                         'piso': row[5],
                                         'departamento': row[6],
                                         'anulacion': anulacion_dato,
                                         'caja_id': row[9],
                                         'lectura': row[10]
                                         })

            # print('datos_cobros...', datos_cobros)
            return datos_cobros

        except Exception as e:
            self.error_operation = "Error al recuperar datos"
            print('ERROR ' + str(e))
            return False

    def datos_expensas(self, usuario, bloque_id, piso_id, caja_id, periodo_ini, periodo_fin, anulados):
        """datos de cobros"""
        try:
            lista_user_perfil = UsersPerfiles.objects.filter(status_id=self.status_activo)

            #sql_add = f"AND l.periodo>='{periodo_ini}' AND l.periodo<='{periodo_fin}' "
            sql_add = ""

            if bloque_id != 0:
                sql_add += f"AND b.bloque_id='{bloque_id}' "

            if piso_id != 0:
                sql_add += f"AND pi.piso_id='{piso_id}' "

            if caja_id != 0:
                sql_add += f"AND ca.caja_id='{caja_id}' "

            if anulados == 'si':
                sql = "SELECT l.total_expensas, l.periodo, l.fecha_cobro, ca.caja, b.bloque, pi.piso, d.departamento, l.user_perfil_id_anula, l.motivo_anula, ca.caja_id, l.lectura "
                sql += "FROM lecturas_anulados l, cajas ca, departamentos d, bloques b, pisos pi "
                sql += f"WHERE l.periodo>='{periodo_ini}' AND l.periodo<='{periodo_fin}' AND l.caja_id=ca.caja_id AND l.departamento_id=d.departamento_id AND d.bloque_id=b.bloque_id AND d.piso_id=pi.piso_id "
                sql_add += f"AND l.status_id='{self.anulado}' "
                sql += sql_add
            else:
                sql = "SELECT l.total_expensas, l.periodo, l.fecha_cobro, ca.caja, b.bloque, pi.piso, d.departamento, l.user_perfil_id_anula, l.motivo_anula, ca.caja_id, l.lectura "
                sql += "FROM lecturas l, cajas ca, departamentos d, bloques b, pisos pi "
                sql += f"WHERE l.periodo>='{periodo_ini}' AND l.periodo<='{periodo_fin}' AND l.caja_id=ca.caja_id AND l.departamento_id=d.departamento_id AND d.bloque_id=b.bloque_id AND d.piso_id=pi.piso_id "
                sql_add += f"AND l.status_id='{self.cobrado}' "
                sql += sql_add

            # toda la consulta
            sql += " ORDER BY ca.caja, l.fecha_cobro, l.periodo "
            # print(sql)

            datos_cobros = []
            with connection.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    anulacion_dato = ''
                    if anulados == 'si':
                        anulacion_dato = ""
                        for user_perfil in lista_user_perfil:
                            if user_perfil.user_perfil_id == row[7]:
                                anulacion_dato += user_perfil.user_id.username
                                break

                        anulacion_dato += ', ' + str(row[8])
                    #print('row: ', row[1], '  mostrar: ', show_periodo(row[1]))
                    datos_cobros.append({'caja': row[3],
                                         'total_expensas': row[0],
                                         'periodo': show_periodo(row[1]),
                                         'fecha_cobro': get_date_show(fecha=row[2], formato='dd-MMM-yyyy HH:ii'),
                                         'bloque': row[4],
                                         'piso': row[5],
                                         'departamento': row[6],
                                         'anulacion': anulacion_dato,
                                         'caja_id': row[9],
                                         'lectura': row[10]
                                         })

            # print('datos_cobros...', datos_cobros)
            return datos_cobros

        except Exception as e:
            self.error_operation = "Error al recuperar datos"
            print('ERROR ' + str(e))
            return False

    def datos_cobros_pendientes(self, usuario, bloque_id, piso_id, periodo_ini, periodo_fin):
        """datos de cobros"""
        try:
            #sql_add = f"AND c.periodo>='{periodo_ini}' AND c.periodo<='{periodo_fin}' "
            sql_add = ""

            if bloque_id != 0:
                sql_add += f"AND b.bloque_id='{bloque_id}' "

            if piso_id != 0:
                sql_add += f"AND pi.piso_id='{piso_id}' "

            sql = "SELECT c.monto_bs, c.periodo, b.bloque, pi.piso, d.departamento "
            sql += "FROM cobros c, departamentos d, bloques b, pisos pi "
            sql += f"WHERE c.periodo>='{periodo_ini}' AND c.periodo<='{periodo_fin}' AND c.departamento_id=d.departamento_id AND d.bloque_id=b.bloque_id AND d.piso_id=pi.piso_id "
            sql_add += f"AND c.status_id='{self.activo}' "
            sql += sql_add

            # toda la consulta
            sql += " ORDER BY c.periodo, b.bloque, pi.piso, d.departamento "
            # print(sql)

            datos_cobros = []
            with connection.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    datos_cobros.append({
                        'monto_bs': row[0],
                        'periodo': show_periodo(row[1]),
                        'bloque': row[2],
                        'piso': row[3],
                        'departamento': row[4]
                    })

            # print('datos_cobros...', datos_cobros)
            return datos_cobros

        except Exception as e:
            self.error_operation = "Error al recuperar datos"
            print('ERROR ' + str(e))
            return False
