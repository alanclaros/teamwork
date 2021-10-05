# from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.fields import CharField, DecimalField, IntegerField, BooleanField
from utils.custome_db_types import DateFieldCustome, DateTimeFieldCustome

from utils.dates_functions import get_date_show, get_month_3digits

from django.apps import apps
from django.conf import settings

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


def get_permissions_user(user, modulo):
    """
    get user permissions per module
    :param user: (object) user object
    :param modulo: (int) modulo id
    :return: (dict) user permissions
    """
    try:
        app_modulo = apps.get_model('permisos', 'Modulos')
        modulo_user = app_modulo.objects.get(pk=int(modulo))
        user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=user)

        app_user_modulos = apps.get_model('permisos', 'UsersModulos')
        user_modulo = app_user_modulos.objects.get(user_perfil_id=user_perfil, modulo_id=modulo_user)

        return user_modulo

    except Exception as ex:
        raise AttributeError('Error al recuperar permiso de usuario: ' + str(user), ', ' + str(modulo))


def get_user_permission_operation(user, modulo, operacion, object_name_id='', object_id='', object_app='', object_model=''):
    """
    return True if user have permission for do operation (just admin user can see other sucursal objects) else False
    :param user: (object) user trying do operation
    :param modulo: (object) modulo id
    :param operacion: (str) operation needed
    :param object_id: (object) table id where user can make operation
    :param object_app: (str) app name of table
    :param object_model: (str) model name of table
    :return: True if have permission else False
    """

    try:
        app_modulo = apps.get_model('permisos', 'Modulos')
        modulo_user = app_modulo.objects.get(pk=int(modulo))
        user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=user)

        app_user_modulo = apps.get_model('permisos', 'UsersModulos')
        user_modulo = app_user_modulo.objects.get(user_perfil_id=user_perfil, modulo_id=modulo_user)

        if user_modulo:
            compare_sucursal = 'no'
            app_table = None
            table = None

            # if object_name_id != '' or object_id != '' or object_app != '' or object_model != '':
            #     compare_sucursal = 'si'
            #     app_table = apps.get_model(object_app, object_model)
            #     table = app_table.objects.get(pk=int(object_id))

            # if compare_sucursal == 'si':
            #     # datos del usuario
            #     app_user_perfil = apps.get_model('permisos', 'UsersPerfiles')
            #     app_punto = apps.get_model('configuraciones', 'Puntos')

            #     perfil_user = app_user_perfil.objects.get(user_id=user)
            #     punto_user = app_punto.objects.select_related('sucursal_id').get(pk=perfil_user.punto_id)

            #     # if perfil_user.perfil_id.perfil_id == settings.PERFIL_ADMIN:
            #     #     return False

            #     if perfil_user.perfil_id.perfil_id == settings.PERFIL_SUPERVISOR:
            #         # usuario supervisor, puede ver datos de la sucursal
            #         if object_name_id == 'punto_id':
            #             punto_id_table = getattr(table, 'punto_id').punto_id
            #             punto_object = app_punto.objects.select_related('sucursal_id').get(pk=punto_id_table)

            #             if punto_user.punto_id.sucursal_id.sucursal_id != punto_object.punto_id.sucursal_id.sucursal_id:
            #                 # no son de la misma sucursal
            #                 return False

            #         if object_name_id == 'caja_id' or object_name_id == 'caja1_id' or object_name_id == 'caja2_id':
            #             # recuperamos objecto de caja
            #             app_caja = apps.get_model('cajas', 'Cajas')
            #             model_caja = app_caja.objects.select_related('punto_id').select_related('punto_id__sucursal_id').get(pk=int(table.caja_id.caja_id))

            #             if punto_user.punto_id.sucursal_id.sucursal_id != model_caja.punto_id.sucursal_id.sucursal_id:
            #                 # no son de la misma sucursal
            #                 return False

            #         if object_name_id == 'plan_pago_id':
            #             # recuperamos el punto del objeto
            #             punto_id_table = getattr(table, 'punto_id')
            #             punto_object = app_punto.objects.select_related('sucursal_id').get(pk=punto_id_table)

            #             if punto_user.punto_id.sucursal_id.sucursal_id != punto_object.punto_id.sucursal_id.sucursal_id:
            #                 # no son de la misma sucursal
            #                 return False

            #         if object_name_id == 'caja_ingreso_id':
            #             # caja de la operacion
            #             caja_id_table = getattr(table, 'caja_id')
            #             # cajas de la sucursal
            #             filtro_caja = {}
            #             status_activo = apps.get_model('status', 'Status').objects.get(pk=int(settings.STATUS_ACTIVO))
            #             filtro_caja['status_id'] = status_activo
            #             filtro_caja['punto_id__sucursal_id'] = punto_user.sucursal_id
            #             cajas_sucursal = apps.get_model('configuraciones', 'Cajas').objects.filter(**filtro_caja).order_by('caja')
            #             pertenece = 'no'
            #             for caja_suc in cajas_sucursal:
            #                 if perfil_user.caja_id == caja_suc.caja_id:
            #                     pertenece = 'si'

            #             if pertenece == 'no':
            #                 return False

            #         if object_name_id == 'caja_egreso_id':
            #             # caja de la operacion
            #             caja_id_table = getattr(table, 'caja_id')
            #             # cajas de la sucursal
            #             filtro_caja = {}
            #             status_activo = apps.get_model('status', 'Status').objects.get(pk=int(settings.STATUS_ACTIVO))
            #             filtro_caja['status_id'] = status_activo
            #             filtro_caja['punto_id__sucursal_id'] = punto_user.sucursal_id
            #             cajas_sucursal = apps.get_model('configuraciones', 'Cajas').objects.filter(**filtro_caja).order_by('caja')
            #             pertenece = 'no'
            #             for caja_suc in cajas_sucursal:
            #                 if perfil_user.caja_id == caja_suc.caja_id:
            #                     pertenece = 'si'

            #             if pertenece == 'no':
            #                 return False

            #         if object_name_id == 'registro_id':
            #             punto_registro = apps.get_model('configuraciones', 'Puntos').objects.get(pk=table.punto_id)

            #             if punto_registro.sucursal_id != punto_user.sucursal_id:
            #                 return False

            #         if object_name_id == 'almacen_id':
            #             almacen_registro = apps.get_model('configuraciones', 'Almacenes').objects.get(pk=table.almacen_id)
            #             #print('almacen registro: ', almacen_registro.sucursal_id, ' punto user: ', punto_user.sucursal_id)
            #             if almacen_registro.sucursal_id != punto_user.sucursal_id:
            #                 return False

            #         if object_name_id == 'venta_id':
            #             venta_registro = apps.get_model('ventas', 'Ventas').objects.select_related('punto_id').get(pk=table.venta_id)

            #             if venta_registro.punto_id.sucursal_id != punto_user.sucursal_id:
            #                 return False

            #         if object_name_id == 'preventa_id':
            #             preventa_registro = apps.get_model('preventas', 'PreVentas').objects.select_related('punto_id').get(pk=table.venta_id)

            #             if preventa_registro.punto_id.sucursal_id != punto_user.sucursal_id:
            #                 return False

            #     if perfil_user.perfil_id.perfil_id == settings.PERFIL_CAJERO:
            #         # usuario supervisor, puede ver datos de la sucursal
            #         if object_name_id == 'punto_id':
            #             punto_id_table = getattr(table, 'punto_id').punto_id
            #             punto_object = app_punto.objects.get(pk=punto_id_table)

            #             if punto_user.punto_id.punto_id != punto_object.punto_id.punto_id:
            #                 # no son de la misma sucursal
            #                 return False

            #         if object_name_id == 'caja_id':
            #             # recuperamos objecto de caja
            #             app_caja = apps.get_model('cajas', 'Cajas')
            #             model_caja = app_caja.objects.select_related('punto_id').get(pk=int(table.caja_id.caja_id))

            #             if punto_user.punto_id.punto_id != model_caja.punto_id.punto_id:
            #                 # no son de la misma sucursal
            #                 return False

            #         if object_name_id == 'caja1_id' or object_name_id == 'caja2_id':
            #             # recuperamos objecto de movimientos de cajas
            #             app_caja = apps.get_model('cajas', 'Cajas')
            #             model_caja = app_caja.objects.select_related('punto_id').select_related('punto_id__sucursal_id').get(pk=int(table.caja_id.caja_id))

            #             if punto_user.punto_id.sucursal_id.sucursal_id != model_caja.punto_id.sucursal_id.sucursal_id:
            #                 # no son de la misma sucursal
            #                 return False

            #         if object_name_id == 'plan_pago_id':
            #             # recuperamos el punto del objeto
            #             punto_id_table = getattr(table, 'punto_id')
            #             punto_object = app_punto.objects.select_related('sucursal_id').get(pk=punto_id_table)

            #             if punto_user.punto_id.sucursal_id.sucursal_id != punto_object.punto_id.sucursal_id.sucursal_id:
            #                 # no son de la misma sucursal
            #                 return False

            #         if object_name_id == 'caja_ingreso_id':
            #             # caja de la operacion
            #             caja_id_table = getattr(table, 'caja_id')

            #             if perfil_user.caja_id != caja_id_table.caja_id:
            #                 return False

            #         if object_name_id == 'caja_egreso_id':
            #             # caja de la operacion
            #             caja_id_table = getattr(table, 'caja_id')

            #             if perfil_user.caja_id != caja_id_table.caja_id:
            #                 return False

            #         if object_name_id == 'registro_id':
            #             punto_registro = apps.get_model('configuraciones', 'Puntos').objects.get(pk=table.punto_id)

            #             if punto_registro.punto_id != punto_user.punto_id:
            #                 return False

            #         if object_name_id == 'almacen_id':
            #             punto_almacen = apps.get_model('configuraciones', 'PuntosAlmacenes').objects.filter(almacen_id=table)
            #             pertenece = 'no'
            #             for punto_al in punto_almacen:
            #                 if punto_al.punto_id.punto_id == punto_user.punto_id:
            #                     pertenece = 'si'

            #             if pertenece == 'no':
            #                 return False

            #         if object_name_id == 'venta_id':
            #             if table.punto_id.punto_id != punto_user.punto_id:
            #                 return False

            #         if object_name_id == 'preventa_id':
            #             #print('entrando preventa...', ' ', table.punto_id, ' 2: ', punto_user.punto_id)
            #             if table.punto_id.punto_id != punto_user.punto_id:
            #                 return False

            if operacion == 'lista':
                # print('permiso lista')
                if user_modulo.enabled:
                    return True

            if operacion == 'adicionar':
                if user_modulo.adicionar:
                    return True

            if operacion == 'modificar':
                if user_modulo.modificar:
                    return True

            if operacion == 'eliminar':
                if user_modulo.eliminar:
                    return True

            if operacion == 'anular':
                if user_modulo.anular:
                    return True

            if operacion == 'imprimir':
                if user_modulo.imprimir:
                    return True

            if operacion == 'permiso':
                if user_modulo.permiso:
                    return True

        # no tiene permiso false
        return False

    except Exception as ex:
        print(f"Error de permiso {user}, {modulo}, {operacion}, {object_name_id}, {object_id}, {object_app}, {object_model} : " + str(ex))
        return False


def get_system_settings():
    retorno = {}
    try:
        app_configuraciones = apps.get_model('configuraciones', 'Configuraciones')
        configuraciones_sistema = app_configuraciones.objects.get(pk=1)
        # retorno = {}
        retorno = configuraciones_sistema.__dict__
        # print(retorno)

        # for attr, value in settings_sistema.__dict__.iteritems():
        #     retorno[attr] = value
        #     print("Attribute: " + str(attr or ""))
        #     print("Value: " + str(value or ""))
    except Exception as ex:
        print('tabla configuraciones no cargada, ' + str(ex))

    return retorno


def current_date():
    datos_settings = get_system_settings()
    anio = '20' + str(datetime.now().year) if len(str(datetime.now().year)) == 2 else str(datetime.now().year)
    mes = '0' + str(datetime.now().month) if len(str(datetime.now().month)) == 1 else str(datetime.now().month)
    dia = '0' + str(datetime.now().day) if len(str(datetime.now().day)) == 1 else str(datetime.now().day)
    fecha = anio + '-' + mes + '-' + dia

    try:
        if datos_settings['usar_fecha_servidor'] == 'no':
            anio = '20' + str(datos_settings['fecha_sistema'].year) if len(str(datos_settings['fecha_sistema'].year)) == 2 else str(datos_settings['fecha_sistema'].year)
            mes = '0' + str(datos_settings['fecha_sistema'].month) if len(str(datos_settings['fecha_sistema'].month)) == 1 else str(datos_settings['fecha_sistema'].month)
            dia = '0' + str(datos_settings['fecha_sistema'].day) if len(str(datos_settings['fecha_sistema'].day)) == 1 else str(datos_settings['fecha_sistema'].day)
            fecha = anio + '-' + mes + '-' + dia
    except Exception as ex:
        print('tabla configuraciones(current date) no cargada, ' + str(ex))

    return fecha


def report_date():
    fecha = current_date()
    fecha = get_date_show(fecha=fecha, formato_ori='yyyy-mm-dd', formato='dd-MMM-yyyy HH:ii')

    return fecha


def current_periodo():
    datos_settings = get_system_settings()
    anio = '20' + str(datetime.now().year) if len(str(datetime.now().year)) == 2 else str(datetime.now().year)
    mes = '0' + str(datetime.now().month) if len(str(datetime.now().month)) == 1 else str(datetime.now().month)
    periodo = anio + mes

    try:
        if datos_settings['usar_fecha_servidor'] == 'no':
            anio = '20' + str(datos_settings['fecha_sistema'].year) if len(str(datos_settings['fecha_sistema'].year)) == 2 else str(datos_settings['fecha_sistema'].year)
            mes = '0' + str(datos_settings['fecha_sistema'].month) if len(str(datos_settings['fecha_sistema'].month)) == 1 else str(datos_settings['fecha_sistema'].month)
            periodo = anio + mes
    except Exception as ex:
        print('tabla configuraciones(current periodo) no cargada, ' + str(ex))

    return periodo


def next_periodo(periodo):
    anio = periodo[0:4]
    mes = periodo[4:6]
    if mes == '12':
        n_anio = int(anio) + 1
        return str(n_anio) + '01'
    else:
        n_mes = int(mes) + 1
        aux_mes = str(n_mes)
        if len(aux_mes) == 1:
            aux_mes = '0' + aux_mes

        return anio + aux_mes


def previous_periodo(periodo):
    anio = periodo[0:4]
    mes = periodo[4:6]
    if mes == '01':
        n_anio = int(anio) - 1
        return str(n_anio) + '12'
    else:
        n_mes = int(mes) - 1
        aux_mes = str(n_mes)
        if len(aux_mes) == 1:
            aux_mes = '0' + aux_mes

        return anio + aux_mes


def rango_periodos(periodo):
    periodo_actual = periodo
    periodo_ant = periodo_actual
    retorno = []
    retorno.append(periodo_actual)
    for i in range(10):
        periodo_ant = previous_periodo(periodo_ant)
        retorno.insert(0, periodo_ant)

    periodo_next = next_periodo(periodo_actual)
    retorno.append(periodo_next)
    periodo_next = next_periodo(periodo_next)
    retorno.append(periodo_next)

    return retorno


def show_periodo(periodo):
    """periodo: yyyymm"""
    anio = periodo[0:4]
    mes = get_month_3digits(periodo[4:6])

    return mes + '-' + anio


def fecha_periodo(periodo, dia):
    anio = periodo[0:4]
    mes = periodo[4:6]
    fecha = anio + '-' + mes + '-' + dia

    return fecha


def get_sucursal_settings(sucursal_id):
    retorno = {}
    try:
        sucursal_datos = apps.get_model('configuraciones', 'Sucursales').objects.get(pk=int(sucursal_id))
        lista = sucursal_datos.__dict__
        retorno['empresa'] = lista['empresa']
        retorno['direccion'] = lista['direccion']
        retorno['ciudad'] = lista['ciudad']
        retorno['telefonos'] = lista['telefonos']
        retorno['actividad'] = lista['actividad']

    except Exception as ex:
        retorno['empresa'] = 'error'
        retorno['direccion'] = 'error'
        retorno['ciudad'] = 'error'
        retorno['telefonos'] = 'error'
        retorno['actividad'] = 'error'

    return retorno


def get_html_column(modelo, not_required, request, instancia, *args):
    """devuelve las restricciones segun el tipo de columna"""
    #print('modelo: ', modelo)
    lista_not_required = []
    if not_required != '':
        div_not = not_required.split(',')
        for not_req in div_not:
            lista_not_required.append(not_req.strip())

    retorno = {}
    for arg in args:
        columna = modelo._meta.get_field(arg)
        #print('columna: ', columna, ' ..lista_not_requ: ', lista_not_required)
        if isinstance(columna, CharField):
            if arg not in lista_not_required:
                retorno[arg] = 'maxlength="' + str(columna.max_length) + '" onkeyup="txtValid(this);" onblur="txtValid(this);" '
            else:
                retorno[arg] = 'maxlength="' + str(columna.max_length) + '" '

            if request:
                retorno[arg] += (' value="' + request.POST[arg].replace('"', '&quot;') + '"') + F' id="{arg}"' + F' name="{arg}"'
            else:
                if instancia:
                    # para el caso de campos nulos
                    if getattr(instancia, arg):
                        retorno[arg] += (' value="' + getattr(instancia, arg).replace('"', '&quot;') + '"' if instancia else '') + F' id="{arg}"' + F' name="{arg}"'
                    else:
                        retorno[arg] += F' value="" id="{arg}" name="{arg}" '
                else:
                    retorno[arg] += F' value="" id="{arg}" name="{arg}" '

        elif isinstance(columna, DecimalField):
            retorno[arg] = 'onkeyup="validarNumeroPunto(this);txtValid(this);" onblur="txtValid(this);" '
            if request:
                retorno[arg] += (' value="' + request.POST[arg] + '"') + F' id="{arg}"' + F' name="{arg}"'
            else:
                if instancia:
                    retorno[arg] += (' value="' + str(getattr(instancia, arg)) + '"' if instancia else '') + F' id="{arg}"' + F' name="{arg}"'
                else:
                    retorno[arg] += F' value="" id="{arg}" name="{arg}" '

        elif isinstance(columna, DateFieldCustome):
            retorno[arg] = 'readonly="readonly"' + F' id="{arg}"' + F' name="{arg}" '
            if request:
                retorno[arg] += ' value="' + request.POST[arg] + '" '
            else:
                if instancia:
                    retorno[arg] += ' value="' + get_date_show(fecha=getattr(instancia, arg), formato='dd-MMM-yyyy') + '" '
                else:
                    retorno[arg] += ' value="" '

        elif isinstance(columna, DateTimeFieldCustome):
            retorno[arg] = 'readonly="readonly"' + F' id="{arg}"' + F' name="{arg}"'
            if request:
                retorno[arg] += ' value="' + request.POST[arg] + '" '
            else:
                if instancia:
                    retorno[arg] += ' value="' + get_date_show(fecha=getattr(instancia, arg), formato='dd-MMM-yyyy') + '" '
                else:
                    retorno[arg] += ' value="" '

        elif isinstance(columna, BooleanField):
            retorno[arg] = '' + F' id="{arg}"' + F' name="{arg}" '

        elif isinstance(columna, IntegerField):
            retorno[arg] = 'onkeyup="validarNumero(this);txtValid(this);" onblur="txtValid(this);" '
            if request:
                retorno[arg] += (' value="' + request.POST[arg] + '"') + F' id="{arg}"' + F' name="{arg}" '
            else:
                if instancia:
                    retorno[arg] += (' value="' + str(getattr(instancia, arg)) + '"' if instancia else '') + F' id="{arg}"' + F' name="{arg}" '
                else:
                    retorno[arg] += F' value="" id="{arg}" name="{arg}" '

        else:
            retorno[arg] = 'sin tipo'

    return retorno
