from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, LeadSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Lead
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LeadListCreateView(APIView):
    """
    Endpoint para listar y crear leads.
    Solo usuarios autenticados con permisos adecuados pueden acceder.
    """
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_queryset(self):
        # Devuelve todos los leads (o filtra según el usuario si es necesario)
        return Lead.objects.all()

    def get(self, request):
        leads = self.get_queryset()
        serializer = LeadSerializer(leads, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LeadSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(dueno=request.user)  # Asigna el dueño como el usuario autenticado
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": f"Error al guardar el lead: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeadDetailView(APIView):
    """
    Endpoint para obtener, actualizar o eliminar un lead específico.
    Requiere autenticación y permisos.
    """
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_queryset(self):
        # Devuelve todos los leads (o filtra según el usuario si es necesario)
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
        serializer = LeadSerializer(lead, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
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
