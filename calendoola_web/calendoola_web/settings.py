import os

from django.contrib.messages import constants as messages

DEBUG = True

ALLOWED_HOSTS = []

SECRET_KEY = '123'
LOGIN_REDIRECT_URL = 'homepage'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'calelib',
    'widget_tweaks',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'caleweb.middleware.CalendoolaMiddleware',

]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'calendoola_db',
        'USER': 'calendoola',
        'PASSWORD': '1111',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
ROOT_URLCONF = 'calendoola_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['caleweb/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'plan_period_filter': 'caleweb.templatetags.plan_period_filter',
                'tags_display_filter': 'caleweb.templatetags.tags_display_filter',
                'task_colorize_priority': 'caleweb.templatetags.task_colorize_priority',
            },
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 4,
        }
    },
]

STATICFILES_DIRS = [
    os.path.join('caleweb', "static"),
]
STATIC_URL = '/caleweb/static/'
STATIC_ROOT = 'calendoola_web/caleweb/static'

LANGUAGE_CODE = 'en-us'
USE_TZ = True
TIME_ZONE = 'Europe/Minsk'

MESSAGE_TAGS = {
    messages.INFO: 'alert-info',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}
