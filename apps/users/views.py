from django.contrib.auth import get_user_model
from django.db.models import Sum, F, Q
from django.utils import timezone
from django.db.models.functions import Coalesce
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
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


class UserMonthTimeLogView(RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return User.objects.filter(pk=self.request.user.pk).annotate(
            time_sum=Sum(
                Coalesce('created_timelog_set__stop', timezone.now()) - F('created_timelog_set__start'),
            filter=Q(created_timelog_set__start__gte=timezone.now() - timezone.timedelta(days=30)))
        ).first()
