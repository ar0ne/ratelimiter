"""
URL configuration for project.
"""
from django.contrib import admin
from django.urls import path

from .api import api as api_v1

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/", api_v1.urls),
]
