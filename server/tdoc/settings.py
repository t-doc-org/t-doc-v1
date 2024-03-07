import io
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Application definition
ROOT_URLCONF = 'tdoc.urls'
WSGI_APPLICATION = 'tdoc.wsgi.application'
INSTALLED_APPS = [
    'tdoc.app',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/cache/t-doc',
        'TIMEOUT': 30 * 24 * 3600,
        'OPTIONS': {'MAX_ENTRIES': 10000},
    }
}

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'fr-ch'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = 'static/'

# Application settings
DOC_ROOT = BASE_DIR.parent / "Documents"
RENDER_MODE = "final"
CACHE_HASH_SEED = b"1"

# Apply overrides from the file pointed by DJANGO_SETTINGS_PATH.
_path = os.environ.get('DJANGO_SETTINGS_PATH', BASE_DIR / 'settings_dev.py')
with io.open(_path, encoding='utf-8') as f:
    code = f.read()
exec(compile(code, _path, 'exec'))
