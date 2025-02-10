from django.contrib import admin
from .models import (
    Profile,
    Departamento,
    Provincia,
    Distrito,
    Origen,
    TipoContacto,
    SubtipoContacto,
    Transferencia,
    TipoVivienda,
    TipoBase,
    TipoPlanContrato,
    Sector,
    Lead,
    Documento,
    TipoDocumento,
    Contrato,
    HistorialLead,
)


# Configuración para Profile
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'telefono', 'direccion', 'fecha_creacion')
    search_fields = ('user__username', 'user__email', 'telefono', 'direccion')
    ordering = ('user__username',)


admin.site.register(Profile, ProfileAdmin)


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


# Configuración para Sector
class SectorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_sector')
    search_fields = ('nombre_sector',)
    ordering = ('nombre_sector',)


admin.site.register(Sector, SectorAdmin)


# Configuración para Lead
class LeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido', 'numero_movil', 'origen', 'dueno', 'estado', 'coordenadas', 'resultado_cobertura')  # 🔥 Agregado resultado_cobertura
    list_filter = ('origen', 'dueno', 'resultado_cobertura')  # 🔥 Agregado filtro por cobertura
    search_fields = ('nombre', 'apellido', 'numero_movil', 'correo', 'direccion', 'resultado_cobertura')  # 🔥 Búsqueda por cobertura
    ordering = ('nombre',)


admin.site.register(Lead, LeadAdmin)


# Configuración para Documento
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_documento', 'numero_documento', 'lead', 'user')
    list_filter = ('tipo_documento',)
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
    list_display = (
        'id', 'nombre_contrato', 'nombre', 'apellido', 'numero_movil',  # ✅ Agregado número móvil
        'plan_contrato', 'tipo_documento', 'numero_documento', 'origen',
        'coordenadas', 'lead', 'fecha_inicio', 'observaciones'
    )
    list_filter = ('fecha_inicio', 'origen', 'plan_contrato')
    search_fields = ('nombre_contrato', 'nombre', 'apellido', 'numero_movil', 'numero_documento')  # ✅ Agregado número móvil
    ordering = ('fecha_inicio',)


admin.site.register(Contrato, ContratoAdmin)


# Configuración para HistorialLead
class HistorialLeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead', 'usuario', 'fecha', 'descripcion', 'tipo_contacto', 'subtipo_contacto')  # ✅ Agregado
    list_filter = ('usuario', 'fecha', 'tipo_contacto', 'subtipo_contacto')  # ✅ Agregado
    search_fields = ('lead__nombre', 'usuario__username', 'descripcion', 'tipo_contacto__nombre_tipo', 'subtipo_contacto__descripcion')  # ✅ Agregado
    ordering = ('fecha',)


admin.site.register(HistorialLead, HistorialLeadAdmin)


# Personalización global del administrador
admin.site.site_header = "Administración del CRM"
admin.site.site_title = "CRM Panel"
admin.site.index_title = "Bienvenido al Panel de Administración del CRM"
