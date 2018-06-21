import os

from django.core.management import execute_from_command_line
from setuptools import setup
from setuptools.command.install import install


class CalendoolaLibraryInstallCommand(install):
    def run(self):
        install.run(self)
        os.system('sudo -u postgres psql -c "create user calendoola password \'1111\'"')
        os.system('sudo -u postgres psql -c "create database testing_calendoola_db owner calendoola"')
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'calelib.database_settings.testing_settings')
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])

        os.system('sudo -u postgres psql -c "create database calendoola_db owner calendoola"')
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'calelib.database_settings.settings')
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])


setup(
    name='calendoola',
    version='1.0',
    packages=[
        'calelib',
        'calelib.models',
        'calelib.database_settings'
    ],
    install_requires=[
        'django==1.11',
        'psycopg2',
    ],
    cmdclass={
        'install': CalendoolaLibraryInstallCommand,
    },
    data_files=['manage.py'],
    include_package_data=True
)
