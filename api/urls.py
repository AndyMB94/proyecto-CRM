from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    LeadListCreateView,
    LeadDetailView,
    LeadSearchByNumberView,
    HistorialEstadoView,
    ProvinciaByDepartamentoView,
    DistritoByProvinciaView,
    SubtipoContactoByTipoContactoView  
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('leads/', LeadListCreateView.as_view(), name='lead_list_create'),  # Listar y crear leads
    path('leads/<int:pk>/', LeadDetailView.as_view(), name='lead_detail'),  # Detalle, actualizar y eliminar lead
    path('leads/search/<str:numero_movil>/', LeadSearchByNumberView.as_view(), name='lead_search_by_number'),  # Buscar leads por número
    path('leads/<int:lead_id>/historial/', HistorialEstadoView.as_view(), name='lead_historial'),  # Historial de cambios de estado
    path('provincias/<int:departamento_id>/', ProvinciaByDepartamentoView.as_view(), name='provincias_by_departamento'),  # Provincias por departamento
    path('distritos/<int:provincia_id>/', DistritoByProvinciaView.as_view(), name='distritos_by_provincia'),  # Distritos por provincia
    path('subtipos/<int:tipo_contacto_id>/', SubtipoContactoByTipoContactoView.as_view(), name='subtipos_by_tipo_contacto'),  # Subtipos por tipo de contacto
]
