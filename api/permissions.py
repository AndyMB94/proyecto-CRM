from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Permiso para usuarios del grupo 'Administradores'.
    """

    message = "No tienes permiso para realizar esta acción."  # Personalizar mensaje
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name="Administradores").exists()


class IsATC(permissions.BasePermission):
    """
    Permiso para usuarios del grupo 'ATC'.
    """

    message = "No tienes permiso para realizar esta acción."  # Personalizar mensaje

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name="ATC").exists()


class IsOperador(permissions.BasePermission):
    """
    Permiso para usuarios del grupo 'Operadores'.
    """

    message = "No tienes permiso para realizar esta acción."  # Personalizar mensaje

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name="Operadores").exists()


class IsRetenciones(permissions.BasePermission):
    """
    Permiso para usuarios del grupo 'Retenciones'.
    """

    message = "No tienes permiso para realizar esta acción."  # Personalizar mensaje
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name="Retenciones").exists()
