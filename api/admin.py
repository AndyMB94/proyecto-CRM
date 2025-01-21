from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Sector, Lead, Estado, Origen

# Configuración personalizada para CustomUser
class CustomUserAdmin(UserAdmin):
    # Campos adicionales en la vista de edición del usuario
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('nombres', 'apellidos', 'telefono')}),
    )
    
    # Campos adicionales en la vista de creación del usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'nombres', 'apellidos', 'telefono', 'password1', 'password2'),
        }),
    )

    # Personaliza las columnas visibles en la lista de usuarios
    list_display = ('username', 'email', 'nombres', 'apellidos', 'is_staff', 'is_active')
    
    # Permite buscar por estos campos en el admin
    search_fields = ('username', 'email', 'nombres', 'apellidos')
    ordering = ('username',)

# Registra el modelo de usuario personalizado
admin.site.register(CustomUser, CustomUserAdmin)


# Configuración para Sector
class SectorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_sector')  # Columnas visibles
    search_fields = ('nombre_sector',)      # Campos de búsqueda
    ordering = ('nombre_sector',)           # Orden alfabético

admin.site.register(Sector, SectorAdmin)


# Configuración para Lead
class LeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_lead', 'nombre', 'apellido', 'correo', 'estado', 'origen', 'sector')  # Columnas visibles
    list_filter = ('estado', 'origen', 'sector')  # Filtros laterales
    search_fields = ('nombre_lead', 'nombre', 'apellido', 'correo')  # Campos de búsqueda
    ordering = ('nombre_lead',)  # Orden alfabético
    list_per_page = 20  # Paginación en la tabla

admin.site.register(Lead, LeadAdmin)


# Configuración para Estado
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_estado', 'descripcion')  # Columnas visibles
    search_fields = ('nombre_estado',)                    # Campos de búsqueda
    ordering = ('nombre_estado',)                         # Orden alfabético

admin.site.register(Estado, EstadoAdmin)


# Configuración para Origen
class OrigenAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_origen', 'descripcion')  # Columnas visibles
    search_fields = ('nombre_origen',)                    # Campos de búsqueda
    ordering = ('nombre_origen',)                         # Orden alfabético

admin.site.register(Origen, OrigenAdmin)


# Personalización global del administrador
admin.site.site_header = "Administración del CRM"
admin.site.site_title = "CRM Panel"
admin.site.index_title = "Bienvenido al Panel de Administración del CRM"
