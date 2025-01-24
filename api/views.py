from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, LeadSerializer, HistorialEstadoSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import (
    Lead,
    Documento,
    HistorialEstado,
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
    Estado,
    Sector,
    Origen,
    CustomUser,
    Contrato
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.utils.timezone import now


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Endpoint para obtener un token de acceso y refresco.
    """
    serializer_class = CustomTokenObtainPairSerializer


class LeadListCreateView(APIView):
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
        Crea un nuevo lead y su documento relacionado.
        """
        serializer = LeadSerializer(data=request.data)
        if serializer.is_valid():
            try:
                lead = serializer.save(dueno=request.user)
                tipo_documento_id = request.data.get('tipo_documento')
                nro_documento = request.data.get('nro_documento')

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

class ConvertLeadToContractView(APIView):
    """
    Endpoint para convertir un lead en un contrato.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, lead_id):
        """
        Convierte un lead en un contrato.
        """
        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            return Response({"error": "Lead no encontrado"}, status=status.HTTP_404_NOT_FOUND)

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
            return Response({
                "message": "Lead convertido a contrato con éxito.",
                "contrato": {
                    "id": contrato.id,
                    "nombre_contrato": contrato.nombre_contrato,
                    "fecha_inicio": contrato.fecha_inicio,
                    "observaciones": contrato.observaciones
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"Error al convertir lead a contrato: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class LeadDetailView(APIView):
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
        estado_anterior = lead.estado
        serializer = LeadSerializer(lead, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                estado_nuevo = lead.estado
                if estado_anterior != estado_nuevo:
                    HistorialEstado.objects.create(
                        lead=lead,
                        estado_anterior=estado_anterior,
                        estado_nuevo=estado_nuevo,
                        usuario=request.user
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
        leads = self.get_queryset().filter(numero_movil__icontains=numero_movil)
        if not leads.exists():
            return Response({"message": "No se encontraron leads con ese número de móvil."}, status=status.HTTP_404_NOT_FOUND)
        serializer = LeadSerializer(leads, many=True)
        return Response(serializer.data)


class HistorialEstadoView(APIView):
    """
    Endpoint para listar el historial de cambios de estado de un lead.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self, lead_id):
        return HistorialEstado.objects.filter(lead_id=lead_id)

    def get(self, request, lead_id):
        queryset = self.get_queryset(lead_id)
        serializer = HistorialEstadoSerializer(queryset, many=True)
        return Response(serializer.data)

class OwnerListView(APIView):
    """
    Endpoint para listar todos los dueños (usuarios del modelo CustomUser).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        owners = CustomUser.objects.all()
        data = [
            {
                "id": owner.id,
                "username": owner.username,
                "email": owner.email,
                "nombres": owner.nombres,
                "apellidos": owner.apellidos,
            }
            for owner in owners
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


class GenericListView(APIView):
    """
    Endpoint genérico para listar elementos de tablas de referencia.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, model_name):
        models_map = {
            "tipo-documento": TipoDocumento,
            "resultado-cobertura": ResultadoCobertura,
            "transferencia": Transferencia,
            "tipo-vivienda": TipoVivienda,
            "tipo-base": TipoBase,
            "estado": Estado,
            "sector": Sector,
            "origen": Origen,
            "departamento": Departamento,  # Añadido para departamentos
            "tipo-contacto": TipoContacto,  # Añadido para tipos de contacto
        }
        model = models_map.get(model_name)
        if not model:
            return Response({"error": "Modelo no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        data = [{"id": obj.id, "nombre": str(obj)} for obj in model.objects.all()]
        return Response(data, status=status.HTTP_200_OK)

