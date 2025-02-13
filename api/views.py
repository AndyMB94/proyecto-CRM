from rest_framework import serializers
from rest_framework import generics
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, LeadSerializer, HistorialLeadSerializer, UserSerializer, ContratoSerializer, DistritoSerializer, ProvinciaSerializer, SubtipoContactoSerializer, LeadsYContratosPorOrigenSerializer, GenericSerializer, ChangePasswordSerializer, ConsultaCoberturaSerializer, OrigenSerializer, TipoBaseSerializer, TipoContactoSerializer, TipoViviendaSerializer, TransferenciaSerializer, TipoPlanContratoSerializer, SectorSerializer, DepartamentoSerializer, TipoDocumentoSerializer
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
import requests
from rest_framework import status
from .models import (
    Lead,
    Documento,
    Departamento,
    Provincia,
    Distrito,
    TipoContacto,
    SubtipoContacto,
    TipoDocumento,
    Transferencia,
    TipoVivienda,
    TipoBase,
    Sector,
    Origen,
    Contrato,
    TipoPlanContrato,
    Profile,
    HistorialLead,
)
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError
from django.db.models import Count
from datetime import datetime
from api.utils import APICliente 



class CustomTokenObtainPairView(TokenObtainPairView):###############
    """
    Endpoint para obtener un token de acceso y refresco.
    """
    serializer_class = CustomTokenObtainPairSerializer


class CreateUserView(APIView):
    """
    Endpoint para crear un usuario con un perfil asociado y su documento.
    """
    authentication_classes = []  # Desactiva la autenticación
    permission_classes = [AllowAny]  # Permite acceso sin restricciones

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            try:
                # Crear usuario
                usuario = serializer.save()

                # Crear o actualizar el perfil
                profile = usuario.profile
                profile.telefono = request.data.get("telefono")
                profile.direccion = request.data.get("direccion")
                profile.save()

                # Obtener tipo de documento
                tipo_documento_id = request.data.get("tipo_documento_id")
                numero_documento = request.data.get("numero_documento")

                if tipo_documento_id and numero_documento:
                    tipo_documento = TipoDocumento.objects.get(id=tipo_documento_id)

                    # Verificar si el documento ya existe
                    if Documento.objects.filter(numero_documento=numero_documento).exists():
                        return Response({"error": "El número de documento ya está registrado."}, status=status.HTTP_400_BAD_REQUEST)

                    # Crear documento y asociarlo al usuario
                    Documento.objects.create(
                        tipo_documento=tipo_documento,
                        numero_documento=numero_documento,
                        user=usuario
                    )

                return Response({"message": f"Usuario '{usuario.username}' creado con éxito."}, status=status.HTTP_201_CREATED)

            except TipoDocumento.DoesNotExist:
                return Response({"error": "Tipo de documento no encontrado."}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    """
    Endpoint para obtener los detalles de un usuario por su ID.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        """
        Obtiene la información de un usuario, su perfil y su documento.
        """
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """
    Endpoint para que el usuario autenticado cambie su propia contraseña.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])  # Cambia la contraseña
            user.save()

            return Response({"message": "Contraseña actualizada correctamente."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeadListCreateView(APIView):
    """
    Endpoint para listar y crear leads.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Devuelve una lista de leads.
        """
        leads = Lead.objects.all()
        serializer = LeadSerializer(leads, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Crea un nuevo lead **solo si `numero_movil` no existe previamente**.
        """
        data = request.data.copy()
        usuario_actual = request.user  # Usuario autenticado que crea el lead
        

        serializer = LeadSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            try:
                # ✅ **2️⃣ Crear el lead SOLO si el número móvil no existe**
                lead = serializer.save(dueno=usuario_actual)

                # 📌 **3️⃣ Registrar historial de creación**
                HistorialLead.objects.create(
                    lead=lead,
                    usuario=usuario_actual,
                    descripcion=f"Lead creado por {usuario_actual.first_name} {usuario_actual.last_name}."
                )

                # 📌 **4️⃣ Si tiene `tipo_contacto` y `subtipo_contacto`, lo registramos en el historial**
                if lead.subtipo_contacto:
                    tipo_contacto = lead.subtipo_contacto.tipo_contacto  # ✅ Objeto
                    subtipo_contacto = lead.subtipo_contacto  # ✅ Objeto

                    HistorialLead.objects.create(
                        lead=lead,
                        usuario=usuario_actual,
                        descripcion=f"Tipo de contacto: {tipo_contacto.nombre_tipo} y Subtipo de contacto: {subtipo_contacto.descripcion}.",
                        tipo_contacto=tipo_contacto,
                        subtipo_contacto=subtipo_contacto
                    )

                # 📌 **5️⃣ CREAR EL DOCUMENTO SOLO SI SE PROPORCIONÓ Y EL LEAD SE CREÓ**
                tipo_documento_id = data.get('tipo_documento')
                nro_documento = data.get('nro_documento')

                if tipo_documento_id and nro_documento:
                    # 🔍 **Verificar si el documento ya existe**
                    if Documento.objects.filter(numero_documento=nro_documento).exists():
                        return Response({"error": "El número de documento ya está registrado."},
                                        status=status.HTTP_400_BAD_REQUEST)

                    # ✅ **Crear el documento SOLO si el lead fue creado correctamente**
                    Documento.objects.create(
                        tipo_documento_id=tipo_documento_id,
                        numero_documento=nro_documento,
                        lead=lead,
                        user=usuario_actual
                    )

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": f"Error al guardar el lead: {str(e)}"},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class LeadDetailView(APIView):
    """
    Endpoint para obtener, actualizar o eliminar un lead específico.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Lead, pk=pk)

    def get(self, request, pk):
        """
        Obtiene el detalle de un lead.
        """
        lead = self.get_object(pk)
        serializer = LeadSerializer(lead)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Actualiza un lead.
        """
        lead = self.get_object(pk)
        usuario_actual = request.user
        data = request.data.copy()

        subtipo_contacto_anterior = lead.subtipo_contacto
        tipo_contacto_anterior = subtipo_contacto_anterior.tipo_contacto if subtipo_contacto_anterior else None

        serializer = LeadSerializer(lead, data=data)
        if serializer.is_valid():
            try:
                lead_actualizado = serializer.save()

                cambios = []

                subtipo_contacto_actual = lead_actualizado.subtipo_contacto
                tipo_contacto_actual = subtipo_contacto_actual.tipo_contacto if subtipo_contacto_actual else None

                if subtipo_contacto_anterior != subtipo_contacto_actual:
                    cambios.append(f"Subtipo de contacto cambiado de {subtipo_contacto_anterior} a {subtipo_contacto_actual}")

                if tipo_contacto_anterior != tipo_contacto_actual:
                    cambios.append(f"Tipo de contacto cambiado de {tipo_contacto_anterior} a {tipo_contacto_actual}.")

                if cambios:
                    HistorialLead.objects.create(
                        lead=lead,
                        usuario=usuario_actual,
                        descripcion=" y ".join(cambios),
                        tipo_contacto=tipo_contacto_actual,
                        subtipo_contacto=subtipo_contacto_actual
                    )


                return Response(serializer.data)

            except Exception as e:
                return Response({"error": f"Error al actualizar el lead: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """
        Actualiza parcialmente un lead (solo los campos enviados).
        """
        lead = self.get_object(pk)
        usuario_actual = request.user
        data = request.data.copy()

        subtipo_contacto_anterior = lead.subtipo_contacto
        tipo_contacto_anterior = subtipo_contacto_anterior.tipo_contacto if subtipo_contacto_anterior else None

        serializer = LeadSerializer(lead, data=data, partial=True)
        if serializer.is_valid():
            try:
                lead_actualizado = serializer.save()

                cambios = []

                subtipo_contacto_actual = lead_actualizado.subtipo_contacto
                tipo_contacto_actual = subtipo_contacto_actual.tipo_contacto if subtipo_contacto_actual else None


                if subtipo_contacto_anterior != subtipo_contacto_actual:
                    cambios.append(f"Subtipo de contacto cambiado de {subtipo_contacto_anterior} a {subtipo_contacto_actual}")

                if tipo_contacto_anterior != tipo_contacto_actual:
                    cambios.append(f"Tipo de contacto cambiado de {tipo_contacto_anterior} a {tipo_contacto_actual}.")

                if cambios:
                    HistorialLead.objects.create(
                        lead=lead,
                        usuario=usuario_actual,
                        descripcion=" y ".join(cambios),
                        tipo_contacto=tipo_contacto_actual,
                        subtipo_contacto=subtipo_contacto_actual
                    )

                return Response(serializer.data)

            except Exception as e:
                return Response({"error": f"Error al actualizar el lead: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        lead = self.get_object(pk)
        if lead is None:
            return Response({"error": "Lead no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        try:
            lead.delete()
            return Response({"message": "Lead eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": f"Error al eliminar el lead: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)



class LeadSearchByNumberView(APIView):
    """
    Endpoint para buscar leads por número de móvil.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, numero_movil):
        """
        Busca leads por número de móvil.
        """
        if len(numero_movil) < 5:
            return Response({"error": "Ingrese al menos 5 dígitos para la búsqueda."}, status=status.HTTP_400_BAD_REQUEST)

        leads = Lead.objects.filter(numero_movil__icontains=numero_movil)
        if not leads.exists():
            return Response({"message": "No se encontraron leads con ese número de móvil."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LeadSerializer(leads, many=True)
        return Response(serializer.data)


class ConvertLeadToContractView(APIView):
    """
    Endpoint para convertir un lead en un contrato.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, lead_id):
        """
        Convierte un lead en un contrato.
        """
        lead = get_object_or_404(Lead, id=lead_id)
        usuario_actual = request.user

        if lead.estado == 1:
            return Response({"error": "Este lead ya ha sido convertido en contrato anteriormente."},
                            status=status.HTTP_400_BAD_REQUEST)

        documento = Documento.objects.filter(lead=lead).first()

        try:
            # ✅ Crear el contrato directamente en la base de datos
            contrato = Contrato.objects.create(
                nombre_contrato=f"{lead.nombre} {lead.apellido}",
                nombre=lead.nombre,
                apellido=lead.apellido,
                numero_movil=lead.numero_movil,
                plan_contrato=lead.plan_contrato,
                tipo_documento=documento.tipo_documento if documento else None,
                numero_documento=documento.numero_documento if documento else None,
                origen=lead.origen,
                coordenadas=lead.coordenadas,
                lead=lead,  # ✅ Se asigna correctamente el lead
                fecha_inicio=now().date(),
                observaciones=request.data.get('observaciones', 'Contrato generado desde el lead')
            )

            # ✅ Marcar el lead como convertido
            lead.estado = 1
            lead.save()

            # ✅ Registrar historial de conversión
            HistorialLead.objects.create(
                lead=lead,
                usuario=usuario_actual,
                descripcion=f"Lead convertido a contrato por {usuario_actual.first_name} {usuario_actual.last_name}."
            )

            # ✅ Serializar el contrato creado para devolverlo en la respuesta
            contrato_serializer = ContratoSerializer(contrato)

            return Response({
                "message": "Lead convertido a contrato con éxito.",
                "contrato": contrato_serializer.data,
                "lead": {
                    "id": lead.id,
                    "nombre": lead.nombre,
                    "apellido": lead.apellido,
                    "estado": lead.estado
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Error al convertir lead a contrato: {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)






class ContratoListView(ListAPIView):
    """
    Endpoint para listar todos los contratos.
    """
    queryset = Contrato.objects.all()
    serializer_class = ContratoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class ContratoDetailView(RetrieveUpdateDestroyAPIView):
    """
    Endpoint para ver, actualizar o eliminar un contrato específico.
    """
    queryset = Contrato.objects.all()
    serializer_class = ContratoSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        """
        🔥 Método PUT para actualizar un contrato COMPLETAMENTE, excepto `numero_movil`.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        """
        🔥 Método PATCH para actualizar parcialmente un contrato, excepto `numero_movil`.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """
        🔥 Método DELETE para eliminar un contrato.
        """
        instance = self.get_object()
        instance.delete()
        return Response({"message": "Contrato eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)






class ProvinciaByDepartamentoView(ListAPIView):
    """
    Devuelve las provincias asociadas a un departamento.
    """
    serializer_class = ProvinciaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        departamento_id = self.kwargs['departamento_id']
        return Provincia.objects.filter(departamento_id=departamento_id)


class DistritoByProvinciaView(ListAPIView):
    """
    Devuelve los distritos asociados a una provincia.
    """
    serializer_class = DistritoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        provincia_id = self.kwargs['provincia_id']
        return Distrito.objects.filter(provincia_id=provincia_id)


class SubtipoContactoByTipoContactoView(ListAPIView):
    """
    Devuelve los subtipos de contacto asociados a un tipo de contacto.
    """
    serializer_class = SubtipoContactoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Deshabilita paginación

    def get_queryset(self):
        tipo_contacto_id = self.kwargs['tipo_contacto_id']
        return SubtipoContacto.objects.filter(tipo_contacto_id=tipo_contacto_id)
    


class LeadHistorialView(APIView):
    """
    Endpoint para obtener el historial de un lead específico SIN paginación.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self, lead_id):
        """
        Devuelve el historial asociado al lead especificado.
        """
        return HistorialLead.objects.filter(lead_id=lead_id).order_by('-fecha')

    def get(self, request, lead_id):
        """
        Retorna el historial completo del lead SIN paginación.
        """
        try:
            queryset = self.get_queryset(lead_id)
            serializer = HistorialLeadSerializer(queryset, many=True)
            return Response(serializer.data)  # 🔥 Ahora devuelve solo la lista

        except Exception as e:
            return Response({"error": f"Error al obtener el historial del lead: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)





class GenericListView(ListAPIView):
    """
    Endpoint genérico para listar elementos de tablas de referencia.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = None

    models_map = {
        "tipo-documento": (TipoDocumento, "nombre_tipo"),
        "transferencia": (Transferencia, "descripcion"),
        "tipo-vivienda": (TipoVivienda, "descripcion"),
        "tipo-base": (TipoBase, "descripcion"),
        "sector": (Sector, "nombre_sector"),
        "origen": (Origen, "nombre_origen"),
        "departamento": (Departamento, "nombre_departamento"),
        "tipo-contacto": (TipoContacto, "nombre_tipo"),
        "tipo-plan-contrato": (TipoPlanContrato, "descripcion"),
    }

    def get_queryset(self):
        model_info = self.models_map.get(self.kwargs.get('model_name'))
        
        if not model_info:
            return Response({"error": "Modelo no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        model, _ = model_info
        return model.objects.all()

    def get_serializer_class(self):
        """
        Crea dinámicamente un serializer con los campos correctos.
        """
        model_info = self.models_map.get(self.kwargs.get('model_name'))
        if model_info:
            model, nombre_campo = model_info

            # Crear un serializer dinámico en tiempo de ejecución y renombrar el campo a "nombre"
            return type(
                "DynamicGenericSerializer",
                (serializers.ModelSerializer,),
                {
                    "Meta": type("Meta", (), {"model": model, "fields": ["id", "nombre"]}),  # ✅ Incluye 'nombre'
                    "nombre": serializers.CharField(source=nombre_campo)  # Mapea "descripcion" a "nombre"
                }
            )

        return GenericSerializer  # Retorna el serializer base si el modelo no es válido




class LeadsYContratosPorOrigenAPIView(generics.GenericAPIView):
    """
    Endpoint para obtener la cantidad de leads y contratos por origen,
    filtrados por mes, año o rango de fechas.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LeadsYContratosPorOrigenSerializer

    def get(self, request, *args, **kwargs):
        # Obtener los parámetros de filtro
        fecha_inicio = request.query_params.get('fecha_inicio')  # YYYY-MM-DD
        fecha_fin = request.query_params.get('fecha_fin')  # YYYY-MM-DD
        mes = request.query_params.get('mes')  # MM
        año = request.query_params.get('año')  # YYYY

        # Preparar el filtro de fechas
        filtros_leads = {}
        filtros_contratos = {}

        # Filtrar por rango de fechas si se proporcionan
        if fecha_inicio:
            filtros_leads['fecha_creacion__gte'] = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            filtros_contratos['lead__fecha_creacion__gte'] = datetime.strptime(fecha_inicio, '%Y-%m-%d')

        if fecha_fin:
            filtros_leads['fecha_creacion__lte'] = datetime.strptime(fecha_fin, '%Y-%m-%d')
            filtros_contratos['lead__fecha_creacion__lte'] = datetime.strptime(fecha_fin, '%Y-%m-%d')

        # Filtro por mes y año
        if mes and año:
            filtros_leads['fecha_creacion__month'] = int(mes)
            filtros_leads['fecha_creacion__year'] = int(año)
            filtros_contratos['lead__fecha_creacion__month'] = int(mes)
            filtros_contratos['lead__fecha_creacion__year'] = int(año)
        elif año:  # Filtrar solo por año
            filtros_leads['fecha_creacion__year'] = int(año)
            filtros_contratos['lead__fecha_creacion__year'] = int(año)

        # Calcular la cantidad total de leads en el período filtrado
        total_leads_global = Lead.objects.filter(**filtros_leads).count()

        # Calcular la cantidad total de contratos en el período filtrado
        total_contratos_global = Contrato.objects.filter(**filtros_contratos).count()

        # Filtrar leads por origen
        leads_por_origen = (
            Lead.objects.filter(**filtros_leads)
            .values('origen__nombre_origen')
            .annotate(total_leads=Count('id'))
            .order_by('origen__nombre_origen')
        )

        # Filtrar contratos por origen
        contratos_por_origen = (
            Contrato.objects.filter(**filtros_contratos)
            .values('lead__origen__nombre_origen')
            .annotate(total_contratos=Count('id'))
            .order_by('lead__origen__nombre_origen')
        )

        # Convertir contratos a diccionario para acceso rápido
        contratos_dict = {
            item['lead__origen__nombre_origen']: item['total_contratos']
            for item in contratos_por_origen
        }

        # Consolidar los datos con serializer
        data = [
            {'origen': item['origen__nombre_origen'], 'total_leads': item['total_leads'],
             'total_contratos': contratos_dict.get(item['origen__nombre_origen'], 0)}
            for item in leads_por_origen
        ]

        # Serializar respuesta
        response = {
            "total_leads_global": total_leads_global,
            "total_contratos_global": total_contratos_global,
            "detalle_por_origen": LeadsYContratosPorOrigenSerializer(data, many=True).data
        }

        return Response(response)



class ConsultaCoberturaView(APIView):
    """
    Endpoint para consultar la cobertura con coordenadas en formato string.
    """
    permission_classes = [AllowAny]  # 🔥 Permite acceso sin autenticación (ajusta si es necesario)
    
    def post(self, request):
        """
        Recibe coordenadas en formato "-latitud, -longitud" y consulta la API externa de cobertura manteniendo cookies.
        """
        coordenadas = request.data.get("coordenadas")

        if not coordenadas:
            return Response({"error": "El campo 'coordenadas' es obligatorio."}, status=400)

        try:
            latitud, longitud = map(str.strip, coordenadas.split(","))

            # 🔥 Usar APICliente para hacer la consulta
            cliente_api = APICliente()
            resultado_cobertura = cliente_api.consultar_cobertura(latitud, longitud)

            return Response({"resultado_cobertura": resultado_cobertura})

        except ValueError:
            return Response({"error": "Formato incorrecto. Debe ser '-latitud, -longitud'."}, status=400)

class LeadMetadataView(APIView):
    """
    Endpoint que devuelve los datos necesarios para llenar el formulario de creación de leads.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Devuelve listas de valores para los select del formulario de leads en una sola solicitud.
        """
        try:
            data = {
                "origenes": OrigenSerializer(Origen.objects.all(), many=True).data,
                "tipo_contactos": TipoContactoSerializer(TipoContacto.objects.all(), many=True).data,
                "subtipo_contactos": SubtipoContactoSerializer(SubtipoContacto.objects.all(), many=True).data,
                "transferencias": TransferenciaSerializer(Transferencia.objects.all(), many=True).data,
                "tipo_viviendas": TipoViviendaSerializer(TipoVivienda.objects.all(), many=True).data,
                "tipo_bases": TipoBaseSerializer(TipoBase.objects.all(), many=True).data,
                "tipo_planes": TipoPlanContratoSerializer(TipoPlanContrato.objects.all(), many=True).data,
                "sectores": SectorSerializer(Sector.objects.all(), many=True).data,
                "tipo_documentos": TipoDocumentoSerializer(TipoDocumento.objects.all(), many=True).data,
                "departamentos": DepartamentoSerializer(Departamento.objects.all(), many=True).data,
                "provincias": ProvinciaSerializer(Provincia.objects.all(), many=True).data,
                "distritos": DistritoSerializer(Distrito.objects.all(), many=True).data,
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Error al obtener metadata: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)