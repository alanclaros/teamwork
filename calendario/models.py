from django.db import models
from status.models import Status
from utils.custome_db_types import DateTimeFieldCustome, DateFieldCustome
from permisos.models import UsersPerfiles
from departamentos.models import Departamentos


class Actividades(models.Model):
    actividad_id = models.AutoField(primary_key=True, db_column='actividad_id')
    actividad = models.CharField(max_length=150, blank=False, null=False, default='')
    codigo = models.CharField(max_length=50, blank=False, null=False, default='')
    color_hex = models.CharField(max_length=50, blank=False, null=False, default='')
    color_txt = models.CharField(max_length=50, blank=False, null=False, default='')

    user_perfil_id = models.ForeignKey(UsersPerfiles, to_field='user_perfil_id', on_delete=models.PROTECT, db_column='user_perfil_id')
    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')

    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'actividades'


class Calendario(models.Model):
    calendario_id = models.AutoField(primary_key=True, db_column='calendario_id')
    actividad_id = models.ForeignKey(Actividades, to_field='actividad_id', on_delete=models.PROTECT, db_column='actividad_id')
    fecha_actividad_ini = DateTimeFieldCustome(null=True, blank=True)
    fecha_actividad_fin = DateTimeFieldCustome(null=True, blank=True)
    departamento_id = models.IntegerField(blank=False, null=False, default=0)

    user_perfil_id_reserva = models.IntegerField(blank=False, null=False, default=0)
    fecha_reserva = DateTimeFieldCustome(null=True, blank=True)

    detalle = models.CharField(max_length=250, blank=False, null=False)
    observacion = models.CharField(max_length=250, blank=False, null=False)

    user_perfil_id_confirma = models.IntegerField(blank=False, null=False, default=0)
    fecha_confirma = DateTimeFieldCustome(null=True, blank=True)

    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')

    user_perfil_id_anula = models.IntegerField(null=True, blank=True, default=0)
    fecha_anula = DateTimeFieldCustome(null=True, blank=True)
    motivo_anula = models.CharField(max_length=250, null=True, blank=True)

    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'calendario'
