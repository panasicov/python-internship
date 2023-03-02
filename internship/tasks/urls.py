from rest_framework.routers import DefaultRouter

from internship.tasks.views import TaskViewSet


router = DefaultRouter()
router.register('task', TaskViewSet, basename="task")

urlpatterns = router.urls
