from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Sector, Lead, Estado, Origen, TipoContacto,
    SubtipoContacto, ResultadoCobertura, Transferencia,
    TipoVivienda, TipoBase, TipoPlanContrato, Documento,
    TipoDocumento, Contrato, Departamento, Provincia, Distrito
)

# Configuración personalizada para CustomUser
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('nombres', 'apellidos', 'telefono')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'nombres', 'apellidos', 'telefono', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'nombres', 'apellidos', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'nombres', 'apellidos')
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)

# Configuración para Sector
class SectorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_sector')
    search_fields = ('nombre_sector',)
    ordering = ('nombre_sector',)

admin.site.register(Sector, SectorAdmin)

# Configuración para Lead
class LeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_lead', 'nombre', 'apellido', 'correo', 'estado', 'origen', 'sector')
    list_filter = ('estado', 'origen', 'sector')
    search_fields = ('nombre_lead', 'nombre', 'apellido', 'correo')
    ordering = ('nombre_lead',)
    list_per_page = 20

admin.site.register(Lead, LeadAdmin)

# Configuración para Estado
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_estado', 'descripcion')
    search_fields = ('nombre_estado',)
    ordering = ('nombre_estado',)

admin.site.register(Estado, EstadoAdmin)

# Configuración para Origen
class OrigenAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_origen', 'descripcion')
    search_fields = ('nombre_origen',)
    ordering = ('nombre_origen',)

admin.site.register(Origen, OrigenAdmin)

# Configuración para TipoContacto
class TipoContactoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_tipo')
    search_fields = ('nombre_tipo',)
    ordering = ('nombre_tipo',)

admin.site.register(TipoContacto, TipoContactoAdmin)

# Configuración para SubtipoContacto
class SubtipoContactoAdmin(admin.ModelAdmin):
    list_display = ('id', 'descripcion', 'tipo_contacto')
    list_filter = ('tipo_contacto',)
    search_fields = ('descripcion',)
    ordering = ('descripcion',)

admin.site.register(SubtipoContacto, SubtipoContactoAdmin)

# Configuración para ResultadoCobertura
class ResultadoCoberturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'descripcion')
    search_fields = ('descripcion',)
    ordering = ('descripcion',)

admin.site.register(ResultadoCobertura, ResultadoCoberturaAdmin)

# Configuración para Transferencia
class TransferenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'descripcion')
    search_fields = ('descripcion',)
    ordering = ('descripcion',)

admin.site.register(Transferencia, TransferenciaAdmin)

# Configuración para TipoVivienda
class TipoViviendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'descripcion')
    search_fields = ('descripcion',)
    ordering = ('descripcion',)

admin.site.register(TipoVivienda, TipoViviendaAdmin)

# Configuración para TipoBase
class TipoBaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'descripcion')
    search_fields = ('descripcion',)
    ordering = ('descripcion',)

admin.site.register(TipoBase, TipoBaseAdmin)

# Configuración para TipoPlanContrato
class TipoPlanContratoAdmin(admin.ModelAdmin):
    list_display = ('id', 'descripcion', 'detalles')
    search_fields = ('descripcion',)
    ordering = ('descripcion',)

admin.site.register(TipoPlanContrato, TipoPlanContratoAdmin)

# Configuración para Documento
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_documento', 'numero_documento', 'lead', 'user')
    list_filter = ('tipo_documento', 'user')
    search_fields = ('numero_documento', 'lead__nombre', 'user__username')
    ordering = ('numero_documento',)

admin.site.register(Documento, DocumentoAdmin)

# Configuración para TipoDocumento
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_tipo', 'descripcion')
    search_fields = ('nombre_tipo',)
    ordering = ('nombre_tipo',)

admin.site.register(TipoDocumento, TipoDocumentoAdmin)

# Configuración para Contrato
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_contrato', 'lead', 'fecha_inicio', 'fecha_fin', 'estado')
    list_filter = ('estado', 'fecha_inicio', 'fecha_fin')
    search_fields = ('nombre_contrato', 'lead__nombre')
    ordering = ('fecha_inicio',)

admin.site.register(Contrato, ContratoAdmin)

# Configuración para Departamento
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_departamento')
    search_fields = ('nombre_departamento',)
    ordering = ('nombre_departamento',)

admin.site.register(Departamento, DepartamentoAdmin)

# Configuración para Provincia
class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_provincia', 'departamento')
    list_filter = ('departamento',)
    search_fields = ('nombre_provincia',)
    ordering = ('nombre_provincia',)

admin.site.register(Provincia, ProvinciaAdmin)

# Configuración para Distrito
class DistritoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_distrito', 'provincia')
    list_filter = ('provincia',)
    search_fields = ('nombre_distrito',)
    ordering = ('nombre_distrito',)

admin.site.register(Distrito, DistritoAdmin)

# Personalización global del administrador
admin.site.site_header = "Administración del CRM"
admin.site.site_title = "CRM Panel"
admin.site.index_title = "Bienvenido al Panel de Administración del CRM"
