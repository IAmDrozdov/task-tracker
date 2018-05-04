from os.path import join, dirname

from setuptools import setup, find_packages

setup(
    name='Calendoola',
    version='0.9',
    packages=find_packages(),
    description='To-do tracker',
    test_suite='tests',
    url='https://bitbucket.org/sashasashadrozdov/calendoola',
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    install_requires=[
        'colorama', 'jsonpickle', 'argcomplete'
    ]
)
