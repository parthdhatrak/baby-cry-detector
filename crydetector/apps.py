"""
Django AppConfig for crydetector.
Loads the ML model at application startup.
"""

import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class CrydetectorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crydetector'
    verbose_name = 'Baby Cry Detector'
    
    def ready(self):
        """
        Called when Django app is ready.
        Loads the ML model at startup to avoid per-request loading.
        """
        # Avoid running during migrations or management commands
        import sys
        if 'runserver' in sys.argv or 'gunicorn' in sys.modules:
            self._load_model()
    
    def _load_model(self):
        """
        Load the cry detection model.
        """
        try:
            from .model_loader import get_model, is_model_available
            
            logger.info("Initializing cry detection model...")
            get_model()
            
            if is_model_available():
                logger.info("Cry detection model loaded successfully at startup")
            else:
                logger.warning("Cry detection model not available - predictions will use mock data")
                
        except Exception as e:
            logger.error(f"Failed to load model at startup: {str(e)}")
