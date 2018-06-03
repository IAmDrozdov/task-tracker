from setuptools import setup

setup(
    name='calendoola',
    version='1.0',
    packages=[
        'calelib',
        'calelib.models',
    ],
    install_requires=[
        'colorama',
        'argcomplete',
    ],
    data_files=['manage.py', 'settings.py']
    , include_package_data=True

)
