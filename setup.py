import os

from setuptools import setup, find_packages

version = '0.0.4.dev1'

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

    packages=find_packages(),
    include_package_data=True,

    license="MIT",
    description='elFinder connector for python.',
    long_description=read('README.rst'),
    install_requires=read('requirements.txt'),
    tests_require=read('requirements.txt') + read('requirements-test.txt'),
    test_suite="nose.collector",

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
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
