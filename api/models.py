from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver


# Modelo Profile para datos adicionales del usuario
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación del perfil

    def __str__(self):
        return f"Perfil de {self.user.username}"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


# Modelo Departamento
class Departamento(models.Model):
    nombre_departamento = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre_departamento


# Modelo Provincia
class Provincia(models.Model):
    nombre_provincia = models.CharField(max_length=100)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_provincia


# Modelo Distrito
class Distrito(models.Model):
    nombre_distrito = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_distrito


# Modelo Origen
class Origen(models.Model):
    nombre_origen = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_origen


# Modelo TipoContacto
class TipoContacto(models.Model):
    nombre_tipo = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre_tipo


# Modelo SubtipoContacto
class SubtipoContacto(models.Model):
    descripcion = models.CharField(max_length=100, unique=True)
    tipo_contacto = models.ForeignKey(TipoContacto, on_delete=models.CASCADE)

    def __str__(self):
        return self.descripcion


# Modelo ResultadoCobertura
class ResultadoCobertura(models.Model):
    descripcion = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.descripcion


# Modelo Transferencia
class Transferencia(models.Model):
    descripcion = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.descripcion


# Modelo TipoVivienda
class TipoVivienda(models.Model):
    descripcion = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.descripcion


# Modelo TipoBase
class TipoBase(models.Model):
    descripcion = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.descripcion


# Modelo TipoPlanContrato
class TipoPlanContrato(models.Model):
    descripcion = models.CharField(max_length=100, unique=True)
    detalles = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.descripcion


# Modelo Sector
class Sector(models.Model):
    nombre_sector = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre_sector


# Modelo Lead
class Lead(models.Model):
    nombre = models.CharField(max_length=100, blank=True, null=True)
    apellido = models.CharField(max_length=100, blank=True, null=True)
    numero_movil = models.CharField(max_length=15, unique=True)
    nombre_compania = models.CharField(max_length=100, blank=True, null=True)
    correo = models.EmailField(max_length=100, blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    origen = models.ForeignKey(Origen, on_delete=models.CASCADE, blank=True, null=True)
    subtipo_contacto = models.ForeignKey(SubtipoContacto, on_delete=models.CASCADE, blank=True, null=True)
    resultado_cobertura = models.ForeignKey(ResultadoCobertura, on_delete=models.PROTECT, blank=True, null=True)
    transferencia = models.ForeignKey(Transferencia, on_delete=models.PROTECT, blank=True, null=True)
    tipo_vivienda = models.ForeignKey(TipoVivienda, on_delete=models.PROTECT, blank=True, null=True)
    tipo_base = models.ForeignKey(TipoBase, on_delete=models.SET_NULL, null=True, blank=True)
    plan_contrato = models.ForeignKey(TipoPlanContrato, on_delete=models.SET_NULL, null=True, blank=True)
    distrito = models.ForeignKey(Distrito, on_delete=models.PROTECT, blank=True, null=True)
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    coordenadas = models.CharField(max_length=100, blank=True, null=True)
    dueno = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=False)

    def clean(self):
        if self.numero_movil and len(self.numero_movil) < 9:
            raise ValidationError("El número móvil debe tener al menos 9 dígitos.")

        if self.subtipo_contacto and self.subtipo_contacto.descripcion.lower() == "transferencia" and not self.transferencia:
            raise ValidationError({
                "transferencia": "El campo 'transferencia' es obligatorio cuando el subtipo de contacto es 'Transferencia'."
            })

    def __str__(self):
        return f"{self.nombre} {self.apellido} - Estado: {'Convertido' if self.estado else 'No convertido'}"


# Modelo Documento
class Documento(models.Model):
    tipo_documento = models.ForeignKey('TipoDocumento', on_delete=models.CASCADE)
    numero_documento = models.CharField(max_length=20, unique=True)
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.numero_documento


# Modelo TipoDocumento
class TipoDocumento(models.Model):
    nombre_tipo = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_tipo


# Modelo Contrato
class Contrato(models.Model):
    nombre_contrato = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)  #  Nombre del cliente
    apellido = models.CharField(max_length=100)  #  Apellido del cliente
    plan_contrato = models.ForeignKey(TipoPlanContrato, on_delete=models.SET_NULL, null=True, blank=True)  #  Plan de contrato
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.SET_NULL, null=True, blank=True)  #  Tipo de documento
    numero_documento = models.CharField(max_length=20, blank=True, null=True)  # ✅ Número de documento
    origen = models.ForeignKey(Origen, on_delete=models.SET_NULL, null=True, blank=True)  #  Origen del lead
    coordenadas = models.CharField(max_length=100, blank=True, null=True)  #  Coordenadas
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    fecha_inicio = models.DateField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_contrato


# Modelo HistorialLead
class HistorialLead(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="historial")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()  # Descripción del cambio o interacción.
    tipo_contacto = models.ForeignKey(TipoContacto, on_delete=models.SET_NULL, null=True, blank=True)  # Nuevo campo
    subtipo_contacto = models.ForeignKey(SubtipoContacto, on_delete=models.SET_NULL, null=True, blank=True)  # Nuevo campo

    def __str__(self):
        return f"Lead: {self.lead} | {self.descripcion} | {self.fecha}"
