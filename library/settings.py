DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'calendoola_db',
        'USER': 'calendoola',
        'PASSWORD': '1111',
        'HOST': 'localhost',
        'PORT': '',
    }
}
INSTALLED_APPS = (
    'django.contrib.postgres',
    'calelib',

)

SECRET_KEY = 'REPLACE_ME'
USE_TZ = True
TIME_ZONE = 'Europe/Minsk'
