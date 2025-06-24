from django.urls import path
from .views import (
    AdvocateRegistrationListCreateAPIView,
    AdvocateRegistrationRetrieveUpdateDestroyAPIView,
    AdvocateUsersListAPIView,
    AdvocateDetailsByEmailAPIView,
)

urlpatterns = [
    path('api/advocates/', AdvocateRegistrationListCreateAPIView.as_view(), name='advocate-list-create'),
    path('api/advocates/<int:pk>/', AdvocateRegistrationRetrieveUpdateDestroyAPIView.as_view(), name='advocate-detail'),
    
    path('api/public/advocates/', AdvocateUsersListAPIView.as_view(), name='public-advocate-users'),
    path('api/public/advocates/<str:email>/', AdvocateDetailsByEmailAPIView.as_view(), name='public-advocate-details'),
]