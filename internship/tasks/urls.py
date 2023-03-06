from django.conf import settings
from django.urls import re_path
from django.views.static import serve
from rest_framework.routers import DefaultRouter

from internship.tasks.views import TaskViewSet, TimeLogViewSet, AttachmentViewSet

router = DefaultRouter(trailing_slash=False)
router.register('task', TaskViewSet, basename="task")
router.register('timelog', TimeLogViewSet, basename="timelog")
router.register('attachment', AttachmentViewSet, basename="attachment")

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
] + router.urls
