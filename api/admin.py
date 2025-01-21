from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

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

# Registra el modelo de usuario personalizado en el admin
admin.site.register(CustomUser, CustomUserAdmin)
