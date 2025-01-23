from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, LeadSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Lead
from rest_framework.permissions import IsAuthenticated


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
        Crea un nuevo lead. El usuario autenticado se asigna como dueño.
        """
        serializer = LeadSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(dueno=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {"error": f"Error al guardar el lead: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeadDetailView(APIView):
    """
    Endpoint para obtener, actualizar o eliminar un lead específico.
    Requiere autenticación.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Devuelve el conjunto de datos de leads.
        """
        return Lead.objects.all()

    def get_object(self, pk):
        """
        Intenta recuperar un lead por su clave primaria (pk).
        Retorna None si no existe.
        """
        try:
            return self.get_queryset().get(pk=pk)
        except Lead.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Devuelve los detalles de un lead específico.
        """
        lead = self.get_object(pk)
        if lead is None:
            return Response({"error": "Lead no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = LeadSerializer(lead)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Actualiza un lead específico.
        """
        lead = self.get_object(pk)
        if lead is None:
            return Response({"error": "Lead no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = LeadSerializer(lead, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data)
            except Exception as e:
                return Response(
                    {"error": f"Error al actualizar el lead: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Elimina un lead específico.
        """
        lead = self.get_object(pk)
        if lead is None:
            return Response({"error": "Lead no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        try:
            lead.delete()
            return Response({"message": "Lead eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"error": f"Error al eliminar el lead: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class LeadSearchByNumberView(APIView):
    """
    Endpoint para buscar leads por número de móvil.
    Requiere autenticación.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, numero_movil):
        """
        Busca leads cuyo número de móvil contenga la cadena proporcionada.
        """
        leads = Lead.objects.filter(numero_movil__icontains=numero_movil)
        if not leads.exists():
            return Response(
                {"message": "No se encontraron leads con ese número de móvil."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = LeadSerializer(leads, many=True)
        return Response(serializer.data)
