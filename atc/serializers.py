from rest_framework import serializers

class AbonadoSerializer(serializers.Serializer):
    idServicio = serializers.CharField()
    filial = serializers.CharField()
    codigoAbonado = serializers.CharField()
    telefono = serializers.CharField(allow_blank=True, required=False)
    celular = serializers.CharField(allow_blank=True, required=False)
    documentoIdentidad = serializers.CharField()
    nombres = serializers.CharField()
    apellidos = serializers.CharField()
    provincia = serializers.CharField(allow_blank=True, required=False)
    distrito = serializers.CharField(allow_blank=True, required=False)
    direccion = serializers.CharField(allow_blank=True, required=False)
    deuda = serializers.FloatField()
    planContratado = serializers.CharField(allow_blank=True, required=False)
    estadoServicio = serializers.CharField()
    fechaInstalacion = serializers.CharField()
    claseServicio = serializers.CharField()
    correo = serializers.EmailField(allow_blank=True, required=False)
    latitud = serializers.CharField(allow_blank=True, required=False)
    longitud = serializers.CharField(allow_blank=True, required=False)

    # Excluimos el campo 'tickets' (no lo incluimos en el serializer)
