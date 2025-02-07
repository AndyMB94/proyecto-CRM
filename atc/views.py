from django.shortcuts import render
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AbonadoSerializer
from rest_framework.permissions import AllowAny

class ConsultaAbonadoView(APIView):
    """
    Permite consultar la API de Nubyx usando `codigoAbonado` o `numeroDocumento`.
    Excluye la clave `tickets` en la respuesta.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        url = "https://api.nubyx.pe/five9/consulta"

        # Obtener los valores de los parámetros enviados en el body
        codigo_abonado = request.data.get("codigoAbonado")
        numero_documento = request.data.get("numeroDocumento")

        # Verificar que al menos uno de los dos parámetros sea enviado
        if not codigo_abonado and not numero_documento:
            return Response(
                {"error": "Debes proporcionar 'codigoAbonado' o 'numeroDocumento' para realizar la consulta."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Definir los datos a enviar según el parámetro proporcionado
        payload = {}
        if codigo_abonado:
            payload["codigoAbonado"] = codigo_abonado
        elif numero_documento:
            payload["numeroDocumento"] = numero_documento  # Si no hay código abonado, usar documento

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

                return Response({"error": "No se encontraron datos para los valores ingresados."}, status=status.HTTP_404_NOT_FOUND)

            return Response({"error": f"Error en la API externa: {response.text}"}, status=response.status_code)

        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
