from django.db import models
from status.models import Status
from utils.custome_db_types import DateTimeFieldCustome, DateFieldCustome
from permisos.models import UsersPerfiles


class Bloques(models.Model):
    bloque_id = models.AutoField(primary_key=True, db_column='bloque_id')
    bloque = models.CharField(max_length=150, blank=False, null=False)
    codigo = models.CharField(max_length=20, blank=False, null=False)
    ubicacion = models.CharField(max_length=250, blank=False)

    user_perfil_id = models.ForeignKey(UsersPerfiles, to_field='user_perfil_id', on_delete=models.PROTECT, db_column='user_perfil_id')
    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')

    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'bloques'


class Pisos(models.Model):
    piso_id = models.AutoField(primary_key=True, db_column='piso_id')
    piso = models.CharField(max_length=150, blank=False, null=False)
    codigo = models.CharField(max_length=20, blank=False, null=False)

    user_perfil_id = models.ForeignKey(UsersPerfiles, to_field='user_perfil_id', on_delete=models.PROTECT, db_column='user_perfil_id')
    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')

    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'pisos'


class Departamentos(models.Model):
    departamento_id = models.AutoField(primary_key=True, db_column='departamento_id')
    bloque_id = models.ForeignKey(Bloques, to_field='bloque_id', on_delete=models.PROTECT, db_column='bloque_id')
    piso_id = models.ForeignKey(Pisos, to_field='piso_id', on_delete=models.PROTECT, db_column='piso_id')

    departamento = models.CharField(max_length=150, blank=False, null=False)
    codigo = models.CharField(max_length=20, blank=False, null=False)

    propietario_apellidos = models.CharField(max_length=150, blank=False, null=False)
    propietario_nombres = models.CharField(max_length=150, blank=False, null=False)
    propietario_ci_nit = models.CharField(max_length=50, blank=False, null=False)
    propietario_fonos = models.CharField(max_length=150, blank=False, null=False)
    propietario_email = models.CharField(max_length=150, blank=False, null=False)

    copropietario_apellidos = models.CharField(max_length=150, blank=False, null=False)
    copropietario_nombres = models.CharField(max_length=150, blank=False, null=False)
    copropietario_ci_nit = models.CharField(max_length=50, blank=False, null=False)
    copropietario_fonos = models.CharField(max_length=150, blank=False, null=False)
    copropietario_email = models.CharField(max_length=150, blank=False, null=False)

    metros2 = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)

    user_perfil_id = models.ForeignKey(UsersPerfiles, to_field='user_perfil_id', on_delete=models.PROTECT, db_column='user_perfil_id')
    status_id = models.ForeignKey(Status, to_field='status_id', on_delete=models.PROTECT, db_column='status_id')

    created_at = DateTimeFieldCustome(null=True, blank=True)
    updated_at = DateTimeFieldCustome(null=True, blank=True)
    deleted_at = DateTimeFieldCustome(null=True, blank=True)

    class Meta:
        db_table = 'departamentos'
