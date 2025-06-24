from django.urls import path
from . import views

urlpatterns = [
    # Advocate-only endpoint
    path('api/calander/events/', views.CalendarEventsView.as_view(), name='calendar-events'),
    # Client-only endpoint
    path('api/client/calander/events/', views.ClientCalendarEventsView.as_view(), name='client-calendar-events'),
]