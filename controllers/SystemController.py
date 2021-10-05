from django.apps import apps
from django.conf import settings

import random
import os.path as path
from datetime import datetime
from utils.permissions import show_periodo, previous_periodo
# import os
# from os import remove


class SystemController(object):
    """
    listas de objetos para los combos
    """

    def __init__(self):
        # propiedades
        self.modelo_name = 'unknow'
        self.modelo_id = 'unknow'
        self.modelo_app = 'unknow'

    def model_exits(self, model):
        lista_models = apps.get_models()
        existe = False
        for model_lista in lista_models:
            aux = model_lista.__name__
            if aux.lower() == model.lower():
                existe = True

        return existe

    def nombre_imagen(self, modulo, imagen):
        """nombre de las imagenes cuando se cargan"""
        pos = 0
        pos_punto = 0
        while pos < len(imagen) - 1:
            pos1 = imagen.find('.', pos)
            if pos1 > 0:
                pos_punto = pos1

            pos = pos + 1

        if pos_punto == 0:
            return 'error'

        datos_imagen = {}

        extension = imagen[(pos_punto + 1):len(imagen)]

        # 0 - 35 caracteres
        abc = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        existe = 0
        nombre_archivo = ''
        nombre_archivo_thumb = ''
        while existe == 0:
            nombre_imagen = ''
            for i in range(1, 30):
                pos = random.randrange(0, 35)
                nombre_imagen += abc[pos]

            nombre_archivo = nombre_imagen + '.' + extension
            nombre_archivo_thumb = nombre_imagen + '_thumb.' + extension

            #full_filename = path.join(settings.STATIC_ROOT, 'media', 'productos', nombre_archivo)
            full_filename = path.join(settings.STATIC_ROOT_APP, 'media', modulo, nombre_archivo)

            if not path.exists(full_filename):
                existe = 1

        datos_imagen['nombre_archivo'] = nombre_archivo
        datos_imagen['nombre_archivo_thumb'] = nombre_archivo_thumb

        return datos_imagen

    def lista_recibos_id(self, fecha, user_perfil):
        anio = '20' + str(fecha.year) if len(str(fecha.year)) == 2 else str(fecha.year)
        mes = '0' + str(fecha.month) if len(str(fecha.month)) == 1 else str(fecha.month)

        # departamento
        departamento = apps.get_model('departamentos', 'Departamentos').objects.get(departamento=user_perfil.user_id.username)
        #print('departamento..: ', departamento)
        periodo = anio + mes
        lista_retorno = []
        cant = 0

        while cant < 10:
            # recuperamos recibo para el periodo y departamento
            cobro = apps.get_model('lecturas', 'Cobros').objects.filter(departamento_id=departamento, periodo=periodo)
            #print('cobro..', cobro)
            if cobro:
                # print('entra...')
                primero = cobro.first()
                objeto = {}
                objeto['cobro_id'] = primero.cobro_id
                objeto['status_id'] = primero.status_id.status_id
                objeto['fecha_cobro'] = primero.fecha_cobro
                objeto['monto_bs'] = primero.monto_bs
                objeto['periodo'] = show_periodo(periodo)
                lista_retorno.append(objeto)

            periodo = previous_periodo(periodo)
            cant += 1

        return lista_retorno
