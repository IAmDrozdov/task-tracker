import os

from setuptools import setup
from setuptools.command.install import install


class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        os.system('sudo -u postgres psql -c "create user calendoola password \'1111\'"')
        os.system('sudo -u postgres psql -c "create database calendoola_db owner calendoola"')
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'calelib.database_settings.settings')
        from django.core.management import execute_from_command_line
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
        'colorama',
        'argcomplete',
    ],
    cmdclass={
        'install': CustomInstallCommand,
    },
    data_files=['manage.py'],
    include_package_data=True
)
