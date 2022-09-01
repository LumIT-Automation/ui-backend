import os
import dns.resolver
from datetime import timedelta

from ui_backend.helpers.Process import Process
from ui_backend.helpers.Log import Log

# JWT settings.
from backend.settings_jwt import *


# Resolver.
consulResolver = dns.resolver.Resolver()
consulResolver.nameservers = ['127.0.0.1']
consulResolver.nameserver_ports = {
    '127.0.0.1': 8600
}

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'o7lx@83-%tdncpo0qx4h#nbf-kd_bbswajgrvigy55-c8z!#dz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# VENV_BIN = ""

# Application definition
# To include the app in our project add a reference to its configuration class in the INSTALLED_APPS.
# The AwxConfig class is in the ui_backend/apps.py file, so its dotted path is 'ui_backend.apps.AwxConfig'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'ui_backend.middleware.Log.LogMiddleware',
    'ui_backend.middleware.HTTP.HTTPMiddleware',
]

ROOT_URLCONF = 'backend.urls'

SETTINGS_PATH = os.path.dirname(os.path.dirname(__file__))
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["os.path.join(SETTINGS_PATH, 'templates')"],
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

WSGI_APPLICATION = 'backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.mysql',
#        'NAME': 'uib',
#        'USER': 'uib',
#        'PASSWORD': 'password',
#        'HOST': '127.0.0.1',
#        'PORT': '3306',
#    }
#}

# Redis cache

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'django': {
            'format': 'DJANGO_UIB - %(message)s',
        },
        'http': {
            'format': 'HTTP_UIB - %(message)s',
        },
    },
    'handlers': {
        #'file': {
        #    'level': 'DEBUG',
        #    'class': 'logging.FileHandler',
        #    'filename': '/var/log/django-ui/django-ui.log',
        #},
        'syslog_django': {
            'class': 'logging.handlers.SysLogHandler',
            'level': 'DEBUG',
            'address': '/dev/log',
            'facility': 'local0',
            'formatter': 'django',
        },
        'syslog_http': {
            'class': 'logging.handlers.SysLogHandler',
            'level': 'DEBUG',
            'address': '/dev/log',
            'facility': 'local0',
            'formatter': 'http',
        },

    },
    'loggers': {
        'django': {
            'handlers': [ 'syslog_django' ],
            'level': 'DEBUG',
        },
        'http': {
            'handlers': [ 'syslog_http' ],
            'level': 'DEBUG',
        },
    },
}

# Django REST Framework.

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTTokenUserAuthentication',
    ],

    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '600/minute',
        'user': '600/minute'
    },

    # Disable browser-view for APIs.
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=480),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'RS256',
    'SIGNING_KEY': '',
    'VERIFYING_KEY': JWT_TOKEN['publicKey'],
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(minutes=480),
}

# Variables.

# Consul adaptive connector: automatically configures any api-* service provided by Consul's agent.
API_BACKEND_BASE_URL = dict()
API_BACKEND_PROTOCOL = "http://"

try:
    ss, st, o = Process.execute("consul catalog services")
    if ss and o:
        for service in o.split("\n"):
            if service and "api-" in service:
                # service like: api-f5.
                technology = service.replace("api-", "")

                try:
                    apiAddress = str(consulResolver.query(service+".service.consul")[0])
                    apiPort = str(str(consulResolver.query(service+".service.consul", "SRV")[0]).split(" ")[2])

                    API_BACKEND_BASE_URL[technology] = API_BACKEND_PROTOCOL+apiAddress+":"+apiPort+"/api/v1/" # from Consul agent's local resolver.
                except Exception:
                    pass
except Exception:
    pass

API_SUPPLICANT_NETWORK_TIMEOUT = 300 # seconds.
API_SUPPLICANT_CACHE_VALIDITY = 60*60*24 # seconds.
