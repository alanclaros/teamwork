from django.db import models
from status.models import Status
from utils.custome_db_types import DateTimeFieldCustome, DateFieldCustome
from permisos.models import UsersPerfiles
from departamentos.models import Departamentos
from configuraciones.models import CobrosManuales, CobrosMensuales, Puntos, Cajas


class Lecturas(models.Model):
    lectura_id = models.AutoField(primary_key=True, db_column='lectura_id')
    departamento_id = models.ForeignKey(Departamentos, to_field='departamento_id', on_delete=models.PROTECT, db_column='departamento_id')

    periodo = models.CharField(max_length=20, blank=False, null=False)
    lectura = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    costo_m3 = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    consumo = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    observacion = models.CharField(max_length=250, blank=False, null=False)

    metros2 = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    costo_expensas_m2 = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    total_expensas = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)

    fecha_cobro = DateTimeFieldCustome(null=True, blank=True)
    user_perfil_id_cobro = models.IntegerField(null=True, blank=True, default=0)
    punto_id = models.IntegerField(blank=False, null=False, default=0)
    caja_id = models.IntegerField(blank=False, null=False, default=0)

    user_perfil_id = models.ForeignKey(UsersPerfiles, to_field='user_perfil_id', on_delete=models.PROTECT, db_column='user_perfil_id')
    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')

    user_perfil_id_anula = models.IntegerField(null=True, blank=True)
    motivo_anula = models.CharField(max_length=250, null=True, blank=True)

    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'lecturas'


class LecturasAnulados(models.Model):
    lectura_anulado_id = models.AutoField(primary_key=True, db_column='lectura_anulado_id')
    lectura_id = models.IntegerField(blank=False, null=False, default=0)
    departamento_id = models.ForeignKey(Departamentos, to_field='departamento_id', on_delete=models.PROTECT, db_column='departamento_id')

    periodo = models.CharField(max_length=20, blank=False, null=False)
    lectura = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    costo_m3 = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    consumo = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    observacion = models.CharField(max_length=250, blank=False, null=False)

    metros2 = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    costo_expensas_m2 = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    total_expensas = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)

    fecha_cobro = DateTimeFieldCustome(null=True, blank=True)
    user_perfil_id_cobro = models.IntegerField(null=True, blank=True, default=0)
    punto_id = models.IntegerField(blank=False, null=False, default=0)
    caja_id = models.IntegerField(blank=False, null=False, default=0)

    user_perfil_id = models.ForeignKey(UsersPerfiles, to_field='user_perfil_id', on_delete=models.PROTECT, db_column='user_perfil_id')
    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')

    user_perfil_id_anula = models.IntegerField(null=True, blank=True)
    motivo_anula = models.CharField(max_length=250, null=True, blank=True)

    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'lecturas_anulados'


class Cobros(models.Model):
    cobro_id = models.AutoField(primary_key=True, db_column='cobro_id')
    departamento_id = models.ForeignKey(Departamentos, to_field='departamento_id', on_delete=models.PROTECT, db_column='departamento_id')

    fecha_cobro = DateTimeFieldCustome(null=True, blank=True)
    monto_bs = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    periodo = models.CharField(max_length=20, null=False, blank=False)
    observacion = models.CharField(max_length=250, null=False, blank=False)
    user_perfil_id_cobro = models.IntegerField(null=True, blank=True, default=0)
    punto_id = models.IntegerField(null=True, blank=True, default=0)
    caja_id = models.IntegerField(null=True, blank=True, default=0)
    user_perfil_id = models.ForeignKey(UsersPerfiles, to_field='user_perfil_id', on_delete=models.PROTECT, db_column='user_perfil_id')
    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')

    user_perfil_id_anula = models.IntegerField(null=True, blank=True)
    motivo_anula = models.CharField(max_length=250, null=True, blank=True)

    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'cobros'


class CobrosAnulados(models.Model):
    cobro_anulado_id = models.AutoField(primary_key=True, db_column='cobro_anulado_id')
    cobro_id = models.IntegerField(blank=False, null=False, default=0)

    departamento_id = models.ForeignKey(Departamentos, to_field='departamento_id', on_delete=models.PROTECT, db_column='departamento_id')

    fecha_cobro = DateTimeFieldCustome(null=True, blank=True)
    monto_bs = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    periodo = models.CharField(max_length=20, null=False, blank=False)
    observacion = models.CharField(max_length=250, null=False, blank=False)
    user_perfil_id_cobro = models.IntegerField(null=True, blank=True, default=0)
    punto_id = models.IntegerField(null=True, blank=True, default=0)
    caja_id = models.IntegerField(null=True, blank=True, default=0)
    user_perfil_id = models.ForeignKey(UsersPerfiles, to_field='user_perfil_id', on_delete=models.PROTECT, db_column='user_perfil_id')
    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')

    user_perfil_id_anula = models.IntegerField(null=True, blank=True)
    motivo_anula = models.CharField(max_length=250, null=True, blank=True)

    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'cobros_anulados'


class CobrosMensualesPeriodos(models.Model):
    cobro_mensual_periodo_id = models.AutoField(primary_key=True, db_column='cobro_mensual_periodo_id')
    cobro_mensual_id = models.ForeignKey(CobrosMensuales, to_field='cobro_mensual_id', on_delete=models.PROTECT, db_column='cobro_mensual_id')

    periodo = models.CharField(max_length=20, null=False, blank=False)
    monto_bs = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    user_perfil_id = models.ForeignKey(UsersPerfiles, to_field='user_perfil_id', on_delete=models.PROTECT, db_column='user_perfil_id')
    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')

    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'cobros_mensuales_periodos'


class CobrosCobrosMensuales(models.Model):
    cobro_cobro_mensual_id = models.AutoField(primary_key=True, db_column='cobro_cobro_mensual_id')
    departamento_id = models.ForeignKey(Departamentos, to_field='departamento_id', on_delete=models.PROTECT, db_column='departamento_id')
    cobro_mensual_id = models.ForeignKey(CobrosMensuales, to_field='cobro_mensual_id', on_delete=models.PROTECT, db_column='cobro_mensual_id')

    fecha_cobro = DateTimeFieldCustome(null=True, blank=True)
    monto_bs = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    periodo = models.CharField(max_length=20, null=False, blank=False)
    observacion = models.CharField(max_length=250, null=False, blank=False)
    user_perfil_id_cobro = models.IntegerField(null=True, blank=True, default=0)
    punto_id = models.IntegerField(null=True, blank=True, default=0)
    caja_id = models.IntegerField(null=True, blank=True, default=0)
    user_perfil_id = models.ForeignKey(UsersPerfiles, to_field='user_perfil_id', on_delete=models.PROTECT, db_column='user_perfil_id')
    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')

    user_perfil_id_anula = models.IntegerField(null=True, blank=True)
    motivo_anula = models.CharField(max_length=250, null=True, blank=True)

    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'cobros_cobros_mensuales'


class CobrosCobrosMensualesAnulados(models.Model):
    cobro_cobro_mensual_anulado_id = models.AutoField(primary_key=True, db_column='cobro_cobro_mensual_anulado_id')
    cobro_cobro_mensual_id = models.IntegerField(blank=False, null=False, default=0)

    departamento_id = models.ForeignKey(Departamentos, to_field='departamento_id', on_delete=models.PROTECT, db_column='departamento_id')
    cobro_mensual_id = models.ForeignKey(CobrosMensuales, to_field='cobro_mensual_id', on_delete=models.PROTECT, db_column='cobro_mensual_id')

    fecha_cobro = DateTimeFieldCustome(null=True, blank=True)
    monto_bs = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    periodo = models.CharField(max_length=20, null=False, blank=False)
    observacion = models.CharField(max_length=250, null=False, blank=False)
    user_perfil_id_cobro = models.IntegerField(null=True, blank=True, default=0)
    punto_id = models.IntegerField(null=True, blank=True, default=0)
    caja_id = models.IntegerField(null=True, blank=True, default=0)
    user_perfil_id = models.ForeignKey(UsersPerfiles, to_field='user_perfil_id', on_delete=models.PROTECT, db_column='user_perfil_id')
    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')

    user_perfil_id_anula = models.IntegerField(null=True, blank=True)
    motivo_anula = models.CharField(max_length=250, null=True, blank=True)

    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'cobros_cobros_mensuales_anulados'


class CobrosCobrosManuales(models.Model):
    cobro_cobro_manual_id = models.AutoField(primary_key=True, db_column='cobro_cobro_manual_id')
    departamento_id = models.ForeignKey(Departamentos, to_field='departamento_id', on_delete=models.PROTECT, db_column='departamento_id')
    cobro_manual_id = models.ForeignKey(CobrosManuales, to_field='cobro_manual_id', on_delete=models.PROTECT, db_column='cobro_manual_id')

    fecha_cobro = DateTimeFieldCustome(null=True, blank=True)
    monto_bs = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    periodo = models.CharField(max_length=20, null=False, blank=False)
    observacion = models.CharField(max_length=250, null=False, blank=False)
    user_perfil_id_cobro = models.IntegerField(null=True, blank=True, default=0)
    punto_id = models.IntegerField(null=True, blank=True, default=0)
    caja_id = models.IntegerField(null=True, blank=True, default=0)
    user_perfil_id = models.ForeignKey(UsersPerfiles, to_field='user_perfil_id', on_delete=models.PROTECT, db_column='user_perfil_id')
    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')

    user_perfil_id_anula = models.IntegerField(null=True, blank=True)
    motivo_anula = models.CharField(max_length=250, null=True, blank=True)

    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'cobros_cobros_manuales'


class CobrosCobrosManualesAnulados(models.Model):
    cobro_cobro_manual_anulado_id = models.AutoField(primary_key=True, db_column='cobro_cobro_manual_anulado_id')
    cobro_cobro_manual_id = models.IntegerField(blank=False, null=False, default=0)

    departamento_id = models.ForeignKey(Departamentos, to_field='departamento_id', on_delete=models.PROTECT, db_column='departamento_id')
    cobro_manual_id = models.ForeignKey(CobrosManuales, to_field='cobro_manual_id', on_delete=models.PROTECT, db_column='cobro_manual_id')

    fecha_cobro = DateTimeFieldCustome(null=True, blank=True)
    monto_bs = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    periodo = models.CharField(max_length=20, null=False, blank=False)
    observacion = models.CharField(max_length=250, null=False, blank=False)
    user_perfil_id_cobro = models.IntegerField(null=True, blank=True, default=0)
    punto_id = models.IntegerField(null=True, blank=True, default=0)
    caja_id = models.IntegerField(null=True, blank=True, default=0)
    user_perfil_id = models.ForeignKey(UsersPerfiles, to_field='user_perfil_id', on_delete=models.PROTECT, db_column='user_perfil_id')
    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')

    user_perfil_id_anula = models.IntegerField(null=True, blank=True)
    motivo_anula = models.CharField(max_length=250, null=True, blank=True)

    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'cobros_cobros_manuales_anulados'


class CobrosDetalles(models.Model):
    cobro_detalle_id = models.AutoField(primary_key=True, db_column='cobro_detalle_id')
    cobro_id = models.ForeignKey(Cobros, to_field='cobro_id', on_delete=models.PROTECT, db_column='cobro_id')

    lectura_id = models.IntegerField(null=True, blank=True, default=0)
    cobro_cobro_mensual_id = models.IntegerField(null=True, blank=True, default=0)
    cobro_cobro_manual_id = models.IntegerField(null=True, blank=True, default=0)

    monto_bs = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    periodo = models.CharField(max_length=20, null=False, blank=False)
    detalle = models.CharField(max_length=250, null=False, blank=False)
    observacion = models.CharField(max_length=250, null=False, blank=False)

    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'cobros_detalles'


class CobrosDetallesAnulados(models.Model):
    cobro_detalle_anulado_id = models.AutoField(primary_key=True, db_column='cobro_detalle_anulado_id')
    cobro_detalle_id = models.IntegerField(blank=False, null=False, default=0)

    cobro_id = models.IntegerField(blank=False, null=False, default=0)

    lectura_id = models.IntegerField(null=True, blank=True, default=0)
    cobro_cobro_mensual_id = models.IntegerField(null=True, blank=True, default=0)
    cobro_cobro_manual_id = models.IntegerField(null=True, blank=True, default=0)

    monto_bs = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    periodo = models.CharField(max_length=20, null=False, blank=False)
    detalle = models.CharField(max_length=250, null=False, blank=False)
    observacion = models.CharField(max_length=250, null=False, blank=False)

    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'cobros_detalles_anulados'
