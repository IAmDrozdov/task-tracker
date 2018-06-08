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
INSTALLED_APPS = (
    'django.contrib.postgres',
    'calelib',

)

SECRET_KEY = 'REPLACE_ME'
USE_TZ = True
TIME_ZONE = 'Europe/Minsk'
