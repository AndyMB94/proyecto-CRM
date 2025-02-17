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
    ContratoListView,
    ConvertLeadToContractView,
    CreateUserView,
    LeadHistorialView,
    LeadsYContratosPorOrigenAPIView,
    ContratoDetailView,
    UserDetailView,
    ChangePasswordView,
    ConsultaCoberturaView,
    LeadMetadataView,
    ExportLeadsView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Token JWT
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Gestión de usuarios
    path('crear-usuario/', CreateUserView.as_view(), name='crear_usuario'),

    path('usuarios/cambiar-password/', ChangePasswordView.as_view(), name='cambiar_password'),

    # Gestión de usuarios
    path('usuarios/<int:user_id>/', UserDetailView.as_view(), name='user_detail'),  # Obtener detalles del usuario


    # Gestión de leads
    path('leads/', LeadListCreateView.as_view(), name='lead_list_create'),  # Listar y crear leads
    path('leads/<int:pk>/', LeadDetailView.as_view(), name='lead_detail'),  # Detalle, actualizar y eliminar lead
    path('leads/search/<str:numero_movil>/', LeadSearchByNumberView.as_view(), name='lead_search_by_number'),  # Buscar leads por número de móvil
    path('leads/<int:lead_id>/convert/', ConvertLeadToContractView.as_view(), name='convert_lead_to_contract'),  # Convertir lead a contrato

    path('consulta-cobertura/', ConsultaCoberturaView.as_view(), name='consulta_cobertura'),

    # Gestión de contratos
    path('contratos/', ContratoListView.as_view(), name='contrato_list'),  # Listar contratos

    path('contratos/<int:pk>/', ContratoDetailView.as_view(), name='contrato_detail'),  # Ver, editar y eliminar contratos

    # Gestión de ubicaciones
    path('provincias/<int:departamento_id>/', ProvinciaByDepartamentoView.as_view(), name='provincias_by_departamento'),  # Provincias por departamento
    path('distritos/<int:provincia_id>/', DistritoByProvinciaView.as_view(), name='distritos_by_provincia'),  # Distritos por provincia

    # Gestión de contactos
    path('subtipos/<int:tipo_contacto_id>/', SubtipoContactoByTipoContactoView.as_view(), name='subtipos_by_tipo_contacto'),  # Subtipos por tipo de contacto

    path('leads/<int:lead_id>/historial/', LeadHistorialView.as_view(), name='lead_historial'),

    path('leads-contratos-por-origen/', LeadsYContratosPorOrigenAPIView.as_view(), name='leads_contratos_por_origen'),

    # Listado genérico de tablas auxiliares
    path('<str:model_name>/', GenericListView.as_view(), name='generic_list'),  # Listar elementos de modelos auxiliares
    path('leads/metadata/', LeadMetadataView.as_view(), name='lead_metadata'),

    path('export-leads/<str:file_format>/', ExportLeadsView.as_view(), name='export_leads'),
]
