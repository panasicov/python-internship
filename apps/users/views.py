from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers import UserListSerializer, UserSerializer


User = get_user_model()


class RegisterUserView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        password = validated_data.pop('password')

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
