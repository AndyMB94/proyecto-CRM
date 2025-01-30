from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Lead, HistorialLead, Documento
from django.contrib.auth.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Agrega campos adicionales al token
        token['email'] = user.email
        token['is_staff'] = user.is_staff

        # Si hay un perfil asociado, añade campos adicionales
        if hasattr(user, 'profile'):
            token['telefono'] = user.profile.telefono
            token['direccion'] = user.profile.direccion
        else:
            token['telefono'] = None
            token['direccion'] = None

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
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }

        # Incluye campos adicionales si hay un perfil asociado
        if hasattr(user, 'profile'):
            user_data.update({
                "telefono": user.profile.telefono,
                "direccion": user.profile.direccion,
            })

        data['user'] = user_data
        return data


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            'id',
            'nombre',
            'apellido',
            'numero_movil',
            'nombre_compania',
            'correo',
            'cargo',
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
            'coordenadas',
            'dueno',
            'fecha_creacion',
            'estado',
        ]

    def validate_numero_movil(self, value):
        """
        Valida que el número móvil sea único y tenga al menos 9 caracteres.
        Permite que el número móvil sea el mismo del objeto que se está actualizando.
        """
        lead_id = self.instance.id if self.instance else None
        if value and len(value) < 9:
            raise serializers.ValidationError("El número móvil debe tener al menos 9 dígitos.")
        if Lead.objects.filter(numero_movil=value).exclude(id=lead_id).exists():
            raise serializers.ValidationError("El número móvil ya está registrado.")
        return value

    def validate_correo(self, value):
        """
        Valida que el correo tenga un formato correcto.
        """
        if value and not serializers.EmailField().run_validation(value):
            raise serializers.ValidationError("El correo electrónico no es válido.")
        return value

    def validate(self, data):
        """
        Si el subtipo_contacto es "Transferencia" y pertenece a "No Contacto",
        el campo transferencia debe ser obligatorio.
        """
        subtipo_contacto = data.get("subtipo_contacto")
        transferencia = data.get("transferencia")

        if subtipo_contacto:
            tipo_contacto = subtipo_contacto.tipo_contacto
            # Verifica si pertenece a "No Contacto" y tiene el subtipo "Transferencia"
            if tipo_contacto.nombre_tipo == "No Contacto" and subtipo_contacto.descripcion == "Transferencia":
                if not transferencia:
                    raise ValidationError({
                        "transferencia": "El campo 'transferencia' es obligatorio cuando el subtipo de contacto es 'Transferencia'."
                    })

        return data


class HistorialLeadSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField()
    lead = serializers.StringRelatedField()

    class Meta:
        model = HistorialLead
        fields = ['id', 'lead', 'usuario', 'descripcion', 'fecha']
