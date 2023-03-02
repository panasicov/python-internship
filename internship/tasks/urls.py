from rest_framework.routers import DefaultRouter

from internship.tasks.views import TaskViewSet, TimeLogViewSet


router = DefaultRouter(trailing_slash=False)
router.register('task', TaskViewSet, basename="task")
router.register('timelog', TimeLogViewSet, basename="task")

urlpatterns = router.urls
