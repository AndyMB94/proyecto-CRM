from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    LeadListCreateView,
    LeadDetailView,
    LeadSearchByNumberView,
    ProvinciaByDepartamentoView,
    DistritoByProvinciaView,
    SubtipoContactoByTipoContactoView,
    GenericListView,
    OwnerListView,
    ContratoListView,
    ConvertLeadToContractView,
    CreateUserView,
    LeadHistorialView,
    LeadsYContratosPorOrigenAPIView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Token JWT
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Gestión de usuarios
    path('crear-usuario/', CreateUserView.as_view(), name='crear_usuario'),

    # Gestión de leads
    path('leads/', LeadListCreateView.as_view(), name='lead_list_create'),  # Listar y crear leads
    path('leads/<int:pk>/', LeadDetailView.as_view(), name='lead_detail'),  # Detalle, actualizar y eliminar lead
    path('leads/search/<str:numero_movil>/', LeadSearchByNumberView.as_view(), name='lead_search_by_number'),  # Buscar leads por número de móvil
    path('leads/<int:lead_id>/convert/', ConvertLeadToContractView.as_view(), name='convert_lead_to_contract'),  # Convertir lead a contrato

    # Gestión de contratos
    path('contratos/', ContratoListView.as_view(), name='contrato_list'),  # Listar contratos

    # Gestión de dueños
    path('owners/', OwnerListView.as_view(), name='owner_list'),  # Listar usuarios (dueños)

    # Gestión de ubicaciones
    path('provincias/<int:departamento_id>/', ProvinciaByDepartamentoView.as_view(), name='provincias_by_departamento'),  # Provincias por departamento
    path('distritos/<int:provincia_id>/', DistritoByProvinciaView.as_view(), name='distritos_by_provincia'),  # Distritos por provincia

    # Gestión de contactos
    path('subtipos/<int:tipo_contacto_id>/', SubtipoContactoByTipoContactoView.as_view(), name='subtipos_by_tipo_contacto'),  # Subtipos por tipo de contacto

    path('leads/<int:lead_id>/historial/', LeadHistorialView.as_view(), name='lead_historial'),

    path('leads-contratos-por-origen/', LeadsYContratosPorOrigenAPIView.as_view(), name='leads_contratos_por_origen'),

    # Listado genérico de tablas auxiliares
    path('<str:model_name>/', GenericListView.as_view(), name='generic_list'),  # Listar elementos de modelos auxiliares
]
