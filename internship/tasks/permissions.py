from rest_framework.permissions import BasePermission

from internship.tasks.models import TimeLog


class CanStartTimeLog(BasePermission):
    message = 'Cannot start a new time log before stopping the last one.'

    def has_permission(self, request, view):
        last_timer = TimeLog.objects.filter(
            task_id=request.data['task'],
            created_by=request.user
        ).order_by('id').last()
        return not (last_timer and not last_timer.duration)


class CanStopTimeLog(BasePermission):
    message = 'Cannot stop time log before starting the new one.'

    def has_permission(self, request, view):
        last_timer = TimeLog.objects.filter(
            task_id=request.data['task'],
            created_by=request.user
        ).order_by('id').last()
        return not (not last_timer or last_timer.duration)
