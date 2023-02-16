from django.urls import path

from rest_framework.routers import DefaultRouter

from apps.tasks.views import (
    TaskViewSet,
)


router = DefaultRouter()
router.register('task', TaskViewSet)


urlpatterns = [

] + router.urls
