from django.urls import path
from .views import CustomTokenObtainPairView, LeadListCreateView, LeadDetailView, LeadSearchView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('leads/', LeadListCreateView.as_view(), name='lead_list_create'),  # Listar y crear leads
    path('leads/<int:pk>/', LeadDetailView.as_view(), name='lead_detail'),  # Detalle, actualizar y eliminar lead
    path('leads/search/', LeadSearchView.as_view(), name='lead_search'),  # Buscar leads por número de móvil
]
