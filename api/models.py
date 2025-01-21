from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

# Custom User Model
class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    nombres = models.CharField(max_length=100, blank=True, null=True)  # Nuevo campo
    apellidos = models.CharField(max_length=100, blank=True, null=True)  # Nuevo campo
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # Define username como identificador principal
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']  # El correo sigue siendo obligatorio

    # Agrega related_name para evitar conflictos
    groups = models.ManyToManyField(
        Group,
        related_name="customuser_groups",
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_permissions",
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_query_name="customuser",
    )

    def __str__(self):
        return self.username

# Estado Model
class Estado(models.Model):
    nombre_estado = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_estado

# Departamento Model
class Departamento(models.Model):
    nombre_departamento = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre_departamento

# Provincia Model
class Provincia(models.Model):
    nombre_provincia = models.CharField(max_length=100)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_provincia

# Distrito Model
class Distrito(models.Model):
    nombre_distrito = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_distrito

# Origen Model
class Origen(models.Model):
    nombre_origen = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_origen

# TipoContacto Model
class TipoContacto(models.Model):
    nombre_tipo = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre_tipo

# SubtipoContacto Model
class SubtipoContacto(models.Model):
    descripcion = models.CharField(max_length=100, unique=True)
    tipo_contacto = models.ForeignKey(TipoContacto, on_delete=models.CASCADE)

    def __str__(self):
        return self.descripcion

# ResultadoCobertura Model
class ResultadoCobertura(models.Model):
    descripcion = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.descripcion

# Transferencia Model
class Transferencia(models.Model):
    descripcion = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.descripcion

# TipoVivienda Model
class TipoVivienda(models.Model):
    descripcion = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.descripcion

# TipoBase Model
class TipoBase(models.Model):
    descripcion = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.descripcion

# TipoPlanContrato Model
class TipoPlanContrato(models.Model):
    descripcion = models.CharField(max_length=100, unique=True)
    detalles = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.descripcion

# Sector Model
class Sector(models.Model):
    nombre_sector = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre_sector

# Lead Model
class Lead(models.Model):
    nombre_lead = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    numero_movil = models.CharField(max_length=15, blank=True, null=True)
    numero_trabajo = models.CharField(max_length=15, blank=True, null=True)
    numero_fax = models.CharField(max_length=15, blank=True, null=True)
    nombre_compania = models.CharField(max_length=100, blank=True, null=True)
    correo = models.EmailField(max_length=100, blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    origen = models.ForeignKey(Origen, on_delete=models.CASCADE)
    subtipo_contacto = models.ForeignKey(SubtipoContacto, on_delete=models.CASCADE)
    resultado_cobertura = models.ForeignKey(ResultadoCobertura, on_delete=models.SET_NULL, null=True, blank=True)
    transferencia = models.ForeignKey(Transferencia, on_delete=models.SET_NULL, null=True, blank=True)
    tipo_vivienda = models.ForeignKey(TipoVivienda, on_delete=models.SET_NULL, null=True, blank=True)
    tipo_base = models.ForeignKey(TipoBase, on_delete=models.SET_NULL, null=True, blank=True)
    plan_contrato = models.ForeignKey(TipoPlanContrato, on_delete=models.SET_NULL, null=True, blank=True)
    distrito = models.ForeignKey(Distrito, on_delete=models.SET_NULL, null=True, blank=True)
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    etiquetas = models.TextField(blank=True, null=True)
    sitio_web = models.URLField(max_length=100, blank=True, null=True)
    skype = models.CharField(max_length=100, blank=True, null=True)
    facebook = models.URLField(max_length=100, blank=True, null=True)
    twitter = models.URLField(max_length=100, blank=True, null=True)
    linkedin = models.URLField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    coordenadas = models.CharField(max_length=100, blank=True, null=True)
    dueno = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_lead

# Documento Model
class Documento(models.Model):
    tipo_documento = models.ForeignKey('TipoDocumento', on_delete=models.CASCADE)
    numero_documento = models.CharField(max_length=20, unique=True)
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.numero_documento

# TipoDocumento Model
class TipoDocumento(models.Model):
    nombre_tipo = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_tipo

# Contrato Model
class Contrato(models.Model):
    nombre_contrato = models.CharField(max_length=100)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_contrato
