from django.apps import apps
from django.conf import settings


class ListasController(object):
    """
    listas de objetos para los combos
    """

    def __init__(self):
        # propiedades
        self.modelo_name = 'unknow'
        self.modelo_id = 'unknow'
        self.modelo_app = 'unknow'

    def get_lista_sucursales(self, user, module='', *select_relateds):
        """
        get sucursales list
        :param user: (object) request user
        :param module: (object) module for list
        :param *args: (list) list select_related modules
        :return: (list) almacenes list
        """

        #print('select relateds: ', *select_relateds)

        status_activo = apps.get_model('status', 'Status').objects.get(pk=int(settings.STATUS_ACTIVO))
        filtros = {}
        filtros['status_id'] = status_activo

        lista_sucursales = apps.get_model('configuraciones', 'Sucursales').objects.filter(**filtros).order_by('sucursal')

        return lista_sucursales

    def get_lista_tipos_monedas(self, user, module='', *select_relateds):
        """
        get tipos monedas list
        :param user: (object) request user
        :param module: (object) module for list
        :param *args: (list) list select_related modules
        :return: (list) tipos monedas list
        """

        #print('select relateds: ', *select_relateds)

        status_activo = apps.get_model('status', 'Status').objects.get(pk=int(settings.STATUS_ACTIVO))
        filtros = {}
        filtros['status_id'] = status_activo

        lista_tipos_monedas = apps.get_model('configuraciones', 'TiposMonedas').objects.filter(**filtros).order_by('codigo')

        return lista_tipos_monedas

    def get_lista_perfiles(self, user, module='', *select_relateds):
        """
        get perfiles list
        :param user: (object) request user
        :param module: (object) module for list
        :param *args: (list) list select_related modules
        :return: (list) perfiles list
        """

        #print('select relateds: ', *select_relateds)
        lista_perfiles = apps.get_model('permisos', 'Perfiles').objects.order_by('perfil')

        return lista_perfiles

    def get_lista_modulos(self, user, module='', *select_relateds):
        """
        get modulos list
        :param user: (object) request user
        :param module: (object) module for list
        :param *args: (list) list select_related modules
        :return: (list) modulos list
        """

        lista_modulos = apps.get_model('permisos', 'Modulos').objects.filter(enabled=True).order_by('position')

        return lista_modulos

    def get_lista_cajas(self, user, module='', *select_relateds):
        """
        get cajas list
        :param user: (object) request user
        :param module: (object) module for list
        :param *args: (list) list select_related modules
        :return: (list) cajas list
        """

        # verificamos el perfil del usuario
        user_perfil = apps.get_model('permisos', 'UsersPerfiles').objects.get(user_id=user)
        status_activo = apps.get_model('status', 'Status').objects.get(pk=int(settings.STATUS_ACTIVO))
        punto_user = apps.get_model('configuraciones', 'Puntos').objects.get(pk=user_perfil.punto_id)
        filtros = {}

        if user_perfil.perfil_id.perfil_id == settings.PERFIL_ADMIN:
            # todas las cajas del sistema
            filtros['status_id'] = status_activo

        if user_perfil.perfil_id.perfil_id == settings.PERFIL_SUPERVISOR:
            filtros['status_id'] = status_activo
            filtros['punto_id__sucursal_id'] = punto_user.sucursal_id

        if user_perfil.perfil_id.perfil_id == settings.PERFIL_CAJERO or module in ['cajas_ingresos', 'cajas_egresos']:
            # para mostrar solo la caja asignada en adicion
            filtros['status_id'] = status_activo
            filtros['caja_id'] = user_perfil.caja_id

        lista_cajas = apps.get_model('configuraciones', 'Cajas').objects.filter(**filtros).order_by('caja')

        return lista_cajas

    def get_lista_puntos(self, user, module='', *select_relateds):
        """
        get cajas list
        :param user: (object) request user
        :param module: (object) module for list
        :param *args: (list) list select_related modules
        :return: (list) cajas list
        """

        status_activo = apps.get_model('status', 'Status').objects.get(pk=int(settings.STATUS_ACTIVO))
        filtros = {}
        filtros['status_id'] = status_activo
        lista_puntos = apps.get_model('configuraciones', 'Puntos').objects.filter(**filtros).order_by('punto')

        return lista_puntos

    def get_cantidad_departamentos(self, user, module=''):
        status_activo = apps.get_model('status', 'Status').objects.get(pk=int(settings.STATUS_ACTIVO))
        filtros = {}
        filtros['status_id'] = status_activo
        cantidad_departamentos = apps.get_model('departamentos', 'Departamentos').objects.filter(**filtros).count()

        return cantidad_departamentos

    def get_lista_cobros_mensuales(self, user, module='', *select_relateds):
        """
        get cobros mensuales list
        :param user: (object) request user
        :param module: (object) module for list
        :param *args: (list) list select_related modules
        :return: (list) cobros mensuales list
        """

        status_activo = apps.get_model('status', 'Status').objects.get(pk=int(settings.STATUS_ACTIVO))
        filtros = {}
        filtros['status_id'] = status_activo
        lista_cobros_mensuales = apps.get_model('configuraciones', 'CobrosMensuales').objects.filter(**filtros).order_by('cobro_mensual')

        return lista_cobros_mensuales

    def get_lista_cobros_manuales(self, user, module='', *select_relateds):
        """
        get cobros manuales list
        :param user: (object) request user
        :param module: (object) module for list
        :param *args: (list) list select_related modules
        :return: (list) cobros manuales list
        """

        status_activo = apps.get_model('status', 'Status').objects.get(pk=int(settings.STATUS_ACTIVO))
        filtros = {}
        filtros['status_id'] = status_activo
        lista_cobros_manuales = apps.get_model('configuraciones', 'CobrosManuales').objects.filter(**filtros).order_by('cobro_manual')

        return lista_cobros_manuales

    def get_lista_bloques(self, user, module='', *select_relateds):
        """
        get bloques list
        :param user: (object) request user
        :param module: (object) module for list
        :param *args: (list) list select_related modules
        :return: (list) bloques list
        """

        status_activo = apps.get_model('status', 'Status').objects.get(pk=int(settings.STATUS_ACTIVO))
        filtros = {}
        filtros['status_id'] = status_activo
        lista_bloques = apps.get_model('departamentos', 'Bloques').objects.filter(**filtros).order_by('bloque')

        return lista_bloques

    def get_lista_actividades(self, user, module='', *select_relateds):
        """
        get actividades list
        :param user: (object) request user
        :param module: (object) module for list
        :param *args: (list) list select_related modules
        :return: (list) actividades list
        """

        status_activo = apps.get_model('status', 'Status').objects.get(pk=int(settings.STATUS_ACTIVO))
        filtros = {}
        filtros['status_id'] = status_activo
        lista_actividades = apps.get_model('calendario', 'Actividades').objects.filter(**filtros).order_by('actividad')

        return lista_actividades

    def get_lista_pisos(self, user, module='', *select_relateds):
        """
        get pisos list
        :param user: (object) request user
        :param module: (object) module for list
        :param *args: (list) list select_related modules
        :return: (list) pisos list
        """

        status_activo = apps.get_model('status', 'Status').objects.get(pk=int(settings.STATUS_ACTIVO))
        filtros = {}
        filtros['status_id'] = status_activo
        lista_pisos = apps.get_model('departamentos', 'Pisos').objects.filter(**filtros).order_by('piso')

        return lista_pisos

    def get_lista_ciudades(self, user, module='', *select_relateds):
        """
        get ciudades list
        :param user: (object) request user
        :param module: (object) module for list
        :param *args: (list) list select_related modules
        :return: (list) ciudades list
        """

        status_activo = apps.get_model('status', 'Status').objects.get(pk=int(settings.STATUS_ACTIVO))
        filtros = {}
        filtros['status_id'] = status_activo
        lista_ciudades = apps.get_model('configuraciones', 'Ciudades').objects.filter(**filtros).order_by('ciudad')

        return lista_ciudades

    def get_minutos(self):
        lista_minutos = []
        minuto = 0
        for i in range(12):
            objeto_minuto = {}
            objeto_minuto['id'] = minuto
            min_txt = str(minuto)
            if len(min_txt) == 1:
                min_txt = '0' + min_txt

            objeto_minuto['minuto'] = min_txt
            lista_minutos.append(objeto_minuto)

            minuto += 5

        return lista_minutos

    def get_horas(self):
        lista_horas = []
        hora = 0
        for i in range(24):
            objeto_hora = {}
            objeto_hora['id'] = hora
            hora_txt = str(hora)
            if len(hora_txt) == 1:
                hora_txt = '0' + hora_txt

            objeto_hora['hora'] = hora_txt
            lista_horas.append(objeto_hora)

            hora += 1

        return lista_horas
