from django.urls import path
from .views import ConsultaAbonadoView

urlpatterns = [
    path('consulta-abonado/', ConsultaAbonadoView.as_view(), name='consulta_abonado'),
]
