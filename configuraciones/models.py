from django.db import models
from django.conf import settings
from django.db.models.fields import BLANK_CHOICE_DASH

from status.models import Status
from permisos.models import UsersPerfiles
from utils.custome_db_types import DateFieldCustome, DateTimeFieldCustome


class Configuraciones(models.Model):
    configuracion_id = models.IntegerField(primary_key=True)
    cant_per_page = models.IntegerField(blank=False, null=False)
    cant_lista_cobranza = models.IntegerField(blank=False, null=False)
    usar_fecha_servidor = models.CharField(max_length=20, blank=False, null=False, default='si')
    fecha_sistema = DateFieldCustome(null=True, blank=True)
    costo_m3 = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False, default=0)
    costo_minimo = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False, default=0)
    unidad_minima_m3 = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False, default=0)
    expensas_monto_m2 = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False, default=0)
    periodo_ini = models.CharField(max_length=20, blank=False, null=False, default='202101')
    periodo_fin = models.CharField(max_length=20, blank=False, null=False, default='202112')

    class Meta:
        db_table = 'configuraciones'


class Paises(models.Model):
    pais_id = models.IntegerField(primary_key=True, db_column='pais_id')
    pais = models.CharField(max_length=150, blank=False)

    class Meta:
        db_table = 'paises'


class Ciudades(models.Model):
    ciudad_id = models.AutoField(primary_key=True, db_column='ciudad_id')
    pais_id = models.ForeignKey(Paises, to_field='pais_id', on_delete=models.PROTECT, db_column='pais_id')
    user_perfil_id = models.ForeignKey(UsersPerfiles, to_field='user_perfil_id', on_delete=models.PROTECT, db_column='user_perfil_id')
    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')
    ciudad = models.CharField(max_length=150, blank=False)
    codigo = models.CharField(max_length=50, blank=False)
    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'ciudades'


class Sucursales(models.Model):
    sucursal_id = models.AutoField(primary_key=True, db_column='sucursal_id')
    ciudad_id = models.ForeignKey(Ciudades, to_field='ciudad_id', on_delete=models.PROTECT, db_column='ciudad_id')
    user_perfil_id = models.ForeignKey(UsersPerfiles, to_field='user_perfil_id', on_delete=models.PROTECT, db_column='user_perfil_id')
    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')
    sucursal = models.CharField(max_length=250, blank=False)
    codigo = models.CharField(max_length=50, blank=False)
    email = models.CharField(max_length=250, blank=False)
    empresa = models.CharField(max_length=250, blank=False)
    direccion = models.CharField(max_length=250, blank=False)
    ciudad = models.CharField(max_length=250, blank=False)
    telefonos = models.CharField(max_length=250, blank=False)
    actividad = models.CharField(max_length=250, blank=False)

    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'sucursales'


class Puntos(models.Model):
    punto_id = models.AutoField(primary_key=True, db_column='punto_id')
    sucursal_id = models.ForeignKey(Sucursales, to_field='sucursal_id', on_delete=models.PROTECT, db_column='sucursal_id')
    user_perfil_id = models.ForeignKey(UsersPerfiles, to_field='user_perfil_id', on_delete=models.PROTECT, db_column='user_perfil_id')
    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')
    punto = models.CharField(max_length=150, blank=False)
    codigo = models.CharField(max_length=50, blank=False)
    impresora_reportes = models.CharField(max_length=250, blank=False)
    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'puntos'


class TiposMonedas(models.Model):
    tipo_moneda_id = models.IntegerField(primary_key=True, db_column='tipo_moneda_id')
    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')
    tipo_moneda = models.CharField(max_length=150, blank=False)
    codigo = models.CharField(max_length=50, blank=False)

    class Meta:
        db_table = 'tipos_monedas'


class Monedas(models.Model):
    moneda_id = models.IntegerField(primary_key=True, db_column='moneda_id')
    tipo_moneda_id = models.ForeignKey(TiposMonedas, to_field='tipo_moneda_id', on_delete=models.PROTECT, db_column='tipo_moneda_id')
    monto = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')

    class Meta:
        db_table = 'monedas'


class Cajas(models.Model):
    caja_id = models.AutoField(primary_key=True, db_column='caja_id')
    punto_id = models.ForeignKey(Puntos, to_field='punto_id', on_delete=models.PROTECT, db_column='punto_id')
    tipo_moneda_id = models.ForeignKey(TiposMonedas, to_field='tipo_moneda_id', on_delete=models.PROTECT, db_column='tipo_moneda_id')
    user_perfil_id = models.ForeignKey(UsersPerfiles, to_field='user_perfil_id', on_delete=models.PROTECT, db_column='user_perfil_id')
    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')
    caja = models.CharField(max_length=150, blank=False)
    codigo = models.CharField(max_length=50, blank=False)
    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'cajas'


class CobrosMensuales(models.Model):
    cobro_mensual_id = models.AutoField(primary_key=True, db_column='cobro_mensual_id')
    cobro_mensual = models.CharField(max_length=150, blank=False, null=False, default='')
    codigo = models.CharField(max_length=20, blank=False, null=False, default='')
    monto_bs = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False, default=0)
    monto_cobrar = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False, default=0)

    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')
    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'cobros_mensuales'


class CobrosManuales(models.Model):
    cobro_manual_id = models.AutoField(primary_key=True, db_column='cobro_manual_id')
    cobro_manual = models.CharField(max_length=150, blank=False, null=False, default='')
    codigo = models.CharField(max_length=20, blank=False, null=False, default='')
    monto_porcentaje = models.CharField(max_length=20, blank=False, null=False, default='')
    monto_bs = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False, default=0)
    porcentaje = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False, default=0)
    cobro_mensual_id = models.IntegerField(db_column='cobro_mensual_id')

    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')
    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'cobros_manuales'
