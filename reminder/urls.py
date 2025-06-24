from django.urls import path
from . import views

urlpatterns = [
    # Advocate-only endpoints
    path('api/reminder/', views.ReminderListCreateView.as_view(), name='reminder-list-create'),
    path('api/reminder/<int:pk>/', views.ReminderRetrieveUpdateDestroyView.as_view(), name='reminder-detail'),
    # Client-only endpoint
    path('api/client/reminder/', views.ClientReminderListView.as_view(), name='client-reminder-list'),
]