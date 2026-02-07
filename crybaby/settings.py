"""
Django settings for crybaby project.
Production-ready configuration for Baby Cry Reason Detection.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY: Load secret key from environment variable
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-key-change-in-production')

# SECURITY: Debug mode - MUST be False in production
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Allowed hosts for deployment
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Render.com specific: Add render hostname
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crydetector',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'crybaby.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'crybaby.wsgi.application'

# Database - SQLite for simplicity (can be upgraded to PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB

# API Key for authentication (stored in environment variable)
API_KEY = os.environ.get('CRY_DETECTION_API_KEY', 'dev-api-key-change-in-production')

# Model configuration
# FIX: Use correct model filename (.keras format) in project root
MODEL_PATH = os.environ.get('MODEL_PATH', str(BASE_DIR / 'baby_cry_reason_model.keras'))

# Audio preprocessing configuration
# FIX: Parameters MUST exactly match training to ensure consistent predictions
AUDIO_CONFIG = {
    'SAMPLE_RATE': 22050,      # Hz - must match training
    'DURATION': 4,              # seconds - fixed audio length from training
    'N_MFCC': 40,               # number of MFCC coefficients
    'N_FFT': 2048,              # FFT window size - must match training
    'HOP_LENGTH': 512,          # hop length between frames - must match training
    # MAX_PAD_LEN calculated: (sample_rate * duration) / hop_length + 1 = (22050 * 4) / 512 + 1 ≈ 173
    'MAX_PAD_LEN': 173,         # time steps for 4 seconds of audio
}

# Cry reason classes (must be alphabetical to match training folder structure)
CRY_CLASSES = ['belly_pain', 'burping', 'discomfort', 'hungry', 'tired']

# Automated reasoning for model predictions (2-3 lines each)
CRY_REASONS = {
    'hungry': "The acoustic pattern shows rhythmic, repeated 'neh' sounds linked to the sucking reflex. Its consistent pitch and melodic tone are classic indicators of a feeding need.",
    'belly_pain': "Detected as high-pitched, intense 'eairh' sounds with sharp energy spikes. The urgency in the spectral frequency suggests abdominal pressure or digestive discomfort.",
    'burping': "The model identified short, percussive bursts of air. These non-melodic sound patterns are typically caused by trapped gas in the upper digestive tract.",
    'discomfort': "Characterized by irregular, whining 'heh' sounds. The fluctuating volume and lack of high-intensity spikes point toward environmental or physical discomfort.",
    'tired': "The sound features deep, yawning vowels with a descending energy profile. These smooth spectral transitions occur when the baby is relaxing and needs sleep."
}

# Security settings for production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
