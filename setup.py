# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import sys

import listable

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = listable.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='django-listable',
    version=version,
    description='A reusable Django app to make integrations with the DataTables javascript library easy.',
    long_description=readme + '\n\n' + history,
    author='Randle Taylor',
    author_email='randle.taylor@gmail.com',
    url='https://github.com/randlet/django-listable',
    packages=[
        'listable',
    ],
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='django-listable',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)