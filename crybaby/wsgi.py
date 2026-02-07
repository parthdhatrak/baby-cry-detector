"""
WSGI config for crybaby project.
Exposes the WSGI callable as a module-level variable named 'application'.
Used by Gunicorn for production deployment.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crybaby.settings')

application = get_wsgi_application()
