from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    time_sum = serializers.SerializerMethodField()

    def get_time_sum(self, obj):
        return sum([timer.duration for timer in obj.created_timer_set.all() if timer.duration])

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'time_sum')


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return '{} {}'.format(obj.first_name, obj.last_name)

    class Meta:
        model = User
        fields = ('id', 'full_name',)
