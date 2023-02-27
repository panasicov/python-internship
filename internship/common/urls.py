from django.urls import path

from internship.common.views import HealthView, ProtectedTestView

urlpatterns = [
    path("health", HealthView.as_view(), name="health_view"),
    path("protected", ProtectedTestView.as_view(), name="protected_view"),
]
