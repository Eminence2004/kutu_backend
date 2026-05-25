import os
import socket
from pathlib import Path
from decouple import config
import dj_database_url
from datetime import timedelta

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
    default='127.0.0.1,localhost,0.0.0.0',
).split(',')]

# Dynamic CSRF trusted origins based on ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS = [
    f"http://{host}" if not host.startswith(('http://', 'https://')) else host
    for host in ALLOWED_HOSTS if host not in ['127.0.0.1', 'localhost', '0.0.0.0']
] + [
    "https://*.sslip.io",
]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
}

# 🔒 Production Security
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ----------------------------
# 3. INSTALLED APPS
# ⚠️ unfold MUST come before django.contrib.admin
# ----------------------------
INSTALLED_APPS = [
    # Unfold (must be first, before django.contrib.admin)
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',

    # Cloudinary for media storage
    'cloudinary_storage',
    'cloudinary',

    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'sslserver',

    # Local apps
    'accounts',
    'navigation',
]

# ----------------------------
# 4. MIDDLEWARE
# ⚠️ WhiteNoise must be right after SecurityMiddleware
# ----------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ----------------------------
# 5. CORS
# ----------------------------
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# ----------------------------
# 6. URLS & WSGI/ASGI
# ----------------------------
ROOT_URLCONF = 'kutu_core.urls'
WSGI_APPLICATION = 'kutu_core.wsgi.application'

# ----------------------------
# 7. DATABASE
# ----------------------------
_db_url = config('DATABASE_URL', default='')

if _db_url and not _db_url.startswith('sqlite'):
    # Production — Neon PostgreSQL with SSL
    DATABASES = {
        'default': dj_database_url.config(
            default=_db_url,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    # Local dev — SQLite, no SSL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ----------------------------
# 8. AUTH & REST FRAMEWORK
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
# 9. TEMPLATES
# ----------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'accounts' / 'templates'],
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
# 10. STATIC & MEDIA
# ----------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ----------------------------
# 10.5. CLOUDINARY (for production media storage)
# ----------------------------
import cloudinary
import cloudinary.uploader
import cloudinary.api

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
}

cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    secure=True
)

# ----------------------------
# 10.6. STORAGES (Django 4.2+ unified storage config)
# Replaces DEFAULT_FILE_STORAGE and STATICFILES_STORAGE
# ----------------------------
_is_production = _db_url and not _db_url.startswith('sqlite')

STORAGES = {
    "default": {
        # Use Cloudinary in production, local filesystem in dev
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage" if _is_production else "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # WhiteNoise for static files in both environments
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ----------------------------
# 11. EMAIL
# ----------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=465, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# ----------------------------
# 12. UNFOLD ADMIN CONFIG
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
        "navigation": [
            {
                "title": "Dashboard",
                "separator": True,
                "items": [
                    {
                        "title": "📊 Stats & Analytics",
                        "link": "/admin/dashboard/",
                        "icon": "bar_chart",
                    },
                ],
            },
            {
                "title": "Users",
                "separator": False,
                "items": [
                    {
                        "title": "👥 Students",
                        "link": "/admin/accounts/user/",
                        "icon": "people",
                    },
                ],
            },
            {
                "title": "Content",
                "separator": False,
                "items": [
                    {
                        "title": "📸 Posts",
                        "link": "/admin/accounts/post/",
                        "icon": "photo_camera",
                    },
                ],
            },
            {
                "title": "Campus Map",
                "separator": False,
                "items": [
                    {
                        "title": "📍 Suggested Locations",
                        "link": "/admin/navigation/suggestedlocation/",
                        "icon": "add_location",
                    },
                    {
                        "title": "🗺️ Post Locations",
                        "link": "/admin/navigation/postlocationsuggestion/",
                        "icon": "location_on",
                    },
                    {
                        "title": "🚻 Washrooms",
                        "link": "/admin/navigation/washroom/",
                        "icon": "wc",
                    },
                ],
            },
        ],
    },
}

# ----------------------------
# 13. INTERNATIONALIZATION
# ----------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ----------------------------
# 14. STARTUP LOG
# ----------------------------
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