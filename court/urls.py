from django.urls import path
from . import views

urlpatterns = [
    path('api/fetch/states/', views.StateFetchAPIView.as_view(), name='fetch-states'),
    path('api/fetch/districts/', views.DistrictFetchAPIView.as_view(), name='fetch-districts'),
    path('api/fetch/complexes/', views.ComplexFetchAPIView.as_view(), name='fetch-complexes'),
    path('api/fetch/courts/', views.CourtFetchAPIView.as_view(), name='fetch-courts'),
    
    path('api/court/', views.CourtListCreateView.as_view(), name='court-list-create'),
    path('api/court/<int:pk>/', views.CourtRetrieveUpdateDestroyView.as_view(), name='court-detail'),
]