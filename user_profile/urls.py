from django.urls import path
from . import views

urlpatterns = [
    path('api/user_profile/', views.ProfileView.as_view(), name='profile'),
    path('api/user_profile/password/change/', views.PasswordChangeView.as_view(), name='password-change'),
]