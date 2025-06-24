from django.urls import path
from . import views

urlpatterns = [
    # Advocate-only endpoints
    path('api/invoice/', views.ClientInvoiceListCreateView.as_view(), name='client-invoice-list-create'),
    path('api/invoice/<int:pk>/', views.ClientInvoiceRetrieveUpdateDestroyView.as_view(), name='client-invoice-detail'),
    # Public endpoints
    path('api/invoice/<int:invoice_id>/download/', views.download_invoice_pdf, name='download-invoice-pdf'),
    path('api/invoice/<int:invoice_id>/print/', views.print_invoice_pdf, name='print-invoice-pdf'),
    # Client-only endpoints
    path('api/client/invoice/', views.ClientInvoiceListView.as_view(), name='client-invoice-list'),
    path('api/client/invoice/<int:pk>/', views.ClientInvoiceRetrieveView.as_view(), name='client-invoice-detail'),
    path('api/client/invoice/<int:invoice_id>/download/', views.client_download_invoice_pdf, name='client-download-invoice-pdf'),
    path('api/client/invoice/<int:invoice_id>/print/', views.client_print_invoice_pdf, name='client-print-invoice-pdf'),
]