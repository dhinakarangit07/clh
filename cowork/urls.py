from django.urls import path
from . import views

app_name = 'cowork'

urlpatterns = [
    # Advocate-only endpoints
    path('api/coworking-request/', views.CoworkingRequestListCreateView.as_view(), name='coworking-request-list-create'),
    path('api/coworking-request/<int:pk>/', views.CoworkingRequestRetrieveUpdateDestroyView.as_view(), name='coworking-request-detail'),
    path('api/coworking-request/check/', views.CoworkingRequestCheckView.as_view(), name='coworking-request-check'),
]