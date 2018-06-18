from setuptools import setup

setup(
    name='calendoola_cli',
    version='1.0',
    packages=[
        'calendoola_cli',
    ],
    install_requires=[
        'colorama',
        'argcomplete',
    ],
    data_files=['manage.py'],
    include_package_data=True
)
