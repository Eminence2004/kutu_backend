# settings.py

import os
from pathlib import Path
from decouple import config
import dj_database_url

# ----------------------------
# 1. BASE DIR
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------
# 2. SECURITY
# ----------------------------
SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = [host.strip() for host in config(
    'ALLOWED_HOSTS', 
    default='127.0.0.1,localhost,0.0.0.0,kutu-backend.onrender.com'
).split(',')]

# ----------------------------
# 3. CORS
# ----------------------------
INSTALLED_APPS = [
    'corsheaders',  # Must be at the top for middleware
    # Default Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',

    # Your apps
    'accounts',
    'unfold',
    
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be high up
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# ----------------------------
# 4. URLS & WSGI
# ----------------------------
ROOT_URLCONF = 'kutu_core.urls'
WSGI_APPLICATION = 'kutu_core.wsgi.application'

# ----------------------------
# 5. DATABASE
# ----------------------------
# Use Render Postgres URL directly
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://kutu_db_user:voBDFr39HRUO7LKlunDp9BrmlxJ7FGoC@dpg-d6idg314tr6s73cbfti0-a/kutu_db',
        conn_max_age=600,
        ssl_require=True
    )
}

# ----------------------------
# 6. AUTH & REST FRAMEWORK
# ----------------------------
AUTH_USER_MODEL = 'accounts.User'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

# ----------------------------
# 7. TEMPLATES
# ----------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ----------------------------
# 8. STATIC & MEDIA
# ----------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ----------------------------
# 9. EMAIL (optional)
# ----------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=465, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# ----------------------------
# 10. UNFOLD CONFIG (Your Admin UI)
# ----------------------------
UNFOLD = {
    "SITE_TITLE": "KsTU Admin",
    "SITE_HEADER": "KsTU Campus Hub",
    "SITE_SYMBOL": "map",
    "COLORS": {
        "primary": {
            "50": "239 246 255",
            "100": "219 234 254",
            "200": "191 219 254",
            "300": "147 197 253",
            "400": "96 165 250",
            "500": "43 89 195",
            "600": "37 99 235",
            "700": "29 78 216",
            "800": "30 64 175",
            "900": "30 58 138",
            "950": "23 37 84",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
    },
}

# ----------------------------
# 11. INTERNATIONALIZATION
# ----------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ----------------------------
# 12. OPTIONAL: Terminal Info (for logs)
# ----------------------------
import socket

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

LOCAL_IP = get_ip()

print(f"\n--- 🚀 KUTU BACKEND STARTING ---")
print(f"Server IP: {LOCAL_IP}")
print(f"-------------------------------\n")