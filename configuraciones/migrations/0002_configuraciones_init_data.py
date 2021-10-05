# Generated by Django 3.2.5 on 2021-07-12 19:01

from django.db import migrations
from configuraciones.models import CobrosManuales, CobrosMensuales, Configuraciones, Paises, Ciudades, Sucursales, Puntos, Cajas, TiposMonedas, Monedas
from permisos.models import UsersPerfiles
from status.models import Status


def load_data(apps, schema_editor):
    # configuraciones
    configuraciones_add = Configuraciones.objects.create(configuracion_id=1, cant_per_page=30, cant_lista_cobranza=10,
                                                         usar_fecha_servidor='si', fecha_sistema='now', costo_m3=1, costo_minimo=10,
                                                         unidad_minima_m3=10, expensas_monto_m2=10.50, periodo_ini='202101', periodo_fin='202112')
    configuraciones_add.save()

    # paises
    paises_add = Paises.objects.create(pais_id=1, pais='Bolivia')
    paises_add.save()

    # datos
    user_perfil = UsersPerfiles.objects.get(pk=1)
    bolivia = Paises.objects.get(pk=1)
    status_activo = Status.objects.get(pk=1)

    # ciudades
    ciudad_add = Ciudades.objects.create(pais_id=bolivia, user_perfil_id=user_perfil, status_id=status_activo, ciudad='Cochabamba', codigo='CBA', created_at='now', updated_at='now')
    ciudad_add.save()

    # ciudad cbba
    cochabamba = Ciudades.objects.get(pk=1)

    # SUCURSALES
    sucursal_add = Sucursales.objects.create(ciudad_id=cochabamba, user_perfil_id=user_perfil, status_id=status_activo, sucursal='Sucursal Central', codigo='SC-CBA', email='acc.claros@gmail.com',
                                             empresa='empresa', direccion='direccion', ciudad='ciudad', telefonos='telefonos', actividad='actividad', created_at='now', updated_at='now')
    sucursal_add.save()

    # sucursal central
    sucursal_central = Sucursales.objects.get(pk=1)

    # puntos
    punto_add = Puntos.objects.create(sucursal_id=sucursal_central, user_perfil_id=user_perfil, status_id=status_activo, punto='Punto 1',
                                      codigo='P1', impresora_reportes='impresora reportes', created_at='now', updated_at='now')
    punto_add.save()

    # tipos monedas
    tipo_moneda_add = TiposMonedas.objects.create(tipo_moneda_id=1, status_id=status_activo, tipo_moneda='Bolivianos', codigo='Bs.')
    tipo_moneda_add.save()

    # monedas
    tipo_bs = TiposMonedas.objects.get(pk=1)
    # bs
    moneda = Monedas.objects.create(moneda_id=1, tipo_moneda_id=tipo_bs, monto=0.10, status_id=status_activo)
    moneda.save()
    moneda = Monedas.objects.create(moneda_id=2, tipo_moneda_id=tipo_bs, monto=0.20, status_id=status_activo)
    moneda.save()
    moneda = Monedas.objects.create(moneda_id=3, tipo_moneda_id=tipo_bs, monto=0.50, status_id=status_activo)
    moneda.save()
    moneda = Monedas.objects.create(moneda_id=4, tipo_moneda_id=tipo_bs, monto=1.00, status_id=status_activo)
    moneda.save()
    moneda = Monedas.objects.create(moneda_id=5, tipo_moneda_id=tipo_bs, monto=2.00, status_id=status_activo)
    moneda.save()
    moneda = Monedas.objects.create(moneda_id=6, tipo_moneda_id=tipo_bs, monto=5.00, status_id=status_activo)
    moneda.save()
    moneda = Monedas.objects.create(moneda_id=7, tipo_moneda_id=tipo_bs, monto=10.00, status_id=status_activo)
    moneda.save()
    moneda = Monedas.objects.create(moneda_id=8, tipo_moneda_id=tipo_bs, monto=20.00, status_id=status_activo)
    moneda.save()
    moneda = Monedas.objects.create(moneda_id=9, tipo_moneda_id=tipo_bs, monto=50.00, status_id=status_activo)
    moneda.save()
    moneda = Monedas.objects.create(moneda_id=10, tipo_moneda_id=tipo_bs, monto=100.00, status_id=status_activo)
    moneda.save()
    moneda = Monedas.objects.create(moneda_id=11, tipo_moneda_id=tipo_bs, monto=200.00, status_id=status_activo)
    moneda.save()

    # cajas
    punto1 = Puntos.objects.get(pk=1)
    caja_Bs = Cajas.objects.create(punto_id=punto1, tipo_moneda_id=tipo_bs, user_perfil_id=user_perfil, status_id=status_activo, caja='Caja Bs', codigo='C.Bs', created_at='now', updated_at='now')
    caja_Bs.save()

    # cobros mensuales
    cobro_mensual = CobrosMensuales.objects.create(cobro_mensual='Jardineria', codigo='JAR', monto_bs=50, monto_cobrar=2.50, status_id=status_activo, created_at='now', updated_at='now')
    cobro_mensual.save()
    cobro_mensual = CobrosMensuales.objects.create(cobro_mensual='Alumbrado', codigo='ALM', monto_bs=100, monto_cobrar=50, status_id=status_activo, created_at='now', updated_at='now')
    cobro_mensual.save()
    cobro_mensual = CobrosMensuales.objects.create(cobro_mensual='Piscina', codigo='PSC', monto_bs=80, monto_cobrar=4, status_id=status_activo, created_at='now', updated_at='now')
    cobro_mensual.save()

    # cobros manuales
    cobro_manual = CobrosManuales.objects.create(cobro_manual='Multa Retraso Luz', codigo='MRL', monto_porcentaje='porcentaje', monto_bs=0,
                                                 porcentaje=10, cobro_mensual_id=0, status_id=status_activo, created_at='now', updated_at='now')
    cobro_manual.save()


def delete_data(apps, schema_editor):
    cobros_manuales_del = apps.get_model('configuraciones', 'CobrosManuales')
    cobros_manuales_del.objects.all().delete

    cobros_mensuales_del = apps.get_model('configuraciones', 'CobrosMensuales')
    cobros_mensuales_del.objects.all().delete

    cajas_del = apps.get_model('configuraciones', 'Cajas')
    cajas_del.objects.all().delete

    monedas_del = apps.get_model('configuraciones', 'Monedas')
    monedas_del.objects.all().delete

    tipos_monedas_del = apps.get_model('configuraciones', 'TiposMonedas')
    tipos_monedas_del.objects.all().delete

    puntos_del = apps.get_model('configuraciones', 'Puntos')
    puntos_del.objects.all().delete

    sucursales_del = apps.get_model('configuraciones', 'Sucursales')
    sucursales_del.objects.all().delete

    ciudades_del = apps.get_model('configuraciones', 'Ciudades')
    ciudades_del.objects.all().delete

    paises_del = apps.get_model('configuraciones', 'Paises')
    paises_del.objects.all().delete

    configuraciones_del = apps.get_model('configuraciones', 'Configuraciones')
    configuraciones_del.objects.all().delete


class Migration(migrations.Migration):

    dependencies = [
        ('configuraciones', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_data, delete_data),
    ]
