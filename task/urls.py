from django.urls import path
from . import views

urlpatterns = [
    # Advocate-only endpoints (also accessible to corporate clients)
    path('api/task/', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('api/task/<int:pk>/', views.TaskRetrieveUpdateDestroyView.as_view(), name='task-detail'),
    path('api/task/assigned/', views.AssignedTaskListView.as_view(), name='assigned-task-list'),
    # Junior-only endpoints
    path('api/junior/task/', views.JuniorTaskListView.as_view(), name='junior-task-list'),
    path('api/junior/task/<int:pk>/status/', views.JuniorTaskStatusUpdateView.as_view(), name='junior-task-status'),
]