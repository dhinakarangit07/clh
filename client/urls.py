from django.urls import path
from . import views

urlpatterns = [
    path('api/client/', views.ClientListCreateView.as_view(), name='client-list-create'),
    path('api/client/<int:pk>/', views.ClientRetrieveUpdateDestroyView.as_view(), name='client-detail'),
]