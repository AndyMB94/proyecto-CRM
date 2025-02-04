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

    # ✅ Permitir edición de claves foráneas enviando solo el ID
    origen = serializers.PrimaryKeyRelatedField(queryset=Origen.objects.all(), required=False, allow_null=True)
    subtipo_contacto = serializers.PrimaryKeyRelatedField(queryset=SubtipoContacto.objects.all(), required=False, allow_null=True)
    resultado_cobertura = serializers.PrimaryKeyRelatedField(queryset=ResultadoCobertura.objects.all(), required=False, allow_null=True)
    transferencia = serializers.PrimaryKeyRelatedField(queryset=Transferencia.objects.all(), required=False, allow_null=True)
    tipo_vivienda = serializers.PrimaryKeyRelatedField(queryset=TipoVivienda.objects.all(), required=False, allow_null=True)
    tipo_base = serializers.PrimaryKeyRelatedField(queryset=TipoBase.objects.all(), required=False, allow_null=True)
    plan_contrato = serializers.PrimaryKeyRelatedField(queryset=TipoPlanContrato.objects.all(), required=False, allow_null=True)
    distrito = serializers.PrimaryKeyRelatedField(queryset=Distrito.objects.all(), required=False, allow_null=True)
    sector = serializers.PrimaryKeyRelatedField(queryset=Sector.objects.all(), required=False, allow_null=True)
    tipo_contacto = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = [
            'id', 'nombre', 'apellido', 'numero_movil', 'nombre_compania',
            'correo', 'cargo', 'origen', 'tipo_contacto', 'subtipo_contacto', 'resultado_cobertura',
            'transferencia', 'tipo_vivienda', 'tipo_base', 'plan_contrato',
            'distrito', 'sector', 'direccion', 'coordenadas', 'dueno', 'fecha_creacion', 'estado'
        ]
        extra_kwargs = {
            'numero_movil': {'required': True},  # ✅ Solo este campo es obligatorio
            'dueno': {'read_only': True},
        }

    def get_tipo_contacto(self, obj):
        """
        Devuelve el tipo de contacto asociado al subtipo de contacto del lead.
        """
        if obj.subtipo_contacto and obj.subtipo_contacto.tipo_contacto:
            return {
                "id": obj.subtipo_contacto.tipo_contacto.id,
                "nombre_tipo": obj.subtipo_contacto.tipo_contacto.nombre_tipo
            }
        return None  # Si no hay subtipo de contacto, devuelve None
    
    def get_dueno(self, obj):
        """ 🔥 Devuelve el nombre completo del dueño """
        return f"{obj.dueno.first_name} {obj.dueno.last_name}" if obj.dueno else None

    # 🔥 Métodos personalizados para devolver ID y Nombre respetando nombres de tablas
    def get_origen(self, obj):
        return {"id": obj.origen.id, "nombre_origen": obj.origen.nombre_origen} if obj.origen else None

    def get_subtipo_contacto(self, obj):
        return {"id": obj.subtipo_contacto.id, "descripcion": obj.subtipo_contacto.descripcion} if obj.subtipo_contacto else None

    def get_resultado_cobertura(self, obj):
        return {"id": obj.resultado_cobertura.id, "descripcion": obj.resultado_cobertura.descripcion} if obj.resultado_cobertura else None

    def get_transferencia(self, obj):
        return {"id": obj.transferencia.id, "descripcion": obj.transferencia.descripcion} if obj.transferencia else None

    def get_tipo_vivienda(self, obj):
        return {"id": obj.tipo_vivienda.id, "descripcion": obj.tipo_vivienda.descripcion} if obj.tipo_vivienda else None

    def get_tipo_base(self, obj):
        return {"id": obj.tipo_base.id, "descripcion": obj.tipo_base.descripcion} if obj.tipo_base else None

    def get_plan_contrato(self, obj):
        return {"id": obj.plan_contrato.id, "descripcion": obj.plan_contrato.descripcion} if obj.plan_contrato else None

    def get_distrito(self, obj):
        return {"id": obj.distrito.id, "nombre_distrito": obj.distrito.nombre_distrito} if obj.distrito else None

    def get_sector(self, obj):
        return {"id": obj.sector.id, "nombre_sector": obj.sector.nombre_sector} if obj.sector else None

    def validate_numero_movil(self, value):
        """ 🔥 Valida que el número tenga al menos 9 dígitos y sea único, excluyendo el Lead actual. """
        if len(value) < 9:
            raise serializers.ValidationError("El número móvil debe tener al menos 9 dígitos.")

        # 🔥 Excluir el mismo Lead al verificar si el número móvil ya existe
        if Lead.objects.filter(numero_movil=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("El número móvil ya está registrado.")

        return value

    def validate_correo(self, value):
        """ 🔥 Valida formato de correo electrónico """
        if value and not serializers.EmailField().run_validation(value):
            raise serializers.ValidationError("El correo electrónico no es válido.")
        return value

    def validate(self, data):
        """ 🔥 Validaciones adicionales para subtipo_contacto y transferencia """

        # Obtener subtipo_contacto y transferencia
        subtipo_contacto = data.get("subtipo_contacto")
        transferencia = data.get("transferencia")

        # 🔍 Si hay subtipo_contacto, verificamos si pertenece a 'No Contacto' y si es 'Transferencia'
        if subtipo_contacto:
            tipo_contacto = subtipo_contacto.tipo_contacto  # Obtiene el tipo de contacto relacionado

            if tipo_contacto and tipo_contacto.nombre_tipo == "No Contacto" and subtipo_contacto.descripcion == "Transferencia":
                # 🚨 Si el subtipo es 'Transferencia' pero transferencia es NULL, lanzar error
                if not transferencia:
                    raise serializers.ValidationError({
                        "transferencia": "El campo 'transferencia' es obligatorio cuando el subtipo de contacto es 'Transferencia'."
                    })

        return data

    def to_representation(self, instance):
        """
        🔥 Modifica la respuesta para que devuelva los datos con ID y nombre en JSON.
        """
        representation = super().to_representation(instance)

        # 📌 Personalizar los campos para devolver ID + Nombre
        if instance.origen:
            representation['origen'] = {
                "id": instance.origen.id,
                "nombre_origen": instance.origen.nombre_origen
            }

        if instance.subtipo_contacto:
            representation['subtipo_contacto'] = {
                "id": instance.subtipo_contacto.id,
                "descripcion": instance.subtipo_contacto.descripcion
            }
            if instance.subtipo_contacto.tipo_contacto:
                representation['tipo_contacto'] = {
                    "id": instance.subtipo_contacto.tipo_contacto.id,
                    "nombre_tipo": instance.subtipo_contacto.tipo_contacto.nombre_tipo
                }

        if instance.resultado_cobertura:
            representation['resultado_cobertura'] = {
                "id": instance.resultado_cobertura.id,
                "descripcion": instance.resultado_cobertura.descripcion
            }

        if instance.transferencia:
            representation['transferencia'] = {
                "id": instance.transferencia.id,
                "descripcion": instance.transferencia.descripcion
            }

        if instance.tipo_vivienda:
            representation['tipo_vivienda'] = {
                "id": instance.tipo_vivienda.id,
                "descripcion": instance.tipo_vivienda.descripcion
            }

        if instance.tipo_base:
            representation['tipo_base'] = {
                "id": instance.tipo_base.id,
                "descripcion": instance.tipo_base.descripcion
            }

        if instance.plan_contrato:
            representation['plan_contrato'] = {
                "id": instance.plan_contrato.id,
                "descripcion": instance.plan_contrato.descripcion
            }

        if instance.distrito:
            representation['distrito'] = {
                "id": instance.distrito.id,
                "nombre_distrito": instance.distrito.nombre_distrito
            }

        if instance.sector:
            representation['sector'] = {
                "id": instance.sector.id,
                "nombre_sector": instance.sector.nombre_sector
            }

        return representation


# 🔹 Serializer para Contratos
class ContratoSerializer(serializers.ModelSerializer):
    lead = serializers.PrimaryKeyRelatedField(read_only=True)

    # ✅ Permitir que estos campos sean editables enviando solo el ID
    plan_contrato = serializers.PrimaryKeyRelatedField(queryset=TipoPlanContrato.objects.all(), required=False, allow_null=True)
    tipo_documento = serializers.PrimaryKeyRelatedField(queryset=TipoDocumento.objects.all(), required=False, allow_null=True)
    origen = serializers.PrimaryKeyRelatedField(queryset=Origen.objects.all(), required=False, allow_null=True)

    usuario_conversion = serializers.SerializerMethodField()

    class Meta:
        model = Contrato
        fields = [
            'id', 'nombre_contrato', 'nombre', 'apellido', 'numero_movil', 'plan_contrato',
            'tipo_documento', 'numero_documento', 'origen', 'coordenadas',
            'fecha_inicio', 'observaciones', 'lead', 'usuario_conversion'
        ]

        extra_kwargs = {
            'numero_movil': {'read_only': True}  # 🔥 No se puede editar
        }

    def to_representation(self, instance):
        """
        🔥 Modifica la respuesta para que devuelva los datos con ID y nombre en JSON.
        """
        representation = super().to_representation(instance)

        # 📌 Personalizamos los campos para que devuelvan ID + Nombre
        if instance.plan_contrato:
            representation['plan_contrato'] = {
                "id": instance.plan_contrato.id,
                "descripcion": instance.plan_contrato.descripcion
            }

        if instance.tipo_documento:
            representation['tipo_documento'] = {
                "id": instance.tipo_documento.id,
                "nombre_tipo": instance.tipo_documento.nombre_tipo
            }

        if instance.origen:
            representation['origen'] = {
                "id": instance.origen.id,
                "nombre_origen": instance.origen.nombre_origen
            }

        return representation

    def get_usuario_conversion(self, obj):
        """
        Obtiene el usuario que convirtió el lead en contrato desde el historial.
        """
        historial_conversion = HistorialLead.objects.filter(
            lead=obj.lead,
            descripcion__icontains="Lead convertido a contrato"
        ).order_by('-fecha').first()  # 🔥 Busca el último registro de conversión

        if historial_conversion and historial_conversion.usuario:
            return {
                "id": historial_conversion.usuario.id,
                "username": historial_conversion.usuario.username,
                "email": historial_conversion.usuario.email,
                "nombre_completo": f"{historial_conversion.usuario.first_name} {historial_conversion.usuario.last_name}"
            }
        return None  # Si no hay historial, devuelve None



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