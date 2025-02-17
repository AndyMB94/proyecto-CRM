from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from django.contrib.auth import authenticate
from rest_framework import serializers
import requests
import re
from .models import (
    Profile, Departamento, Provincia, Distrito, Origen, TipoContacto,
    SubtipoContacto, Transferencia, TipoVivienda,
    TipoBase, TipoPlanContrato, Sector, Lead, Documento, TipoDocumento,
    Contrato, HistorialLead
)
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.conf import settings


# 🔹 Serializer para obtener el Token JWT con información adicional
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Agrega el username al token JWT
        token['username'] = user.username  

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
    tipo_documento = serializers.SerializerMethodField()
    numero_documento = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name', 'profile', 'tipo_documento', 'numero_documento']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        user = User.objects.create_user(**validated_data)

        # Asociar perfil con los datos proporcionados
        Profile.objects.filter(user=user).update(**profile_data)

        return user
    def get_tipo_documento(self, obj):
        """ 🔥 Obtiene el tipo de documento del usuario """
        documento = Documento.objects.filter(user=obj).first()
        if documento and documento.tipo_documento:
            return {
                "id": documento.tipo_documento.id,
                "nombre_tipo": documento.tipo_documento.nombre_tipo
            }
        return None  

    def get_numero_documento(self, obj):
        """ 🔥 Obtiene el número de documento del usuario """
        documento = Documento.objects.filter(user=obj).first()
        return documento.numero_documento if documento else None


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para cambiar la contraseña del usuario autenticado.
    """
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        """ 🔥 Verifica que la contraseña actual sea correcta """
        user = self.context['request'].user
        if not check_password(value, user.password):
            raise serializers.ValidationError("La contraseña actual es incorrecta.")
        return value

    def validate_new_password(self, value):
        """ 🔥 Valida que la nueva contraseña sea segura """
        if len(value) < 8:
            raise serializers.ValidationError("La nueva contraseña debe tener al menos 8 caracteres.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("La nueva contraseña debe contener al menos un número.")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("La nueva contraseña debe contener al menos una mayúscula.")
        return value

    def validate(self, data):
        """ 🔥 Verifica que `new_password` y `confirm_new_password` coincidan """
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"confirm_new_password": "Las contraseñas no coinciden."})
        return data

# 🔹 Serializers para Ubicación
class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = ['id', 'nombre_departamento']


class ProvinciaSerializer(serializers.ModelSerializer):
    departamento_id = serializers.IntegerField(source='departamento.id', read_only=True) 

    class Meta:
        model = Provincia
        fields = ['id', 'nombre_provincia','departamento_id']


class DistritoSerializer(serializers.ModelSerializer):
    provincia_id = serializers.IntegerField(source='provincia.id', read_only=True)

    class Meta:
        model = Distrito
        fields = ['id', 'nombre_distrito','provincia_id']


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
    tipo_contacto_id = serializers.IntegerField(source='tipo_contacto.id', read_only=True)

    class Meta:
        model = SubtipoContacto
        fields = ['id', 'descripcion','tipo_contacto_id']


# 🔹 Serializers para Tipos de Clasificación

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
    coordenadas = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    resultado_cobertura = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    transferencia = serializers.PrimaryKeyRelatedField(queryset=Transferencia.objects.all(), required=False, allow_null=True)
    tipo_vivienda = serializers.PrimaryKeyRelatedField(queryset=TipoVivienda.objects.all(), required=False, allow_null=True)
    tipo_base = serializers.PrimaryKeyRelatedField(queryset=TipoBase.objects.all(), required=False, allow_null=True)
    plan_contrato = serializers.PrimaryKeyRelatedField(queryset=TipoPlanContrato.objects.all(), required=False, allow_null=True)
    distrito = serializers.PrimaryKeyRelatedField(queryset=Distrito.objects.all(), required=False, allow_null=True)
    sector = serializers.PrimaryKeyRelatedField(queryset=Sector.objects.all(), required=False, allow_null=True)
    tipo_contacto = serializers.SerializerMethodField()
    tipo_documento = serializers.SerializerMethodField()  # ✅ Muestra el tipo de documento del lead
    numero_documento = serializers.SerializerMethodField()  # ✅ Muestra el número de documento
    latitud = serializers.FloatField(write_only=True, required=False)  # 🔥 Entrada separada
    longitud = serializers.FloatField(write_only=True, required=False)  # 🔥 Entrada separada

    class Meta:
        model = Lead
        fields = [
            'id', 'nombre', 'apellido', 'numero_movil', 'nombre_compania',
            'correo', 'cargo', 'origen', 'tipo_contacto', 'subtipo_contacto',
            'transferencia', 'tipo_vivienda', 'tipo_base', 'plan_contrato',
            'distrito', 'sector', 'direccion', 'coordenadas', 'dueno', 'fecha_creacion', 'estado',
            'tipo_documento', 'numero_documento', 'latitud', 'longitud', 'resultado_cobertura'
        ]
        extra_kwargs = {
            'numero_movil': {'required': True},  # ✅ Solo este campo es obligatorio
            'dueno': {'read_only': True},
        }

    def create(self, validated_data):
        """
        🔥 Personaliza la creación del Lead eliminando `latitud` y `longitud`
        """
        latitud = validated_data.pop('latitud', None)
        longitud = validated_data.pop('longitud', None)

        # ✅ Si tiene latitud y longitud, generamos coordenadas y consultamos cobertura
        if latitud is not None and longitud is not None:
            validated_data['coordenadas'] = f"{latitud}, {longitud}"

        return super().create(validated_data)


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

    def get_tipo_documento(self, obj):
        """ 🔥 Obtiene el tipo de documento del lead """
        documento = Documento.objects.filter(lead=obj).first()
        if documento and documento.tipo_documento:
            return {
                "id": documento.tipo_documento.id,
                "nombre_tipo": documento.tipo_documento.nombre_tipo
            }
        return None  # Si no hay documento, devuelve None

    def get_numero_documento(self, obj):
        """ 🔥 Obtiene el número de documento del lead """
        documento = Documento.objects.filter(lead=obj).first()
        return documento.numero_documento if documento else None

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

        # ✅ EXCLUIR EL LEAD ACTUAL EN VALIDACIÓN
        request = self.context.get("request")
        lead_id = self.instance.id if self.instance else None  # Obtener ID si es actualización

        if Lead.objects.filter(numero_movil=value).exclude(id=lead_id).exists():
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

        # ✅ Ajuste para devolver las coordenadas exactamente como se ingresaron
        if instance.coordenadas:
            try:
                lat, lon = instance.coordenadas.split(",")  # Aseguramos que se separa correctamente
                representation['coordenadas'] = f"{float(lat):.6f}, {float(lon):.6f}".rstrip("0").rstrip(".")
            except ValueError:
                representation['coordenadas'] = instance.coordenadas  # Dejarlo como está si no se puede dividir

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
            representation['resultado_cobertura'] = instance.resultado_cobertura  # ✅ Devolver directamente el string

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
            provincia = instance.distrito.provincia
            departamento = provincia.departamento

            representation['distrito'] = {
                "id": instance.distrito.id,
                "nombre_distrito": instance.distrito.nombre_distrito
            }

            representation['provincia'] = {
                "id": provincia.id,
                "nombre_provincia": provincia.nombre_provincia
            }

            representation['departamento'] = {
                "id": departamento.id,
                "nombre_departamento": departamento.nombre_departamento
            }

        if instance.sector:
            representation['sector'] = {
                "id": instance.sector.id,
                "nombre_sector": instance.sector.nombre_sector
            }

        # 🔥 Agregar tipo_documento y numero_documento
        documento = Documento.objects.filter(lead=instance).first()
        if documento:
            representation['tipo_documento'] = {
                "id": documento.tipo_documento.id,
                "nombre_tipo": documento.tipo_documento.nombre_tipo
            }
            representation['numero_documento'] = documento.numero_documento

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
    
    
class ConsultaCoberturaSerializer(serializers.Serializer):
    coordenadas = serializers.CharField()

    def validate_coordenadas(self, value):
        """
        🔥 Valida y separa latitud y longitud de la cadena de coordenadas.
        """
        try:
            latitud, longitud = map(str.strip, value.split(","))
            return {"latitud": latitud, "longitud": longitud}
        except ValueError:
            raise serializers.ValidationError("Formato incorrecto. Debe ser '-latitud, -longitud'.")

class ExportLeadSerializer(serializers.ModelSerializer):
    origen = OrigenSerializer()
    tipo_contacto = serializers.SerializerMethodField()
    subtipo_contacto = SubtipoContactoSerializer()
    transferencia = TransferenciaSerializer()
    tipo_vivienda = TipoViviendaSerializer()
    tipo_base = TipoBaseSerializer()
    plan_contrato = TipoPlanContratoSerializer()
    distrito = DistritoSerializer()
    sector = SectorSerializer()
    tipo_documento = serializers.SerializerMethodField()  # 🔥 Obtener tipo de documento
    numero_documento = serializers.SerializerMethodField()  # 🔥 Obtener número de documento
    provincia = serializers.SerializerMethodField()
    departamento = serializers.SerializerMethodField()
    dueno = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = [
            'id', 'nombre', 'apellido', 'numero_movil', 'nombre_compania',
            'correo', 'cargo', 'origen', 'tipo_contacto', 'subtipo_contacto',
            'transferencia', 'tipo_vivienda', 'tipo_base', 'plan_contrato',
            'distrito', 'provincia', 'departamento', 'sector', 'direccion',
            'coordenadas', 'dueno', 'fecha_creacion', 'estado', 'tipo_documento',
            'numero_documento', 'resultado_cobertura'
        ]

    def get_tipo_contacto(self, obj):
        """ Retorna el tipo de contacto a partir del subtipo """
        if obj.subtipo_contacto and obj.subtipo_contacto.tipo_contacto:
            return {
                "id": obj.subtipo_contacto.tipo_contacto.id,
                "nombre_tipo": obj.subtipo_contacto.tipo_contacto.nombre_tipo
            }
        return None
    
    def get_dueno(self, obj):
        """ Retorna el nombre completo del dueño """
        return f"{obj.dueno.first_name} {obj.dueno.last_name}" if obj.dueno else None

    def get_provincia(self, obj):
        """ Retorna la provincia del lead """
        if obj.distrito and obj.distrito.provincia:
            return {
                "id": obj.distrito.provincia.id,
                "nombre_provincia": obj.distrito.provincia.nombre_provincia
            }
        return None

    def get_departamento(self, obj):
        """ Retorna el departamento del lead """
        if obj.distrito and obj.distrito.provincia and obj.distrito.provincia.departamento:
            return {
                "id": obj.distrito.provincia.departamento.id,
                "nombre_departamento": obj.distrito.provincia.departamento.nombre_departamento
            }
        return None
    
    def get_tipo_documento(self, obj):
        """ 🔥 Obtiene el tipo de documento del lead """
        documento = Documento.objects.filter(lead=obj).first()
        if documento and documento.tipo_documento:
            return {
                "id": documento.tipo_documento.id,
                "nombre_tipo": documento.tipo_documento.nombre_tipo
            }
        return None  # Si no hay documento, devuelve None
    
    def get_numero_documento(self, obj):
        """ 🔥 Obtiene el número de documento del lead """
        documento = Documento.objects.filter(lead=obj).first()
        return documento.numero_documento if documento else None

class ExportHistorialLeadSerializer(serializers.ModelSerializer):
    numero_movil = serializers.CharField(source="lead.numero_movil", read_only=True)
    cliente = serializers.SerializerMethodField()
    usuario = serializers.SerializerMethodField()
    tipo_contacto = serializers.CharField(source="tipo_contacto.nombre_tipo", allow_null=True)
    subtipo_contacto = serializers.CharField(source="subtipo_contacto.descripcion", allow_null=True)

    class Meta:
        model = HistorialLead
        fields = ["numero_movil", "cliente", "usuario", "descripcion", "fecha", "tipo_contacto", "subtipo_contacto"]

    def get_cliente(self, obj):
        """ 🔥 Concatena el nombre y apellido del lead """
        if obj.lead:
            return f"{obj.lead.nombre} {obj.lead.apellido}".strip()
        return "Desconocido"

    def get_usuario(self, obj):
        return f"{obj.usuario.first_name} {obj.usuario.last_name}" if obj.usuario else "Desconocido"
