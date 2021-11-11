"""meeting_sample URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from meeting_sample import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/common/', include('common.urls')),
    path('api/user/', include('user.urls')),
    path('api/meeting/', include('meeting.urls')),
    path('api/poll/', include('poll.urls')),
    path('api/group/', include('group.urls')),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(
            title="Meeting Sample",
            default_version='v1.0.0',
            description="meeting sample backend API",
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )
    urlpatterns += [
        re_path('^swagger(?P<format>.json|.yaml)$', schema_view.without_ui(cache_timeout=0),
                name='schema-json'),
        path('swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    ]
