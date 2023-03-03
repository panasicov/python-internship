__all__ = [
    'RegisterUserView',
    'UserListView',
    'UserMonthTimeView'
]

from django.contrib.auth import get_user_model
from rest_framework.generics import (
    CreateAPIView, ListAPIView, RetrieveAPIView
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from internship.users.serializers import (
    UserListSerializer, UserSerializer,
    UserMonthTimeSerializer
)

User = get_user_model()


class RegisterUserView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data["password"]

        user = serializer.save()
        user.set_password(password)
        user.save()

        token = RefreshToken.for_user(user)
        return Response({
            'refresh': str(token),
            'access': str(token.access_token),
        })


class UserListView(ListAPIView):
    queryset = User.objects.only('first_name', 'last_name')
    serializer_class = UserListSerializer
    permission_classes = (AllowAny,)


class UserMonthTimeView(RetrieveAPIView):
    serializer_class = UserMonthTimeSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
