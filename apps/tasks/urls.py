from rest_framework.routers import DefaultRouter

from apps.tasks.views import TaskViewSet


router = DefaultRouter()
router.register('task', TaskViewSet, basename="task")

urlpatterns = [

] + router.urls
