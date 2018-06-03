DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'primarydb',
        'USER': 'test',
        'PASSWORD': '1111',
        'HOST': 'localhost',
        'PORT': '',
    }
}

INSTALLED_APPS = (
    'calelib',
    'django.contrib.postgres',
)

SECRET_KEY = 'REPLACE_ME'
USE_TZ = True
TIME_ZONE = 'UTC'
