from django.urls import path
from . import views

urlpatterns = [
    # Advocate-only endpoints
    path('api/case/', views.CaseListCreateView.as_view(), name='case-list-create'),
    path('api/case/<int:pk>/', views.CaseRetrieveUpdateDestroyView.as_view(), name='case-detail'),
    path('api/case/scrape/<str:cnr_number>/', views.CaseScrapeView.as_view(), name='case-scrape'),
    # Client-only endpoints
    path('api/client/case/', views.ClientCaseListView.as_view(), name='client-case-list'),
    path('api/client/case/<int:pk>/', views.ClientCaseDetailView.as_view(), name='client-case-detail'),
    # Junior-only endpoints
    path('api/junior/case/', views.JuniorCaseListView.as_view(), name='junior-case-list'),
    path('api/junior/case/<int:pk>/', views.JuniorCaseDetailView.as_view(), name='junior-case-detail'),
]