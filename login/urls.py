from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, CustomTokenRefreshView, UserDetailView, CustomTokenObtainPairView

urlpatterns = [
    path("api/auth/signup/", RegisterView.as_view(), name="signup"),
    path("api/auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/user/", UserDetailView.as_view(), name="user_detail"),
]