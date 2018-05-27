from setuptools import setup

setup(
    name='calendoola',
    version='1.0',
    packages=[
        'calelib',
        'calelib.db',
        'calelib.etc',
        'calelib.models',
        'calelib.modules'
    ],
    install_requires=[
        'colorama',
        'jsonpickle',
        'argcomplete',
    ]
)
