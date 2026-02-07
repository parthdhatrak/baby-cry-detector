"""
ASGI config for crybaby project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crybaby.settings')

application = get_asgi_application()
