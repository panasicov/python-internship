from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from internship.users.views import (
    RegisterUserView, UserListView,
    UserMonthTimeView
)

urlpatterns = [
    path('register', RegisterUserView.as_view(), name='token_register'),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('users', UserListView().as_view(), name='user_list'),
    path('users/me/month_time', UserMonthTimeView().as_view(), name='user_month_time'),
]
