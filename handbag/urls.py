from django.urls import path
from . import views

app_name = 'handbag'

urlpatterns = [
    # Advocate-only endpoints
    path('api/handbag-request/', views.HandbagRequestListCreateView.as_view(), name='handbag-request-list-create'),
    path('api/handbag-request/<int:pk>/', views.HandbagRequestRetrieveUpdateDestroyView.as_view(), name='handbag-request-detail'),
    path('api/handbag-request/check/', views.HandbagRequestCheckView.as_view(), name='handbag-request-check'),
]