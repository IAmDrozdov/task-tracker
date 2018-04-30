from os.path import join, dirname

from setuptools import setup, find_packages

setup(
    name='Calendoola',
    version='0.9',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    install_requires=[
        'colorama', 'jsonpickle', 'argcomplete'
    ]
)
