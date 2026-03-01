import socket
import os
from pathlib import Path
from decouple import config

# 1. Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. AUTO-IP DETECTION
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

# 3. SECURITY
SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DEBUG', default=True, cast=bool)
# Added a list comprehension to ensure no empty strings or spaces break the server
ALLOWED_HOSTS = [host.strip() for host in config('ALLOWED_HOSTS', default=f'{LOCAL_IP},127.0.0.1,localhost,0.0.0.0').split(',')]

# 4. CORS
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# 5. APPLICATION DEFINITION
INSTALLED_APPS = [
    "unfold",  # <--- CRITICAL: Must be at the top
    "unfold.contrib.filters",  # Optional modern filters
    "unfold.contrib.forms",    # Optional modern forms
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Your Apps
    'accounts',
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kutu_core.urls'

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

WSGI_APPLICATION = 'kutu_core.wsgi.application'

# 6. DATABASE (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='kutu_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default=5432, cast=int),
    }
}

# 7. AUTH & REST FRAMEWORK
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

# 8. EMAIL & MEDIA
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = 'static/'

# 9. INTERNATIONALIZATION
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 10. UNFOLD CONFIGURATION (The "Nice UI" settings)
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
            "500": "43 89 195", # Your Brand Blue #2b59c3
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

# Terminal Info
print(f"\n--- 🚀 KUTU BACKEND STARTING ---")
print(f"Server IP: {LOCAL_IP}")
print(f"API Base: http://{LOCAL_IP}:8000")
print(f"-------------------------------\n")