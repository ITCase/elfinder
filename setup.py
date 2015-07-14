import os

from setuptools import setup

version = '0.0.3'

here = os.path.dirname(os.path.realpath(__file__))


def read(name):
    with open(os.path.join(here, name)) as f:
        return f.read()

setup(
    name='elfinder',
    version=version,
    url='http://github.com/ITCase/elfinder/',
    author='Svintsov Dmitry',
    author_email='sacrud@uralbash.ru',

    py_modules=['elfinder'],

    license="BSD",
    description='elFinder connector for python.',
    long_description=read('README.rst'),
    install_requires=read('requirements.txt'),

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Internet",
        "Topic :: Multimedia",
    ],
)
