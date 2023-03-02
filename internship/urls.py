from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from internship.common.helpers import schema_view

urlpatterns = [
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path('admin/', admin.site.urls),
    path("", include("internship.users.urls")),
    path("", include("internship.tasks.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
