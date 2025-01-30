from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, LeadSerializer, HistorialLeadSerializer
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
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
    ResultadoCobertura,
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



class CustomTokenObtainPairView(TokenObtainPairView):###############
    """
    Endpoint para obtener un token de acceso y refresco.
    """
    serializer_class = CustomTokenObtainPairSerializer


class CreateUserView(APIView):###############
    """
    Endpoint para crear un usuario y asociarle un documento, teléfono, dirección, 
    nombre y apellido.
    """
    authentication_classes = []  # Desactiva la autenticación
    permission_classes = [AllowAny]  # Permite acceso sin restricciones

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        tipo_documento_id = request.data.get("tipo_documento_id")
        numero_documento = request.data.get("numero_documento")
        telefono = request.data.get("telefono")
        direccion = request.data.get("direccion")

        if not username or not password or not tipo_documento_id or not numero_documento:
            return Response({"error": "Faltan campos obligatorios."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Crear usuario
            usuario = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_staff=False,
                is_superuser=False
            )

            # Crear o actualizar el perfil
            profile = Profile.objects.get(user=usuario)
            profile.telefono = telefono
            profile.direccion = direccion
            profile.save()

            # Obtener tipo de documento
            tipo_documento = TipoDocumento.objects.get(id=tipo_documento_id)

            # Crear y asociar documento
            Documento.objects.create(
                tipo_documento=tipo_documento,
                numero_documento=numero_documento,
                user=usuario
            )

            return Response({"message": f"Usuario '{username}' creado con éxito."}, status=status.HTTP_201_CREATED)

        except TipoDocumento.DoesNotExist:
            return Response({"error": "Tipo de documento no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class LeadListCreateView(APIView):###############
    """
    Endpoint para listar y crear leads.
    Requiere autenticación.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Devuelve el conjunto de datos de leads.
        """
        return Lead.objects.all()

    def get(self, request):
        """
        Devuelve una lista de leads.
        """
        leads = self.get_queryset()
        serializer = LeadSerializer(leads, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Crea un nuevo lead y su documento relacionado, permitiendo seleccionar un dueño.
        """
        data = request.data.copy()

        # Asigna el dueño autenticado si no se especifica en el payload
        if "dueno" not in data or not data["dueno"]:
            data["dueno"] = request.user.id

        # Asegurar que el estado del lead sea 0 por defecto
        data["estado"] = 0  

        serializer = LeadSerializer(data=data)
        if serializer.is_valid():
            try:
                lead = serializer.save()  # Guarda el lead con el dueño especificado o autenticado

                # Registrar el historial del lead
                HistorialLead.objects.create(
                    lead=lead,
                    usuario=request.user,
                    descripcion="Lead creado",
                )

                # Crear el documento relacionado si se incluye
                tipo_documento_id = data.get('tipo_documento')
                nro_documento = data.get('nro_documento')
                if tipo_documento_id and nro_documento:
                    if Documento.objects.filter(numero_documento=nro_documento).exists():
                        raise ValidationError({"nro_documento": "El número de documento ya está registrado."})
                    Documento.objects.create(
                        tipo_documento_id=tipo_documento_id,
                        numero_documento=nro_documento,
                        lead=lead,
                        user=request.user
                    )

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except ValidationError as ve:
                return Response({"error": ve.detail}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": f"Error al guardar el lead: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConvertLeadToContractView(APIView):###############
    """
    Endpoint para convertir un lead en un contrato.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, lead_id):
        """
        Convierte un lead en un contrato y actualiza su estado a 1.
        """
        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            return Response({"error": "Lead no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar si el lead ya ha sido convertido
        if lead.estado == 1:
            return Response({"error": "Este lead ya ha sido convertido en contrato anteriormente."},
                            status=status.HTTP_400_BAD_REQUEST)

        nombre_contrato = f"{lead.nombre} {lead.apellido}"
        fecha_inicio = now().date()
        observaciones = request.data.get('observaciones', '')

        try:
            contrato = Contrato.objects.create(
                nombre_contrato=nombre_contrato,
                lead=lead,
                fecha_inicio=fecha_inicio,
                observaciones=observaciones
            )

            # Actualizar estado del lead a 1
            lead.estado = 1
            lead.save()

            # Registrar en el historial del lead solo si la conversion es exitosa
            HistorialLead.objects.create(
                lead=lead,
                usuario=request.user,
                descripcion=f"Lead convertido a contrato: {contrato.nombre_contrato}",
            )

            return Response({
                "message": "Lead convertido a contrato con éxito.",
                "contrato": {
                    "id": contrato.id,
                    "nombre_contrato": contrato.nombre_contrato,
                    "fecha_inicio": contrato.fecha_inicio,
                    "observaciones": contrato.observaciones
                },
                "lead": {
                    "id": lead.id,
                    "nombre": lead.nombre,
                    "apellido": lead.apellido,
                    "estado": lead.estado  # Se devuelve el estado actualizado
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Error al convertir lead a contrato: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)



class LeadDetailView(APIView):###############
    """
    Endpoint para obtener, actualizar o eliminar un lead específico.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Lead.objects.all()

    def get_object(self, pk):
        try:
            return self.get_queryset().get(pk=pk)
        except Lead.DoesNotExist:
            return None

    def get(self, request, pk):
        lead = self.get_object(pk)
        if lead is None:
            return Response({"error": "Lead no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = LeadSerializer(lead)
        return Response(serializer.data)

    def put(self, request, pk):
        lead = self.get_object(pk)
        if lead is None:
            return Response({"error": "Lead no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data.copy()

        # Evita que el estado se modifique manualmente
        if "estado" in data:
            data.pop("estado") 
        serializer = LeadSerializer(lead, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()

                # Registrar el historial del lead
                HistorialLead.objects.create(
                    lead=lead,
                    usuario=request.user,
                    descripcion="Lead actualizado",
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

    def get_queryset(self):
        return Lead.objects.all()

    def get(self, request, numero_movil):
        if len(numero_movil) < 5:
            return Response({"error": "Ingrese al menos 5 dígitos para la búsqueda."}, status=status.HTTP_400_BAD_REQUEST)

        leads = self.get_queryset().filter(numero_movil__icontains=numero_movil)
        if not leads.exists():
            return Response({"message": "No se encontraron leads con ese número de móvil."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LeadSerializer(leads, many=True)
        return Response(serializer.data)


class OwnerListView(APIView):###############
    """
    Endpoint para listar todos los dueños, incluyendo campos de perfil si están presentes.
    """
    permission_classes = [IsAuthenticated]  # Verifica que el usuario esté autenticado

    def get(self, request):
        """
        Devuelve una lista de todos los usuarios (dueños) junto con su información de perfil.
        """
        owners = User.objects.all()
        data = [
            {
                "id": owner.id,
                "username": owner.username,
                "email": owner.email,
                "telefono": getattr(owner.profile, 'telefono', None),
                "direccion": getattr(owner.profile, 'direccion', None),
            }
            for owner in owners
        ]
        return Response(data, status=status.HTTP_200_OK)

class ContratoListView(APIView):###############
    """
    Endpoint para listar todos los contratos.
    """
    queryset = Contrato.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Devuelve una lista de todos los contratos.
        """
        contratos = Contrato.objects.all()
        data = [
            {
                "id": contrato.id,
                "nombre_contrato": contrato.nombre_contrato,
                "fecha_inicio": contrato.fecha_inicio,
                "observaciones": contrato.observaciones,
                "lead": {
                    "id": contrato.lead.id,
                    "nombre": contrato.lead.nombre,
                    "apellido": contrato.lead.apellido,
                },
            }
            for contrato in contratos
        ]
        return Response(data, status=status.HTTP_200_OK)


class ProvinciaByDepartamentoView(APIView):
    """
    Devuelve las provincias asociadas a un departamento.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, departamento_id):
        provincias = Provincia.objects.filter(departamento_id=departamento_id)
        data = [{"id": provincia.id, "nombre": provincia.nombre_provincia} for provincia in provincias]
        return Response(data, status=status.HTTP_200_OK)


class DistritoByProvinciaView(APIView):
    """
    Devuelve los distritos asociados a una provincia.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, provincia_id):
        distritos = Distrito.objects.filter(provincia_id=provincia_id)
        data = [{"id": distrito.id, "nombre": distrito.nombre_distrito} for distrito in distritos]
        return Response(data, status=status.HTTP_200_OK)


class SubtipoContactoByTipoContactoView(APIView):
    """
    Devuelve los subtipos de contacto asociados a un tipo de contacto.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, tipo_contacto_id):
        subtipos = SubtipoContacto.objects.filter(tipo_contacto_id=tipo_contacto_id)
        data = [{"id": subtipo.id, "descripcion": subtipo.descripcion} for subtipo in subtipos]
        return Response(data, status=status.HTTP_200_OK)
    
class HistorialPagination(PageNumberPagination):
    page_size = 10

class LeadHistorialView(APIView):
    """
    Endpoint para obtener el historial de un lead específico.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = HistorialPagination

    def get_queryset(self):
        """
        Devuelve el historial asociado al lead especificado en los argumentos de la vista.
        """
        lead_id = self.kwargs.get('lead_id')  # Obtiene el lead_id de los argumentos de la URL
        return HistorialLead.objects.filter(lead_id=lead_id).order_by('-fecha')

    def get(self, request, lead_id):
        """
        Retorna el historial paginado del lead.
        """
        try:
            queryset = self.get_queryset()
            paginator = self.pagination_class()
            paginated_historial = paginator.paginate_queryset(queryset, request)
            serializer = HistorialLeadSerializer(paginated_historial, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({"error": f"Error al obtener el historial del lead: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)




class GenericListView(APIView):
    """
    Endpoint genérico para listar elementos de tablas de referencia.
    """
    permission_classes = [IsAuthenticated]  # Cambia si necesitas aplicar permisos más específicos.

    def get_queryset(self, model):
        """
        Devuelve un queryset dinámico basado en el modelo proporcionado.
        """
        return model.objects.all()

    def get(self, request, model_name):
        models_map = {
            "tipo-documento": TipoDocumento,
            "resultado-cobertura": ResultadoCobertura,
            "transferencia": Transferencia,
            "tipo-vivienda": TipoVivienda,
            "tipo-base": TipoBase,
            "sector": Sector,
            "origen": Origen,
            "departamento": Departamento,
            "tipo-contacto": TipoContacto,
            "tipo-plan-contrato": TipoPlanContrato,
        }
        model = models_map.get(model_name)
        if not model:
            return Response({"error": "Modelo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        queryset = self.get_queryset(model)
        data = [{"id": obj.id, "nombre": str(obj)} for obj in queryset]
        return Response(data, status=status.HTTP_200_OK)


class LeadsYContratosPorOrigenAPIView(APIView):###############
    """
    Endpoint para obtener la cantidad de leads y contratos por origen,
    filtrados por mes, año o rango de fechas.
    """
    permission_classes = [IsAuthenticated]

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

        # Consolidar los datos
        data = [
            {
                'origen': item['origen__nombre_origen'],
                'total_leads': item['total_leads'],
                'total_contratos': contratos_dict.get(item['origen__nombre_origen'], 0),
            }
            for item in leads_por_origen
        ]

        # Agregar datos globales al response
        response = {
            "total_leads_global": total_leads_global,
            "total_contratos_global": total_contratos_global,
            "detalle_por_origen": data
        }

        return Response(response)