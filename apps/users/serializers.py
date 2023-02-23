from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    time_sum_minutes = serializers.SerializerMethodField()

    def get_time_sum_minutes(self, obj):
        try:
            return obj.time_sum.total_seconds() / 60
        except AttributeError:
            instance = obj.created_timelog_set.annotate(
                time_sum=Sum(
                    Coalesce('stop', timezone.now()) - F('start')
                )
            ).first()
            if instance and instance.time_sum:
                return instance.time_sum.total_seconds() / 60

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'time_sum_minutes')


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return '{} {}'.format(obj.first_name, obj.last_name)

    class Meta:
        model = User
        fields = ('id', 'full_name',)
