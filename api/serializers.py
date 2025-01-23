from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Lead, HistorialEstado


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Agrega campos adicionales al token
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        token['nombres'] = user.nombres  # Incluye el nombre
        token['apellidos'] = user.apellidos  # Incluye el apellido
        token['telefono'] = user.telefono  # Incluye el teléfono
        return token

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if not username or not password:
            raise AuthenticationFailed("Se requieren username y password")

        # Autenticación con username
        user = authenticate(request=self.context.get('request'), username=username, password=password)

        if not user:
            raise AuthenticationFailed("Credenciales inválidas", code='authorization')

        if not user.is_active:
            raise AuthenticationFailed("Cuenta inactiva", code='authorization')

        # Retorna el token generado
        data = super().validate(attrs)
        data['user'] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "nombres": user.nombres,
            "apellidos": user.apellidos,
            "telefono": user.telefono,
        }
        return data


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            'id',
            'nombre_lead',
            'nombre',
            'apellido',
            'numero_movil',
            'numero_trabajo',
            'nombre_compania',
            'correo',
            'cargo',
            'estado',
            'origen',
            'subtipo_contacto',
            'resultado_cobertura',
            'transferencia',
            'tipo_vivienda',
            'tipo_base',
            'plan_contrato',
            'distrito',
            'sector',
            'direccion',
            'etiquetas',
            'coordenadas',
            'dueno',
            'fecha_creacion',
        ]

class HistorialEstadoSerializer(serializers.ModelSerializer):
    estado_anterior = serializers.StringRelatedField()
    estado_nuevo = serializers.StringRelatedField()
    usuario = serializers.StringRelatedField()

    class Meta:
        model = HistorialEstado
        fields = ['id', 'lead', 'estado_anterior', 'estado_nuevo', 'usuario', 'fecha_cambio']