from django.contrib.auth import get_user_model
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers import RegisterUserSerializer, UserListSerializer


User = get_user_model()


class RegisterUserView(GenericAPIView):
    serializer_class = RegisterUserSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        password = validated_data.pop('password')
        user = User.objects.create(**validated_data,)
        user.set_password(password)
        user.save()

        token = RefreshToken.for_user(user)
        return Response({
            'refresh': str(token),
            'access': str(token.access_token),
        })


class UserListView(ListAPIView):
    queryset = User.objects.only('id', 'first_name', 'last_name')
    serializer_class = UserListSerializer
    permission_classes = (AllowAny,)
