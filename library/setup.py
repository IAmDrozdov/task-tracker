from setuptools import setup

setup(
    name='calendoola',
    version='1.0',
    packages=[
        'calelib',
        'calelib.models',
        'postgres',
    ],
    install_requires=[
        'colorama',
        'argcomplete',
    ]
    , include_package_data=True

)
