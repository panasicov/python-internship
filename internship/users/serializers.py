from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Sum
from rest_framework import serializers
from dateutil.relativedelta import relativedelta


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'password')


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return '{} {}'.format(obj.first_name, obj.last_name)

    class Meta:
        model = User
        fields = ('id', 'full_name',)


class UserMonthTimeSerializer(serializers.ModelSerializer):
    time_sum_minutes = serializers.SerializerMethodField()

    def get_time_sum_minutes(self, obj):
        duration_sum = obj.created_timelog_set.filter(
            created_by=self.context.get('request', None).user,
            start__gte=timezone.now() - relativedelta(month=1)
        ).aggregate(
            Sum('duration')
        )['duration__sum']
        return duration_sum.total_seconds() / 60

    class Meta:
        model = User
        fields = ('time_sum_minutes',)
