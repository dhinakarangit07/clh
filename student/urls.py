from django.urls import path
from .views import (
    LawStudentListCreateAPIView,
    LawStudentRetrieveUpdateDestroyAPIView
)

urlpatterns = [
    path('api/student/', LawStudentListCreateAPIView.as_view(), name='lawstudent-list-create'),
    path('api/student/<int:pk>/', LawStudentRetrieveUpdateDestroyAPIView.as_view(), name='lawstudent-detail'),
]
