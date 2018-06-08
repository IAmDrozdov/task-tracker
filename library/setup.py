import os

from setuptools import setup
from setuptools.command.install import install


class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        psql_cmd_create_user = "create user {} password '{}'".format('calendoola',
                                                                     '1111')
        os.system("sudo -u postgres psql -c \"{}\"".format(psql_cmd_create_user))
        psql_cmd_create_db = "create database {} owner {}".format('calendoola_db',
                                                                  'calendoola')
        os.system("sudo -u postgres psql -c '{}'".format(psql_cmd_create_db))
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
