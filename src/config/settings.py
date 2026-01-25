"""
Django settings for CodeVoice project.
"""

from pathlib import Path
import os
import environ # This comes from 'django-environ' in your requirements.txt

# --- 1. SETUP ENV READER ---
# Initialize environment variables
env = environ.Env()

# --- 2. DEFINE PATHS ---
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Take environment variables from .env file at the project root
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# --- 3. SECURITY ---
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-change-me-later')

# SECURITY WARNING: don't run with debug turned on in production!
# We use 'False' as a default if DEBUG is not set in .env
DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = ['*'] # Allow all hosts for local dev/Docker


# --- 4. INSTALLED APPS ---
INSTALLED_APPS = [
    # TEACHER NOTE 1:
    # 'daphne' must be at the very top to override the default 'runserver' command.
    # This allows 'python manage.py runserver' to handle WebSockets.
    'daphne',

    # Default Django Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-Party Apps (From your requirements.txt)
    'rest_framework',      # For building APIs
    'corsheaders',         # For handling Cross-Origin requests
    # 'django_celery_results', # (Optional: Uncomment if using Celery Results later)

    # Local Apps (Your custom logic)
    # We prefix them with 'apps.' because they live in the 'src/apps/' folder.
    'apps.users',
    # 'apps.interviews',
    # 'apps.simulation', # We will enable this later when we build the AI brain
]

# --- 5. MIDDLEWARE ---
# Middleware is a security gate. Every request passes through this list from top to bottom.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    
    # CorsMiddleware should be as high as possible, before any view logic
    'corsheaders.middleware.CorsMiddleware', 
    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- 6. CORE CONFIGURATIONS ---

# Points to src/config/urls.py
ROOT_URLCONF = 'config.urls'

# The entry points we created earlier
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Templates (HTML files)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # We will create a global 'templates' folder later
        'DIRS': [BASE_DIR / 'templates'], 
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

# --- 7. DATABASE CONFIGURATION ---
# TEACHER NOTE:
# We use 'env.db()' which looks for a DATABASE_URL in your .env file.
# Format: postgres://user:password@localhost:5432/dbname
DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')
}

# --- 8. PASSWORD VALIDATION ---
# Checks if passwords are too simple (standard Django security).
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# --- 9. INTERNATIONALIZATION ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- 10. STATIC FILES (CSS, JavaScript, Images) ---
# This is where Django collects files to serve them to the browser.
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# --- 11. CUSTOM USER MODEL ---
# TEACHER NOTE (CRITICAL):
# By default, Django uses a built-in user model. 
# We are overriding it with our own 'User' model in the 'users' app.
# If we don't set this now, changing it later is a nightmare.
AUTH_USER_MODEL = 'users.User'

# --- 12. CORS CONFIGURATION ---
# Allows your frontend (or API clients) to talk to this backend.
CORS_ALLOW_ALL_ORIGINS = True # For development only. strict in production!

# --- 13. PROJECT SPECIFIC SETTINGS (Environment Variables) ---
# We load these here so we can import 'settings' elsewhere and access them easily.

# LiveKit (Video/Audio Streaming)
LIVEKIT_API_URL = env('LIVEKIT_URL', default='ws://localhost:7880')
LIVEKIT_API_KEY = env('LIVEKIT_API_KEY')
LIVEKIT_API_SECRET = env('LIVEKIT_API_SECRET')

# AI Services
KRUTRIM_API_KEY = env('KRUTRIM_API_KEY', default='')
DEEPGRAM_API_KEY = env('DEEPGRAM_API_KEY', default='')

# Celery (Async Tasks)
CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/0')