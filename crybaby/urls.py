"""
URL configuration for crybaby project.
Routes for both API and template views.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('crydetector.urls')),  # Include crydetector app URLs
]
