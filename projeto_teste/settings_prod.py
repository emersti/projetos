"""
Django settings for projeto_teste project - Produção
"""

import os
import dj_database_url
from decouple import config
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-your-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,safetyscorebrasil.com.br,www.safetyscorebrasil.com.br', cast=lambda v: [s.strip() for s in v.split(',')])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'consulta_risco',  # Nossa app principal
    'django_ses',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para servir arquivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'consulta_risco.middleware.MaintenanceMiddleware',  # Middleware de manutenção
]

ROOT_URLCONF = 'projeto_teste.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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

WSGI_APPLICATION = 'projeto_teste.wsgi.application'

# Database
# Usando PostgreSQL em produção
DATABASES = {
    'default': dj_database_url.parse(
        config('DATABASE_URL', default='sqlite:///db.sqlite3')
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Configuração do WhiteNoise para arquivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configurações de Sessão
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
SESSION_COOKIE_HTTPONLY = True
SESSION_SAVE_EVERY_REQUEST = True

# Configurações de Segurança
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Configurações de HTTPS (quando disponível)
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Criar diretório de logs se não existir
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Configurações de arquivos de mídia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configurações de CSRF
CSRF_TRUSTED_ORIGINS = [
    "https://safetyscorebrasil.com.br",
    "https://www.safetyscorebrasil.com.br",
]

# Configurações de CORS
CORS_ALLOWED_ORIGINS = [
    "https://safetyscorebrasil.com.br",
    "https://www.safetyscorebrasil.com.br",
]

# Configurações de email
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
#EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
#EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
#EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
#EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
# DEFAULT_FROM_EMAIL: usa o valor da variável de ambiente ou EMAIL_HOST_USER como fallback, ou um padrão
#DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER or 'noreply@safetyscorebrasil.com.br')

# Configurações de cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
    }
}

# Configurações de AWS S3 (opcional)
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')

# Configurações de internacionalização
USE_I18N = False
USE_L10N = False

# Configurações de middleware de idioma
MIDDLEWARE.insert(2, 'django.middleware.locale.LocaleMiddleware')

# Configurações de context processors
TEMPLATES[0]['OPTIONS']['context_processors'].extend([
    'django.template.context_processors.i18n',
    'consulta_risco.context_processors.ultima_atualizacao',
])

# Configurações de idiomas suportados
LANGUAGES = [
    ('pt-br', 'Português'),
    ('en', 'English'),
]

# Diretório para arquivos de tradução
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Configurações de segurança adicional
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# Configurações de sessão adicional
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# Configurações de arquivos estáticos adicionais
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Configurações de WhiteNoise
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

# Email Backend
EMAIL_BACKEND = 'django_ses.SESBackend'

# AWS Credentials
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_SES_REGION_NAME = config('AWS_SES_REGION_NAME', default='us-east-1')
AWS_SES_REGION_ENDPOINT = config('AWS_SES_REGION_ENDPOINT', default='email.us-east-1.amazonses.com')

# Email Settings
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='contato@stigliani.com.br')
SERVER_EMAIL = config('SERVER_EMAIL', default='contato@stigliani.com.br')

# Configuration Set (opcional - crie depois se precisar)
# AWS_SES_CONFIGURATION_SET = 'my-configuration-set'

# Para desenvolvimento local (mostra no console)
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


















