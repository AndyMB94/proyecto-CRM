import requests

class APICliente:
    """
    Cliente HTTP para consultar la API de cobertura y mantener cookies.
    """

    def __init__(self):
        # Crear una sesión que mantiene cookies
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
        })
        self.api_url = "https://nubyx.purpura.pe/admin/cobertura"

    def consultar_cobertura(self, latitud, longitud):
        """
        Envía la solicitud a la API de cobertura manteniendo cookies.
        """
        payload = {"latitud": str(latitud), "longitud": str(longitud)}

        try:
            response = self.session.post(self.api_url, data=payload)

            if response.status_code == 200:
                return response.json().get("mensaje", "SIN_COBERTURA")

            return f"Error {response.status_code}: {response.text}"

        except requests.exceptions.RequestException as e:
            return f"Error en la solicitud: {str(e)}"
