from django.urls import path
from . import views

urlpatterns = [
    path('api/advocate/', views.AdvocateListCreateView.as_view(), name='advocate-list-create'),
    path('api/advocate/<int:pk>/', views.AdvocateRetrieveUpdateDestroyView.as_view(), name='advocate-detail'),
]