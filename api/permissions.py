from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Permiso para usuarios del grupo 'Administradores' o que sean staff.
    """
    message = "No tienes permiso para realizar esta acción."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.is_staff or request.user.groups.filter(name="Administradores").exists())
        )


class IsATC(permissions.BasePermission):
    """
    Permiso para usuarios del grupo 'ATC' o que sean staff.
    """
    message = "No tienes permiso para realizar esta acción."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.is_staff or request.user.groups.filter(name="ATC").exists())
        )


class IsOperador(permissions.BasePermission):
    """
    Permiso para usuarios del grupo 'Operadores' o que sean staff.
    """
    message = "No tienes permiso para realizar esta acción."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.is_staff or request.user.groups.filter(name="Operadores").exists())
        )


class IsRetenciones(permissions.BasePermission):
    """
    Permiso para usuarios del grupo 'Retenciones' o que sean staff.
    """
    message = "No tienes permiso para realizar esta acción."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.is_staff or request.user.groups.filter(name="Retenciones").exists())
        )
