from django.urls import path
from .views import ConsultaAbonadoView

urlpatterns = [
    path('consulta/', ConsultaAbonadoView.as_view(), name='consulta'),
]
