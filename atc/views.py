from django.shortcuts import render
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AbonadoSerializer
from rest_framework.permissions import AllowAny

# Create your views here.

class ConsultaAbonadoView(APIView):
    """
    Consume la API de Nubyx y devuelve la información del abonado,
    excluyendo los datos de tickets, utilizando un serializer.
    """

    permission_classes = [AllowAny]
    def post(self, request):
        url = "https://api.nubyx.pe/five9/consulta"
        codigo_abonado = request.data.get("codigoAbonado")

        if not codigo_abonado:
            return Response({"error": "El campo 'codigoAbonado' es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        # Configurar los datos en formato x-www-form-urlencoded
        payload = {"codigoAbonado": codigo_abonado}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            # Hacer la solicitud a la API externa
            response = requests.post(url, data=payload, headers=headers)

            # Verificar si la respuesta es correcta (código 200)
            if response.status_code == 200:
                data = response.json()

                if isinstance(data, list) and len(data) > 0:
                    abonado_data = data[0]  # Extraemos el primer elemento de la lista
                    
                    # Excluir el campo 'tickets'
                    abonado_data.pop("tickets", None)

                    # Validar los datos con el serializer
                    serializer = AbonadoSerializer(data=abonado_data)

                    if serializer.is_valid():
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                return Response({"error": "No se encontraron datos para el código ingresado"}, status=status.HTTP_404_NOT_FOUND)

            return Response({"error": f"Error en la API externa: {response.text}"}, status=response.status_code)

        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)