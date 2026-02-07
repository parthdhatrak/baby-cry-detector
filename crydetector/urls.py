"""
URL configuration for crydetector app.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Template views
    path('', views.home_view, name='home'),
    
    # API endpoints
    path('api/v1/predict/', views.api_v1_predict, name='api_v1_predict'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
]
