from setuptools import setup

setup(
    name='calendoola',
    version='1.0',
    packages=[
        'calelib',
        'calelib.models',
        'calelib.database_settings',
    ],
    install_requires=[
        'colorama',
        'argcomplete',
    ],
    data_files=['settings.py', 'manage.py']
    , include_package_data=True
)
