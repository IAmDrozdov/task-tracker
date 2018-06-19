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
    entry_points={
        'console_scripts': [
            'calendoola_cli = calendoola_cli.__main__:main'
        ]
    },
    data_files=['manage.py'],
    include_package_data=True
)
