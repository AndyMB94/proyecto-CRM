from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import (
    Profile, Departamento, Provincia, Distrito, Origen, TipoContacto,
    SubtipoContacto, ResultadoCobertura, Transferencia, TipoVivienda,
    TipoBase, TipoPlanContrato, Sector, Lead, Documento, TipoDocumento,
    Contrato, HistorialLead
)
from django.contrib.auth.models import User


# 🔹 Serializer para obtener el Token JWT con información adicional
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

        user = authenticate(request=self.context.get('request'), username=username, password=password)

        if not user:
            raise AuthenticationFailed("Credenciales inválidas", code='authorization')

        if not user.is_active:
            raise AuthenticationFailed("Cuenta inactiva", code='authorization')

        data = super().validate(attrs)
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }

        if hasattr(user, 'profile'):
            user_data.update({
                "telefono": user.profile.telefono,
                "direccion": user.profile.direccion,
            })

        data['user'] = user_data
        return data


# 🔹 Serializer para Usuario y Perfil
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['telefono', 'direccion', 'fecha_creacion']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name', 'profile']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        user = User.objects.create_user(**validated_data)

        # Asociar perfil con los datos proporcionados
        Profile.objects.filter(user=user).update(**profile_data)

        return user


# 🔹 Serializers para Ubicación
class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = ['id', 'nombre_departamento']


class ProvinciaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Provincia
        fields = ['id', 'nombre_provincia']


class DistritoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Distrito
        fields = ['id', 'nombre_distrito']


# 🔹 Serializers para Origen y Tipos de Contacto
class OrigenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Origen
        fields = ['id', 'nombre_origen', 'descripcion']


class TipoContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoContacto
        fields = ['id', 'nombre_tipo']


class SubtipoContactoSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubtipoContacto
        fields = ['id', 'descripcion']


# 🔹 Serializers para Tipos de Clasificación
class ResultadoCoberturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoCobertura
        fields = ['id', 'descripcion']


class TransferenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transferencia
        fields = ['id', 'descripcion']


class TipoViviendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoVivienda
        fields = ['id', 'descripcion']


class TipoBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoBase
        fields = ['id', 'descripcion']


class TipoPlanContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPlanContrato
        fields = ['id', 'descripcion', 'detalles']


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = ['id', 'nombre_sector']


# 🔹 Serializer para Leads
class LeadSerializer(serializers.ModelSerializer):
    dueno = serializers.SerializerMethodField()  # ✅ Muestra el nombre y apellido del dueño

    class Meta:
        model = Lead
        fields = [
            'id', 'nombre', 'apellido', 'numero_movil', 'nombre_compania',
            'correo', 'cargo', 'origen', 'subtipo_contacto', 'resultado_cobertura',
            'transferencia', 'tipo_vivienda', 'tipo_base', 'plan_contrato',
            'distrito', 'sector', 'direccion', 'coordenadas', 'dueno', 'fecha_creacion', 'estado'
        ]
        extra_kwargs = {
            'numero_movil': {'required': True},  # ✅ Solo este campo es obligatorio
            'dueno': {'read_only': True},
        }
    
    def get_dueno(self, obj):
        """ 🔥 Devuelve el nombre completo del dueño en vez de solo el ID """
        if obj.dueno:
            return f"{obj.dueno.first_name} {obj.dueno.last_name}"  # ✅ Retorna 'Nombre Apellido'
        return None  # En caso de que no haya dueño

    def validate_numero_movil(self, value):
        """ 🔥 Valida que el número tenga al menos 9 dígitos y sea único """
        if len(value) < 9:
            raise serializers.ValidationError("El número móvil debe tener al menos 9 dígitos.")
        if Lead.objects.filter(numero_movil=value).exists():
            raise serializers.ValidationError("El número móvil ya está registrado.")
        return value

    def validate_correo(self, value):
        """ 🔥 Valida formato de correo electrónico """
        if value and not serializers.EmailField().run_validation(value):
            raise serializers.ValidationError("El correo electrónico no es válido.")
        return value

    def validate(self, data):
        """ 🔥 Validaciones adicionales para subtipo_contacto y transferencia """
        subtipo_contacto = data.get("subtipo_contacto")
        transferencia = data.get("transferencia")

        if subtipo_contacto:
            tipo_contacto = subtipo_contacto.tipo_contacto
            if tipo_contacto.nombre_tipo == "No Contacto" and subtipo_contacto.descripcion == "Transferencia":
                if not transferencia:
                    raise ValidationError({
                        "transferencia": "El campo 'transferencia' es obligatorio cuando el subtipo de contacto es 'Transferencia'."
                    })

        # 🔥 Si no hay `numero_movil`, el lead NO se crea
        if "numero_movil" not in data or not data["numero_movil"]:
            raise serializers.ValidationError({"numero_movil": "Este campo es obligatorio para crear un lead."})

        return data


# 🔹 Serializer para Contratos
class ContratoSerializer(serializers.ModelSerializer):
    lead = serializers.PrimaryKeyRelatedField(queryset=Lead.objects.all())

    class Meta:
        model = Contrato
        fields = [
            'id', 'nombre_contrato', 'nombre', 'apellido', 'numero_movil', 'plan_contrato',
            'tipo_documento', 'numero_documento', 'origen', 'coordenadas',
            'fecha_inicio', 'observaciones', 'lead'
        ]



# 🔹 Serializer para Documentos
class DocumentoSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    lead = LeadSerializer()
    tipo_documento = serializers.StringRelatedField()

    class Meta:
        model = Documento
        fields = ['id', 'tipo_documento', 'numero_documento', 'lead', 'user']


# 🔹 Serializer para Tipos de Documentos
class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = ['id', 'nombre_tipo', 'descripcion']


# 🔹 Serializer para Historial de Leads
class HistorialLeadSerializer(serializers.ModelSerializer):
    usuario = UserSerializer()
    lead = serializers.PrimaryKeyRelatedField(read_only=True)
    tipo_contacto = serializers.StringRelatedField()  # 🔥 Muestra el nombre del tipo de contacto
    subtipo_contacto = serializers.StringRelatedField()  # 🔥 Muestra la descripción del subtipo de contacto

    class Meta:
        model = HistorialLead
        fields = ['id', 'lead', 'usuario', 'tipo_contacto', 'subtipo_contacto', 'descripcion', 'fecha']


# 🔹 Serializer para Leads y Contratos por Origen
class LeadsYContratosPorOrigenSerializer(serializers.Serializer):
    origen = serializers.CharField()
    total_leads = serializers.IntegerField()
    total_contratos = serializers.IntegerField()


# 🔹 Serializer genérico para modelos con solo ID y nombre
class GenericSerializer(serializers.ModelSerializer):
    nombre = serializers.SerializerMethodField()

    class Meta:
        model = None  # Se asignará dinámicamente en la vista
        fields = ['id', 'nombre']

    def get_nombre(self, obj):
        return str(obj)  # Usa la representación en string del objeto