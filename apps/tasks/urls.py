from django.urls import path

from apps.tasks.views import (
    TaskView, TaskItemView, UserTaskView,
    CompletedTasksView, AssignTaskItemView,
    CompleteTaskItemView, TaskItemCommentView
)


urlpatterns = [
    path("task", TaskView.as_view(), name="task"),
    path("task/<int:pk>", TaskItemView.as_view(), name="task_item"),
    path("task/my", UserTaskView.as_view(), name="user_task"),
    path("task/completed", CompletedTasksView.as_view(), name="completed_tasks"),
    path("task/<int:pk>/assign", AssignTaskItemView.as_view(), name="assign_task"),
    path("task/<int:pk>/complete", CompleteTaskItemView.as_view(), name="complete_task"),
    path("task/<int:pk>/comment", TaskItemCommentView.as_view(), name="add_comment"),
]
